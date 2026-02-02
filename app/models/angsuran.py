# ============================================================================
# FILE: app/models/angsuran.py
# ============================================================================

from sqlalchemy import Column, Integer, String, Date, Enum, Text, ForeignKey, DECIMAL, TIMESTAMP, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class StatusAngsuran(str, enum.Enum):
    BELUM_BAYAR = "belum_bayar"
    LUNAS = "lunas"
    TERLAMBAT = "terlambat"


class Angsuran(Base):
    __tablename__ = "angsuran"
    __table_args__ = (
        UniqueConstraint('id_pinjaman', 'angsuran_ke', name='unique_pinjaman_angsuran'),
    )
    
    id_angsuran = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_pinjaman = Column(Integer, ForeignKey("pinjaman.id_pinjaman", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    no_angsuran = Column(String(30), unique=True, nullable=False, index=True)
    angsuran_ke = Column(Integer, nullable=False)
    tanggal_jatuh_tempo = Column(Date, nullable=False, index=True)
    nominal_angsuran = Column(DECIMAL(15, 2), nullable=False)
    pokok = Column(DECIMAL(15, 2), nullable=False)
    bunga = Column(DECIMAL(15, 2), nullable=False)
    denda = Column(DECIMAL(15, 2), default=0)
    total_bayar = Column(DECIMAL(15, 2), default=0)
    tanggal_bayar = Column(Date, index=True)
    status = Column(Enum(StatusAngsuran), default=StatusAngsuran.BELUM_BAYAR, index=True)
    keterangan = Column(Text)
    id_user = Column(Integer, ForeignKey("user.id_user", ondelete="SET NULL", onupdate="CASCADE"), comment="User yang mencatat pembayaran")
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    pinjaman = relationship("Pinjaman", back_populates="angsuran")
    user = relationship("User", back_populates="angsuran")
    
    def __repr__(self):
        return f"<Angsuran(id={self.id_angsuran}, no={self.no_angsuran}, ke={self.angsuran_ke}, status={self.status})>"