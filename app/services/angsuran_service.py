# ============================================================================
# FILE: app/services/angsuran_service.py  — UPDATED with date filter
# ============================================================================

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from app.models.angsuran import Angsuran, StatusAngsuran
from app.models.pinjaman import Pinjaman, StatusPinjaman
from app.schemas.angsuran import (
    AngsuranBayar, AngsuranScheduleResponse, AngsuranScheduleItem,
    AngsuranSummary
)
from app.core.exceptions import NotFoundException, BadRequestException, BusinessLogicException
from app.config import settings


def generate_no_angsuran(id_pinjaman: int, angsuran_ke: int) -> str:
    """Generate nomor angsuran unik"""
    now = datetime.now()
    return f"ANG-{now.strftime('%Y%m%d')}-{id_pinjaman}-{angsuran_ke}"


def generate_angsuran_schedule(db: Session, pinjaman: Pinjaman):
    """Generate jadwal angsuran setelah pinjaman disetujui"""
    if not pinjaman.tanggal_pencairan:
        raise BusinessLogicException("Tanggal pencairan harus diisi")
    
    # Hapus angsuran lama jika ada
    db.query(Angsuran).filter(Angsuran.id_pinjaman == pinjaman.id_pinjaman).delete()
    
    # Generate angsuran
    tanggal_mulai = pinjaman.tanggal_pencairan
    sisa_pinjaman = float(pinjaman.total_pinjaman)
    nominal_angsuran = float(pinjaman.nominal_angsuran)
    total_bunga = float(pinjaman.total_bunga)
    lama_angsuran = pinjaman.lama_angsuran
    
    # Hitung porsi bunga per angsuran (flat rate)
    bunga_per_angsuran = total_bunga / lama_angsuran
    pokok_per_angsuran = nominal_angsuran - bunga_per_angsuran
    
    for i in range(1, lama_angsuran + 1):
        # Tanggal jatuh tempo = tanggal pencairan + i bulan
        tanggal_jatuh_tempo = tanggal_mulai + relativedelta(months=i)
        
        # Untuk angsuran terakhir, sesuaikan nominal agar pas
        if i == lama_angsuran:
            pokok_angsuran = sisa_pinjaman - bunga_per_angsuran
            nominal_final = sisa_pinjaman
        else:
            pokok_angsuran = pokok_per_angsuran
            nominal_final = nominal_angsuran
        
        angsuran = Angsuran(
            id_pinjaman=pinjaman.id_pinjaman,
            no_angsuran=generate_no_angsuran(pinjaman.id_pinjaman, i),
            angsuran_ke=i,
            tanggal_jatuh_tempo=tanggal_jatuh_tempo,
            nominal_angsuran=nominal_final,
            pokok=pokok_angsuran,
            bunga=bunga_per_angsuran,
            denda=0,
            total_bayar=0,
            status=StatusAngsuran.BELUM_BAYAR
        )
        
        db.add(angsuran)
        sisa_pinjaman -= pokok_angsuran
    
    db.commit()


def calculate_denda(tanggal_jatuh_tempo: date, tanggal_bayar: date, nominal: float) -> float:
    """Kalkulasi denda keterlambatan"""
    if tanggal_bayar <= tanggal_jatuh_tempo:
        return 0.0
    
    hari_terlambat = (tanggal_bayar - tanggal_jatuh_tempo).days
    denda_persen = settings.DENDA_KETERLAMBATAN_PERSEN
    denda_per_hari = nominal * (denda_persen / 100)
    total_denda = denda_per_hari * hari_terlambat
    
    return total_denda


def bayar_angsuran(
    db: Session,
    id_angsuran: int,
    data: AngsuranBayar,
    id_user: int
) -> Angsuran:
    """Bayar angsuran"""
    angsuran = db.query(Angsuran).filter(Angsuran.id_angsuran == id_angsuran).first()
    if not angsuran:
        raise NotFoundException("Angsuran tidak ditemukan")
    
    if angsuran.status == StatusAngsuran.LUNAS:
        raise BusinessLogicException("Angsuran sudah lunas")
    
    # Hitung denda
    denda = calculate_denda(
        angsuran.tanggal_jatuh_tempo,
        data.tanggal_bayar,
        float(angsuran.nominal_angsuran)
    )
    
    total_tagihan = float(angsuran.nominal_angsuran) + denda
    
    if float(data.total_bayar) < total_tagihan:
        raise BusinessLogicException(
            f"Pembayaran kurang. Total tagihan: Rp {total_tagihan:,.2f} (termasuk denda Rp {denda:,.2f})"
        )
    
    # Update angsuran
    angsuran.tanggal_bayar = data.tanggal_bayar
    angsuran.denda = denda
    angsuran.total_bayar = data.total_bayar
    angsuran.keterangan = data.keterangan
    angsuran.id_user = id_user
    
    # Set status
    if data.tanggal_bayar > angsuran.tanggal_jatuh_tempo:
        angsuran.status = StatusAngsuran.TERLAMBAT
    else:
        angsuran.status = StatusAngsuran.LUNAS
    
    db.commit()
    db.refresh(angsuran)
    
    # Update sisa pinjaman
    update_sisa_pinjaman(db, angsuran.id_pinjaman)
    
    # Check apakah pinjaman sudah lunas
    from app.services.pinjaman_service import check_pinjaman_lunas
    check_pinjaman_lunas(db, angsuran.id_pinjaman)
    
    return angsuran


