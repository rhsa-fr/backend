# ============================================================================
# FILE: app/schemas/pinjaman.py (UPDATED WITH SYARAT)
# ============================================================================

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, TYPE_CHECKING
from datetime import date, datetime
from enum import Enum

if TYPE_CHECKING:
    from app.schemas.syarat_peminjaman import PinjamanSyaratDetailResponse


class StatusPinjaman(str, Enum):
    PENDING = "pending"
    DISETUJUI = "disetujui"
    DITOLAK = "ditolak"
    LUNAS = "lunas"


class PinjamanBase(BaseModel):
    id_anggota: int = Field(..., description="ID anggota")
    nominal_pinjaman: float = Field(..., gt=0, description="Nominal pinjaman pokok")
    bunga_persen: float = Field(..., ge=0, le=100, description="Persentase bunga per tahun")
    lama_angsuran: int = Field(..., gt=0, le=60, description="Lama angsuran dalam bulan")
    keperluan: Optional[str] = Field(None, description="Keperluan pinjaman")
    
    @field_validator('nominal_pinjaman')
    @classmethod
    def validate_nominal(cls, v):
        if v < 1000000:
            raise ValueError('Nominal pinjaman minimal Rp 1.000.000')
        if v > 100000000:
            raise ValueError('Nominal pinjaman maksimal Rp 100.000.000')
        return v


class PinjamanCreate(PinjamanBase):
    tanggal_pengajuan: date = Field(..., description="Tanggal pengajuan pinjaman")
    syarat_ids: Optional[List[int]] = Field(default=None, description="List ID syarat yang dilampirkan")


class PinjamanUpdate(BaseModel):
    keperluan: Optional[str] = None
    bunga_persen: Optional[float] = Field(None, ge=0, le=100)
    lama_angsuran: Optional[int] = Field(None, gt=0, le=60)


class PinjamanApprove(BaseModel):
    tanggal_persetujuan: date = Field(..., description="Tanggal persetujuan")
    tanggal_pencairan: date = Field(..., description="Tanggal pencairan")
    catatan_persetujuan: Optional[str] = Field(None, description="Catatan persetujuan dari ketua")


class PinjamanReject(BaseModel):
    tanggal_persetujuan: date = Field(..., description="Tanggal penolakan")
    catatan_persetujuan: str = Field(..., min_length=10, description="Alasan penolakan minimal 10 karakter")


class PinjamanInDB(PinjamanBase):
    id_pinjaman: int
    no_pinjaman: str
    tanggal_pengajuan: date
    total_bunga: float
    total_pinjaman: float
    nominal_angsuran: float
    status: StatusPinjaman
    tanggal_persetujuan: Optional[date] = None
    tanggal_pencairan: Optional[date] = None
    tanggal_lunas: Optional[date] = None
    id_user_pengaju: Optional[int] = None
    id_user_persetujuan: Optional[int] = None
    catatan_persetujuan: Optional[str] = None
    sisa_pinjaman: float
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PinjamanResponse(BaseModel):
    id_pinjaman: int
    id_anggota: int
    nama_anggota: Optional[str] = None
    no_pinjaman: str
    tanggal_pengajuan: date
    nominal_pinjaman: float
    bunga_persen: float
    total_bunga: float
    total_pinjaman: float
    lama_angsuran: int
    nominal_angsuran: float
    keperluan: Optional[str] = None
    status: StatusPinjaman
    tanggal_persetujuan: Optional[date] = None
    tanggal_pencairan: Optional[date] = None
    tanggal_lunas: Optional[date] = None
    catatan_persetujuan: Optional[str] = None
    sisa_pinjaman: float
    created_at: datetime
    
    # Informasi syarat
    total_syarat: Optional[int] = Field(0, description="Total syarat yang berlaku")
    syarat_terpenuhi: Optional[int] = Field(0, description="Syarat yang terpenuhi")
    
    model_config = ConfigDict(from_attributes=True)


class PinjamanDetailResponse(PinjamanResponse):
    anggota: Optional[dict] = None
    user_pengaju: Optional[dict] = None
    user_persetujuan: Optional[dict] = None
    total_angsuran: Optional[int] = Field(0, description="Total jumlah angsuran")
    angsuran_lunas: Optional[int] = Field(0, description="Jumlah angsuran yang sudah lunas")
    angsuran_belum_bayar: Optional[int] = Field(0, description="Jumlah angsuran yang belum dibayar")
    
    # Detail syarat
    detail_syarat: Optional[List["PinjamanSyaratDetailResponse"]] = Field(None, description="Detail syarat peminjaman")
    
    model_config = ConfigDict(from_attributes=True)


class PinjamanCalculation(BaseModel):
    nominal_pinjaman: float = Field(..., gt=0, description="Nominal pinjaman")
    bunga_persen: float = Field(..., ge=0, le=100, description="Persentase bunga")
    lama_angsuran: int = Field(..., gt=0, le=60, description="Lama angsuran (bulan)")
    total_bunga: float = Field(..., description="Total bunga yang harus dibayar")
    total_pinjaman: float = Field(..., description="Total pinjaman + bunga")
    nominal_angsuran: float = Field(..., description="Nominal per angsuran")
    
    model_config = ConfigDict(from_attributes=True)