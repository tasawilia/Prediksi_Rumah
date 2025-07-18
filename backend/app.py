from flask import Flask, jsonify, request, redirect
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import traceback

import pandas as pd
import numpy as np  # Pastikan numpy diimport untuk expm1 dan perhitungan
import joblib

app = Flask(__name__)
CORS(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'prediksi_rumah'
app.config['MYSQL_SSL_DISABLED'] = True

app.config["JWT_SECRET_KEY"] = "your-secret-key"  
jwt = JWTManager(app)

mysql = MySQL(app)

# mapping_daerah harus pakai lowercase dan strip
mapping_daerah_df = pd.read_csv('mapping_daerah.csv')
mapping_daerah_df.columns = mapping_daerah_df.columns.str.strip()
mapping_daerah = {
    nama.strip().lower(): kode
    for nama, kode in zip(mapping_daerah_df['Daerah'], mapping_daerah_df['Kode'])
}

# mapping_koordinat juga pakai nama daerah lowercase dan strip
mapping_koordinat_df = pd.read_csv("mapping_daerah_koordinat.csv")
mapping_koordinat_df.columns = mapping_koordinat_df.columns.str.strip()
mapping_koordinat = {
    row["Daerah"].strip().lower(): (row["Garis_Lintang"], row["Garis_Bujur"])
    for _, row in mapping_koordinat_df.iterrows()
}


@app.route('/')
def root():
    return redirect('/login')

from werkzeug.security import check_password_hash

@app.route("/token", methods=["GET"])
def get_token():
    token = create_access_token(identity={"user_id": 1})
    return jsonify(access_token=token)

@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    return jsonify(message="Access granted")

#--------------------------------------------------login-----------------------------------------------
from werkzeug.security import check_password_hash

@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email dan password harus diisi'}), 400

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, nama, email, password FROM user WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[3], password):
            access_token = create_access_token(identity={'id': user[0], 'email': user[2]})
            return jsonify({
                'message': 'Login berhasil',
                'token': access_token,
                'user': {
                    'id': user[0],
                    'nama': user[1],
                    'email': user[2]
                }
            }), 200
        else:
            return jsonify({'error': 'Email atau password salah'}), 401

    return jsonify({'error': 'Request harus dalam format JSON'}), 400

#--------------------------------------------------regis-----------------------------------------------
@app.route('/register', methods=['POST'])
def register():
    if request.is_json:
        data = request.get_json()
        
        nama = data.get('nama')
        email = data.get('email')
        password = data.get('password')
        konfirmasi_password = data.get('konfirmasiPassword')  # Ambil field konfirmasiPassword jika dikirim

        if not (nama and email and password):
            return jsonify({'error': 'Nama, email, dan password harus diisi'}), 400


        # Konfirmasi password wajib diisi
        if konfirmasi_password is None:
            return jsonify({'error': 'Konfirmasi password harus diisi'}), 400
        # Validasi konfirmasi password
        if password != konfirmasi_password:
            return jsonify({'error': 'Password dan konfirmasi password tidak sama'}), 400

        # Periksa apakah email sudah terdaftar
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT email FROM user WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        cursor.close()

        if existing_user:
            return jsonify({'error': 'Email sudah terdaftar'}), 400

        hashed_password = generate_password_hash(password)


        from datetime import datetime
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO user (nama, email, password, create_at) VALUES (%s, %s, %s, %s)",
            (nama, email, hashed_password, datetime.now())
        )
        mysql.connection.commit()
        cursor.close()

        return jsonify({
            'user': {
            'nama': nama,
            'email': email
        }
        }), 200
    return jsonify({'error': 'Request harus dalam format JSON'}), 400

#--------------------------------------------------prediksi harga-----------------------------------------------
# Load model dan mapping
model_bundle = joblib.load("model_prediksi1_rumah.pkl")
model = model_bundle['model']
scaler = model_bundle['scaler']
selector = model_bundle['selector']
kmeans = model_bundle['kmeans']
log_transform_applied = model_bundle['log_transform_applied']
selected_features = model_bundle['selected_features']

# Gunakan mapping dari file koordinat saja (sudah lengkap)
mapping_df = pd.read_csv("mapping_daerah_koordinat.csv")
mapping_daerah = dict(zip(mapping_df["Daerah"], mapping_df["Kode"]))
mapping_kode = mapping_daerah  # Tidak perlu ulang baca


# Membalikkan mapping untuk daerah_id ke nama daerah
daerah_dict = {v: k for k, v in mapping_daerah.items()}

# Load mapping daerah + koordinat
mapping_df = pd.read_csv("mapping_daerah_koordinat.csv")

# Buat dictionary nama daerah -> kode
mapping_kode = dict(zip(mapping_df["Daerah"], mapping_df["Kode"]))

