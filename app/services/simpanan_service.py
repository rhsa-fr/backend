# ============================================================================
# FILE: app/services/simpanan_service.py
# ============================================================================

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date, datetime
from app.models.simpanan import Simpanan, TipeTransaksi
from app.models.anggota import Anggota
from app.models.jenis_simpanan import JenisSimpanan
from app.schemas.anggota import SimpananCreate, SimpananResponse, SaldoSimpananResponse
from app.core.exceptions import NotFoundException, BadRequestException, BusinessLogicException


def generate_no_transaksi() -> str:
    """Generate nomor transaksi unik"""
    now = datetime.now()
    return f"TRX-{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}"


def get_saldo_terakhir(
    db: Session,
    id_anggota: int,
    id_jenis_simpanan: int
) -> float:
    """Get saldo terakhir untuk anggota dan jenis simpanan tertentu"""
    last_simpanan = db.query(Simpanan).filter(
        and_(
            Simpanan.id_anggota == id_anggota,
            Simpanan.id_jenis_simpanan == id_jenis_simpanan
        )
    ).order_by(Simpanan.created_at.desc()).first()
    
    return float(last_simpanan.saldo_akhir) if last_simpanan else 0.0


def setor_simpanan(
    db: Session,
    data: SimpananCreate,
    id_user: int
) -> Simpanan:
    """Setor simpanan"""
    # Validasi anggota
    anggota = db.query(Anggota).filter(Anggota.id_anggota == data.id_anggota).first()
    if not anggota:
        raise NotFoundException("Anggota tidak ditemukan")
    
    if anggota.status != "aktif":
        raise BusinessLogicException("Anggota tidak aktif")
    
    # Validasi jenis simpanan
    jenis = db.query(JenisSimpanan).filter(
        JenisSimpanan.id_jenis_simpanan == data.id_jenis_simpanan
    ).first()
    if not jenis:
        raise NotFoundException("Jenis simpanan tidak ditemukan")
    
    if not jenis.is_active:
        raise BusinessLogicException("Jenis simpanan tidak aktif")
    
    # Hitung saldo baru
    saldo_lama = get_saldo_terakhir(db, data.id_anggota, data.id_jenis_simpanan)
    saldo_baru = saldo_lama + float(data.nominal)
    
    # Create transaksi
    simpanan = Simpanan(
        id_anggota=data.id_anggota,
        id_jenis_simpanan=data.id_jenis_simpanan,
        no_transaksi=generate_no_transaksi(),
        tanggal_transaksi=data.tanggal_transaksi,
        tipe_transaksi=TipeTransaksi.SETOR,
        nominal=data.nominal,
        saldo_akhir=saldo_baru,
        keterangan=data.keterangan,
        id_user=id_user
    )
    
    db.add(simpanan)
    db.commit()
    db.refresh(simpanan)
    
    return simpanan


def tarik_simpanan(
    db: Session,
    data: SimpananCreate,
    id_user: int
) -> Simpanan:
    """Tarik simpanan"""
    # Validasi anggota
    anggota = db.query(Anggota).filter(Anggota.id_anggota == data.id_anggota).first()
    if not anggota:
        raise NotFoundException("Anggota tidak ditemukan")
    
    if anggota.status != "aktif":
        raise BusinessLogicException("Anggota tidak aktif")
    
    # Validasi jenis simpanan
    jenis = db.query(JenisSimpanan).filter(
        JenisSimpanan.id_jenis_simpanan == data.id_jenis_simpanan
    ).first()
    if not jenis:
        raise NotFoundException("Jenis simpanan tidak ditemukan")
    
    # Validasi saldo
    saldo_lama = get_saldo_terakhir(db, data.id_anggota, data.id_jenis_simpanan)
    if saldo_lama < float(data.nominal):
        raise BusinessLogicException(
            f"Saldo tidak cukup. Saldo tersedia: Rp {saldo_lama:,.2f}"
        )
    
    # Hitung saldo baru
    saldo_baru = saldo_lama - float(data.nominal)
    
    # Create transaksi
    simpanan = Simpanan(
        id_anggota=data.id_anggota,
        id_jenis_simpanan=data.id_jenis_simpanan,
        no_transaksi=generate_no_transaksi(),
        tanggal_transaksi=data.tanggal_transaksi,
        tipe_transaksi=TipeTransaksi.TARIK,
        nominal=data.nominal,
        saldo_akhir=saldo_baru,
        keterangan=data.keterangan,
        id_user=id_user
    )
    
    db.add(simpanan)
    db.commit()
    db.refresh(simpanan)
    
    return simpanan


