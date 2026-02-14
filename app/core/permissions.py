# ============================================================================
# FILE: app/core/permissions.py (IMPROVED VERSION)
# ============================================================================

from typing import List, Optional, Callable
from functools import wraps
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_access_token


security = HTTPBearer()


# ============================================================================
# PERMISSION MATRIX - Role-Based Access Control
# ============================================================================
PERMISSIONS = {
    "admin": {
        "users": ["create", "read", "update", "delete", "activate", "deactivate"],
        "anggota": ["create", "read", "update", "delete", "export"],
        "profil_anggota": ["create", "read", "update", "delete"],
        "jenis_simpanan": ["create", "read", "update", "delete"],
        "simpanan": ["create", "read", "update", "delete", "setor", "tarik", "export"],
        "pinjaman": ["create", "read", "update", "delete", "approve", "reject", "export"],
        "angsuran": ["create", "read", "update", "delete", "bayar", "export"],
        "laporan": ["read", "export"],
        "dashboard": ["read"],
    },
    "ketua": {
        "users": ["read"],  # Hanya bisa lihat user
        "anggota": ["read", "export"],
        "profil_anggota": ["read"],
        "jenis_simpanan": ["read"],
        "simpanan": ["read", "export"],
        "pinjaman": ["read", "approve", "reject", "export"],  # Ketua approve/reject pinjaman
        "angsuran": ["read", "export"],
        "laporan": ["read", "export"],
        "dashboard": ["read"],
    },
    "bendahara": {
        "users": [],  # Tidak bisa akses users
        "anggota": ["read"],
        "profil_anggota": ["read"],
        "jenis_simpanan": ["read"],
        "simpanan": ["create", "read", "setor", "tarik", "export"],  # Bendahara kelola simpanan
        "pinjaman": ["create", "read", "export"],  # Bendahara bisa input pinjaman
        "angsuran": ["create", "read", "bayar", "export"],  # Bendahara bayar angsuran
        "laporan": ["read"],
        "dashboard": ["read"],
    },
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def has_permission(user_role: str, resource: str, action: str) -> bool:
    """
    Check if user role has permission for specific action on a resource.
    
    Args:
        user_role: User's role (admin, ketua, bendahara)
        resource: Resource name (users, anggota, simpanan, etc.)
        action: Action to perform (create, read, update, delete, etc.)
        
    Returns:
        True if user has permission, False otherwise
    """
    if user_role not in PERMISSIONS:
        return False
    
    if resource not in PERMISSIONS[user_role]:
        return False
    
    return action in PERMISSIONS[user_role][resource]


def check_permission(user_role: str, resource: str, action: str) -> None:
    """
    Check permission and raise HTTPException if not allowed.
    
    Args:
        user_role: User's role
        resource: Resource name
        action: Action name
        
    Raises:
        HTTPException: If permission denied
    """
    if not has_permission(user_role, resource, action):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied. Role '{user_role}' cannot '{action}' on '{resource}'",
        )


# ============================================================================
# AUTHENTICATION & AUTHORIZATION
# ============================================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """
    Get current authenticated user from JWT token.
    
    Returns:
        Dictionary with user info (id, username, role)
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "id": int(payload.get("sub")),
        "username": payload.get("username"),
        "role": payload.get("role")
    }


# ============================================================================
# ROLE-BASED DEPENDENCIES
# ============================================================================

class RoleChecker:
    """
    Dependency class to check if user has required role(s).
    
    Usage:
        @router.get("/admin-only")
        def admin_endpoint(user = Depends(RoleChecker(["admin"]))):
            return {"message": "Admin access"}
    """
    
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security), 
        db: Session = Depends(get_db)
    ):
        token = credentials.credentials
        payload = decode_access_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_role = payload.get("role")
        
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required roles: {', '.join(self.allowed_roles)}",
            )
        
        return {
            "id": int(payload.get("sub")),
            "username": payload.get("username"),
            "role": user_role
        }


class PermissionChecker:
    """
    Dependency class to check if user has specific permission.
    
    Usage:
        @router.post("/pinjaman")
        def create_pinjaman(
            user = Depends(PermissionChecker("pinjaman", "create"))
        ):
            return {"message": "Pinjaman created"}
    """
    
    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action
    
    def __call__(self, current_user: dict = Depends(get_current_user)):
        check_permission(current_user["role"], self.resource, self.action)
        return current_user


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def require_role(allowed_roles: List[str]):
    """
    Factory function to create RoleChecker dependency.
    
    Usage:
        @router.post("/pinjaman/{id}/approve")
        def approve_pinjaman(user = Depends(require_role(["ketua"]))):
            pass
    """
    return RoleChecker(allowed_roles)


def require_permission(resource: str, action: str):
    """
    Factory function to create PermissionChecker dependency.
    
    Usage:
        @router.post("/pinjaman")
        def create_pinjaman(user = Depends(require_permission("pinjaman", "create"))):
            pass
    """
    return PermissionChecker(resource, action)


# ============================================================================
# SPECIFIC ROLE CHECKERS
# ============================================================================

def is_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Check if current user is admin."""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def is_ketua(current_user: dict = Depends(get_current_user)) -> dict:
    """Check if current user is ketua."""
    if current_user["role"] != "ketua":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ketua access required",
        )
    return current_user


def is_bendahara(current_user: dict = Depends(get_current_user)) -> dict:
    """Check if current user is bendahara."""
    if current_user["role"] != "bendahara":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bendahara access required",
        )
    return current_user


def is_admin_or_ketua(current_user: dict = Depends(get_current_user)) -> dict:
    """Check if current user is admin or ketua."""
    if current_user["role"] not in ["admin", "ketua"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Ketua access required",
        )
    return current_user


def is_admin_or_bendahara(current_user: dict = Depends(get_current_user)) -> dict:
    """Check if current user is admin or bendahara."""
    if current_user["role"] not in ["admin", "bendahara"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Bendahara access required",
        )
    return current_user


# ============================================================================
# PERMISSION DECORATOR (for service layer)
# ============================================================================

def check_resource_permission(resource: str, action: str):
    """
    Decorator to check permission in service functions.
    
    Usage:
        @check_resource_permission("pinjaman", "approve")
        def approve_pinjaman_service(db, user_role, ...):
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Assume user_role is passed as kwarg
            user_role = kwargs.get("user_role")
            if user_role and not has_permission(user_role, resource, action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied for {action} on {resource}",
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# PERMISSION HELPERS FOR BUSINESS LOGIC
# ============================================================================

def can_user_approve_pinjaman(user_role: str) -> bool:
    """Check if user can approve pinjaman."""
    return has_permission(user_role, "pinjaman", "approve")


def can_user_bayar_angsuran(user_role: str) -> bool:
    """Check if user can bayar angsuran."""
    return has_permission(user_role, "angsuran", "bayar")


def can_user_manage_simpanan(user_role: str) -> bool:
    """Check if user can setor/tarik simpanan."""
    return (has_permission(user_role, "simpanan", "setor") and 
            has_permission(user_role, "simpanan", "tarik"))


def get_user_permissions(user_role: str) -> dict:
    """
    Get all permissions for a user role.
    
    Returns:
        Dict of resources and their allowed actions
    """
    return PERMISSIONS.get(user_role, {})