# Buat dictionary nama daerah -> (garis_lintang, garis_bujur)
mapping_df["Garis_Lintang"] = mapping_df["Garis_Lintang"].astype(str).str.replace(",", ".").astype(float)
mapping_df["Garis_Bujur"] = mapping_df["Garis_Bujur"].astype(str).str.replace(",", ".").astype(float)
mapping_koordinat = {
    row["Daerah"]: (row["Garis_Lintang"], row["Garis_Bujur"])
    for _, row in mapping_df.iterrows()
}

# Daftar fasilitas sesuai model training (One-Hot Encoding)
fasilitas_all = [
    "Ac", "Akses Parkir", "Carport", "Cctv", "Cuci Tangan", "Gerbang Utama",
    "Jalur Telepon", "Jogging Track", "Keamanan 24 Jam", "Kitchen Set", "Kolam Ikan",
    "Kolam Renang", "Kulkas", "Lapangan Basket", "Lapangan Bola", "Lapangan Bulu Tangkis",
    "Lapangan Tenis", "Lapangan Voli", "Masjid", "Mesin Cuci", "Pemanas Air",
    "Playground", "Taman", "Tempat Gym", "Tempat Jemuran", "Tempat Laundry"
]

@app.route("/prediksi", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        daerah = data.get("daerah")
        luas_tanah = float(data.get("luas_tanah", 0))
        luas_bangunan = float(data.get("luas_bangunan", 0))
        fasilitas_input = data.get("fasilitas", [])

        if not daerah or daerah not in mapping_kode:
            return jsonify({"error": "Daerah tidak valid"}), 400
        if luas_tanah <= 0 or luas_bangunan <= 0:
            return jsonify({"error": "Luas tanah dan bangunan harus lebih dari 0"}), 400

        fasilitas_encoded = {f: 1 if f in fasilitas_input else 0 for f in fasilitas_all}

        garis_lintang, garis_bujur = mapping_koordinat[daerah]

        # Fitur turunan
        rasio_luas = luas_bangunan / (luas_tanah + 1e-6)
        jumlah_fasilitas = sum(fasilitas_encoded.values())
        luas_total = luas_tanah + luas_bangunan
        perbandingan_luas = luas_bangunan / (luas_tanah + 1e-6)
        fasilitas_premium = int(
            fasilitas_encoded.get("Kolam Renang", 0) == 1 or
            fasilitas_encoded.get("Keamanan 24 Jam", 0) == 1 or
            fasilitas_encoded.get("Playground", 0) == 1
        )

        # Data input lengkap
        input_data = {
            "Daerah": mapping_kode[daerah],
            "Garis_Lintang": float(str(garis_lintang).replace(",", ".")),
            "Garis_Bujur": float(str(garis_bujur).replace(",", ".")),
            "Luas_Tanah": luas_tanah,
            "Luas_Bangunan": luas_bangunan,
            "Rasio_Luas": rasio_luas,
            "Jumlah_Fasilitas": jumlah_fasilitas,
            "Luas_Total": luas_total,
            "Perbandingan_Luas": perbandingan_luas,
            "Fasilitas_Premium": fasilitas_premium,
            **fasilitas_encoded
        }

        df_input = pd.DataFrame([input_data])

        # Cluster lokasi
        df_input["Lokasi_Cluster"] = kmeans.predict(df_input[["Garis_Lintang", "Garis_Bujur"]])

        # Standarisasi numerik (harus sama dengan training)
        numeric_cols = [
            "Garis_Lintang", "Garis_Bujur", "Luas_Tanah", "Luas_Bangunan",
            "Rasio_Luas", "Jumlah_Fasilitas", "Luas_Total", "Perbandingan_Luas"
        ]
        df_input[numeric_cols] = scaler.transform(df_input[numeric_cols])

        # Urutkan kolom sesuai training
        df_input = df_input.reindex(columns=selected_features)

        # Seleksi fitur
        X_selected = selector.transform(df_input)

        prediksi = model.predict(X_selected)[0]
        if log_transform_applied:
            prediksi = np.expm1(prediksi)

        return jsonify({"prediksi_harga": round(prediksi)})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Terjadi kesalahan server: {str(e)}"}), 500

@app.route("/daerah", methods=["GET"])
def get_daerah():
    # Ambil urutan asli dari file mapping_daerah.csv
    mapping_daerah_df = pd.read_csv('mapping_daerah.csv')
    daftar_daerah = mapping_daerah_df['Daerah'].astype(str).str.strip().tolist()
    return jsonify(daftar_daerah)

#--------------------------------------------------simpan prediksi-----------------------------------------------

@app.route('/simpan', methods=['POST'])
def simpan_prediksi():
    data = request.json
    try:
        cursor = mysql.connection.cursor()

        user_id = int(data.get('user_id'))
        daerah_input = data.get('daerah', '').strip().lower()  # Normalisasi input
        luas_tanah = data.get('luas_tanah')
        luas_bangunan = data.get('luas_bangunan')
        prediksi_harga = data.get('prediksi_harga')
        fasilitas = data.get('fasilitas', [])

        print(f"Daerah yang diterima: {daerah_input}")  # Debugging

        # Cek apakah daerah dikenali, normalisasi key pada mapping_daerah
        normalized_mapping_daerah = {key.lower(): value for key, value in mapping_daerah.items()}
        
        if daerah_input not in normalized_mapping_daerah:
            return jsonify({'error': f"Daerah '{data.get('daerah')}' tidak ditemukan dalam mapping."}), 400

        daerah_kode = normalized_mapping_daerah[daerah_input]

        all_fasilitas = [
            "Ac", "Akses Parkir", "Carport", "Cctv", "Gerbang Utama", "Jalur Telepon",
            "Jogging Track", "Kitchen Set", "Kolam Ikan", "Kolam Renang", "Kulkas",
            "Lapangan Basket", "Lapangan Bola", "Lapangan Bulu Tangkis", "Lapangan Tenis",
            "Lapangan Voli", "Masjid", "Mesin Cuci", "Pemanas Air", "Playground",
            "Taman", "Tempat Gym", "Tempat Jemuran", "Tempat Laundry"
        ]
        fasilitas_data = [1 if f in fasilitas else 0 for f in all_fasilitas]

        query = f"""
            INSERT INTO prediksi (
                user_id, daerah, luas_tanah, luas_bangunan,
                {", ".join(f.lower().replace(" ", "_") for f in all_fasilitas)},
                hasil_prediksi, created_at
            )
            VALUES (
                %s, %s, %s, %s,
                {", ".join(["%s"] * len(all_fasilitas))},
                %s, %s
            )
        """
        values = [user_id, daerah_kode, luas_tanah, luas_bangunan] + fasilitas_data + [prediksi_harga, datetime.now()]
        cursor.execute(query, values)
        mysql.connection.commit()

        return jsonify({"message": "Data berhasil disimpan."}), 200

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

#--------------------------------------------------riwayat prediksi-----------------------------------------------
@app.route('/riwayat/<int:user_id>')
def riwayat(user_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM prediksi WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        rows = cursor.fetchall()

        column_names = [desc[0] for desc in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]

        # Proses hasil untuk mengganti kode daerah dengan nama daerah
        for item in results:
            encoded = item.get('daerah')
            item['daerah'] = daerah_dict.get(encoded, f"Daerah-{encoded}")  # Menggunakan daerah_dict untuk mendapatkan nama daerah

            # Format created_at jadi string
            if isinstance(item['created_at'], datetime):
                item['created_at'] = item['created_at'].strftime('%Y-%m-%dT%H:%M:%S')

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#--------------------------------------------------hapus riwayat prediksi-----------------------------------------------
@app.route('/riwayat/<int:id>', methods=['DELETE'])
def hapus_riwayat(id):
    try:
        cur = mysql.connection.cursor()
        # Periksa apakah data dengan ID tersebut ada
        cur.execute("SELECT * FROM prediksi WHERE id = %s", (id,))
        data = cur.fetchone()

        if data:
            cur.execute("DELETE FROM prediksi WHERE id = %s", (id,))
            mysql.connection.commit()
            return jsonify({'message': 'Riwayat berhasil dihapus.'}), 200
        else:
            return jsonify({'message': 'Riwayat tidak ditemukan.'}), 404
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'message': f'Error: {str(e)}'}), 500