def get_simpanan_list(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    id_anggota: Optional[int] = None,
    id_jenis_simpanan: Optional[int] = None,
    tipe_transaksi: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> tuple[List[Simpanan], int]:
    """Get list simpanan dengan filter"""
    query = db.query(Simpanan)
    
    if id_anggota:
        query = query.filter(Simpanan.id_anggota == id_anggota)
    
    if id_jenis_simpanan:
        query = query.filter(Simpanan.id_jenis_simpanan == id_jenis_simpanan)
    
    if tipe_transaksi:
        query = query.filter(Simpanan.tipe_transaksi == tipe_transaksi)
    
    if start_date:
        query = query.filter(Simpanan.tanggal_transaksi >= start_date)
    
    if end_date:
        query = query.filter(Simpanan.tanggal_transaksi <= end_date)
    
    total = query.count()
    simpanan_list = query.order_by(Simpanan.created_at.desc()).offset(skip).limit(limit).all()
    
    return simpanan_list, total


def get_simpanan_by_id(db: Session, id_simpanan: int) -> Simpanan:
    """Get simpanan by ID"""
    simpanan = db.query(Simpanan).filter(Simpanan.id_simpanan == id_simpanan).first()
    if not simpanan:
        raise NotFoundException("Transaksi simpanan tidak ditemukan")
    return simpanan


def get_saldo_anggota(
    db: Session,
    id_anggota: int
) -> List[SaldoSimpananResponse]:
    """Get saldo per jenis simpanan untuk anggota"""
    anggota = db.query(Anggota).filter(Anggota.id_anggota == id_anggota).first()
    if not anggota:
        raise NotFoundException("Anggota tidak ditemukan")
    
    # Query saldo per jenis simpanan
    result = db.query(
        Simpanan.id_jenis_simpanan,
        JenisSimpanan.nama_jenis,
        func.sum(
            func.case(
                (Simpanan.tipe_transaksi == TipeTransaksi.SETOR, Simpanan.nominal),
                else_=0
            )
        ).label('total_setor'),
        func.sum(
            func.case(
                (Simpanan.tipe_transaksi == TipeTransaksi.TARIK, Simpanan.nominal),
                else_=0
            )
        ).label('total_tarik')
    ).join(
        JenisSimpanan, Simpanan.id_jenis_simpanan == JenisSimpanan.id_jenis_simpanan
    ).filter(
        Simpanan.id_anggota == id_anggota
    ).group_by(
        Simpanan.id_jenis_simpanan, JenisSimpanan.nama_jenis
    ).all()
    
    saldo_list = []
    for item in result:
        total_setor = float(item.total_setor or 0)
        total_tarik = float(item.total_tarik or 0)
        saldo = total_setor - total_tarik
        
        saldo_list.append(SaldoSimpananResponse(
            id_anggota=id_anggota,
            nama_anggota=anggota.nama_lengkap,
            id_jenis_simpanan=item.id_jenis_simpanan,
            nama_jenis_simpanan=item.nama_jenis,
            total_setor=total_setor,
            total_tarik=total_tarik,
            saldo=saldo
        ))
    
    return saldo_list


def get_total_saldo_anggota(db: Session, id_anggota: int) -> float:
    """Get total saldo semua jenis simpanan untuk anggota"""
    saldo_list = get_saldo_anggota(db, id_anggota)
    return sum(item.saldo for item in saldo_list)
