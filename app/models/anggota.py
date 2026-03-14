# ============================================================================
# FILE: app/models/anggota.py  — REPLACE existing file
# ============================================================================

from sqlalchemy import Column, Integer, String, Date, Enum, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class StatusAnggota(str, enum.Enum):
    AKTIF     = "aktif"
    NON_AKTIF = "non-aktif"
    KELUAR    = "keluar"


class Anggota(Base):
    __tablename__ = "anggota"

    id_anggota        = Column(Integer, primary_key=True, index=True, autoincrement=True)
    no_anggota        = Column(String(20), unique=True, nullable=False, index=True)
    nama_lengkap      = Column(String(100), nullable=False, index=True)
    email             = Column(String(100), unique=True)
    no_telepon        = Column(String(15))
    tanggal_bergabung = Column(Date, nullable=False)

    status = Column(
        Enum(StatusAnggota, values_callable=lambda obj: [e.value for e in obj]),
        default=StatusAnggota.AKTIF,
        index=True,
    )

    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(),
                        onupdate=func.current_timestamp())

    # Relationships
    profil   = relationship("ProfilAnggota", back_populates="anggota",
                            uselist=False, cascade="all, delete-orphan")
    simpanan = relationship("Simpanan", back_populates="anggota")
    pinjaman = relationship("Pinjaman", back_populates="anggota")

    def __repr__(self):
        return f"<Anggota(id={self.id_anggota}, no={self.no_anggota}, nama={self.nama_lengkap})>"