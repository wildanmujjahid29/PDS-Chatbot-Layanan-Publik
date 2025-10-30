from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, validator


class LoginRequest(BaseModel):
    """Request schema untuk login"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Response schema untuk login success"""
    access_token: str
    token_type: str = "bearer"
    username: str
    full_name: Optional[str] = None


class AdminUser(BaseModel):
    """Schema untuk admin user info"""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None


class AdminUserCreate(BaseModel):
    """Schema untuk create admin user"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v


class ChangePasswordRequest(BaseModel):
    """Request schema untuk change password"""
    old_password: str
    new_password: str
    
    @validator('new_password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v
