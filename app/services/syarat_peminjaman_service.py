# ============================================================================
# FILE: app/services/syarat_peminjaman_service.py
# ============================================================================

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
from app.models.syarat_peminjaman import SyaratPeminjaman
from app.models.pinjaman_syarat import PinjamanSyarat
from app.models.pinjaman import Pinjaman
from app.schemas.syarat_peminjaman import (
    SyaratPeminjamanCreate, SyaratPeminjamanUpdate,
    PinjamanSyaratCreate, PinjamanSyaratUpdate,
    PinjamanSyaratVerify, SyaratChecklistResponse,
    PinjamanSyaratDetailResponse, SyaratPeminjamanResponse
)
from app.core.exceptions import NotFoundException, ConflictException, BusinessLogicException


# ============================================================================
# SYARAT PEMINJAMAN CRUD
# ============================================================================

def create_syarat_peminjaman(db: Session, data: SyaratPeminjamanCreate) -> SyaratPeminjaman:
    """Create syarat peminjaman baru"""
    # Check kode conflict
    existing = db.query(SyaratPeminjaman).filter(
        SyaratPeminjaman.kode_syarat == data.kode_syarat
    ).first()
    if existing:
        raise ConflictException(f"Kode syarat '{data.kode_syarat}' sudah digunakan")
    
    syarat = SyaratPeminjaman(
        kode_syarat=data.kode_syarat,
        nama_syarat=data.nama_syarat,
        deskripsi=data.deskripsi,
        is_wajib=data.is_wajib,
        min_nominal_pinjaman=data.min_nominal_pinjaman,
        max_nominal_pinjaman=data.max_nominal_pinjaman,
        dokumen_diperlukan=data.dokumen_diperlukan,
        urutan=data.urutan,
        is_active=True
    )
    
    db.add(syarat)
    db.commit()
    db.refresh(syarat)
    
    return syarat


def get_syarat_list(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    nominal_pinjaman: Optional[float] = None
) -> tuple[List[SyaratPeminjaman], int]:
    """
    Get list syarat peminjaman
    
    Args:
        nominal_pinjaman: Jika diisi, filter syarat berdasarkan nominal pinjaman
    """
    query = db.query(SyaratPeminjaman)
    
    if is_active is not None:
        query = query.filter(SyaratPeminjaman.is_active == is_active)
    
    # Filter berdasarkan nominal pinjaman
    if nominal_pinjaman is not None:
        query = query.filter(
            and_(
                (SyaratPeminjaman.min_nominal_pinjaman == None) | 
                (SyaratPeminjaman.min_nominal_pinjaman <= nominal_pinjaman),
                (SyaratPeminjaman.max_nominal_pinjaman == None) | 
                (SyaratPeminjaman.max_nominal_pinjaman >= nominal_pinjaman)
            )
        )
    
    total = query.count()
    syarat_list = query.order_by(SyaratPeminjaman.urutan.asc()).offset(skip).limit(limit).all()
    
    return syarat_list, total


def get_syarat_by_id(db: Session, id_syarat: int) -> SyaratPeminjaman:
    """Get syarat by ID"""
    syarat = db.query(SyaratPeminjaman).filter(
        SyaratPeminjaman.id_syarat == id_syarat
    ).first()
    if not syarat:
        raise NotFoundException("Syarat peminjaman tidak ditemukan")
    return syarat


