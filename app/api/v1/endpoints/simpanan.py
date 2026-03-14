# ============================================================================
# FILE: app/api/v1/endpoints/simpanan.py  — UPDATED with Jenis Simpanan CRUD
# ============================================================================

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.core.permissions import get_current_user, is_admin
from app.models.simpanan import Simpanan
from app.models.jenis_simpanan import JenisSimpanan
from app.schemas.anggota import (
    SimpananCreate,
    SimpananResponse,
    SaldoSimpananResponse,
    JenisSimpananResponse,
    JenisSimpananCreate,
    JenisSimpananUpdate,
)
from app.schemas.common import PaginatedResponse, PaginationMeta, MessageResponse
from app.services import simpanan_service
from app.core.exceptions import NotFoundException, ConflictException, BadRequestException

router = APIRouter()


# ── Helper: Simpanan model → response ────────────────────────────────────────
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


def _jenis_to_response(j: JenisSimpanan) -> JenisSimpananResponse:
    return JenisSimpananResponse(
        id_jenis_simpanan=j.id_jenis_simpanan,
        kode_jenis=j.kode_jenis,
        nama_jenis=j.nama_jenis,
        deskripsi=j.deskripsi,
        is_wajib=j.is_wajib,
        nominal_tetap=float(j.nominal_tetap),
        is_active=j.is_active,
    )


# ============================================================================
# JENIS SIMPANAN ENDPOINTS
# ============================================================================

