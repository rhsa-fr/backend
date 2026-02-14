# ============================================================================
# FILE: app/models/syarat_peminjaman.py
# ============================================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class SyaratPeminjaman(Base):
    __tablename__ = "syarat_peminjaman"
    
    id_syarat = Column(Integer, primary_key=True, index=True, autoincrement=True)
    kode_syarat = Column(String(20), unique=True, nullable=False, index=True)
    nama_syarat = Column(String(100), nullable=False)
    deskripsi = Column(Text)
    is_wajib = Column(Boolean, default=True, comment="Apakah syarat ini wajib dipenuhi")
    min_nominal_pinjaman = Column(DECIMAL(15, 2), nullable=True, comment="Minimal nominal untuk syarat ini berlaku")
    max_nominal_pinjaman = Column(DECIMAL(15, 2), nullable=True, comment="Maksimal nominal untuk syarat ini berlaku")
    dokumen_diperlukan = Column(String(255), nullable=True, comment="Jenis dokumen yang diperlukan")
    is_active = Column(Boolean, default=True, index=True)
    urutan = Column(Integer, default=0, comment="Urutan tampilan")
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    pinjaman_syarat = relationship("PinjamanSyarat", back_populates="syarat", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SyaratPeminjaman(id={self.id_syarat}, kode={self.kode_syarat}, nama={self.nama_syarat})>"