def update_syarat_peminjaman(
    db: Session,
    id_syarat: int,
    data: SyaratPeminjamanUpdate
) -> SyaratPeminjaman:
    """Update syarat peminjaman"""
    syarat = get_syarat_by_id(db, id_syarat)
    
    # Check kode conflict
    if data.kode_syarat and data.kode_syarat != syarat.kode_syarat:
        existing = db.query(SyaratPeminjaman).filter(
            SyaratPeminjaman.kode_syarat == data.kode_syarat,
            SyaratPeminjaman.id_syarat != id_syarat
        ).first()
        if existing:
            raise ConflictException(f"Kode syarat '{data.kode_syarat}' sudah digunakan")
        syarat.kode_syarat = data.kode_syarat
    
    if data.nama_syarat is not None:
        syarat.nama_syarat = data.nama_syarat
    if data.deskripsi is not None:
        syarat.deskripsi = data.deskripsi
    if data.is_wajib is not None:
        syarat.is_wajib = data.is_wajib
    if data.min_nominal_pinjaman is not None:
        syarat.min_nominal_pinjaman = data.min_nominal_pinjaman
    if data.max_nominal_pinjaman is not None:
        syarat.max_nominal_pinjaman = data.max_nominal_pinjaman
    if data.dokumen_diperlukan is not None:
        syarat.dokumen_diperlukan = data.dokumen_diperlukan
    if data.is_active is not None:
        syarat.is_active = data.is_active
    if data.urutan is not None:
        syarat.urutan = data.urutan
    
    db.commit()
    db.refresh(syarat)
    
    return syarat


def delete_syarat_peminjaman(db: Session, id_syarat: int):
    """Delete syarat peminjaman"""
    syarat = get_syarat_by_id(db, id_syarat)
    
    # Check jika syarat sudah digunakan
    usage_count = db.query(PinjamanSyarat).filter(
        PinjamanSyarat.id_syarat == id_syarat
    ).count()
    
    if usage_count > 0:
        raise BusinessLogicException(
            f"Syarat tidak dapat dihapus karena sudah digunakan pada {usage_count} pinjaman. "
            "Silakan non-aktifkan saja."
        )
    
    db.delete(syarat)
    db.commit()


# ============================================================================
# PINJAMAN SYARAT MANAGEMENT
# ============================================================================

def attach_syarat_to_pinjaman(
    db: Session,
    id_pinjaman: int,
    nominal_pinjaman: float
) -> List[PinjamanSyarat]:
    """
    Attach syarat yang berlaku ke pinjaman baru
    Dipanggil otomatis saat create pinjaman
    """
    # Get syarat yang berlaku untuk nominal ini
    syarat_list, _ = get_syarat_list(
        db,
        is_active=True,
        nominal_pinjaman=nominal_pinjaman
    )
    
    pinjaman_syarat_list = []
    for syarat in syarat_list:
        pinjaman_syarat = PinjamanSyarat(
            id_pinjaman=id_pinjaman,
            id_syarat=syarat.id_syarat,
            is_terpenuhi=False
        )
        db.add(pinjaman_syarat)
        pinjaman_syarat_list.append(pinjaman_syarat)
    
    db.commit()
    
    return pinjaman_syarat_list


def update_pinjaman_syarat(
    db: Session,
    id_pinjaman_syarat: int,
    data: PinjamanSyaratUpdate
) -> PinjamanSyarat:
    """Update status pinjaman syarat"""
    pinjaman_syarat = db.query(PinjamanSyarat).filter(
        PinjamanSyarat.id_pinjaman_syarat == id_pinjaman_syarat
    ).first()
    
    if not pinjaman_syarat:
        raise NotFoundException("Pinjaman syarat tidak ditemukan")
    
    if data.is_terpenuhi is not None:
        pinjaman_syarat.is_terpenuhi = data.is_terpenuhi
    if data.dokumen_path is not None:
        pinjaman_syarat.dokumen_path = data.dokumen_path
    if data.catatan is not None:
        pinjaman_syarat.catatan = data.catatan
    
    db.commit()
    db.refresh(pinjaman_syarat)
    
    return pinjaman_syarat


