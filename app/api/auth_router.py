from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_admin
from app.schemas.auth_schemas import (AdminUser, AdminUserCreate,
                                      ChangePasswordRequest, LoginRequest,
                                      TokenResponse)
from app.services.auth_service import (authenticate_admin,
                                       change_admin_password,
                                       create_admin_user, generate_login_token)

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    """
    Endpoint login untuk admin.

    Kredensial default (jika digunakan di environment pengujian):
    - username: admin
    - password: admin123

    Mengembalikan token JWT untuk admin yang berhasil diautentikasi.
    """
    # Authenticate admin
    admin = authenticate_admin(request.username, request.password)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate JWT token
    access_token = generate_login_token(admin)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        username=admin["username"],
        full_name=admin.get("full_name")
    )


@router.get("/me", response_model=AdminUser)
def get_current_admin_info(admin: dict = Depends(get_current_admin)):
    """
    Ambil informasi admin yang sedang terautentikasi.
    Membutuhkan token JWT yang valid di header Authorization.
    """
    return AdminUser(**admin)


@router.post("/register", response_model=AdminUser)
def register_admin(request: AdminUserCreate, admin: dict = Depends(get_current_admin)):
    """
    Daftarkan admin baru.
    Hanya dapat diakses oleh admin yang sudah terautentikasi.
    """
    # Create new admin
    new_admin = create_admin_user(
        username=request.username,
        email=request.email,
        password=request.password,
        full_name=request.full_name
    )
    
    if not new_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create admin user. Username or email may already exist."
        )
    
    return AdminUser(**new_admin)


@router.post("/change-password")
def change_password(request: ChangePasswordRequest, admin: dict = Depends(get_current_admin)):
    """
    Ubah password admin saat ini.
    Membutuhkan token JWT yang valid.
    """
    success = change_admin_password(
        username=admin["username"],
        old_password=request.old_password,
        new_password=request.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password. Old password may be incorrect."
        )
    
    return {
        "success": True,
        "message": "Password changed successfully"
    }


@router.post("/logout")
def logout(admin: dict = Depends(get_current_admin)):
    """
    Logout admin (client disarankan menghapus token di sisi klien).
    """
    return {
        "success": True,
        "message": "Logged out successfully"
    }
