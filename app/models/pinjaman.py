# ============================================================================
# FILE: app/models/pinjaman.py
# ============================================================================

from sqlalchemy import Column, Integer, String, Date, Enum, Text, ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class StatusPinjaman(str, enum.Enum):
    PENDING = "pending"
    DISETUJUI = "disetujui"
    DITOLAK = "ditolak"
    LUNAS = "lunas"


class Pinjaman(Base):
    __tablename__ = "pinjaman"
    
    id_pinjaman = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_anggota = Column(Integer, ForeignKey("anggota.id_anggota", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False, index=True)
    no_pinjaman = Column(String(30), unique=True, nullable=False, index=True)
    tanggal_pengajuan = Column(Date, nullable=False, index=True)
    nominal_pinjaman = Column(DECIMAL(15, 2), nullable=False)
    bunga_persen = Column(DECIMAL(5, 2), nullable=False, default=0)
    total_bunga = Column(DECIMAL(15, 2), nullable=False, default=0)
    total_pinjaman = Column(DECIMAL(15, 2), nullable=False)
    lama_angsuran = Column(Integer, nullable=False, comment="dalam bulan")
    nominal_angsuran = Column(DECIMAL(15, 2), nullable=False)
    keperluan = Column(Text)
    status = Column(Enum(StatusPinjaman), default=StatusPinjaman.PENDING, index=True)
    tanggal_persetujuan = Column(Date, index=True)
    tanggal_pencairan = Column(Date)
    tanggal_lunas = Column(Date)
    id_user_pengaju = Column(Integer, ForeignKey("user.id_user", ondelete="SET NULL", onupdate="CASCADE"), comment="User yang input pengajuan")
    id_user_persetujuan = Column(Integer, ForeignKey("user.id_user", ondelete="SET NULL", onupdate="CASCADE"), comment="Ketua yang menyetujui")
    catatan_persetujuan = Column(Text)
    sisa_pinjaman = Column(DECIMAL(15, 2), default=0)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    anggota = relationship("Anggota", back_populates="pinjaman")
    user_pengaju = relationship("User", back_populates="pinjaman_pengaju", foreign_keys=[id_user_pengaju])
    user_persetujuan = relationship("User", back_populates="pinjaman_persetujuan", foreign_keys=[id_user_persetujuan])
    angsuran = relationship("Angsuran", back_populates="pinjaman", cascade="all, delete-orphan")
    pinjaman_syarat = relationship("PinjamanSyarat", back_populates="pinjaman", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Pinjaman(id={self.id_pinjaman}, no={self.no_pinjaman}, status={self.status})>"