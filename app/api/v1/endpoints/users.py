# ============================================================================
# FILE: app/api/v1/endpoints/users.py
# ============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserChangePassword
from app.schemas.common import PaginatedResponse, PaginationMeta, MessageResponse
from app.core.security import hash_password, verify_password
from app.core.permissions import get_current_user, is_admin
from app.core.exceptions import NotFoundException, ConflictException, BadRequestException

router = APIRouter()


@router.get("", response_model=PaginatedResponse[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 10,
    current_user: dict = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Get list users (admin only)"""
    total = db.query(User).count()
    users = db.query(User).offset(skip).limit(limit).all()
    
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    
    return PaginatedResponse(
        data=[UserResponse.model_validate(user) for user in users],
        meta=PaginationMeta(
            total=total,
            skip=skip,
            limit=limit,
            page=page,
            total_pages=total_pages
        )
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    current_user: dict = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Create user baru (admin only)"""
    # Check username sudah ada
    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        raise ConflictException("Username sudah digunakan")
    
    # Hash password
    hashed_password = hash_password(data.password)
    
    # Create user
    user = User(
        username=data.username,
        password=hashed_password,
        role=data.role,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.get("/{id_user}", response_model=UserResponse)
def get_user(
    id_user: int,
    current_user: dict = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Get user by ID (admin only)"""
    user = db.query(User).filter(User.id_user == id_user).first()
    if not user:
        raise NotFoundException("User tidak ditemukan")
    
    return UserResponse.model_validate(user)


@router.put("/{id_user}", response_model=UserResponse)
def update_user(
    id_user: int,
    data: UserUpdate,
    current_user: dict = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Update user (admin only)"""
    user = db.query(User).filter(User.id_user == id_user).first()
    if not user:
        raise NotFoundException("User tidak ditemukan")
    
    # Update username
    if data.username is not None:
        # Check username conflict
        existing = db.query(User).filter(
            User.username == data.username,
            User.id_user != id_user
        ).first()
        if existing:
            raise ConflictException("Username sudah digunakan")
        user.username = data.username
    
    # Update password
    if data.password is not None:
        user.password = hash_password(data.password)
    
    # Update role
    if data.role is not None:
        user.role = data.role
    
    # Update is_active
    if data.is_active is not None:
        user.is_active = data.is_active
    
    db.commit()
    db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.delete("/{id_user}", response_model=MessageResponse)
def delete_user(
    id_user: int,
    current_user: dict = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Delete user (admin only)"""
    user = db.query(User).filter(User.id_user == id_user).first()
    if not user:
        raise NotFoundException("User tidak ditemukan")
    
    # Tidak bisa hapus diri sendiri
    if user.id_user == current_user["id"]:
        raise BadRequestException("Tidak bisa menghapus akun sendiri")
    
    db.delete(user)
    db.commit()
    
    return MessageResponse(message="User berhasil dihapus")


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    data: UserChangePassword,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change password user yang sedang login"""
    user = db.query(User).filter(User.id_user == current_user["id"]).first()
    if not user:
        raise NotFoundException("User tidak ditemukan")
    
    # Verify old password
    if not verify_password(data.old_password, user.password):
        raise BadRequestException("Password lama tidak sesuai")
    
    # Update password
    user.password = hash_password(data.new_password)
    db.commit()
    
    return MessageResponse(message="Password berhasil diubah")
