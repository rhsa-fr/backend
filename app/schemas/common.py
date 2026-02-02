# ============================================================================
# FILE: app/schemas/common.py
# ============================================================================

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Generic, TypeVar, List, Any
from datetime import datetime

DataT = TypeVar('DataT')


class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0, description="Jumlah data yang dilewati")
    limit: int = Field(10, ge=1, le=100, description="Jumlah data per halaman")
    
    model_config = ConfigDict(from_attributes=True)


class PaginationMeta(BaseModel):
    total: int = Field(..., description="Total semua data")
    skip: int = Field(..., description="Data yang dilewati")
    limit: int = Field(..., description="Limit per halaman")
    page: int = Field(..., description="Halaman saat ini")
    total_pages: int = Field(..., description="Total halaman")
    
    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[DataT]):
    data: List[DataT] = Field(..., description="List data")
    meta: PaginationMeta = Field(..., description="Metadata pagination")
    
    model_config = ConfigDict(from_attributes=True)


class SuccessResponse(BaseModel, Generic[DataT]):
    status: str = Field("success", description="Status response")
    message: str = Field(..., description="Pesan response")
    data: Optional[DataT] = Field(None, description="Data response")
    
    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    status: str = Field("error", description="Status response")
    message: str = Field(..., description="Pesan error")
    errors: Optional[List[dict]] = Field(None, description="Detail error")
    
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str = Field(..., description="Pesan")
    
    model_config = ConfigDict(from_attributes=True)


class IDResponse(BaseModel):
    id: int = Field(..., description="ID resource")
    message: str = Field(..., description="Pesan")
    
    model_config = ConfigDict(from_attributes=True)


class BulkDeleteResponse(BaseModel):
    deleted_count: int = Field(..., description="Jumlah data yang dihapus")
    message: str = Field(..., description="Pesan")
    
    model_config = ConfigDict(from_attributes=True)


class HealthCheckResponse(BaseModel):
    status: str = Field("healthy", description="Status aplikasi")
    timestamp: datetime = Field(..., description="Waktu pengecekan")
    database: str = Field(..., description="Status database connection")
    version: str = Field(..., description="Versi aplikasi")
    
    model_config = ConfigDict(from_attributes=True)


class FilterParams(BaseModel):
    search: Optional[str] = Field(None, description="Keyword pencarian")
    sort_by: Optional[str] = Field(None, description="Field untuk sorting")
    sort_order: Optional[str] = Field("asc", description="Urutan sorting: asc atau desc")
    
    model_config = ConfigDict(from_attributes=True)


class DateRangeFilter(BaseModel):
    start_date: Optional[datetime] = Field(None, description="Tanggal mulai")
    end_date: Optional[datetime] = Field(None, description="Tanggal akhir")
    
    model_config = ConfigDict(from_attributes=True)


class StatisticResponse(BaseModel):
    label: str = Field(..., description="Label statistik")
    value: float = Field(..., description="Nilai statistik")
    unit: Optional[str] = Field(None, description="Satuan (Rp, %, unit, dll)")
    
    model_config = ConfigDict(from_attributes=True)


class DashboardStats(BaseModel):
    total_anggota: int = Field(0, description="Total anggota aktif")
    total_simpanan: float = Field(0, description="Total saldo simpanan")
    total_pinjaman_aktif: float = Field(0, description="Total pinjaman aktif")
    total_pinjaman_pending: int = Field(0, description="Total pinjaman pending approval")
    total_angsuran_jatuh_tempo: int = Field(0, description="Total angsuran jatuh tempo")
    total_angsuran_terlambat: int = Field(0, description="Total angsuran terlambat")
    
    model_config = ConfigDict(from_attributes=True)


class ExportParams(BaseModel):
    format: str = Field("excel", description="Format export: excel, pdf, csv")
    start_date: Optional[datetime] = Field(None, description="Tanggal mulai untuk filter")
    end_date: Optional[datetime] = Field(None, description="Tanggal akhir untuk filter")
    
    model_config = ConfigDict(from_attributes=True)


class ValidationError(BaseModel):
    field: str = Field(..., description="Nama field yang error")
    message: str = Field(..., description="Pesan error")
    
    model_config = ConfigDict(from_attributes=True)


class BulkOperationResponse(BaseModel):
    success_count: int = Field(0, description="Jumlah operasi berhasil")
    failed_count: int = Field(0, description="Jumlah operasi gagal")
    errors: Optional[List[dict]] = Field(None, description="Detail error untuk operasi yang gagal")
    message: str = Field(..., description="Pesan response")
    
    model_config = ConfigDict(from_attributes=True)