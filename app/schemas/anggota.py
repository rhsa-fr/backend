# ============================================================================
# FILE: app/schemas/anggota.py
# ============================================================================

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import date, datetime
from enum import Enum


class StatusAnggota(str, Enum):
    AKTIF = "aktif"
    NON_AKTIF = "non-aktif"
    KELUAR = "keluar"


class JenisKelamin(str, Enum):
    LAKI_LAKI = "L"
    PEREMPUAN = "P"


# Anggota Schemas
class AnggotaBase(BaseModel):
    nama_lengkap: str = Field(..., min_length=3, max_length=100, description="Nama lengkap anggota")
    email: Optional[EmailStr] = Field(None, description="Email anggota")
    no_telepon: Optional[str] = Field(None, max_length=15, description="Nomor telepon")
    tanggal_bergabung: date = Field(..., description="Tanggal bergabung koperasi")


class AnggotaCreate(AnggotaBase):
    pass


class AnggotaUpdate(BaseModel):
    nama_lengkap: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    no_telepon: Optional[str] = Field(None, max_length=15)
    tanggal_bergabung: Optional[date] = None
    status: Optional[StatusAnggota] = None


class AnggotaInDB(AnggotaBase):
    id_anggota: int
    no_anggota: str
    status: StatusAnggota
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AnggotaResponse(BaseModel):
    id_anggota: int
    no_anggota: str
    nama_lengkap: str
    email: Optional[str] = None
    no_telepon: Optional[str] = None
    tanggal_bergabung: date
    status: StatusAnggota
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Profil Anggota Schemas
class ProfilAnggotaBase(BaseModel):
    nik: Optional[str] = Field(None, max_length=16, description="NIK KTP")
    tempat_lahir: Optional[str] = Field(None, max_length=50, description="Tempat lahir")
    tanggal_lahir: Optional[date] = Field(None, description="Tanggal lahir")
    jenis_kelamin: Optional[JenisKelamin] = Field(None, description="Jenis kelamin: L atau P")
    alamat: Optional[str] = Field(None, description="Alamat lengkap")
    kota: Optional[str] = Field(None, max_length=50, description="Kota")
    provinsi: Optional[str] = Field(None, max_length=50, description="Provinsi")
    kode_pos: Optional[str] = Field(None, max_length=10, description="Kode pos")
    pekerjaan: Optional[str] = Field(None, max_length=50, description="Pekerjaan")
    foto_profil: Optional[str] = Field(None, max_length=255, description="Path foto profil")


class ProfilAnggotaCreate(ProfilAnggotaBase):
    id_anggota: int = Field(..., description="ID anggota")


class ProfilAnggotaUpdate(ProfilAnggotaBase):
    pass


class ProfilAnggotaInDB(ProfilAnggotaBase):
    id_profil: int
    id_anggota: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProfilAnggotaResponse(ProfilAnggotaBase):
    id_profil: int
    id_anggota: int
    
    model_config = ConfigDict(from_attributes=True)


# Combined Response
class AnggotaDetailResponse(AnggotaResponse):
    profil: Optional[ProfilAnggotaResponse] = None
    total_simpanan: Optional[float] = Field(0, description="Total saldo simpanan")
    total_pinjaman_aktif: Optional[float] = Field(0, description="Total pinjaman aktif")
    
    model_config = ConfigDict(from_attributes=True)


# Jenis Simpanan Schemas
class JenisSimpananBase(BaseModel):
    kode_jenis: str = Field(..., max_length=10, description="Kode jenis simpanan")
    nama_jenis: str = Field(..., max_length=50, description="Nama jenis simpanan")
    deskripsi: Optional[str] = Field(None, description="Deskripsi jenis simpanan")
    is_wajib: bool = Field(False, description="Apakah simpanan wajib")
    nominal_tetap: float = Field(0, ge=0, description="Nominal tetap untuk simpanan wajib")


class JenisSimpananCreate(JenisSimpananBase):
    pass


class JenisSimpananUpdate(BaseModel):
    kode_jenis: Optional[str] = Field(None, max_length=10)
    nama_jenis: Optional[str] = Field(None, max_length=50)
    deskripsi: Optional[str] = None
    is_wajib: Optional[bool] = None
    nominal_tetap: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None


class JenisSimpananInDB(JenisSimpananBase):
    id_jenis_simpanan: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class JenisSimpananResponse(BaseModel):
    id_jenis_simpanan: int
    kode_jenis: str
    nama_jenis: str
    deskripsi: Optional[str] = None
    is_wajib: bool
    nominal_tetap: float
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


# Simpanan Schemas
class TipeTransaksi(str, Enum):
    SETOR = "setor"
    TARIK = "tarik"


class SimpananBase(BaseModel):
    id_anggota: int = Field(..., description="ID anggota")
    id_jenis_simpanan: int = Field(..., description="ID jenis simpanan")
    tanggal_transaksi: date = Field(..., description="Tanggal transaksi")
    tipe_transaksi: TipeTransaksi = Field(..., description="Tipe transaksi: setor atau tarik")
    nominal: float = Field(..., gt=0, description="Nominal transaksi")
    keterangan: Optional[str] = Field(None, description="Keterangan transaksi")


class SimpananCreate(SimpananBase):
    pass


class SimpananInDB(SimpananBase):
    id_simpanan: int
    no_transaksi: str
    saldo_akhir: float
    id_user: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SimpananResponse(BaseModel):
    id_simpanan: int
    id_anggota: int
    nama_anggota: Optional[str] = None
    id_jenis_simpanan: int
    nama_jenis_simpanan: Optional[str] = None
    no_transaksi: str
    tanggal_transaksi: date
    tipe_transaksi: TipeTransaksi
    nominal: float
    saldo_akhir: float
    keterangan: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SaldoSimpananResponse(BaseModel):
    id_anggota: int
    nama_anggota: str
    id_jenis_simpanan: int
    nama_jenis_simpanan: str
    total_setor: float
    total_tarik: float
    saldo: float
    
    model_config = ConfigDict(from_attributes=True)