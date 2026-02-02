# ============================================================================
# FILE: app/models/jenis_simpanan.py
# ============================================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class JenisSimpanan(Base):
    __tablename__ = "jenis_simpanan"
    
    id_jenis_simpanan = Column(Integer, primary_key=True, index=True, autoincrement=True)
    kode_jenis = Column(String(10), unique=True, nullable=False, index=True)
    nama_jenis = Column(String(50), nullable=False)
    deskripsi = Column(Text)
    is_wajib = Column(Boolean, default=False)
    nominal_tetap = Column(DECIMAL(15, 2), default=0)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    simpanan = relationship("Simpanan", back_populates="jenis_simpanan")
    
    def __repr__(self):
        return f"<JenisSimpanan(id={self.id_jenis_simpanan}, kode={self.kode_jenis}, nama={self.nama_jenis})>"