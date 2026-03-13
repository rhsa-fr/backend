# ============================================================================
# FILE: app/models/simpanan.py  — REPLACE existing file
# ============================================================================
 
from sqlalchemy import Column, Integer, String, Date, Enum, Text, ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base
 
 
class TipeTransaksi(str, enum.Enum):
    SETOR = "setor"
    TARIK = "tarik"
 
 
class Simpanan(Base):
    __tablename__ = "simpanan"
 
    id_simpanan       = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_anggota        = Column(Integer, ForeignKey("anggota.id_anggota",
                               ondelete="RESTRICT", onupdate="CASCADE"), nullable=False, index=True)
    id_jenis_simpanan = Column(Integer, ForeignKey("jenis_simpanan.id_jenis_simpanan",
                               ondelete="RESTRICT", onupdate="CASCADE"), nullable=False, index=True)
    no_transaksi      = Column(String(30), unique=True, nullable=False, index=True)
    tanggal_transaksi = Column(Date, nullable=False, index=True)
 
    # FIX: values_callable
    tipe_transaksi = Column(
        Enum(TipeTransaksi, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False, index=True,
    )
 
    nominal    = Column(DECIMAL(15, 2), nullable=False)
    saldo_akhir = Column(DECIMAL(15, 2), nullable=False, default=0)
    keterangan = Column(Text)
    id_user    = Column(Integer, ForeignKey("user.id_user",
                        ondelete="SET NULL", onupdate="CASCADE"))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(),
                        onupdate=func.current_timestamp())
 
    # Relationships
    anggota        = relationship("Anggota", back_populates="simpanan")
    jenis_simpanan = relationship("JenisSimpanan", back_populates="simpanan")
    user           = relationship("User", back_populates="simpanan", foreign_keys=[id_user])
 
    def __repr__(self):
        return f"<Simpanan(id={self.id_simpanan}, no={self.no_transaksi}, tipe={self.tipe_transaksi})>"