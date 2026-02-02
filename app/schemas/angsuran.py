# ============================================================================
# FILE: app/schemas/angsuran.py
# ============================================================================

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime
from enum import Enum


class StatusAngsuran(str, Enum):
    BELUM_BAYAR = "belum_bayar"
    LUNAS = "lunas"
    TERLAMBAT = "terlambat"


class AngsuranBase(BaseModel):
    id_pinjaman: int = Field(..., description="ID pinjaman")
    angsuran_ke: int = Field(..., gt=0, description="Angsuran ke berapa")
    tanggal_jatuh_tempo: date = Field(..., description="Tanggal jatuh tempo")
    nominal_angsuran: float = Field(..., gt=0, description="Nominal angsuran")
    pokok: float = Field(..., gt=0, description="Porsi pokok pinjaman")
    bunga: float = Field(..., ge=0, description="Porsi bunga")


class AngsuranCreate(AngsuranBase):
    pass


class AngsuranUpdate(BaseModel):
    tanggal_jatuh_tempo: Optional[date] = None
    nominal_angsuran: Optional[float] = Field(None, gt=0)
    pokok: Optional[float] = Field(None, gt=0)
    bunga: Optional[float] = Field(None, ge=0)


class AngsuranBayar(BaseModel):
    tanggal_bayar: date = Field(..., description="Tanggal pembayaran")
    total_bayar: float = Field(..., gt=0, description="Total yang dibayar (angsuran + denda)")
    keterangan: Optional[str] = Field(None, description="Keterangan pembayaran")


class AngsuranInDB(AngsuranBase):
    id_angsuran: int
    no_angsuran: str
    denda: float
    total_bayar: float
    tanggal_bayar: Optional[date] = None
    status: StatusAngsuran
    keterangan: Optional[str] = None
    id_user: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AngsuranResponse(BaseModel):
    id_angsuran: int
    id_pinjaman: int
    no_pinjaman: Optional[str] = None
    no_angsuran: str
    angsuran_ke: int
    tanggal_jatuh_tempo: date
    nominal_angsuran: float
    pokok: float
    bunga: float
    denda: float
    total_bayar: float
    tanggal_bayar: Optional[date] = None
    status: StatusAngsuran
    keterangan: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AngsuranDetailResponse(AngsuranResponse):
    pinjaman: Optional[dict] = None
    anggota: Optional[dict] = None
    hari_keterlambatan: Optional[int] = Field(0, description="Jumlah hari keterlambatan")
    
    model_config = ConfigDict(from_attributes=True)


class AngsuranScheduleItem(BaseModel):
    angsuran_ke: int
    tanggal_jatuh_tempo: date
    nominal_angsuran: float
    pokok: float
    bunga: float
    sisa_pinjaman: float
    
    model_config = ConfigDict(from_attributes=True)


class AngsuranScheduleResponse(BaseModel):
    id_pinjaman: int
    no_pinjaman: str
    total_pinjaman: float
    lama_angsuran: int
    nominal_angsuran: float
    schedule: list[AngsuranScheduleItem] = Field(..., description="Jadwal angsuran")
    
    model_config = ConfigDict(from_attributes=True)


class AngsuranSummary(BaseModel):
    id_pinjaman: int
    no_pinjaman: str
    total_angsuran: int = Field(..., description="Total jumlah angsuran")
    angsuran_lunas: int = Field(..., description="Angsuran yang sudah lunas")
    angsuran_belum_bayar: int = Field(..., description="Angsuran yang belum dibayar")
    angsuran_terlambat: int = Field(..., description="Angsuran yang terlambat")
    total_dibayar: float = Field(..., description="Total yang sudah dibayar")
    sisa_pinjaman: float = Field(..., description="Sisa pinjaman yang belum dibayar")
    
    model_config = ConfigDict(from_attributes=True)


class AngsuranJatuhTempoResponse(BaseModel):
    id_angsuran: int
    id_pinjaman: int
    no_pinjaman: str
    id_anggota: int
    nama_anggota: str
    no_anggota: str
    angsuran_ke: int
    tanggal_jatuh_tempo: date
    nominal_angsuran: float
    denda: float
    hari_keterlambatan: int = Field(0, description="Jumlah hari keterlambatan")
    status: StatusAngsuran
    
    model_config = ConfigDict(from_attributes=True)