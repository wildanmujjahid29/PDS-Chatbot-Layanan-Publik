from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.auth import decode_access_token
from app.services.auth_service import get_admin_by_username

security = HTTPBearer()


def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to get current authenticated admin from JWT token.
    Use this to protect admin endpoints.
    
    Usage:
        @router.get("/protected")
        def protected_endpoint(admin: dict = Depends(get_current_admin)):
            return {"admin": admin["username"]}
    """
    token = credentials.credentials
    
    # Decode token
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get admin user from database
    admin = get_admin_by_username(username)
    
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin user not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not admin.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin user is inactive"
        )
    
    return admin


def get_current_admin_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """
    Optional authentication - returns admin if authenticated, None otherwise.
    Use this for endpoints that work differently for authenticated admins.
    """
    if credentials is None:
        return None
    
    try:
        return get_current_admin(credentials)
    except HTTPException:
        return None
