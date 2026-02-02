# ============================================================================
# FILE: app/api/v1/router.py
# ============================================================================

from fastapi import APIRouter
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
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(anggota.router, prefix="/anggota", tags=["Anggota"])
router.include_router(simpanan.router, prefix="/simpanan", tags=["Simpanan"])
router.include_router(pinjaman.router, prefix="/pinjaman", tags=["Pinjaman"])
router.include_router(angsuran.router, prefix="/angsuran", tags=["Angsuran"])
