-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 05 Feb 2026 pada 03.31
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
-- Database: `koperasi_simpan_pinjam`
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

-- --------------------------------------------------------

--
-- Struktur dari tabel `user`
--

CREATE TABLE `user` (
  `id_user` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
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
(1, 'admin@koprasi.com',     '$2b$12$muLaz5lNHR3gEZVsaXcVjuwjTKpDQDHwxFD27aiaMBVgqChG9uo1S', 'admin',     1, '2026-02-02 10:00:30', '2026-02-02 10:00:30'),
(2, 'ketua@koprasi.com',     '$2b$12$tUUT2I4fZZlMucdNAeIGC.hs2PL2UAkh0pm1jIuzv9IGsI/SCFmBC', 'ketua',     1, '2026-02-02 10:00:30', '2026-02-02 10:00:30'),
(3, 'bendahara@koprasi.com', '$2b$12$0N6NmHOd0AnixmQNS9adU.KIzhlIxYvo42fGxQMzbWzlBMHuqMESe', 'bendahara', 1, '2026-02-02 10:00:30', '2026-02-02 10:00:30');

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
  MODIFY `id_anggota` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `angsuran`
--
ALTER TABLE `angsuran`
  MODIFY `id_angsuran` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `jenis_simpanan`
--
ALTER TABLE `jenis_simpanan`
  MODIFY `id_jenis_simpanan` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT untuk tabel `pinjaman`
--
ALTER TABLE `pinjaman`
  MODIFY `id_pinjaman` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `profil_anggota`
--
ALTER TABLE `profil_anggota`
  MODIFY `id_profil` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `simpanan`
--
ALTER TABLE `simpanan`
  MODIFY `id_simpanan` int(11) NOT NULL AUTO_INCREMENT;

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
-- ============================================================================
-- SQL MIGRATION: Add Syarat Peminjaman Tables
-- ============================================================================
-- Run this SQL to add syarat peminjaman feature to existing database
-- ============================================================================

-- Create table syarat_peminjaman
CREATE TABLE IF NOT EXISTS `syarat_peminjaman` (
  `id_syarat` int(11) NOT NULL AUTO_INCREMENT,
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
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id_syarat`),
  UNIQUE KEY `kode_syarat` (`kode_syarat`),
  KEY `idx_kode_syarat` (`kode_syarat`),
  KEY `idx_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create table pinjaman_syarat
CREATE TABLE IF NOT EXISTS `pinjaman_syarat` (
  `id_pinjaman_syarat` int(11) NOT NULL AUTO_INCREMENT,
  `id_pinjaman` int(11) NOT NULL,
  `id_syarat` int(11) NOT NULL,
  `is_terpenuhi` tinyint(1) DEFAULT 0 COMMENT 'Apakah syarat sudah terpenuhi',
  `dokumen_path` varchar(255) DEFAULT NULL COMMENT 'Path file dokumen jika ada',
  `catatan` text DEFAULT NULL COMMENT 'Catatan terkait pemenuhan syarat',
  `tanggal_verifikasi` timestamp NULL DEFAULT NULL COMMENT 'Tanggal verifikasi syarat',
  `id_user_verifikasi` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id_pinjaman_syarat`),
  KEY `id_pinjaman` (`id_pinjaman`),
  KEY `id_syarat` (`id_syarat`),
  KEY `id_user_verifikasi` (`id_user_verifikasi`),
  KEY `idx_pinjaman` (`id_pinjaman`),
  KEY `idx_syarat` (`id_syarat`),
  CONSTRAINT `pinjaman_syarat_ibfk_1` FOREIGN KEY (`id_pinjaman`) REFERENCES `pinjaman` (`id_pinjaman`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `pinjaman_syarat_ibfk_2` FOREIGN KEY (`id_syarat`) REFERENCES `syarat_peminjaman` (`id_syarat`) ON UPDATE CASCADE,
  CONSTRAINT `pinjaman_syarat_ibfk_3` FOREIGN KEY (`id_user_verifikasi`) REFERENCES `user` (`id_user`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default syarat peminjaman
INSERT INTO `syarat_peminjaman` 
  (`kode_syarat`, `nama_syarat`, `deskripsi`, `is_wajib`, `min_nominal_pinjaman`, `max_nominal_pinjaman`, `dokumen_diperlukan`, `is_active`, `urutan`) 
VALUES
  ('SYR001', 'Fotocopy KTP', 'Fotocopy KTP anggota yang masih berlaku', 1, NULL, NULL, 'KTP', 1, 1),
  ('SYR002', 'Fotocopy KK', 'Fotocopy Kartu Keluarga', 1, NULL, NULL, 'KK', 1, 2),
  ('SYR003', 'Slip Gaji', 'Slip gaji 3 bulan terakhir', 1, 5000000, NULL, 'Slip Gaji', 1, 3),
  ('SYR004', 'Jaminan BPKB', 'BPKB kendaraan sebagai jaminan', 1, 10000000, NULL, 'BPKB', 1, 4),
  ('SYR005', 'Surat Pernyataan', 'Surat pernyataan sanggup membayar angsuran', 1, NULL, NULL, 'Surat Pernyataan', 1, 5),
  ('SYR006', 'Pas Foto 4x6', 'Pas foto terbaru ukuran 4x6', 0, NULL, NULL, 'Pas Foto', 1, 6),
  ('SYR007', 'NPWP', 'Nomor Pokok Wajib Pajak', 0, 20000000, NULL, 'NPWP', 1, 7),
  ('SYR008', 'Sertifikat Rumah', 'Sertifikat rumah sebagai jaminan tambahan', 0, 50000000, NULL, 'Sertifikat', 1, 8);

COMMIT;

-- ============================================================================
-- NOTES:
-- ============================================================================
-- 1. Syarat SYR001, SYR002, SYR005 wajib untuk semua nominal
-- 2. Syarat SYR003 wajib untuk pinjaman >= 5 juta
-- 3. Syarat SYR004 wajib untuk pinjaman >= 10 juta  
-- 4. Syarat SYR006 opsional untuk semua nominal
-- 5. Syarat SYR007 opsional untuk pinjaman >= 20 juta
-- 6. Syarat SYR008 opsional untuk pinjaman >= 50 juta
-- ============================================================================
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
