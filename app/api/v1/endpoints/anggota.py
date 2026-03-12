# ============================================================================
# FILE: app/api/v1/endpoints/anggota.py
# ============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.anggota import Anggota, StatusAnggota
from app.models.profil_anggota import ProfilAnggota
from app.schemas.anggota import (
    AnggotaCreate, AnggotaUpdate, AnggotaResponse, AnggotaDetailResponse,
    ProfilAnggotaCreate, ProfilAnggotaUpdate, ProfilAnggotaResponse
)
from app.schemas.common import PaginatedResponse, PaginationMeta, MessageResponse
from app.core.permissions import get_current_user
from app.core.exceptions import NotFoundException, ConflictException

router = APIRouter()


def generate_no_anggota(db: Session) -> str:
    """Generate nomor anggota unik"""
    now = datetime.now()
    prefix = f"A-{now.strftime('%Y%m%d')}"
    
    # Get last number today
    last_anggota = db.query(Anggota).filter(
        Anggota.no_anggota.like(f"{prefix}%")
    ).order_by(Anggota.no_anggota.desc()).first()
    
    if last_anggota:
        last_num = int(last_anggota.no_anggota.split('-')[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"{prefix}-{new_num:03d}"


@router.get("", response_model=PaginatedResponse[AnggotaResponse])
def get_anggota_list(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list anggota"""
    query = db.query(Anggota)
    
    if status:
        query = query.filter(Anggota.status == status)
    
    if search:
        query = query.filter(
            Anggota.nama_lengkap.contains(search) |
            Anggota.no_anggota.contains(search)
        )
    
    total = query.count()
    anggota_list = query.order_by(Anggota.created_at.desc()).offset(skip).limit(limit).all()
    
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    
    return PaginatedResponse(
        data=[AnggotaResponse.model_validate(a) for a in anggota_list],
        meta=PaginationMeta(
            total=total,
            skip=skip,
            limit=limit,
            page=page,
            total_pages=total_pages
        )
    )


@router.post("", response_model=AnggotaResponse, status_code=status.HTTP_201_CREATED)
def create_anggota(
    data: AnggotaCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create anggota baru"""
    # Check email conflict
    if data.email:
        existing = db.query(Anggota).filter(Anggota.email == data.email).first()
        if existing:
            raise ConflictException("Email sudah digunakan")
    
    # Generate no_anggota
    no_anggota = generate_no_anggota(db)
    
    # Create anggota
    anggota = Anggota(
        no_anggota=no_anggota,
        nama_lengkap=data.nama_lengkap,
        email=data.email,
        no_telepon=data.no_telepon,
        tanggal_bergabung=data.tanggal_bergabung,
        status=StatusAnggota.AKTIF
    )
    
    db.add(anggota)
    db.commit()
    db.refresh(anggota)
    
    return AnggotaResponse.model_validate(anggota)


@router.get("/{id_anggota}", response_model=AnggotaResponse)
def get_anggota(
    id_anggota: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get anggota by ID"""
    anggota = db.query(Anggota).filter(Anggota.id_anggota == id_anggota).first()
    if not anggota:
        raise NotFoundException("Anggota tidak ditemukan")
    
    return AnggotaResponse.model_validate(anggota)


@router.get("/{id_anggota}/detail", response_model=AnggotaDetailResponse)
def get_anggota_detail(
    id_anggota: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detail anggota dengan profil dan saldo"""
    anggota = db.query(Anggota).filter(Anggota.id_anggota == id_anggota).first()
    if not anggota:
        raise NotFoundException("Anggota tidak ditemukan")
    
    # Get profil
    profil_data = None
    if anggota.profil:
        profil_data = ProfilAnggotaResponse.model_validate(anggota.profil)
    
    # Get total simpanan
    from app.services.simpanan_service import get_total_saldo_anggota
    try:
        total_simpanan = get_total_saldo_anggota(db, id_anggota)
    except:
        total_simpanan = 0
    
    # Get total pinjaman aktif
    from app.models.pinjaman import Pinjaman, StatusPinjaman
    from sqlalchemy import func
    total_pinjaman = db.query(func.sum(Pinjaman.sisa_pinjaman)).filter(
    Pinjaman.id_anggota == id_anggota,
    Pinjaman.status == StatusPinjaman.DISETUJUI
    ).scalar() or 0
    
    response_data = AnggotaResponse.model_validate(anggota).model_dump()
    response_data["profil"] = profil_data
    response_data["total_simpanan"] = float(total_simpanan)
    response_data["total_pinjaman_aktif"] = float(total_pinjaman)
    
    return AnggotaDetailResponse(**response_data)


@router.put("/{id_anggota}", response_model=AnggotaResponse)
def update_anggota(
    id_anggota: int,
    data: AnggotaUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update anggota"""
    anggota = db.query(Anggota).filter(Anggota.id_anggota == id_anggota).first()
    if not anggota:
        raise NotFoundException("Anggota tidak ditemukan")
    
    # Update fields
    if data.nama_lengkap is not None:
        anggota.nama_lengkap = data.nama_lengkap
    
    if data.email is not None:
        # Check email conflict
        existing = db.query(Anggota).filter(
            Anggota.email == data.email,
            Anggota.id_anggota != id_anggota
        ).first()
        if existing:
            raise ConflictException("Email sudah digunakan")
        anggota.email = data.email
    
    if data.no_telepon is not None:
        anggota.no_telepon = data.no_telepon
    
    if data.tanggal_bergabung is not None:
        anggota.tanggal_bergabung = data.tanggal_bergabung
    
    if data.status is not None:
        anggota.status = data.status
    
    db.commit()
    db.refresh(anggota)
    
    return AnggotaResponse.model_validate(anggota)


@router.delete("/{id_anggota}", response_model=MessageResponse)
def delete_anggota(
    id_anggota: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete anggota"""
    anggota = db.query(Anggota).filter(Anggota.id_anggota == id_anggota).first()
    if not anggota:
        raise NotFoundException("Anggota tidak ditemukan")
    
    db.delete(anggota)
    db.commit()
    
    return MessageResponse(message="Anggota berhasil dihapus")


# Profil Anggota Endpoints
@router.post("/{id_anggota}/profil", response_model=ProfilAnggotaResponse, status_code=status.HTTP_201_CREATED)
def create_profil_anggota(
    id_anggota: int,
    data: ProfilAnggotaUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create atau update profil anggota"""
    # Check anggota exists
    anggota = db.query(Anggota).filter(Anggota.id_anggota == id_anggota).first()
    if not anggota:
        raise NotFoundException("Anggota tidak ditemukan")
    
    # Check profil exists
    profil = db.query(ProfilAnggota).filter(ProfilAnggota.id_anggota == id_anggota).first()
    
    if profil:
        # Update existing profil
        if data.nik is not None:
            profil.nik = data.nik
        if data.tempat_lahir is not None:
            profil.tempat_lahir = data.tempat_lahir
        if data.tanggal_lahir is not None:
            profil.tanggal_lahir = data.tanggal_lahir
        if data.jenis_kelamin is not None:
            profil.jenis_kelamin = data.jenis_kelamin
        if data.alamat is not None:
            profil.alamat = data.alamat
        if data.kota is not None:
            profil.kota = data.kota
        if data.provinsi is not None:
            profil.provinsi = data.provinsi
        if data.kode_pos is not None:
            profil.kode_pos = data.kode_pos
        if data.pekerjaan is not None:
            profil.pekerjaan = data.pekerjaan
        if data.foto_profil is not None:
            profil.foto_profil = data.foto_profil
    else:
        # Create new profil
        profil = ProfilAnggota(
            id_anggota=id_anggota,
            nik=data.nik,
            tempat_lahir=data.tempat_lahir,
            tanggal_lahir=data.tanggal_lahir,
            jenis_kelamin=data.jenis_kelamin,
            alamat=data.alamat,
            kota=data.kota,
            provinsi=data.provinsi,
            kode_pos=data.kode_pos,
            pekerjaan=data.pekerjaan,
            foto_profil=data.foto_profil
        )
        db.add(profil)
    
    db.commit()
    db.refresh(profil)
    
    return ProfilAnggotaResponse.model_validate(profil)


@router.get("/{id_anggota}/profil", response_model=ProfilAnggotaResponse)
def get_profil_anggota(
    id_anggota: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get profil anggota"""
    profil = db.query(ProfilAnggota).filter(ProfilAnggota.id_anggota == id_anggota).first()
    if not profil:
        raise NotFoundException("Profil anggota tidak ditemukan")
    
    return ProfilAnggotaResponse.model_validate(profil)
