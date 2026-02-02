# ============================================================================
# FILE: app/schemas/token.py
# ============================================================================

from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.user import UserRole


class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None


class TokenPayload(BaseModel):
    sub: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    role: UserRole = Field(..., description="User role")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int = Field(..., description="Issued at timestamp")


class LoginRequest(BaseModel):
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict = Field(..., description="User information")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")