def update_sisa_pinjaman(db: Session, id_pinjaman: int):
    """Update sisa pinjaman berdasarkan angsuran yang sudah dibayar"""
    pinjaman = db.query(Pinjaman).filter(Pinjaman.id_pinjaman == id_pinjaman).first()
    if not pinjaman:
        return
    
    # Hitung total pokok yang sudah dibayar
    from sqlalchemy import func
    total_pokok_dibayar = db.query(
        func.sum(Angsuran.pokok)
    ).filter(
        and_(
            Angsuran.id_pinjaman == id_pinjaman,
            Angsuran.status.in_([StatusAngsuran.LUNAS, StatusAngsuran.TERLAMBAT])
        )
    ).scalar() or 0
    
    sisa = float(pinjaman.nominal_pinjaman) - float(total_pokok_dibayar)
    pinjaman.sisa_pinjaman = max(sisa, 0)
    db.commit()


def get_angsuran_list(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    id_pinjaman: Optional[int] = None,
    status: Optional[str] = None,
    # ── FILTER BARU: bulan/tahun berdasarkan tanggal_jatuh_tempo ──────────
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> tuple[List[Angsuran], int]:
    """Get list angsuran dengan filter"""
    query = db.query(Angsuran)
    
    if id_pinjaman:
        query = query.filter(Angsuran.id_pinjaman == id_pinjaman)
    
    if status:
        query = query.filter(Angsuran.status == status)

    # Filter berdasarkan rentang tanggal jatuh tempo
    if start_date:
        query = query.filter(Angsuran.tanggal_jatuh_tempo >= start_date)

    if end_date:
        query = query.filter(Angsuran.tanggal_jatuh_tempo <= end_date)
    
    total = query.count()
    angsuran_list = query.order_by(Angsuran.tanggal_jatuh_tempo.asc()).offset(skip).limit(limit).all()
    
    return angsuran_list, total


def get_angsuran_by_id(db: Session, id_angsuran: int) -> Angsuran:
    """Get angsuran by ID"""
    angsuran = db.query(Angsuran).filter(Angsuran.id_angsuran == id_angsuran).first()
    if not angsuran:
        raise NotFoundException("Angsuran tidak ditemukan")
    return angsuran


def get_angsuran_by_pinjaman(db: Session, id_pinjaman: int) -> List[Angsuran]:
    """Get semua angsuran untuk pinjaman tertentu"""
    return db.query(Angsuran).filter(
        Angsuran.id_pinjaman == id_pinjaman
    ).order_by(Angsuran.angsuran_ke.asc()).all()


def get_angsuran_jatuh_tempo(
    db: Session,
    tanggal: Optional[date] = None,
    include_terlambat: bool = True
) -> List[Angsuran]:
    """Get angsuran yang jatuh tempo"""
    if not tanggal:
        tanggal = date.today()
    
    query = db.query(Angsuran).filter(
        Angsuran.status == StatusAngsuran.BELUM_BAYAR
    )
    
    if include_terlambat:
        query = query.filter(Angsuran.tanggal_jatuh_tempo <= tanggal)
    else:
        query = query.filter(Angsuran.tanggal_jatuh_tempo == tanggal)
    
    return query.order_by(Angsuran.tanggal_jatuh_tempo.asc()).all()


def get_angsuran_summary(db: Session, id_pinjaman: int) -> AngsuranSummary:
    """Get summary angsuran untuk pinjaman"""
    pinjaman = db.query(Pinjaman).filter(Pinjaman.id_pinjaman == id_pinjaman).first()
    if not pinjaman:
        raise NotFoundException("Pinjaman tidak ditemukan")
    
    angsuran_list = get_angsuran_by_pinjaman(db, id_pinjaman)
    
    total_angsuran = len(angsuran_list)
    angsuran_lunas = sum(1 for a in angsuran_list if a.status in [StatusAngsuran.LUNAS, StatusAngsuran.TERLAMBAT])
    angsuran_belum_bayar = sum(1 for a in angsuran_list if a.status == StatusAngsuran.BELUM_BAYAR)
    angsuran_terlambat = sum(1 for a in angsuran_list if a.status == StatusAngsuran.TERLAMBAT)
    
    total_dibayar = sum(float(a.total_bayar) for a in angsuran_list if a.total_bayar)
    
    return AngsuranSummary(
        id_pinjaman=id_pinjaman,
        no_pinjaman=pinjaman.no_pinjaman,
        total_angsuran=total_angsuran,
        angsuran_lunas=angsuran_lunas,
        angsuran_belum_bayar=angsuran_belum_bayar,
        angsuran_terlambat=angsuran_terlambat,
        total_dibayar=total_dibayar,
        sisa_pinjaman=float(pinjaman.sisa_pinjaman)
    )


def get_schedule_angsuran(db: Session, id_pinjaman: int) -> AngsuranScheduleResponse:
    """Get jadwal angsuran untuk pinjaman"""
    pinjaman = db.query(Pinjaman).filter(Pinjaman.id_pinjaman == id_pinjaman).first()
    if not pinjaman:
        raise NotFoundException("Pinjaman tidak ditemukan")
    
    angsuran_list = get_angsuran_by_pinjaman(db, id_pinjaman)
    
    items = []
    for a in angsuran_list:
        items.append(AngsuranScheduleItem(
            angsuran_ke=a.angsuran_ke,
            tanggal_jatuh_tempo=a.tanggal_jatuh_tempo,
            nominal_angsuran=float(a.nominal_angsuran),
            pokok=float(a.pokok),
            bunga=float(a.bunga),
            status=a.status,
            tanggal_bayar=a.tanggal_bayar,
            total_bayar=float(a.total_bayar) if a.total_bayar else None,
        ))
    
    return AngsuranScheduleResponse(
        id_pinjaman=id_pinjaman,
        no_pinjaman=pinjaman.no_pinjaman,
        lama_angsuran=pinjaman.lama_angsuran,
        jadwal=items,
    )