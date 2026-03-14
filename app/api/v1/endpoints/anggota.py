# ============================================================================
# FILE: app/api/v1/endpoints/anggota.py  — REPLACE existing file
# ============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.anggota import Anggota, StatusAnggota
from app.models.profil_anggota import ProfilAnggota
from app.schemas.anggota import (
    AnggotaCreate, AnggotaUpdate, AnggotaResponse, AnggotaDetailResponse,
    ProfilAnggotaCreate, ProfilAnggotaUpdate, ProfilAnggotaResponse,
)
from app.schemas.common import PaginatedResponse, PaginationMeta, MessageResponse
from app.core.permissions import get_current_user
from app.core.exceptions import NotFoundException, ConflictException

router = APIRouter()


# ── Helpers ───────────────────────────────────────────────────────────────────
def generate_no_anggota(db: Session) -> str:
    now = datetime.now()
    prefix = f"A-{now.strftime('%Y%m%d')}"
    last = (
        db.query(Anggota)
        .filter(Anggota.no_anggota.like(f"{prefix}%"))
        .order_by(Anggota.no_anggota.desc())
        .first()
    )
    num = int(last.no_anggota.split("-")[-1]) + 1 if last else 1
    return f"{prefix}-{num:03d}"


def _clean_profil(profil: ProfilAnggota, db: Session) -> ProfilAnggota:
    """
    Bersihkan data lama: string kosong '' di kolom enum → NULL.
    Diperlukan karena data lama mungkin tersimpan sebagai '' bukan NULL.
    """
    if profil.jenis_kelamin == "":
        profil.jenis_kelamin = None
        db.commit()
    return profil


# ── GET /anggota ──────────────────────────────────────────────────────────────
@router.get("", response_model=PaginatedResponse[AnggotaResponse])
def get_anggota_list(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Anggota)
    if status:
        query = query.filter(Anggota.status == status)
    if search:
        query = query.filter(
            Anggota.nama_lengkap.contains(search) | Anggota.no_anggota.contains(search)
        )
    total = query.count()
    anggota_list = query.order_by(Anggota.created_at.desc()).offset(skip).limit(limit).all()
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    return PaginatedResponse(
        data=[AnggotaResponse.model_validate(a) for a in anggota_list],
        meta=PaginationMeta(total=total, skip=skip, limit=limit, page=page, total_pages=total_pages),
    )


