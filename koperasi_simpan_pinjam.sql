-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 14 Mar 2026 pada 05.47
-- Versi server: 10.4.32-MariaDB
-- Versi PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `koperasi_sp`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `anggota`
--

CREATE TABLE `anggota` (
  `id_anggota` int(11) NOT NULL,
  `no_anggota` varchar(20) NOT NULL,
  `nama_lengkap` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `no_telepon` varchar(15) DEFAULT NULL,
  `tanggal_bergabung` date NOT NULL,
  `status` enum('aktif','non-aktif','keluar') DEFAULT 'aktif',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `anggota`
--

INSERT INTO `anggota` (`id_anggota`, `no_anggota`, `nama_lengkap`, `email`, `no_telepon`, `tanggal_bergabung`, `status`, `created_at`, `updated_at`) VALUES
(1, 'A-20260313-001', 'Susanto Jaidi', 'susanto@gmail.com', '081736183', '2026-03-13', 'aktif', '2026-03-13 08:38:19', '2026-03-13 08:38:19'),
(2, 'A-20260313-002', 'Bambang Yuda', 'yuda@gmail.com', '087318318', '2026-03-13', 'aktif', '2026-03-13 13:13:29', '2026-03-13 13:13:29'),
(3, 'A-20260313-003', 'Budi Sulaiman', 'sulaiman@gmail.com', '083184880', '2026-03-01', 'aktif', '2026-03-13 13:14:29', '2026-03-13 13:14:29'),
(4, 'A-20260313-004', 'Pipit Muenah', 'pipit@gmail.com', '089712871', '2026-03-11', 'aktif', '2026-03-13 13:15:46', '2026-03-13 13:15:46');

-- --------------------------------------------------------

--
-- Struktur dari tabel `angsuran`
--

CREATE TABLE `angsuran` (
  `id_angsuran` int(11) NOT NULL,
  `id_pinjaman` int(11) NOT NULL,
  `no_angsuran` varchar(30) NOT NULL,
  `angsuran_ke` int(11) NOT NULL,
  `tanggal_jatuh_tempo` date NOT NULL,
  `nominal_angsuran` decimal(15,2) NOT NULL,
  `pokok` decimal(15,2) NOT NULL,
  `bunga` decimal(15,2) NOT NULL,
  `denda` decimal(15,2) DEFAULT 0.00,
  `total_bayar` decimal(15,2) DEFAULT 0.00,
  `tanggal_bayar` date DEFAULT NULL,
  `status` enum('belum_bayar','lunas','terlambat') DEFAULT 'belum_bayar',
  `keterangan` text DEFAULT NULL,
  `id_user` int(11) DEFAULT NULL COMMENT 'User yang mencatat pembayaran',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `angsuran`
--

INSERT INTO `angsuran` (`id_angsuran`, `id_pinjaman`, `no_angsuran`, `angsuran_ke`, `tanggal_jatuh_tempo`, `nominal_angsuran`, `pokok`, `bunga`, `denda`, `total_bayar`, `tanggal_bayar`, `status`, `keterangan`, `id_user`, `created_at`, `updated_at`) VALUES
(1, 1, 'ANG-20260314-1-1', 1, '2026-04-13', 425000.00, 416666.67, 8333.33, 0.00, 425000.00, '2026-03-13', 'lunas', NULL, 3, '2026-03-13 18:08:44', '2026-03-13 20:19:46'),
(2, 1, 'ANG-20260314-1-2', 2, '2026-05-13', 425000.00, 416666.67, 8333.33, 0.00, 0.00, NULL, 'belum_bayar', NULL, NULL, '2026-03-13 18:08:44', '2026-03-13 18:08:44'),
(3, 1, 'ANG-20260314-1-3', 3, '2026-06-13', 425000.00, 416666.67, 8333.33, 0.00, 0.00, NULL, 'belum_bayar', NULL, NULL, '2026-03-13 18:08:44', '2026-03-13 18:08:44'),
(4, 1, 'ANG-20260314-1-4', 4, '2026-07-13', 425000.00, 416666.67, 8333.33, 0.00, 0.00, NULL, 'belum_bayar', NULL, NULL, '2026-03-13 18:08:44', '2026-03-13 18:08:44'),
(5, 1, 'ANG-20260314-1-5', 5, '2026-08-13', 425000.00, 416666.67, 8333.33, 0.00, 0.00, NULL, 'belum_bayar', NULL, NULL, '2026-03-13 18:08:44', '2026-03-13 18:08:44'),
(6, 1, 'ANG-20260314-1-6', 6, '2026-09-13', 425000.00, 416666.67, 8333.33, 0.00, 0.00, NULL, 'belum_bayar', NULL, NULL, '2026-03-13 18:08:44', '2026-03-13 18:08:44'),
(7, 1, 'ANG-20260314-1-7', 7, '2026-10-13', 425000.00, 416666.67, 8333.33, 0.00, 0.00, NULL, 'belum_bayar', NULL, NULL, '2026-03-13 18:08:44', '2026-03-13 18:08:44'),
(8, 1, 'ANG-20260314-1-8', 8, '2026-11-13', 425000.00, 416666.67, 8333.33, 0.00, 0.00, NULL, 'belum_bayar', NULL, NULL, '2026-03-13 18:08:44', '2026-03-13 18:08:44'),
(9, 1, 'ANG-20260314-1-9', 9, '2026-12-13', 425000.00, 416666.67, 8333.33, 0.00, 0.00, NULL, 'belum_bayar', NULL, NULL, '2026-03-13 18:08:44', '2026-03-13 18:08:44'),
(10, 1, 'ANG-20260314-1-10', 10, '2027-01-13', 425000.00, 416666.67, 8333.33, 0.00, 0.00, NULL, 'belum_bayar', NULL, NULL, '2026-03-13 18:08:44', '2026-03-13 18:08:44'),
(11, 1, 'ANG-20260314-1-11', 11, '2027-02-13', 425000.00, 416666.67, 8333.33, 0.00, 0.00, NULL, 'belum_bayar', NULL, NULL, '2026-03-13 18:08:44', '2026-03-13 18:08:44'),
(12, 1, 'ANG-20260314-1-12', 12, '2027-03-13', 516666.67, 508333.33, 8333.33, 0.00, 0.00, NULL, 'belum_bayar', NULL, NULL, '2026-03-13 18:08:44', '2026-03-13 18:08:44');

-- --------------------------------------------------------

--
-- Struktur dari tabel `jenis_simpanan`
--

CREATE TABLE `jenis_simpanan` (
  `id_jenis_simpanan` int(11) NOT NULL,
  `kode_jenis` varchar(10) NOT NULL,
  `nama_jenis` varchar(50) NOT NULL,
  `deskripsi` text DEFAULT NULL,
  `is_wajib` tinyint(1) DEFAULT 0,
  `nominal_tetap` decimal(15,2) DEFAULT 0.00,
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `jenis_simpanan`
--

INSERT INTO `jenis_simpanan` (`id_jenis_simpanan`, `kode_jenis`, `nama_jenis`, `deskripsi`, `is_wajib`, `nominal_tetap`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 'SP', 'Simpanan Pokok', 'Simpanan yang dibayarkan saat pertama kali menjadi anggota', 1, 100000.00, 1, '2026-02-02 10:00:30', '2026-02-02 10:00:30'),
(2, 'SW', 'Simpanan Wajib', 'Simpanan yang wajib dibayar setiap bulan', 1, 50000.00, 1, '2026-02-02 10:00:30', '2026-02-02 10:00:30'),
(3, 'SS', 'Simpanan Sukarela', 'Simpanan yang bersifat sukarela dan dapat diambil sewaktu-waktu', 0, 0.00, 1, '2026-02-02 10:00:30', '2026-02-02 10:00:30');

-- --------------------------------------------------------

--
-- Struktur dari tabel `pinjaman`
--

CREATE TABLE `pinjaman` (
  `id_pinjaman` int(11) NOT NULL,
  `id_anggota` int(11) NOT NULL,
  `no_pinjaman` varchar(30) NOT NULL,
  `tanggal_pengajuan` date NOT NULL,
  `nominal_pinjaman` decimal(15,2) NOT NULL,
  `bunga_persen` decimal(5,2) NOT NULL DEFAULT 0.00,
  `total_bunga` decimal(15,2) NOT NULL DEFAULT 0.00,
  `total_pinjaman` decimal(15,2) NOT NULL,
  `lama_angsuran` int(11) NOT NULL COMMENT 'dalam bulan',
  `nominal_angsuran` decimal(15,2) NOT NULL,
  `keperluan` text DEFAULT NULL,
  `status` enum('pending','disetujui','ditolak','lunas') DEFAULT 'pending',
  `tanggal_persetujuan` date DEFAULT NULL,
  `tanggal_pencairan` date DEFAULT NULL,
  `tanggal_lunas` date DEFAULT NULL,
  `id_user_pengaju` int(11) DEFAULT NULL COMMENT 'User yang input pengajuan',
  `id_user_persetujuan` int(11) DEFAULT NULL COMMENT 'Ketua yang menyetujui',
  `catatan_persetujuan` text DEFAULT NULL,
  `sisa_pinjaman` decimal(15,2) DEFAULT 0.00,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `pinjaman`
--

INSERT INTO `pinjaman` (`id_pinjaman`, `id_anggota`, `no_pinjaman`, `tanggal_pengajuan`, `nominal_pinjaman`, `bunga_persen`, `total_bunga`, `total_pinjaman`, `lama_angsuran`, `nominal_angsuran`, `keperluan`, `status`, `tanggal_persetujuan`, `tanggal_pencairan`, `tanggal_lunas`, `id_user_pengaju`, `id_user_persetujuan`, `catatan_persetujuan`, `sisa_pinjaman`, `created_at`, `updated_at`) VALUES
(1, 4, 'PJM-20260313-201734', '2026-03-13', 5000000.00, 2.00, 100000.00, 5100000.00, 12, 425000.00, 'Modal Usaha', 'disetujui', '2026-03-13', '2026-03-13', NULL, 1, 2, '', 4583333.33, '2026-03-13 13:17:34', '2026-03-13 20:19:46');

-- --------------------------------------------------------

--
-- Struktur dari tabel `pinjaman_syarat`
--

CREATE TABLE `pinjaman_syarat` (
  `id_pinjaman_syarat` int(11) NOT NULL,
  `id_pinjaman` int(11) NOT NULL,
  `id_syarat` int(11) NOT NULL,
  `is_terpenuhi` tinyint(1) DEFAULT 0 COMMENT 'Apakah syarat sudah terpenuhi',
  `dokumen_path` varchar(255) DEFAULT NULL COMMENT 'Path file dokumen jika ada',
  `catatan` text DEFAULT NULL COMMENT 'Catatan terkait pemenuhan syarat',
  `tanggal_verifikasi` timestamp NULL DEFAULT NULL COMMENT 'Tanggal verifikasi syarat',
  `id_user_verifikasi` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `profil_anggota`
--

CREATE TABLE `profil_anggota` (
  `id_profil` int(11) NOT NULL,
  `id_anggota` int(11) NOT NULL,
  `nik` varchar(16) DEFAULT NULL,
  `tempat_lahir` varchar(50) DEFAULT NULL,
  `tanggal_lahir` date DEFAULT NULL,
  `jenis_kelamin` enum('L','P') DEFAULT NULL,
  `alamat` text DEFAULT NULL,
  `kota` varchar(50) DEFAULT NULL,
  `provinsi` varchar(50) DEFAULT NULL,
  `kode_pos` varchar(10) DEFAULT NULL,
  `pekerjaan` varchar(50) DEFAULT NULL,
  `foto_profil` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `profil_anggota`
--

INSERT INTO `profil_anggota` (`id_profil`, `id_anggota`, `nik`, `tempat_lahir`, `tanggal_lahir`, `jenis_kelamin`, `alamat`, `kota`, `provinsi`, `kode_pos`, `pekerjaan`, `foto_profil`, `created_at`, `updated_at`) VALUES
(1, 4, '3214218941981', 'Cirebon', '1999-05-12', 'P', 'Jatibarang', 'Kab. Sumedang', 'Jawa Barat', '45311', 'Petani', NULL, '2026-03-13 17:45:44', '2026-03-14 04:36:26');

-- --------------------------------------------------------

--
-- Struktur dari tabel `simpanan`
--

CREATE TABLE `simpanan` (
  `id_simpanan` int(11) NOT NULL,
  `id_anggota` int(11) NOT NULL,
  `id_jenis_simpanan` int(11) NOT NULL,
  `no_transaksi` varchar(30) NOT NULL,
  `tanggal_transaksi` date NOT NULL,
  `tipe_transaksi` enum('setor','tarik') NOT NULL,
  `nominal` decimal(15,2) NOT NULL,
  `saldo_akhir` decimal(15,2) NOT NULL DEFAULT 0.00,
  `keterangan` text DEFAULT NULL,
  `id_user` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `simpanan`
--

INSERT INTO `simpanan` (`id_simpanan`, `id_anggota`, `id_jenis_simpanan`, `no_transaksi`, `tanggal_transaksi`, `tipe_transaksi`, `nominal`, `saldo_akhir`, `keterangan`, `id_user`, `created_at`, `updated_at`) VALUES
(1, 4, 2, 'TRX-20260314-005650', '2026-03-13', 'setor', 200000.00, 200000.00, NULL, 1, '2026-03-13 17:56:50', '2026-03-13 17:56:50');

-- --------------------------------------------------------

--
-- Struktur dari tabel `syarat_peminjaman`
--

CREATE TABLE `syarat_peminjaman` (
  `id_syarat` int(11) NOT NULL,
  `kode_syarat` varchar(20) NOT NULL,
  `nama_syarat` varchar(100) NOT NULL,
  `deskripsi` text DEFAULT NULL,
  `is_wajib` tinyint(1) DEFAULT 1 COMMENT 'Apakah syarat ini wajib dipenuhi',
  `min_nominal_pinjaman` decimal(15,2) DEFAULT NULL COMMENT 'Minimal nominal untuk syarat ini berlaku',
  `max_nominal_pinjaman` decimal(15,2) DEFAULT NULL COMMENT 'Maksimal nominal untuk syarat ini berlaku',
  `dokumen_diperlukan` varchar(255) DEFAULT NULL COMMENT 'Jenis dokumen yang diperlukan',
  `is_active` tinyint(1) DEFAULT 1,
  `urutan` int(11) DEFAULT 0 COMMENT 'Urutan tampilan',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `syarat_peminjaman`
--

INSERT INTO `syarat_peminjaman` (`id_syarat`, `kode_syarat`, `nama_syarat`, `deskripsi`, `is_wajib`, `min_nominal_pinjaman`, `max_nominal_pinjaman`, `dokumen_diperlukan`, `is_active`, `urutan`, `created_at`, `updated_at`) VALUES
(1, 'SYR001', 'Fotocopy KTP', 'Fotocopy KTP anggota yang masih berlaku', 1, NULL, NULL, 'KTP', 1, 1, '2026-03-11 16:21:00', '2026-03-11 16:21:00'),
(2, 'SYR002', 'Fotocopy KK', 'Fotocopy Kartu Keluarga', 1, NULL, NULL, 'KK', 1, 2, '2026-03-11 16:21:00', '2026-03-11 16:21:00'),
(3, 'SYR003', 'Slip Gaji', 'Slip gaji 3 bulan terakhir', 1, 5000000.00, NULL, 'Slip Gaji', 1, 3, '2026-03-11 16:21:00', '2026-03-11 16:21:00'),
(4, 'SYR004', 'Jaminan BPKB', 'BPKB kendaraan sebagai jaminan', 1, 10000000.00, NULL, 'BPKB', 1, 4, '2026-03-11 16:21:00', '2026-03-11 16:21:00'),
(5, 'SYR005', 'Surat Pernyataan', 'Surat pernyataan sanggup membayar angsuran', 1, NULL, NULL, 'Surat Pernyataan', 1, 5, '2026-03-11 16:21:00', '2026-03-11 16:21:00'),
(6, 'SYR006', 'Pas Foto 4x6', 'Pas foto terbaru ukuran 4x6', 0, NULL, NULL, 'Pas Foto', 1, 6, '2026-03-11 16:21:00', '2026-03-11 16:21:00'),
(7, 'SYR007', 'NPWP', 'Nomor Pokok Wajib Pajak', 0, 20000000.00, NULL, 'NPWP', 1, 7, '2026-03-11 16:21:00', '2026-03-11 16:21:00'),
(8, 'SYR008', 'Sertifikat Rumah', 'Sertifikat rumah sebagai jaminan tambahan', 0, 50000000.00, NULL, 'Sertifikat', 1, 8, '2026-03-11 16:21:00', '2026-03-11 16:21:00');

-- --------------------------------------------------------

--
-- Struktur dari tabel `user`
--

CREATE TABLE `user` (
  `id_user` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('admin','ketua','bendahara') NOT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `user`
--

INSERT INTO `user` (`id_user`, `username`, `password`, `role`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 'admin@koprasi.com', '$2b$12$WJKehEM1KG06rMPAC8y5HOTWGtzpySN/Mhs9Wg7riNoRN8T.Ny8qC', 'admin', 1, '2026-03-11 16:51:30', '2026-03-11 16:51:30'),
(2, 'ketua@koprasi.com', '$2b$12$rX.c9mDRSsxKMStOCSCi4e8DWT42QH7VUDluKpZ6u3wKHH6UmEYdm', 'ketua', 1, '2026-03-11 16:51:30', '2026-03-11 16:51:30'),
(3, 'bendahara@koprasi.com', '$2b$12$cN.ce7dO177gabY.9ENnh.ZBfitKYEE6N1BY0To4iBtoBacuWBxJy', 'bendahara', 1, '2026-03-11 16:51:30', '2026-03-11 16:51:30');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `anggota`
--
ALTER TABLE `anggota`
  ADD PRIMARY KEY (`id_anggota`),
  ADD UNIQUE KEY `no_anggota` (`no_anggota`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `idx_no_anggota` (`no_anggota`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_nama` (`nama_lengkap`);

--
-- Indeks untuk tabel `angsuran`
--
ALTER TABLE `angsuran`
  ADD PRIMARY KEY (`id_angsuran`),
  ADD UNIQUE KEY `no_angsuran` (`no_angsuran`),
  ADD UNIQUE KEY `unique_pinjaman_angsuran` (`id_pinjaman`,`angsuran_ke`),
  ADD KEY `id_user` (`id_user`),
  ADD KEY `idx_no_angsuran` (`no_angsuran`),
  ADD KEY `idx_pinjaman` (`id_pinjaman`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_jatuh_tempo` (`tanggal_jatuh_tempo`),
  ADD KEY `idx_tanggal_bayar` (`tanggal_bayar`);

--
-- Indeks untuk tabel `jenis_simpanan`
--
ALTER TABLE `jenis_simpanan`
  ADD PRIMARY KEY (`id_jenis_simpanan`),
  ADD UNIQUE KEY `kode_jenis` (`kode_jenis`),
  ADD KEY `idx_kode` (`kode_jenis`),
  ADD KEY `idx_active` (`is_active`);

--
-- Indeks untuk tabel `pinjaman`
--
ALTER TABLE `pinjaman`
  ADD PRIMARY KEY (`id_pinjaman`),
  ADD UNIQUE KEY `no_pinjaman` (`no_pinjaman`),
  ADD KEY `id_user_pengaju` (`id_user_pengaju`),
  ADD KEY `id_user_persetujuan` (`id_user_persetujuan`),
  ADD KEY `idx_no_pinjaman` (`no_pinjaman`),
  ADD KEY `idx_anggota` (`id_anggota`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_tanggal_pengajuan` (`tanggal_pengajuan`),
  ADD KEY `idx_tanggal_persetujuan` (`tanggal_persetujuan`);

--
-- Indeks untuk tabel `pinjaman_syarat`
--
ALTER TABLE `pinjaman_syarat`
  ADD PRIMARY KEY (`id_pinjaman_syarat`),
  ADD KEY `id_pinjaman` (`id_pinjaman`),
  ADD KEY `id_syarat` (`id_syarat`),
  ADD KEY `id_user_verifikasi` (`id_user_verifikasi`),
  ADD KEY `idx_pinjaman` (`id_pinjaman`),
  ADD KEY `idx_syarat` (`id_syarat`);

--
-- Indeks untuk tabel `profil_anggota`
--
ALTER TABLE `profil_anggota`
  ADD PRIMARY KEY (`id_profil`),
  ADD UNIQUE KEY `id_anggota` (`id_anggota`),
  ADD UNIQUE KEY `nik` (`nik`),
  ADD KEY `idx_nik` (`nik`),
  ADD KEY `idx_anggota` (`id_anggota`);

--
-- Indeks untuk tabel `simpanan`
--
ALTER TABLE `simpanan`
  ADD PRIMARY KEY (`id_simpanan`),
  ADD UNIQUE KEY `no_transaksi` (`no_transaksi`),
  ADD KEY `id_user` (`id_user`),
  ADD KEY `idx_no_transaksi` (`no_transaksi`),
  ADD KEY `idx_anggota` (`id_anggota`),
  ADD KEY `idx_jenis` (`id_jenis_simpanan`),
  ADD KEY `idx_tanggal` (`tanggal_transaksi`),
  ADD KEY `idx_tipe` (`tipe_transaksi`);

--
-- Indeks untuk tabel `syarat_peminjaman`
--
ALTER TABLE `syarat_peminjaman`
  ADD PRIMARY KEY (`id_syarat`),
  ADD UNIQUE KEY `kode_syarat` (`kode_syarat`),
  ADD KEY `idx_kode_syarat` (`kode_syarat`),
  ADD KEY `idx_active` (`is_active`);

--
-- Indeks untuk tabel `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id_user`),
  ADD UNIQUE KEY `username` (`username`),
  ADD KEY `idx_username` (`username`),
  ADD KEY `idx_role` (`role`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `anggota`
--
ALTER TABLE `anggota`
  MODIFY `id_anggota` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT untuk tabel `angsuran`
--
ALTER TABLE `angsuran`
  MODIFY `id_angsuran` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT untuk tabel `jenis_simpanan`
--
ALTER TABLE `jenis_simpanan`
  MODIFY `id_jenis_simpanan` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT untuk tabel `pinjaman`
--
ALTER TABLE `pinjaman`
  MODIFY `id_pinjaman` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT untuk tabel `pinjaman_syarat`
--
ALTER TABLE `pinjaman_syarat`
  MODIFY `id_pinjaman_syarat` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `profil_anggota`
--
ALTER TABLE `profil_anggota`
  MODIFY `id_profil` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT untuk tabel `simpanan`
--
ALTER TABLE `simpanan`
  MODIFY `id_simpanan` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT untuk tabel `syarat_peminjaman`
--
ALTER TABLE `syarat_peminjaman`
  MODIFY `id_syarat` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT untuk tabel `user`
--
ALTER TABLE `user`
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Ketidakleluasaan untuk tabel pelimpahan (Dumped Tables)
--

--
-- Ketidakleluasaan untuk tabel `angsuran`
--
ALTER TABLE `angsuran`
  ADD CONSTRAINT `angsuran_ibfk_1` FOREIGN KEY (`id_pinjaman`) REFERENCES `pinjaman` (`id_pinjaman`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `angsuran_ibfk_2` FOREIGN KEY (`id_user`) REFERENCES `user` (`id_user`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `pinjaman`
--
ALTER TABLE `pinjaman`
  ADD CONSTRAINT `pinjaman_ibfk_1` FOREIGN KEY (`id_anggota`) REFERENCES `anggota` (`id_anggota`) ON UPDATE CASCADE,
  ADD CONSTRAINT `pinjaman_ibfk_2` FOREIGN KEY (`id_user_pengaju`) REFERENCES `user` (`id_user`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `pinjaman_ibfk_3` FOREIGN KEY (`id_user_persetujuan`) REFERENCES `user` (`id_user`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `pinjaman_syarat`
--
ALTER TABLE `pinjaman_syarat`
  ADD CONSTRAINT `pinjaman_syarat_ibfk_1` FOREIGN KEY (`id_pinjaman`) REFERENCES `pinjaman` (`id_pinjaman`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `pinjaman_syarat_ibfk_2` FOREIGN KEY (`id_syarat`) REFERENCES `syarat_peminjaman` (`id_syarat`) ON UPDATE CASCADE,
  ADD CONSTRAINT `pinjaman_syarat_ibfk_3` FOREIGN KEY (`id_user_verifikasi`) REFERENCES `user` (`id_user`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `profil_anggota`
--
ALTER TABLE `profil_anggota`
  ADD CONSTRAINT `profil_anggota_ibfk_1` FOREIGN KEY (`id_anggota`) REFERENCES `anggota` (`id_anggota`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `simpanan`
--
ALTER TABLE `simpanan`
  ADD CONSTRAINT `simpanan_ibfk_1` FOREIGN KEY (`id_anggota`) REFERENCES `anggota` (`id_anggota`) ON UPDATE CASCADE,
  ADD CONSTRAINT `simpanan_ibfk_2` FOREIGN KEY (`id_jenis_simpanan`) REFERENCES `jenis_simpanan` (`id_jenis_simpanan`) ON UPDATE CASCADE,
  ADD CONSTRAINT `simpanan_ibfk_3` FOREIGN KEY (`id_user`) REFERENCES `user` (`id_user`) ON DELETE SET NULL ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
