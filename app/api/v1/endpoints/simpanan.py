# ============================================================================
# FILE: app/api/v1/endpoints/simpanan.py  — REPLACE existing file
# ============================================================================

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.core.permissions import get_current_user
from app.models.simpanan import Simpanan
from app.models.jenis_simpanan import JenisSimpanan
from app.schemas.anggota import (
    SimpananCreate,
    SimpananResponse,
    SaldoSimpananResponse,
    JenisSimpananResponse,
)
from app.schemas.common import PaginatedResponse, PaginationMeta, MessageResponse
from app.services import simpanan_service

router = APIRouter()


# ── Helper: model → response dict ────────────────────────────────────────────
def _to_response(s: Simpanan) -> SimpananResponse:
    return SimpananResponse(
        id_simpanan=s.id_simpanan,
        id_anggota=s.id_anggota,
        nama_anggota=s.anggota.nama_lengkap if s.anggota else None,
        id_jenis_simpanan=s.id_jenis_simpanan,
        nama_jenis_simpanan=s.jenis_simpanan.nama_jenis if s.jenis_simpanan else None,
        no_transaksi=s.no_transaksi,
        tanggal_transaksi=s.tanggal_transaksi,
        tipe_transaksi=s.tipe_transaksi,
        nominal=float(s.nominal),
        saldo_akhir=float(s.saldo_akhir),
        keterangan=s.keterangan,
        created_at=s.created_at,
    )


# ── GET /simpanan — list transaksi dengan filter ──────────────────────────────
@router.get("", response_model=PaginatedResponse[SimpananResponse])
def get_simpanan_list(
    skip: int = 0,
    limit: int = 10,
    id_anggota: Optional[int] = None,
    id_jenis_simpanan: Optional[int] = None,
    tipe_transaksi: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list transaksi simpanan"""
    simpanan_list, total = simpanan_service.get_simpanan_list(
        db=db,
        skip=skip,
        limit=limit,
        id_anggota=id_anggota,
        id_jenis_simpanan=id_jenis_simpanan,
        tipe_transaksi=tipe_transaksi,
        start_date=start_date,
        end_date=end_date,
    )
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1

    return PaginatedResponse(
        data=[_to_response(s) for s in simpanan_list],
        meta=PaginationMeta(
            total=total, skip=skip, limit=limit, page=page, total_pages=total_pages
        ),
    )


# ── POST /simpanan/setor ──────────────────────────────────────────────────────
@router.post("/setor", response_model=SimpananResponse, status_code=status.HTTP_201_CREATED)
def setor_simpanan(
    data: SimpananCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Setor simpanan"""
    s = simpanan_service.setor_simpanan(db=db, data=data, id_user=current_user["id"])
    return _to_response(s)


# ── POST /simpanan/tarik ──────────────────────────────────────────────────────
@router.post("/tarik", response_model=SimpananResponse, status_code=status.HTTP_201_CREATED)
def tarik_simpanan(
    data: SimpananCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Tarik simpanan — backend akan reject jika saldo tidak cukup"""
    s = simpanan_service.tarik_simpanan(db=db, data=data, id_user=current_user["id"])
    return _to_response(s)


# ── GET /simpanan/saldo/{id_anggota} ─────────────────────────────────────────
@router.get("/saldo/{id_anggota}", response_model=List[SaldoSimpananResponse])
def get_saldo_anggota(
    id_anggota: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get saldo per jenis simpanan untuk satu anggota"""
    return simpanan_service.get_saldo_anggota(db=db, id_anggota=id_anggota)


# ── GET /simpanan/jenis — list jenis simpanan aktif ───────────────────────────
@router.get("/jenis", response_model=List[JenisSimpananResponse])
def get_jenis_simpanan(
    is_active: Optional[bool] = True,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list jenis simpanan"""
    query = db.query(JenisSimpanan)
    if is_active is not None:
        query = query.filter(JenisSimpanan.is_active == is_active)
    jenis_list = query.order_by(JenisSimpanan.id_jenis_simpanan).all()
    return [
        JenisSimpananResponse(
            id_jenis_simpanan=j.id_jenis_simpanan,
            kode_jenis=j.kode_jenis,
            nama_jenis=j.nama_jenis,
            deskripsi=j.deskripsi,
            is_wajib=j.is_wajib,
            nominal_tetap=float(j.nominal_tetap),
            is_active=j.is_active,
        )
        for j in jenis_list
    ]


# ── GET /simpanan/{id} ────────────────────────────────────────────────────────
@router.get("/{simpanan_id}", response_model=SimpananResponse)
def get_simpanan_by_id(
    simpanan_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get transaksi simpanan by ID"""
    s = simpanan_service.get_simpanan_by_id(db=db, id_simpanan=simpanan_id)
    return _to_response(s)