# ── POST /anggota ─────────────────────────────────────────────────────────────
@router.post("", response_model=AnggotaResponse, status_code=status.HTTP_201_CREATED)
def create_anggota(
    data: AnggotaCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.email:
        if db.query(Anggota).filter(Anggota.email == data.email).first():
            raise ConflictException("Email sudah digunakan")

    anggota = Anggota(
        no_anggota=generate_no_anggota(db),
        nama_lengkap=data.nama_lengkap,
        email=data.email,
        no_telepon=data.no_telepon,
        tanggal_bergabung=data.tanggal_bergabung,
        status=StatusAnggota.AKTIF,
    )
    db.add(anggota)
    db.commit()
    db.refresh(anggota)
    return AnggotaResponse.model_validate(anggota)


# ── GET /anggota/{id} ─────────────────────────────────────────────────────────
@router.get("/{id_anggota}", response_model=AnggotaResponse)
def get_anggota(
    id_anggota: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    anggota = db.query(Anggota).filter(Anggota.id_anggota == id_anggota).first()
    if not anggota:
        raise NotFoundException("Anggota tidak ditemukan")
    return AnggotaResponse.model_validate(anggota)


# ── GET /anggota/{id}/detail ──────────────────────────────────────────────────
@router.get("/{id_anggota}/detail", response_model=AnggotaDetailResponse)
def get_anggota_detail(
    id_anggota: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    anggota = db.query(Anggota).filter(Anggota.id_anggota == id_anggota).first()
    if not anggota:
        raise NotFoundException("Anggota tidak ditemukan")

    profil = db.query(ProfilAnggota).filter(ProfilAnggota.id_anggota == id_anggota).first()

    # Bersihkan data lama sebelum serialize
    if profil:
        profil = _clean_profil(profil, db)

    from app.models.simpanan import Simpanan
    from app.models.pinjaman import Pinjaman, StatusPinjaman
    from sqlalchemy import func as sqlfunc

    total_simpanan_result = db.query(sqlfunc.sum(Simpanan.saldo_akhir)).filter(
        Simpanan.id_anggota == id_anggota
    ).scalar()

    total_pinjaman_result = db.query(sqlfunc.sum(Pinjaman.sisa_pinjaman)).filter(
        Pinjaman.id_anggota == id_anggota,
        Pinjaman.status == StatusPinjaman.DISETUJUI,
    ).scalar()

    response_data = AnggotaDetailResponse.model_validate(anggota)
    response_data.profil = ProfilAnggotaResponse.model_validate(profil) if profil else None
    response_data.total_simpanan = float(total_simpanan_result or 0)
    response_data.total_pinjaman_aktif = float(total_pinjaman_result or 0)

    return response_data


# ── PUT /anggota/{id} ─────────────────────────────────────────────────────────
@router.put("/{id_anggota}", response_model=AnggotaResponse)
def update_anggota(
    id_anggota: int,
    data: AnggotaUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    anggota = db.query(Anggota).filter(Anggota.id_anggota == id_anggota).first()
    if not anggota:
        raise NotFoundException("Anggota tidak ditemukan")

    if data.email and data.email != anggota.email:
        if db.query(Anggota).filter(Anggota.email == data.email).first():
            raise ConflictException("Email sudah digunakan")

    if data.nama_lengkap      is not None: anggota.nama_lengkap      = data.nama_lengkap
    if data.email             is not None: anggota.email             = data.email
    if data.no_telepon        is not None: anggota.no_telepon        = data.no_telepon
    if data.tanggal_bergabung is not None: anggota.tanggal_bergabung = data.tanggal_bergabung
    if data.status            is not None: anggota.status            = data.status

    db.commit()
    db.refresh(anggota)
    return AnggotaResponse.model_validate(anggota)


# ── DELETE /anggota/{id} ──────────────────────────────────────────────────────
@router.delete("/{id_anggota}", response_model=MessageResponse)
def delete_anggota(
    id_anggota: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    anggota = db.query(Anggota).filter(Anggota.id_anggota == id_anggota).first()
    if not anggota:
        raise NotFoundException("Anggota tidak ditemukan")
    db.delete(anggota)
    db.commit()
    return MessageResponse(message="Anggota berhasil dihapus")


# ── POST /anggota/{id}/profil ─────────────────────────────────────────────────
@router.post("/{id_anggota}/profil", response_model=ProfilAnggotaResponse)
def upsert_profil_anggota(
    id_anggota: int,
    data: ProfilAnggotaCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create atau update profil anggota"""
    if not db.query(Anggota).filter(Anggota.id_anggota == id_anggota).first():
        raise NotFoundException("Anggota tidak ditemukan")

    profil = db.query(ProfilAnggota).filter(ProfilAnggota.id_anggota == id_anggota).first()

    # Semua field profil yang perlu di-update
    FIELDS = [
        "nik", "tempat_lahir", "tanggal_lahir",
        "jenis_kelamin",   # Validator schema sudah konversi "" → None
        "alamat", "kota", "provinsi", "kode_pos",
        "pekerjaan", "foto_profil",
    ]

    if profil:
        # ── FIX UTAMA: set SEMUA field langsung tanpa kondisi "if not None" ──
        # Dengan ini, jika user mengosongkan field (mengirim None),
        # nilai di DB ikut dikosongkan — tidak diabaikan seperti sebelumnya.
        for field in FIELDS:
            setattr(profil, field, getattr(data, field, None))
    else:
        profil = ProfilAnggota(
            id_anggota=id_anggota,
            **{f: getattr(data, f, None) for f in FIELDS}
        )
        db.add(profil)

    db.commit()
    db.refresh(profil)

    # Pastikan string kosong tidak lolos ke response serializer
    if profil.jenis_kelamin == "":
        profil.jenis_kelamin = None
        db.commit()

    return ProfilAnggotaResponse.model_validate(profil)


# ── GET /anggota/{id}/profil ──────────────────────────────────────────────────
@router.get("/{id_anggota}/profil", response_model=ProfilAnggotaResponse)
def get_profil_anggota(
    id_anggota: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profil = db.query(ProfilAnggota).filter(ProfilAnggota.id_anggota == id_anggota).first()
    if not profil:
        raise NotFoundException("Profil anggota tidak ditemukan")

    # Bersihkan data lama dari DB
    profil = _clean_profil(profil, db)

    return ProfilAnggotaResponse.model_validate(profil)