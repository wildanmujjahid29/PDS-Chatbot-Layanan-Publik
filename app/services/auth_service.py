from datetime import timedelta
from typing import Any, Dict, Optional

from app.core.auth import (create_access_token, get_password_hash,
                           verify_password)
from app.database.client import supabase


def authenticate_admin(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate admin user with username and password.
    
    Args:
        username: Admin username
        password: Plain password
        
    Returns:
        Admin user data if valid, None otherwise
    """
    # Get admin user from database
    result = supabase.table("admin_users").select("*").eq("username", username).eq("is_active", True).execute()
    
    if not result.data or len(result.data) == 0:
        return None
    
    admin_user = result.data[0]
    
    # Verify password
    if not verify_password(password, admin_user["password_hash"]):
        return None
    
    # Update last login
    supabase.table("admin_users").update({"last_login": "now()"}).eq("id", admin_user["id"]).execute()
    
    return admin_user


def create_admin_user(username: str, email: str, password: str, full_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Create new admin user.
    
    Args:
        username: Admin username
        email: Admin email
        password: Plain password
        full_name: Full name (optional)
        
    Returns:
        Created admin user data or None if failed
    """
    # Hash password
    password_hash = get_password_hash(password)
    
    # Insert to database
    try:
        result = supabase.table("admin_users").insert({
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "full_name": full_name
        }).execute()
        
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return None


def get_admin_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Get admin user by username.
    """
    result = supabase.table("admin_users").select("id, username, email, full_name, is_active, last_login, created_at").eq("username", username).execute()
    
    if result.data and len(result.data) > 0:
        return result.data[0]
    return None


def change_admin_password(username: str, old_password: str, new_password: str) -> bool:
    """
    Change admin password.
    
    Args:
        username: Admin username
        old_password: Current password
        new_password: New password
        
    Returns:
        True if successful, False otherwise
    """
    # Verify old password first
    admin = authenticate_admin(username, old_password)
    if not admin:
        return False
    
    # Hash new password
    new_password_hash = get_password_hash(new_password)
    
    # Update password
    result = supabase.table("admin_users").update({
        "password_hash": new_password_hash,
        "updated_at": "now()"
    }).eq("username", username).execute()
    
    return bool(result.data)


def generate_login_token(admin_user: Dict[str, Any]) -> str:
    """
    Generate JWT token for admin user.
    
    Args:
        admin_user: Admin user data
        
    Returns:
        JWT token string
    """
    access_token = create_access_token(
        data={"sub": admin_user["username"], "user_id": admin_user["id"]},
        expires_delta=timedelta(hours=24)
    )
    return access_token
