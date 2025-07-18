-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 13, 2025 at 06:29 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `prediksi_rumah`
--

-- --------------------------------------------------------

--
-- Table structure for table `prediksi`
--

CREATE TABLE `prediksi` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `daerah` int(11) NOT NULL,
  `luas_tanah` float NOT NULL,
  `luas_bangunan` float NOT NULL,
  `ac` tinyint(1) NOT NULL DEFAULT 1,
  `akses_parkir` tinyint(1) NOT NULL DEFAULT 1,
  `carport` tinyint(1) NOT NULL DEFAULT 1,
  `cctv` tinyint(1) NOT NULL DEFAULT 1,
  `gerbang_utama` tinyint(1) NOT NULL DEFAULT 1,
  `jalur_telepon` tinyint(1) NOT NULL DEFAULT 1,
  `jogging_track` tinyint(1) NOT NULL DEFAULT 1,
  `kitchen_set` tinyint(1) NOT NULL DEFAULT 1,
  `kolam_ikan` tinyint(1) NOT NULL DEFAULT 1,
  `kolam_renang` tinyint(1) NOT NULL DEFAULT 1,
  `kulkas` tinyint(1) NOT NULL DEFAULT 1,
  `lapangan_basket` tinyint(1) NOT NULL DEFAULT 1,
  `lapangan_bola` tinyint(1) NOT NULL DEFAULT 1,
  `lapangan_bulu_tangkis` tinyint(1) NOT NULL DEFAULT 1,
  `lapangan_tenis` tinyint(1) NOT NULL DEFAULT 1,
  `lapangan_voli` tinyint(1) NOT NULL DEFAULT 1,
  `masjid` tinyint(1) NOT NULL DEFAULT 1,
  `mesin_cuci` tinyint(1) NOT NULL DEFAULT 1,
  `pemanas_air` tinyint(1) NOT NULL DEFAULT 1,
  `playground` tinyint(1) NOT NULL DEFAULT 1,
  `taman` tinyint(1) NOT NULL DEFAULT 1,
  `tempat_gym` tinyint(1) NOT NULL DEFAULT 1,
  `tempat_jemuran` tinyint(1) NOT NULL DEFAULT 1,
  `tempat_laundry` tinyint(1) NOT NULL DEFAULT 1,
  `hasil_prediksi` bigint(20) NOT NULL,
  `created_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `prediksi`
--

INSERT INTO `prediksi` (`id`, `user_id`, `daerah`, `luas_tanah`, `luas_bangunan`, `ac`, `akses_parkir`, `carport`, `cctv`, `gerbang_utama`, `jalur_telepon`, `jogging_track`, `kitchen_set`, `kolam_ikan`, `kolam_renang`, `kulkas`, `lapangan_basket`, `lapangan_bola`, `lapangan_bulu_tangkis`, `lapangan_tenis`, `lapangan_voli`, `masjid`, `mesin_cuci`, `pemanas_air`, `playground`, `taman`, `tempat_gym`, `tempat_jemuran`, `tempat_laundry`, `hasil_prediksi`, `created_at`) VALUES
(9, 3, 56, 99, 75, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 541392105, '2025-05-13 22:50:06'),
(10, 3, 41, 155, 125, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 698355833, '2025-05-13 23:25:30');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `nama` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `create_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `nama`, `email`, `password`, `create_at`) VALUES
(1, 'Mai Tasa Wilia', 'maitasaw@gmail.com', '123454321', '2025-05-07 04:05:55'),
(2, 'Mai Tasa Wilia', 'maitasaw21@gmail.com', 'scrypt:32768:8:1$7Xae68jo2MKPaOU9$171a1791030f2a2aaa5145f4d6a93a6f2b8be8ba5461ba8d3c43ffae78714ddf9162eb69fb1f58b9b860bcc3767772905a3bdcee3b53b7e0962ecdfcdf810378', '0000-00-00 00:00:00'),
(3, 'tata', 'tata@gmail.com', 'scrypt:32768:8:1$jnZtSNhCffzn44kb$64559b8392c04aeeece94c8916dc18712e5562ab004653bdf7d222453b935e1d571cf995380e5b7aa570f6c32b5bdff8409f71748ec71e5db7bb9aca92385214', '0000-00-00 00:00:00');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `prediksi`
--
ALTER TABLE `prediksi`
  ADD PRIMARY KEY (`id`),
  ADD KEY `prediksi_user_id` (`user_id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `prediksi`
--
ALTER TABLE `prediksi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `prediksi`
--
ALTER TABLE `prediksi`
  ADD CONSTRAINT `prediksi_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
