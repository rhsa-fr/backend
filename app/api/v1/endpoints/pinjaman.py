# ============================================================================
# FILE: app/api/v1/endpoints/pinjaman.py
# ============================================================================

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.schemas.pinjaman import (
    PinjamanCreate, PinjamanUpdate, PinjamanResponse, PinjamanDetailResponse,
    PinjamanApprove, PinjamanReject, PinjamanCalculation
)
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.core.permissions import get_current_user, is_ketua
from app.services import pinjaman_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse[PinjamanResponse])
def get_pinjaman_list(
    skip: int = 0,
    limit: int = 10,
    id_anggota: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list pinjaman"""
    pinjaman_list, total = pinjaman_service.get_pinjaman_list(
        db=db,
        skip=skip,
        limit=limit,
        id_anggota=id_anggota,
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    
    # Convert to response
    data = []
    for pinjaman in pinjaman_list:
        response_data = {
            "id_pinjaman": pinjaman.id_pinjaman,
            "id_anggota": pinjaman.id_anggota,
            "nama_anggota": pinjaman.anggota.nama_lengkap if pinjaman.anggota else None,
            "no_pinjaman": pinjaman.no_pinjaman,
            "tanggal_pengajuan": pinjaman.tanggal_pengajuan,
            "nominal_pinjaman": float(pinjaman.nominal_pinjaman),
            "bunga_persen": float(pinjaman.bunga_persen),
            "total_bunga": float(pinjaman.total_bunga),
            "total_pinjaman": float(pinjaman.total_pinjaman),
            "lama_angsuran": pinjaman.lama_angsuran,
            "nominal_angsuran": float(pinjaman.nominal_angsuran),
            "keperluan": pinjaman.keperluan,
            "status": pinjaman.status,
            "tanggal_persetujuan": pinjaman.tanggal_persetujuan,
            "tanggal_pencairan": pinjaman.tanggal_pencairan,
            "tanggal_lunas": pinjaman.tanggal_lunas,
            "catatan_persetujuan": pinjaman.catatan_persetujuan,
            "sisa_pinjaman": float(pinjaman.sisa_pinjaman),
            "created_at": pinjaman.created_at
        }
        data.append(PinjamanResponse(**response_data))
    
    return PaginatedResponse(
        data=data,
        meta=PaginationMeta(
            total=total,
            skip=skip,
            limit=limit,
            page=page,
            total_pages=total_pages
        )
    )


@router.post("", response_model=PinjamanResponse, status_code=status.HTTP_201_CREATED)
def create_pinjaman(
    data: PinjamanCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create pengajuan pinjaman"""
    pinjaman = pinjaman_service.create_pinjaman(
        db=db,
        data=data,
        id_user=current_user["id"]
    )
    
    response_data = {
        "id_pinjaman": pinjaman.id_pinjaman,
        "id_anggota": pinjaman.id_anggota,
        "nama_anggota": pinjaman.anggota.nama_lengkap if pinjaman.anggota else None,
        "no_pinjaman": pinjaman.no_pinjaman,
        "tanggal_pengajuan": pinjaman.tanggal_pengajuan,
        "nominal_pinjaman": float(pinjaman.nominal_pinjaman),
        "bunga_persen": float(pinjaman.bunga_persen),
        "total_bunga": float(pinjaman.total_bunga),
        "total_pinjaman": float(pinjaman.total_pinjaman),
        "lama_angsuran": pinjaman.lama_angsuran,
        "nominal_angsuran": float(pinjaman.nominal_angsuran),
        "keperluan": pinjaman.keperluan,
        "status": pinjaman.status,
        "tanggal_persetujuan": pinjaman.tanggal_persetujuan,
        "tanggal_pencairan": pinjaman.tanggal_pencairan,
        "tanggal_lunas": pinjaman.tanggal_lunas,
        "catatan_persetujuan": pinjaman.catatan_persetujuan,
        "sisa_pinjaman": float(pinjaman.sisa_pinjaman),
        "created_at": pinjaman.created_at
    }
    
    return PinjamanResponse(**response_data)


@router.get("/pending", response_model=List[PinjamanResponse])
def get_pinjaman_pending(
    current_user: dict = Depends(is_ketua),
    db: Session = Depends(get_db)
):
    """Get semua pinjaman pending approval (ketua only)"""
    pinjaman_list = pinjaman_service.get_pinjaman_pending(db)
    
    data = []
    for pinjaman in pinjaman_list:
        response_data = {
            "id_pinjaman": pinjaman.id_pinjaman,
            "id_anggota": pinjaman.id_anggota,
            "nama_anggota": pinjaman.anggota.nama_lengkap if pinjaman.anggota else None,
            "no_pinjaman": pinjaman.no_pinjaman,
            "tanggal_pengajuan": pinjaman.tanggal_pengajuan,
            "nominal_pinjaman": float(pinjaman.nominal_pinjaman),
            "bunga_persen": float(pinjaman.bunga_persen),
            "total_bunga": float(pinjaman.total_bunga),
            "total_pinjaman": float(pinjaman.total_pinjaman),
            "lama_angsuran": pinjaman.lama_angsuran,
            "nominal_angsuran": float(pinjaman.nominal_angsuran),
            "keperluan": pinjaman.keperluan,
            "status": pinjaman.status,
            "tanggal_persetujuan": pinjaman.tanggal_persetujuan,
            "tanggal_pencairan": pinjaman.tanggal_pencairan,
            "tanggal_lunas": pinjaman.tanggal_lunas,
            "catatan_persetujuan": pinjaman.catatan_persetujuan,
            "sisa_pinjaman": float(pinjaman.sisa_pinjaman),
            "created_at": pinjaman.created_at
        }
        data.append(PinjamanResponse(**response_data))
    
    return data


@router.get("/{id_pinjaman}", response_model=PinjamanResponse)
def get_pinjaman(
    id_pinjaman: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pinjaman by ID"""
    pinjaman = pinjaman_service.get_pinjaman_by_id(db, id_pinjaman)
    
    response_data = {
        "id_pinjaman": pinjaman.id_pinjaman,
        "id_anggota": pinjaman.id_anggota,
        "nama_anggota": pinjaman.anggota.nama_lengkap if pinjaman.anggota else None,
        "no_pinjaman": pinjaman.no_pinjaman,
        "tanggal_pengajuan": pinjaman.tanggal_pengajuan,
        "nominal_pinjaman": float(pinjaman.nominal_pinjaman),
        "bunga_persen": float(pinjaman.bunga_persen),
        "total_bunga": float(pinjaman.total_bunga),
        "total_pinjaman": float(pinjaman.total_pinjaman),
        "lama_angsuran": pinjaman.lama_angsuran,
        "nominal_angsuran": float(pinjaman.nominal_angsuran),
        "keperluan": pinjaman.keperluan,
        "status": pinjaman.status,
        "tanggal_persetujuan": pinjaman.tanggal_persetujuan,
        "tanggal_pencairan": pinjaman.tanggal_pencairan,
        "tanggal_lunas": pinjaman.tanggal_lunas,
        "catatan_persetujuan": pinjaman.catatan_persetujuan,
        "sisa_pinjaman": float(pinjaman.sisa_pinjaman),
        "created_at": pinjaman.created_at
    }
    
    return PinjamanResponse(**response_data)


@router.put("/{id_pinjaman}", response_model=PinjamanResponse)
def update_pinjaman(
    id_pinjaman: int,
    data: PinjamanUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update pinjaman (hanya yang masih pending)"""
    pinjaman = pinjaman_service.update_pinjaman(db, id_pinjaman, data)
    
    response_data = {
        "id_pinjaman": pinjaman.id_pinjaman,
        "id_anggota": pinjaman.id_anggota,
        "nama_anggota": pinjaman.anggota.nama_lengkap if pinjaman.anggota else None,
        "no_pinjaman": pinjaman.no_pinjaman,
        "tanggal_pengajuan": pinjaman.tanggal_pengajuan,
        "nominal_pinjaman": float(pinjaman.nominal_pinjaman),
        "bunga_persen": float(pinjaman.bunga_persen),
        "total_bunga": float(pinjaman.total_bunga),
        "total_pinjaman": float(pinjaman.total_pinjaman),
        "lama_angsuran": pinjaman.lama_angsuran,
        "nominal_angsuran": float(pinjaman.nominal_angsuran),
        "keperluan": pinjaman.keperluan,
        "status": pinjaman.status,
        "tanggal_persetujuan": pinjaman.tanggal_persetujuan,
        "tanggal_pencairan": pinjaman.tanggal_pencairan,
        "tanggal_lunas": pinjaman.tanggal_lunas,
        "catatan_persetujuan": pinjaman.catatan_persetujuan,
        "sisa_pinjaman": float(pinjaman.sisa_pinjaman),
        "created_at": pinjaman.created_at
    }
    
    return PinjamanResponse(**response_data)


@router.put("/{id_pinjaman}/approve", response_model=PinjamanResponse)
def approve_pinjaman(
    id_pinjaman: int,
    data: PinjamanApprove,
    current_user: dict = Depends(is_ketua),
    db: Session = Depends(get_db)
):
    """Approve pinjaman (ketua only)"""
    pinjaman = pinjaman_service.approve_pinjaman(
        db=db,
        id_pinjaman=id_pinjaman,
        data=data,
        id_user=current_user["id"]
    )
    
    response_data = {
        "id_pinjaman": pinjaman.id_pinjaman,
        "id_anggota": pinjaman.id_anggota,
        "nama_anggota": pinjaman.anggota.nama_lengkap if pinjaman.anggota else None,
        "no_pinjaman": pinjaman.no_pinjaman,
        "tanggal_pengajuan": pinjaman.tanggal_pengajuan,
        "nominal_pinjaman": float(pinjaman.nominal_pinjaman),
        "bunga_persen": float(pinjaman.bunga_persen),
        "total_bunga": float(pinjaman.total_bunga),
        "total_pinjaman": float(pinjaman.total_pinjaman),
        "lama_angsuran": pinjaman.lama_angsuran,
        "nominal_angsuran": float(pinjaman.nominal_angsuran),
        "keperluan": pinjaman.keperluan,
        "status": pinjaman.status,
        "tanggal_persetujuan": pinjaman.tanggal_persetujuan,
        "tanggal_pencairan": pinjaman.tanggal_pencairan,
        "tanggal_lunas": pinjaman.tanggal_lunas,
        "catatan_persetujuan": pinjaman.catatan_persetujuan,
        "sisa_pinjaman": float(pinjaman.sisa_pinjaman),
        "created_at": pinjaman.created_at
    }
    
    return PinjamanResponse(**response_data)


@router.put("/{id_pinjaman}/reject", response_model=PinjamanResponse)
def reject_pinjaman(
    id_pinjaman: int,
    data: PinjamanReject,
    current_user: dict = Depends(is_ketua),
    db: Session = Depends(get_db)
):
    """Reject pinjaman (ketua only)"""
    pinjaman = pinjaman_service.reject_pinjaman(
        db=db,
        id_pinjaman=id_pinjaman,
        data=data,
        id_user=current_user["id"]
    )
    
    response_data = {
        "id_pinjaman": pinjaman.id_pinjaman,
        "id_anggota": pinjaman.id_anggota,
        "nama_anggota": pinjaman.anggota.nama_lengkap if pinjaman.anggota else None,
        "no_pinjaman": pinjaman.no_pinjaman,
        "tanggal_pengajuan": pinjaman.tanggal_pengajuan,
        "nominal_pinjaman": float(pinjaman.nominal_pinjaman),
        "bunga_persen": float(pinjaman.bunga_persen),
        "total_bunga": float(pinjaman.total_bunga),
        "total_pinjaman": float(pinjaman.total_pinjaman),
        "lama_angsuran": pinjaman.lama_angsuran,
        "nominal_angsuran": float(pinjaman.nominal_angsuran),
        "keperluan": pinjaman.keperluan,
        "status": pinjaman.status,
        "tanggal_persetujuan": pinjaman.tanggal_persetujuan,
        "tanggal_pencairan": pinjaman.tanggal_pencairan,
        "tanggal_lunas": pinjaman.tanggal_lunas,
        "catatan_persetujuan": pinjaman.catatan_persetujuan,
        "sisa_pinjaman": float(pinjaman.sisa_pinjaman),
        "created_at": pinjaman.created_at
    }
    
    return PinjamanResponse(**response_data)


@router.post("/calculate", response_model=PinjamanCalculation)
def calculate_pinjaman(
    data: PinjamanCalculation,
    current_user: dict = Depends(get_current_user)
):
    """Kalkulasi pinjaman (simulasi)"""
    return pinjaman_service.calculate_pinjaman(
        nominal_pinjaman=data.nominal_pinjaman,
        bunga_persen=data.bunga_persen,
        lama_angsuran=data.lama_angsuran
    )
