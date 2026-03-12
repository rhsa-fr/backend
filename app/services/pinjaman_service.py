# ============================================================================
# FILE: app/services/pinjaman_service.py
# ============================================================================

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.models.pinjaman import Pinjaman, StatusPinjaman
from app.models.anggota import Anggota
from app.models.angsuran import Angsuran, StatusAngsuran
from app.schemas.pinjaman import (
    PinjamanCreate, PinjamanApprove, PinjamanReject,
    PinjamanCalculation, PinjamanUpdate
)
from app.core.exceptions import NotFoundException, BadRequestException, BusinessLogicException
from app.config import settings


def generate_no_pinjaman() -> str:
    """Generate nomor pinjaman unik"""
    now = datetime.now()
    return f"PJM-{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}"


def calculate_pinjaman(
    nominal_pinjaman: float,
    bunga_persen: float,
    lama_angsuran: int
) -> PinjamanCalculation:
    """Kalkulasi pinjaman"""
    total_bunga = nominal_pinjaman * (bunga_persen / 100)
    total_pinjaman = nominal_pinjaman + total_bunga
    nominal_angsuran = total_pinjaman / lama_angsuran
    
    return PinjamanCalculation(
        nominal_pinjaman=nominal_pinjaman,
        bunga_persen=bunga_persen,
        lama_angsuran=lama_angsuran,
        total_bunga=total_bunga,
        total_pinjaman=total_pinjaman,
        nominal_angsuran=nominal_angsuran
    )


def create_pinjaman(
    db: Session,
    data: PinjamanCreate,
    id_user: int
) -> Pinjaman:
    """Create pengajuan pinjaman"""
    # Validasi anggota
    anggota = db.query(Anggota).filter(Anggota.id_anggota == data.id_anggota).first()
    if not anggota:
        raise NotFoundException("Anggota tidak ditemukan")
    
    if anggota.status != "aktif":
        raise BusinessLogicException("Anggota tidak aktif")
    
    # Validasi pinjaman aktif
    pinjaman_aktif = db.query(Pinjaman).filter(
        and_(
            Pinjaman.id_anggota == data.id_anggota,
            Pinjaman.status.in_([StatusPinjaman.PENDING, StatusPinjaman.DISETUJUI])
        )
    ).first()
    
    if pinjaman_aktif:
        raise BusinessLogicException(
            "Anggota masih memiliki pinjaman aktif atau pending"
        )
    
    # Kalkulasi
    calc = calculate_pinjaman(
        float(data.nominal_pinjaman),
        float(data.bunga_persen),
        data.lama_angsuran
    )
    
    # Create pinjaman
    pinjaman = Pinjaman(
        id_anggota=data.id_anggota,
        no_pinjaman=generate_no_pinjaman(),
        tanggal_pengajuan=data.tanggal_pengajuan,
        nominal_pinjaman=data.nominal_pinjaman,
        bunga_persen=data.bunga_persen,
        total_bunga=calc.total_bunga,
        total_pinjaman=calc.total_pinjaman,
        lama_angsuran=data.lama_angsuran,
        nominal_angsuran=calc.nominal_angsuran,
        keperluan=data.keperluan,
        status=StatusPinjaman.PENDING,
        sisa_pinjaman=calc.total_pinjaman,
        id_user_pengaju=id_user
    )
    
    db.add(pinjaman)
    db.commit()
    db.refresh(pinjaman)
    
    return pinjaman


def approve_pinjaman(
    db: Session,
    id_pinjaman: int,
    data: PinjamanApprove,
    id_user: int
) -> Pinjaman:
    """Approve pinjaman by ketua"""
    pinjaman = db.query(Pinjaman).filter(Pinjaman.id_pinjaman == id_pinjaman).first()
    if not pinjaman:
        raise NotFoundException("Pinjaman tidak ditemukan")
    
    if pinjaman.status != StatusPinjaman.PENDING:
        raise BusinessLogicException("Pinjaman sudah diproses sebelumnya")
    
    # Update pinjaman
    pinjaman.status = StatusPinjaman.DISETUJUI
    pinjaman.tanggal_persetujuan = data.tanggal_persetujuan
    pinjaman.tanggal_pencairan = data.tanggal_pencairan
    pinjaman.catatan_persetujuan = data.catatan_persetujuan
    pinjaman.id_user_persetujuan = id_user
    
    db.commit()
    db.refresh(pinjaman)
    
    # Generate angsuran schedule
    from app.services.angsuran_service import generate_angsuran_schedule
    generate_angsuran_schedule(db, pinjaman)
    
    return pinjaman