def verify_pinjaman_syarat(
    db: Session,
    id_pinjaman_syarat: int,
    data: PinjamanSyaratVerify,
    id_user: int
) -> PinjamanSyarat:
    """Verify pinjaman syarat (by ketua or admin)"""
    pinjaman_syarat = db.query(PinjamanSyarat).filter(
        PinjamanSyarat.id_pinjaman_syarat == id_pinjaman_syarat
    ).first()
    
    if not pinjaman_syarat:
        raise NotFoundException("Pinjaman syarat tidak ditemukan")
    
    pinjaman_syarat.is_terpenuhi = data.is_terpenuhi
    pinjaman_syarat.catatan = data.catatan
    pinjaman_syarat.tanggal_verifikasi = datetime.now()
    pinjaman_syarat.id_user_verifikasi = id_user
    
    db.commit()
    db.refresh(pinjaman_syarat)
    
    return pinjaman_syarat


def get_pinjaman_syarat_checklist(
    db: Session,
    id_pinjaman: int
) -> SyaratChecklistResponse:
    """Get checklist syarat untuk pinjaman"""
    pinjaman = db.query(Pinjaman).filter(Pinjaman.id_pinjaman == id_pinjaman).first()
    if not pinjaman:
        raise NotFoundException("Pinjaman tidak ditemukan")
    
    # Get all syarat for this pinjaman
    pinjaman_syarat_list = db.query(PinjamanSyarat).filter(
        PinjamanSyarat.id_pinjaman == id_pinjaman
    ).all()
    
    total_syarat = len(pinjaman_syarat_list)
    syarat_terpenuhi = sum(1 for ps in pinjaman_syarat_list if ps.is_terpenuhi)
    syarat_belum_terpenuhi = total_syarat - syarat_terpenuhi
    
    # Check semua syarat wajib
    syarat_wajib_belum_terpenuhi = db.query(PinjamanSyarat).join(
        SyaratPeminjaman
    ).filter(
        PinjamanSyarat.id_pinjaman == id_pinjaman,
        SyaratPeminjaman.is_wajib == True,
        PinjamanSyarat.is_terpenuhi == False
    ).count()
    
    semua_syarat_wajib_terpenuhi = (syarat_wajib_belum_terpenuhi == 0)
    
    persentase_kelengkapan = (syarat_terpenuhi / total_syarat * 100) if total_syarat > 0 else 0
    
    # Build detail syarat
    detail_syarat = []
    for ps in pinjaman_syarat_list:
        detail_syarat.append(PinjamanSyaratDetailResponse(
            id_pinjaman_syarat=ps.id_pinjaman_syarat,
            id_pinjaman=ps.id_pinjaman,
            id_syarat=ps.id_syarat,
            is_terpenuhi=ps.is_terpenuhi,
            dokumen_path=ps.dokumen_path,
            catatan=ps.catatan,
            tanggal_verifikasi=ps.tanggal_verifikasi,
            id_user_verifikasi=ps.id_user_verifikasi,
            created_at=ps.created_at,
            syarat=SyaratPeminjamanResponse.model_validate(ps.syarat) if ps.syarat else None,
            nama_syarat=ps.syarat.nama_syarat if ps.syarat else None,
            deskripsi_syarat=ps.syarat.deskripsi if ps.syarat else None,
            dokumen_diperlukan=ps.syarat.dokumen_diperlukan if ps.syarat else None
        ))
    
    return SyaratChecklistResponse(
        total_syarat=total_syarat,
        syarat_terpenuhi=syarat_terpenuhi,
        syarat_belum_terpenuhi=syarat_belum_terpenuhi,
        persentase_kelengkapan=round(persentase_kelengkapan, 2),
        semua_syarat_wajib_terpenuhi=semua_syarat_wajib_terpenuhi,
        detail_syarat=detail_syarat
    )


def check_syarat_before_approve(db: Session, id_pinjaman: int) -> bool:
    """
    Check apakah semua syarat wajib sudah terpenuhi sebelum approve
    
    Returns:
        True jika semua syarat wajib terpenuhi, False otherwise
    """
    checklist = get_pinjaman_syarat_checklist(db, id_pinjaman)
    return checklist.semua_syarat_wajib_terpenuhi