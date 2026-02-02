# ============================================================================
# FILE: app/core/permissions.py
# ============================================================================

from typing import List, Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_access_token


security = HTTPBearer()


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
    
    def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
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
        
        # Return user info for use in endpoint
        return {
            "id": int(payload.get("sub")),
            "username": payload.get("username"),
            "role": user_role
        }


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: Bearer token from request header
        db: Database session
        
    Returns:
        Dictionary with user info (id, username, role)
        
    Raises:
        HTTPException: If token is invalid or expired
        
    Usage:
        @router.get("/profile")
        def get_profile(current_user = Depends(get_current_user)):
            return current_user
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


def require_role(allowed_roles: List[str]):
    """
    Decorator factory to require specific roles for an endpoint.
    
    Args:
        allowed_roles: List of roles that are allowed to access the endpoint
        
    Returns:
        RoleChecker dependency
        
    Usage:
        @router.post("/pinjaman/{id}/approve")
        def approve_pinjaman(
            id: int,
            current_user = Depends(require_role(["ketua"]))
        ):
            return {"message": "Pinjaman approved"}
    """
    return RoleChecker(allowed_roles)


def is_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Check if current user is admin.
    
    Usage:
        @router.delete("/users/{id}")
        def delete_user(id: int, current_user = Depends(is_admin)):
            # Only admin can access
    """
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def is_ketua(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Check if current user is ketua.
    
    Usage:
        @router.put("/pinjaman/{id}/approve")
        def approve(id: int, current_user = Depends(is_ketua)):
            # Only ketua can access
    """
    if current_user["role"] != "ketua":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ketua access required",
        )
    return current_user


def is_bendahara(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Check if current user is bendahara.
    
    Usage:
        @router.post("/simpanan/setor")
        def setor(data: dict, current_user = Depends(is_bendahara)):
            # Only bendahara can access
    """
    if current_user["role"] != "bendahara":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bendahara access required",
        )
    return current_user


def is_admin_or_ketua(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Check if current user is admin or ketua.
    
    Usage:
        @router.get("/laporan/keuangan")
        def laporan(current_user = Depends(is_admin_or_ketua)):
            # Admin or ketua can access
    """
    if current_user["role"] not in ["admin", "ketua"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Ketua access required",
        )
    return current_user


def has_permission(user_role: str, required_roles: List[str]) -> bool:
    """
    Check if user role is in the list of required roles.
    
    Args:
        user_role: Current user's role
        required_roles: List of roles that are allowed
        
    Returns:
        True if user has permission, False otherwise
        
    Usage:
        if has_permission(current_user["role"], ["admin", "ketua"]):
            # Do something
    """
    return user_role in required_roles


# Permission matrix for reference
PERMISSIONS = {
    "admin": {
        "users": ["create", "read", "update", "delete"],
        "anggota": ["create", "read", "update", "delete"],
        "simpanan": ["create", "read", "update", "delete"],
        "pinjaman": ["create", "read", "update", "delete", "approve"],
        "angsuran": ["create", "read", "update", "delete"],
        "laporan": ["read"],
    },
    "ketua": {
        "users": [],
        "anggota": ["read"],
        "simpanan": ["read"],
        "pinjaman": ["read", "approve", "reject"],
        "angsuran": ["read"],
        "laporan": ["read"],
    },
    "bendahara": {
        "users": [],
        "anggota": ["read"],
        "simpanan": ["create", "read", "update"],
        "pinjaman": ["read"],
        "angsuran": ["create", "read", "update"],
        "laporan": ["read"],
    },
}


def check_permission(user_role: str, resource: str, action: str) -> bool:
    """
    Check if user has permission for specific action on a resource.
    
    Args:
        user_role: User's role (admin, ketua, bendahara)
        resource: Resource name (users, anggota, simpanan, etc.)
        action: Action to perform (create, read, update, delete, approve, etc.)
        
    Returns:
        True if user has permission, False otherwise
        
    Usage:
        if check_permission(current_user["role"], "pinjaman", "approve"):
            # User can approve pinjaman
    """
    if user_role not in PERMISSIONS:
        return False
    
    if resource not in PERMISSIONS[user_role]:
        return False
    
    return action in PERMISSIONS[user_role][resource]