# ── GET /simpanan/jenis — list semua jenis simpanan ───────────────────────────
@router.get("/jenis", response_model=List[JenisSimpananResponse])
def get_jenis_simpanan(
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get list jenis simpanan.
    - is_active=true  → hanya aktif (untuk dropdown transaksi)
    - is_active=false → hanya nonaktif
    - tanpa filter    → semua (untuk halaman admin)
    """
    query = db.query(JenisSimpanan)
    if is_active is not None:
        query = query.filter(JenisSimpanan.is_active == is_active)
    jenis_list = query.order_by(JenisSimpanan.id_jenis_simpanan).all()
    return [_jenis_to_response(j) for j in jenis_list]


# ── POST /simpanan/jenis — tambah jenis simpanan (admin only) ─────────────────
@router.post("/jenis", response_model=JenisSimpananResponse, status_code=status.HTTP_201_CREATED)
def create_jenis_simpanan(
    data: JenisSimpananCreate,
    current_user: dict = Depends(is_admin),
    db: Session = Depends(get_db),
):
    """Tambah jenis simpanan baru (admin only)"""
    # Cek kode unik
    existing = db.query(JenisSimpanan).filter(
        JenisSimpanan.kode_jenis == data.kode_jenis.upper()
    ).first()
    if existing:
        raise ConflictException(f"Kode jenis '{data.kode_jenis}' sudah digunakan")

    # Validasi nominal tidak negatif
    if data.nominal_tetap < 0:
        raise BadRequestException("Nominal tidak boleh negatif")

    jenis = JenisSimpanan(
        kode_jenis=data.kode_jenis.upper(),
        nama_jenis=data.nama_jenis,
        deskripsi=data.deskripsi,
        is_wajib=data.is_wajib,
        nominal_tetap=data.nominal_tetap,
        is_active=True,
    )
    db.add(jenis)
    db.commit()
    db.refresh(jenis)
    return _jenis_to_response(jenis)


# ── GET /simpanan/jenis/{id} — detail jenis simpanan ─────────────────────────
@router.get("/jenis/{id_jenis}", response_model=JenisSimpananResponse)
def get_jenis_simpanan_by_id(
    id_jenis: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get jenis simpanan by ID"""
    jenis = db.query(JenisSimpanan).filter(
        JenisSimpanan.id_jenis_simpanan == id_jenis
    ).first()
    if not jenis:
        raise NotFoundException("Jenis simpanan tidak ditemukan")
    return _jenis_to_response(jenis)


# ── PUT /simpanan/jenis/{id} — update jenis simpanan (admin only) ─────────────
@router.put("/jenis/{id_jenis}", response_model=JenisSimpananResponse)
def update_jenis_simpanan(
    id_jenis: int,
    data: JenisSimpananUpdate,
    current_user: dict = Depends(is_admin),
    db: Session = Depends(get_db),
):
    """Update jenis simpanan (admin only)"""
    jenis = db.query(JenisSimpanan).filter(
        JenisSimpanan.id_jenis_simpanan == id_jenis
    ).first()
    if not jenis:
        raise NotFoundException("Jenis simpanan tidak ditemukan")

    # Cek konflik kode jika berubah
    if data.kode_jenis is not None:
        conflict = db.query(JenisSimpanan).filter(
            JenisSimpanan.kode_jenis == data.kode_jenis.upper(),
            JenisSimpanan.id_jenis_simpanan != id_jenis,
        ).first()
        if conflict:
            raise ConflictException(f"Kode jenis '{data.kode_jenis}' sudah digunakan")
        jenis.kode_jenis = data.kode_jenis.upper()

    # Validasi nominal
    if data.nominal_tetap is not None:
        if data.nominal_tetap < 0:
            raise BadRequestException("Nominal tidak boleh negatif")
        jenis.nominal_tetap = data.nominal_tetap

    if data.nama_jenis  is not None: jenis.nama_jenis  = data.nama_jenis
    if data.deskripsi   is not None: jenis.deskripsi   = data.deskripsi
    if data.is_wajib    is not None: jenis.is_wajib    = data.is_wajib
    if data.is_active   is not None: jenis.is_active   = data.is_active

    db.commit()
    db.refresh(jenis)
    return _jenis_to_response(jenis)


# ── DELETE /simpanan/jenis/{id} — hapus / nonaktifkan jenis simpanan ──────────
@router.delete("/jenis/{id_jenis}", response_model=MessageResponse)
def delete_jenis_simpanan(
    id_jenis: int,
    current_user: dict = Depends(is_admin),
    db: Session = Depends(get_db),
):
    """
    Nonaktifkan jenis simpanan (soft delete).
    Jika belum pernah dipakai di transaksi → hapus permanen.
    Jika sudah dipakai → hanya set is_active = False.
    """
    jenis = db.query(JenisSimpanan).filter(
        JenisSimpanan.id_jenis_simpanan == id_jenis
    ).first()
    if not jenis:
        raise NotFoundException("Jenis simpanan tidak ditemukan")

    # Cek apakah sudah pernah dipakai di transaksi
    used = db.query(Simpanan).filter(
        Simpanan.id_jenis_simpanan == id_jenis
    ).first()

    if used:
        # Soft delete: nonaktifkan saja
        jenis.is_active = False
        db.commit()
        return MessageResponse(message=f"Jenis simpanan '{jenis.nama_jenis}' dinonaktifkan (sudah digunakan dalam transaksi)")
    else:
        # Hard delete: belum pernah dipakai
        db.delete(jenis)
        db.commit()
        return MessageResponse(message=f"Jenis simpanan '{jenis.nama_jenis}' berhasil dihapus")


# ── PATCH /simpanan/jenis/{id}/toggle — toggle aktif/nonaktif ────────────────
@router.patch("/jenis/{id_jenis}/toggle", response_model=JenisSimpananResponse)
def toggle_jenis_simpanan(
    id_jenis: int,
    current_user: dict = Depends(is_admin),
    db: Session = Depends(get_db),
):
    """Toggle status aktif jenis simpanan (admin only)"""
    jenis = db.query(JenisSimpanan).filter(
        JenisSimpanan.id_jenis_simpanan == id_jenis
    ).first()
    if not jenis:
        raise NotFoundException("Jenis simpanan tidak ditemukan")
    jenis.is_active = not jenis.is_active
    db.commit()
    db.refresh(jenis)
    return _jenis_to_response(jenis)


# ============================================================================
# SIMPANAN TRANSAKSI ENDPOINTS
# ============================================================================

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