#--------------------------------------------------profil-----------------------------------------------
@app.route('/userProfilUpdate', methods=['PUT'])
def update_profil():
    try:
        # Ambil data dari frontend
        data = request.get_json()
        print("[DEBUG] Data diterima dari frontend:", data)

        user_id = data.get('id')
        nama = data.get('nama')
        email = data.get('email')
        password = data.get('password')

        # Log nilai input untuk memastikan semuanya terbaca
        print(f"[DEBUG] user_id={user_id}, nama={nama}, email={email}, password={'ADA' if password else 'TIDAK ADA'}")

        # Validasi input wajib
        if not user_id or not nama or not email:
            print("[ERROR] Validasi gagal: data tidak lengkap")
            return jsonify({'error': 'Data tidak lengkap'}), 400

        # Mulai query ke database
        cursor = mysql.connection.cursor()

        if password:
            hashed_password = generate_password_hash(password)
            cursor.execute("""
                UPDATE user SET nama = %s, email = %s, password = %s WHERE id = %s
            """, (nama, email, hashed_password, user_id))
        else:
            cursor.execute("""
                UPDATE user SET nama = %s, email = %s WHERE id = %s
            """, (nama, email, user_id))

        mysql.connection.commit()
        cursor.close()

        print(f"[INFO] User ID {user_id} berhasil diperbarui.")
        return jsonify({
            'message': 'Profil berhasil diperbarui',
            'user': {
                'id': user_id,
                'nama': nama,
                'email': email
            }
        }), 200

    except Exception as e:
        print("[FATAL] Terjadi error saat update profil:")
        traceback.print_exc()
        return jsonify({'error': f'Gagal menyimpan perubahan. {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)