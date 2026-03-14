# ============================================================================
# FILE: app/api/v1/endpoints/angsuran.py  — UPDATED with date filter
# ============================================================================

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.schemas.angsuran import (
    AngsuranResponse, AngsuranBayar, AngsuranSummary,
    AngsuranScheduleResponse, AngsuranJatuhTempoResponse
)
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.core.permissions import get_current_user, is_bendahara
from app.services import angsuran_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse[AngsuranResponse])
def get_angsuran_list(
    skip: int = 0,
    limit: int = 10,
    id_pinjaman: Optional[int] = None,
    status: Optional[str] = None,
    # ── Filter tanggal jatuh tempo (untuk filter per bulan) ───────────────
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list angsuran dengan filter status dan rentang tanggal jatuh tempo"""
    angsuran_list, total = angsuran_service.get_angsuran_list(
        db=db,
        skip=skip,
        limit=limit,
        id_pinjaman=id_pinjaman,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )
    
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    
    # Convert to response
    data = []
    for angsuran in angsuran_list:
        response_data = {
            "id_angsuran": angsuran.id_angsuran,
            "id_pinjaman": angsuran.id_pinjaman,
            "no_pinjaman": angsuran.pinjaman.no_pinjaman if angsuran.pinjaman else None,
            "no_angsuran": angsuran.no_angsuran,
            "angsuran_ke": angsuran.angsuran_ke,
            "tanggal_jatuh_tempo": angsuran.tanggal_jatuh_tempo,
            "nominal_angsuran": float(angsuran.nominal_angsuran),
            "pokok": float(angsuran.pokok),
            "bunga": float(angsuran.bunga),
            "denda": float(angsuran.denda),
            "total_bayar": float(angsuran.total_bayar),
            "tanggal_bayar": angsuran.tanggal_bayar,
            "status": angsuran.status,
            "keterangan": angsuran.keterangan,
            "created_at": angsuran.created_at
        }
        data.append(AngsuranResponse(**response_data))
    
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


@router.get("/pinjaman/{id_pinjaman}", response_model=List[AngsuranResponse])
def get_angsuran_by_pinjaman(
    id_pinjaman: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get semua angsuran untuk pinjaman tertentu"""
    angsuran_list = angsuran_service.get_angsuran_by_pinjaman(db, id_pinjaman)
    
    data = []
    for angsuran in angsuran_list:
        response_data = {
            "id_angsuran": angsuran.id_angsuran,
            "id_pinjaman": angsuran.id_pinjaman,
            "no_pinjaman": angsuran.pinjaman.no_pinjaman if angsuran.pinjaman else None,
            "no_angsuran": angsuran.no_angsuran,
            "angsuran_ke": angsuran.angsuran_ke,
            "tanggal_jatuh_tempo": angsuran.tanggal_jatuh_tempo,
            "nominal_angsuran": float(angsuran.nominal_angsuran),
            "pokok": float(angsuran.pokok),
            "bunga": float(angsuran.bunga),
            "denda": float(angsuran.denda),
            "total_bayar": float(angsuran.total_bayar),
            "tanggal_bayar": angsuran.tanggal_bayar,
            "status": angsuran.status,
            "keterangan": angsuran.keterangan,
            "created_at": angsuran.created_at
        }
        data.append(AngsuranResponse(**response_data))
    
    return data


@router.get("/pinjaman/{id_pinjaman}/schedule", response_model=AngsuranScheduleResponse)
def get_schedule_angsuran(
    id_pinjaman: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get jadwal angsuran untuk pinjaman"""
    return angsuran_service.get_schedule_angsuran(db, id_pinjaman)


@router.get("/pinjaman/{id_pinjaman}/summary", response_model=AngsuranSummary)
def get_angsuran_summary(
    id_pinjaman: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary angsuran untuk pinjaman"""
    return angsuran_service.get_angsuran_summary(db, id_pinjaman)


@router.get("/jatuh-tempo", response_model=List[AngsuranJatuhTempoResponse])
def get_angsuran_jatuh_tempo(
    tanggal: Optional[date] = None,
    include_terlambat: bool = True,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get angsuran yang jatuh tempo"""
    angsuran_list = angsuran_service.get_angsuran_jatuh_tempo(
        db=db,
        tanggal=tanggal,
        include_terlambat=include_terlambat
    )
    
    data = []
    for angsuran in angsuran_list:
        pinjaman = angsuran.pinjaman
        anggota = pinjaman.anggota if pinjaman else None
        
        # Hitung hari keterlambatan
        check_date = tanggal if tanggal else date.today()
        if check_date > angsuran.tanggal_jatuh_tempo:
            hari_terlambat = (check_date - angsuran.tanggal_jatuh_tempo).days
        else:
            hari_terlambat = 0
        
        response_data = {
            "id_angsuran": angsuran.id_angsuran,
            "id_pinjaman": angsuran.id_pinjaman,
            "no_pinjaman": pinjaman.no_pinjaman if pinjaman else "",
            "id_anggota": anggota.id_anggota if anggota else 0,
            "nama_anggota": anggota.nama_lengkap if anggota else "",
            "no_anggota": anggota.no_anggota if anggota else "",
            "angsuran_ke": angsuran.angsuran_ke,
            "tanggal_jatuh_tempo": angsuran.tanggal_jatuh_tempo,
            "nominal_angsuran": float(angsuran.nominal_angsuran),
            "denda": float(angsuran.denda),
            "hari_keterlambatan": hari_terlambat,
            "status": angsuran.status
        }
        data.append(AngsuranJatuhTempoResponse(**response_data))
    
    return data


@router.get("/{id_angsuran}", response_model=AngsuranResponse)
def get_angsuran(
    id_angsuran: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get angsuran by ID"""
    angsuran = angsuran_service.get_angsuran_by_id(db, id_angsuran)
    
    response_data = {
        "id_angsuran": angsuran.id_angsuran,
        "id_pinjaman": angsuran.id_pinjaman,
        "no_pinjaman": angsuran.pinjaman.no_pinjaman if angsuran.pinjaman else None,
        "no_angsuran": angsuran.no_angsuran,
        "angsuran_ke": angsuran.angsuran_ke,
        "tanggal_jatuh_tempo": angsuran.tanggal_jatuh_tempo,
        "nominal_angsuran": float(angsuran.nominal_angsuran),
        "pokok": float(angsuran.pokok),
        "bunga": float(angsuran.bunga),
        "denda": float(angsuran.denda),
        "total_bayar": float(angsuran.total_bayar),
        "tanggal_bayar": angsuran.tanggal_bayar,
        "status": angsuran.status,
        "keterangan": angsuran.keterangan,
        "created_at": angsuran.created_at
    }
    return AngsuranResponse(**response_data)


@router.post("/{id_angsuran}/bayar", response_model=AngsuranResponse)
def bayar_angsuran(
    id_angsuran: int,
    data: AngsuranBayar,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bayar angsuran"""
    is_bendahara(current_user)
    angsuran = angsuran_service.bayar_angsuran(
        db=db,
        id_angsuran=id_angsuran,
        data=data,
        id_user=current_user["id"]
    )
    
    response_data = {
        "id_angsuran": angsuran.id_angsuran,
        "id_pinjaman": angsuran.id_pinjaman,
        "no_pinjaman": angsuran.pinjaman.no_pinjaman if angsuran.pinjaman else None,
        "no_angsuran": angsuran.no_angsuran,
        "angsuran_ke": angsuran.angsuran_ke,
        "tanggal_jatuh_tempo": angsuran.tanggal_jatuh_tempo,
        "nominal_angsuran": float(angsuran.nominal_angsuran),
        "pokok": float(angsuran.pokok),
        "bunga": float(angsuran.bunga),
        "denda": float(angsuran.denda),
        "total_bayar": float(angsuran.total_bayar),
        "tanggal_bayar": angsuran.tanggal_bayar,
        "status": angsuran.status,
        "keterangan": angsuran.keterangan,
        "created_at": angsuran.created_at
    }
    return AngsuranResponse(**response_data)