# ============================================================================
# FILE: app/api/v1/endpoints/auth.py
# ============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserLogin
from app.schemas.token import LoginResponse
from app.core.security import verify_password, create_token_response
from app.core.permissions import get_current_user
from app.core.exceptions import UnauthorizedException

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Login user dan generate JWT token"""
    # Cari user berdasarkan username
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user:
        raise UnauthorizedException("Username atau password salah")
    
    # Verify password
    if not verify_password(credentials.password, user.password):
        raise UnauthorizedException("Username atau password salah")
    
    # Check apakah user aktif
    if not user.is_active:
        raise UnauthorizedException("User tidak aktif")
    
    # Generate token response
    return create_token_response(
        user_id=user.id_user,
        username=user.username,
        role=user.role.value
    )


@router.get("/me")
def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get informasi user yang sedang login"""
    user = db.query(User).filter(User.id_user == current_user["id"]).first()
    
    if not user:
        raise UnauthorizedException("User tidak ditemukan")
    
    return {
        "id_user": user.id_user,
        "username": user.username,
        "role": user.role.value,
        "is_active": user.is_active,
        "created_at": user.created_at
    }


@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user)):
    """Logout user (client-side harus hapus token)"""
    return {
        "message": "Logout berhasil. Silakan hapus token dari client."
    }
