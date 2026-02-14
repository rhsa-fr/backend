# ============================================================================
# FILE: app/schemas/syarat_peminjaman.py
# ============================================================================

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal


class SyaratPeminjamanBase(BaseModel):
    kode_syarat: str = Field(..., max_length=20, description="Kode unik syarat")
    nama_syarat: str = Field(..., max_length=100, description="Nama syarat peminjaman")
    deskripsi: Optional[str] = Field(None, description="Deskripsi lengkap syarat")
    is_wajib: bool = Field(True, description="Apakah syarat wajib dipenuhi")
    min_nominal_pinjaman: Optional[float] = Field(None, description="Minimal nominal pinjaman")
    max_nominal_pinjaman: Optional[float] = Field(None, description="Maksimal nominal pinjaman")
    dokumen_diperlukan: Optional[str] = Field(None, description="Jenis dokumen yang diperlukan")
    urutan: int = Field(0, description="Urutan tampilan syarat")


class SyaratPeminjamanCreate(SyaratPeminjamanBase):
    pass


class SyaratPeminjamanUpdate(BaseModel):
    kode_syarat: Optional[str] = Field(None, max_length=20)
    nama_syarat: Optional[str] = Field(None, max_length=100)
    deskripsi: Optional[str] = None
    is_wajib: Optional[bool] = None
    min_nominal_pinjaman: Optional[float] = None
    max_nominal_pinjaman: Optional[float] = None
    dokumen_diperlukan: Optional[str] = None
    is_active: Optional[bool] = None
    urutan: Optional[int] = None


class SyaratPeminjamanResponse(SyaratPeminjamanBase):
    id_syarat: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PinjamanSyaratBase(BaseModel):
    id_syarat: int = Field(..., description="ID syarat peminjaman")
    is_terpenuhi: bool = Field(False, description="Status pemenuhan syarat")
    dokumen_path: Optional[str] = Field(None, description="Path file dokumen")
    catatan: Optional[str] = Field(None, description="Catatan terkait syarat")


class PinjamanSyaratCreate(PinjamanSyaratBase):
    pass


class PinjamanSyaratUpdate(BaseModel):
    is_terpenuhi: Optional[bool] = None
    dokumen_path: Optional[str] = None
    catatan: Optional[str] = None


class PinjamanSyaratVerify(BaseModel):
    is_terpenuhi: bool = Field(..., description="Apakah syarat terpenuhi")
    catatan: Optional[str] = Field(None, description="Catatan verifikasi")


class PinjamanSyaratResponse(PinjamanSyaratBase):
    id_pinjaman_syarat: int
    id_pinjaman: int
    tanggal_verifikasi: Optional[datetime] = None
    id_user_verifikasi: Optional[int] = None
    created_at: datetime
    
    # Relasi
    syarat: Optional[SyaratPeminjamanResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


class PinjamanSyaratDetailResponse(PinjamanSyaratResponse):
    """Response dengan detail syarat dan status pemenuhan"""
    nama_syarat: Optional[str] = None
    deskripsi_syarat: Optional[str] = None
    dokumen_diperlukan: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class SyaratChecklistResponse(BaseModel):
    """Response untuk checklist syarat pada pengajuan pinjaman"""
    total_syarat: int = Field(..., description="Total syarat yang berlaku")
    syarat_terpenuhi: int = Field(..., description="Jumlah syarat yang terpenuhi")
    syarat_belum_terpenuhi: int = Field(..., description="Jumlah syarat belum terpenuhi")
    persentase_kelengkapan: float = Field(..., description="Persentase kelengkapan syarat")
    semua_syarat_wajib_terpenuhi: bool = Field(..., description="Apakah semua syarat wajib terpenuhi")
    detail_syarat: list[PinjamanSyaratDetailResponse] = Field(..., description="Detail setiap syarat")
    
    model_config = ConfigDict(from_attributes=True)