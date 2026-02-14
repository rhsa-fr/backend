# ============================================================================
# FILE: app/api/v1/endpoints/syarat_peminjaman.py
# ============================================================================

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.syarat_peminjaman import (
    SyaratPeminjamanCreate, SyaratPeminjamanUpdate, SyaratPeminjamanResponse,
    PinjamanSyaratUpdate, PinjamanSyaratVerify, PinjamanSyaratDetailResponse,
    SyaratChecklistResponse
)
from app.schemas.common import PaginatedResponse, PaginationMeta, MessageResponse
from app.core.permissions import (
    get_current_user, require_permission, is_admin, is_admin_or_ketua
)
from app.services import syarat_peminjaman_service

router = APIRouter()


# ============================================================================
# SYARAT PEMINJAMAN ENDPOINTS (Admin only)
# ============================================================================

@router.get("/master", response_model=PaginatedResponse[SyaratPeminjamanResponse])
def get_syarat_list(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    nominal_pinjaman: Optional[float] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list master syarat peminjaman"""
    syarat_list, total = syarat_peminjaman_service.get_syarat_list(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active,
        nominal_pinjaman=nominal_pinjaman
    )
    
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    
    return PaginatedResponse(
        data=[SyaratPeminjamanResponse.model_validate(s) for s in syarat_list],
        meta=PaginationMeta(
            total=total,
            skip=skip,
            limit=limit,
            page=page,
            total_pages=total_pages
        )
    )


@router.post("/master", response_model=SyaratPeminjamanResponse, status_code=status.HTTP_201_CREATED)
def create_syarat(
    data: SyaratPeminjamanCreate,
    current_user: dict = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Create syarat peminjaman baru (admin only)"""
    syarat = syarat_peminjaman_service.create_syarat_peminjaman(db, data)
    return SyaratPeminjamanResponse.model_validate(syarat)


@router.get("/master/{id_syarat}", response_model=SyaratPeminjamanResponse)
def get_syarat(
    id_syarat: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get syarat peminjaman by ID"""
    syarat = syarat_peminjaman_service.get_syarat_by_id(db, id_syarat)
    return SyaratPeminjamanResponse.model_validate(syarat)


@router.put("/master/{id_syarat}", response_model=SyaratPeminjamanResponse)
def update_syarat(
    id_syarat: int,
    data: SyaratPeminjamanUpdate,
    current_user: dict = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Update syarat peminjaman (admin only)"""
    syarat = syarat_peminjaman_service.update_syarat_peminjaman(db, id_syarat, data)
    return SyaratPeminjamanResponse.model_validate(syarat)


@router.delete("/master/{id_syarat}", response_model=MessageResponse)
def delete_syarat(
    id_syarat: int,
    current_user: dict = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Delete syarat peminjaman (admin only)"""
    syarat_peminjaman_service.delete_syarat_peminjaman(db, id_syarat)
    return MessageResponse(message="Syarat peminjaman berhasil dihapus")


# ============================================================================
# PINJAMAN SYARAT ENDPOINTS
# ============================================================================

@router.get("/pinjaman/{id_pinjaman}/checklist", response_model=SyaratChecklistResponse)
def get_pinjaman_checklist(
    id_pinjaman: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get checklist syarat untuk pinjaman tertentu"""
    return syarat_peminjaman_service.get_pinjaman_syarat_checklist(db, id_pinjaman)


@router.put("/pinjaman-syarat/{id_pinjaman_syarat}", response_model=PinjamanSyaratDetailResponse)
def update_pinjaman_syarat(
    id_pinjaman_syarat: int,
    data: PinjamanSyaratUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update pinjaman syarat (upload dokumen, catatan)
    Bisa dilakukan oleh admin, bendahara, atau ketua
    """
    pinjaman_syarat = syarat_peminjaman_service.update_pinjaman_syarat(
        db, id_pinjaman_syarat, data
    )
    
    response_data = PinjamanSyaratDetailResponse(
        id_pinjaman_syarat=pinjaman_syarat.id_pinjaman_syarat,
        id_pinjaman=pinjaman_syarat.id_pinjaman,
        id_syarat=pinjaman_syarat.id_syarat,
        is_terpenuhi=pinjaman_syarat.is_terpenuhi,
        dokumen_path=pinjaman_syarat.dokumen_path,
        catatan=pinjaman_syarat.catatan,
        tanggal_verifikasi=pinjaman_syarat.tanggal_verifikasi,
        id_user_verifikasi=pinjaman_syarat.id_user_verifikasi,
        created_at=pinjaman_syarat.created_at,
        syarat=SyaratPeminjamanResponse.model_validate(pinjaman_syarat.syarat) if pinjaman_syarat.syarat else None,
        nama_syarat=pinjaman_syarat.syarat.nama_syarat if pinjaman_syarat.syarat else None,
        deskripsi_syarat=pinjaman_syarat.syarat.deskripsi if pinjaman_syarat.syarat else None,
        dokumen_diperlukan=pinjaman_syarat.syarat.dokumen_diperlukan if pinjaman_syarat.syarat else None
    )
    
    return response_data


@router.post("/pinjaman-syarat/{id_pinjaman_syarat}/verify", response_model=PinjamanSyaratDetailResponse)
def verify_pinjaman_syarat(
    id_pinjaman_syarat: int,
    data: PinjamanSyaratVerify,
    current_user: dict = Depends(is_admin_or_ketua),
    db: Session = Depends(get_db)
):
    """
    Verify pinjaman syarat (admin or ketua only)
    Menandai apakah syarat sudah terpenuhi atau belum
    """
    pinjaman_syarat = syarat_peminjaman_service.verify_pinjaman_syarat(
        db, id_pinjaman_syarat, data, current_user["id"]
    )
    
    response_data = PinjamanSyaratDetailResponse(
        id_pinjaman_syarat=pinjaman_syarat.id_pinjaman_syarat,
        id_pinjaman=pinjaman_syarat.id_pinjaman,
        id_syarat=pinjaman_syarat.id_syarat,
        is_terpenuhi=pinjaman_syarat.is_terpenuhi,
        dokumen_path=pinjaman_syarat.dokumen_path,
        catatan=pinjaman_syarat.catatan,
        tanggal_verifikasi=pinjaman_syarat.tanggal_verifikasi,
        id_user_verifikasi=pinjaman_syarat.id_user_verifikasi,
        created_at=pinjaman_syarat.created_at,
        syarat=SyaratPeminjamanResponse.model_validate(pinjaman_syarat.syarat) if pinjaman_syarat.syarat else None,
        nama_syarat=pinjaman_syarat.syarat.nama_syarat if pinjaman_syarat.syarat else None,
        deskripsi_syarat=pinjaman_syarat.syarat.deskripsi if pinjaman_syarat.syarat else None,
        dokumen_diperlukan=pinjaman_syarat.syarat.dokumen_diperlukan if pinjaman_syarat.syarat else None
    )
    
    return response_data