# ============================================================================
# FILE: app/models/user.py  — REPLACE existing file
# ============================================================================

from sqlalchemy import Column, Integer, String, Boolean, Enum as SAEnum, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN     = "admin"
    KETUA     = "ketua"
    BENDAHARA = "bendahara"


class User(Base):
    __tablename__ = "user"

    id_user    = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username   = Column(String(50), unique=True, nullable=False, index=True)
    password   = Column(String(255), nullable=False)

    # FIX: values_callable
    role = Column(
        SAEnum(UserRole, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False, index=True,
    )

    is_active  = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(),
                        onupdate=func.current_timestamp())

    # Relationships
    simpanan             = relationship("Simpanan", back_populates="user",
                                        foreign_keys="[Simpanan.id_user]")
    pinjaman_pengaju     = relationship("Pinjaman", back_populates="user_pengaju",
                                        foreign_keys="[Pinjaman.id_user_pengaju]")
    pinjaman_persetujuan = relationship("Pinjaman", back_populates="user_persetujuan",
                                        foreign_keys="[Pinjaman.id_user_persetujuan]")
    angsuran             = relationship("Angsuran", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id_user}, username={self.username}, role={self.role})>"