def reject_pinjaman(
    db: Session,
    id_pinjaman: int,
    data: PinjamanReject,
    id_user: int
) -> Pinjaman:
    """Reject pinjaman by ketua"""
    pinjaman = db.query(Pinjaman).filter(Pinjaman.id_pinjaman == id_pinjaman).first()
    if not pinjaman:
        raise NotFoundException("Pinjaman tidak ditemukan")
    
    if pinjaman.status != StatusPinjaman.PENDING:
        raise BusinessLogicException("Pinjaman sudah diproses sebelumnya")
    
    # Update pinjaman
    pinjaman.status = StatusPinjaman.DITOLAK
    pinjaman.tanggal_persetujuan = data.tanggal_persetujuan
    pinjaman.catatan_persetujuan = data.catatan_persetujuan
    pinjaman.id_user_persetujuan = id_user
    
    db.commit()
    db.refresh(pinjaman)
    
    return pinjaman


def update_pinjaman(
    db: Session,
    id_pinjaman: int,
    data: PinjamanUpdate
) -> Pinjaman:
    """Update pinjaman (hanya yang masih pending)"""
    pinjaman = db.query(Pinjaman).filter(Pinjaman.id_pinjaman == id_pinjaman).first()
    if not pinjaman:
        raise NotFoundException("Pinjaman tidak ditemukan")
    
    if pinjaman.status != StatusPinjaman.PENDING:
        raise BusinessLogicException("Hanya pinjaman pending yang bisa diupdate")
    
    # Update fields
    if data.keperluan is not None:
        pinjaman.keperluan = data.keperluan
    
    if data.bunga_persen is not None or data.lama_angsuran is not None:
        bunga = float(data.bunga_persen) if data.bunga_persen else float(pinjaman.bunga_persen)
        lama = data.lama_angsuran if data.lama_angsuran else pinjaman.lama_angsuran
        
        calc = calculate_pinjaman(float(pinjaman.nominal_pinjaman), bunga, lama)
        
        pinjaman.bunga_persen = bunga
        pinjaman.lama_angsuran = lama
        pinjaman.total_bunga = calc.total_bunga
        pinjaman.total_pinjaman = calc.total_pinjaman
        pinjaman.nominal_angsuran = calc.nominal_angsuran
        pinjaman.sisa_pinjaman = calc.total_pinjaman
    
    db.commit()
    db.refresh(pinjaman)
    
    return pinjaman


def get_pinjaman_list(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    id_anggota: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> tuple[List[Pinjaman], int]:
    """Get list pinjaman dengan filter"""
    query = db.query(Pinjaman)
    
    if id_anggota:
        query = query.filter(Pinjaman.id_anggota == id_anggota)
    
    if status:
        query = query.filter(Pinjaman.status == status)
    
    if start_date:
        query = query.filter(Pinjaman.tanggal_pengajuan >= start_date)
    
    if end_date:
        query = query.filter(Pinjaman.tanggal_pengajuan <= end_date)
    
    total = query.count()
    pinjaman_list = query.order_by(Pinjaman.created_at.desc()).offset(skip).limit(limit).all()
    
    return pinjaman_list, total


def get_pinjaman_by_id(db: Session, id_pinjaman: int) -> Pinjaman:
    """Get pinjaman by ID"""
    pinjaman = db.query(Pinjaman).filter(Pinjaman.id_pinjaman == id_pinjaman).first()
    if not pinjaman:
        raise NotFoundException("Pinjaman tidak ditemukan")
    return pinjaman


def get_pinjaman_pending(db: Session) -> List[Pinjaman]:
    """Get semua pinjaman pending approval"""
    return db.query(Pinjaman).filter(
        Pinjaman.status == StatusPinjaman.PENDING
    ).order_by(Pinjaman.tanggal_pengajuan.asc()).all()


def check_pinjaman_lunas(db: Session, id_pinjaman: int):
    """Check dan update status pinjaman jika sudah lunas"""
    pinjaman = get_pinjaman_by_id(db, id_pinjaman)
    
    if pinjaman.status != StatusPinjaman.DISETUJUI:
        return
    
    # Check semua angsuran
    angsuran_belum_lunas = db.query(Angsuran).filter(
    and_(
        Angsuran.id_pinjaman == id_pinjaman,
        Angsuran.status == StatusAngsuran.BELUM_BAYAR 
        )
    ).count()
    
    if angsuran_belum_lunas == 0:
        pinjaman.status = StatusPinjaman.LUNAS
        pinjaman.tanggal_lunas = date.today()
        pinjaman.sisa_pinjaman = 0
        db.commit()