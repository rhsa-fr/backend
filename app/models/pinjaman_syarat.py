# ============================================================================
# FILE: app/models/pinjaman_syarat.py
# ============================================================================

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class PinjamanSyarat(Base):
    __tablename__ = "pinjaman_syarat"
    
    id_pinjaman_syarat = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_pinjaman = Column(Integer, ForeignKey("pinjaman.id_pinjaman", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    id_syarat = Column(Integer, ForeignKey("syarat_peminjaman.id_syarat", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False, index=True)
    is_terpenuhi = Column(Boolean, default=False, comment="Apakah syarat sudah terpenuhi")
    dokumen_path = Column(String(255), nullable=True, comment="Path file dokumen jika ada")
    catatan = Column(Text, nullable=True, comment="Catatan terkait pemenuhan syarat")
    tanggal_verifikasi = Column(TIMESTAMP, nullable=True, comment="Tanggal verifikasi syarat")
    id_user_verifikasi = Column(Integer, ForeignKey("user.id_user", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    pinjaman = relationship("Pinjaman", back_populates="pinjaman_syarat")
    syarat = relationship("SyaratPeminjaman", back_populates="pinjaman_syarat")
    user_verifikasi = relationship("User", foreign_keys=[id_user_verifikasi])
    
    def __repr__(self):
        return f"<PinjamanSyarat(pinjaman_id={self.id_pinjaman}, syarat_id={self.id_syarat}, terpenuhi={self.is_terpenuhi})>"