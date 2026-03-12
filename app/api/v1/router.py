# ============================================================================
# FILE: app/api/v1/router.py
# ============================================================================

from fastapi import APIRouter

# ── Import semua models agar SQLAlchemy bisa resolve relationships ──
import app.models.user
import app.models.anggota
import app.models.profil_anggota
import app.models.jenis_simpanan
import app.models.simpanan
import app.models.pinjaman
import app.models.angsuran
import app.models.syarat_peminjaman
import app.models.pinjaman_syarat      # ← INI YANG MENYEBABKAN ERROR (belum di-import)

from app.api.v1.endpoints import (
    auth,
    users,
    anggota,
    simpanan,
    pinjaman,
    angsuran
)

router = APIRouter()

# Include all endpoint routers
router.include_router(auth.router,     prefix="/auth",     tags=["Authentication"])
router.include_router(users.router,    prefix="/users",    tags=["Users"])
router.include_router(anggota.router,  prefix="/anggota",  tags=["Anggota"])
router.include_router(simpanan.router, prefix="/simpanan", tags=["Simpanan"])
router.include_router(pinjaman.router, prefix="/pinjaman", tags=["Pinjaman"])
router.include_router(angsuran.router, prefix="/angsuran", tags=["Angsuran"])