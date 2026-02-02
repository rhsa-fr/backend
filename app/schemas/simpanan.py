# ============================================================================
# FILE: app/schemas/simpanan.py
# ============================================================================

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime
from enum import Enum


class TipeTransaksi(str, Enum):
    SETOR = "setor"
    TARIK = "tarik"


class SimpananBase(BaseModel):
    id_anggota: int = Field(..., description="ID anggota")
    id_jenis_simpanan: int = Field(..., description="ID jenis simpanan")
    no_transaksi: str = Field(..., description="Nomor transaksi")
    tanggal_transaksi: date = Field(..., description="Tanggal transaksi")
    tipe_transaksi: TipeTransaksi = Field(..., description="Tipe transaksi: setor atau tarik")
    nominal: float = Field(..., gt=0, description="Nominal transaksi")
    keterangan: Optional[str] = Field(None, description="Keterangan tambahan")


class SimpananCreate(SimpananBase):
    pass


class SimpananUpdate(BaseModel):
    no_transaksi: Optional[str] = Field(None, description="Nomor transaksi")
    tanggal_transaksi: Optional[date] = Field(None, description="Tanggal transaksi")
    tipe_transaksi: Optional[TipeTransaksi] = Field(None, description="Tipe transaksi")
    nominal: Optional[float] = Field(None, gt=0, description="Nominal transaksi")
    keterangan: Optional[str] = Field(None, description="Keterangan tambahan")


class SimpananResponse(SimpananBase):
    id_simpanan: int = Field(..., description="ID simpanan")
    saldo_akhir: float = Field(..., description="Saldo akhir")
    id_user: Optional[int] = Field(None, description="ID user yang melakukan transaksi")
    created_at: datetime = Field(..., description="Waktu pembuatan")
    updated_at: datetime = Field(..., description="Waktu pembaruan terakhir")
    
    model_config = ConfigDict(from_attributes=True)
