# ============================================================================
# FILE: app/models/profil_anggota.py
# ============================================================================

from sqlalchemy import Column, Integer, String, Date, Enum, Text, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class JenisKelamin(str, enum.Enum):
    LAKI_LAKI = "L"
    PEREMPUAN = "P"


class ProfilAnggota(Base):
    __tablename__ = "profil_anggota"
    
    id_profil = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_anggota = Column(Integer, ForeignKey("anggota.id_anggota", ondelete="CASCADE", onupdate="CASCADE"), unique=True, nullable=False, index=True)
    nik = Column(String(16), unique=True, index=True)
    tempat_lahir = Column(String(50))
    tanggal_lahir = Column(Date)
    jenis_kelamin = Column(Enum(JenisKelamin))
    alamat = Column(Text)
    kota = Column(String(50))
    provinsi = Column(String(50))
    kode_pos = Column(String(10))
    pekerjaan = Column(String(50))
    foto_profil = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    anggota = relationship("Anggota", back_populates="profil")
    
    def __repr__(self):
        return f"<ProfilAnggota(id={self.id_profil}, anggota_id={self.id_anggota})>"