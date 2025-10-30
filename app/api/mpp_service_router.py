from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_admin
from app.schemas.auth_schemas import AdminUser
from app.schemas.mpp_service_schemas import (Service, ServiceCreate,
                                             ServiceUpdate)
from app.services.mpp_service import (create_service, create_services,
                                      delete_service, get_service,
                                      get_services, update_service)

router = APIRouter()

@router.post("/", response_model=Service)
def create_service_endpoint(
    service: ServiceCreate,
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Buat layanan baru. Membutuhkan autentikasi admin."""
    return create_service(service)

@router.post("/bulk", response_model=List[Service])
def create_services_bulk_endpoint(
    services: List[ServiceCreate],
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Buat banyak layanan sekaligus (bulk). Membutuhkan autentikasi admin."""
    return create_services(services)

@router.get("/", response_model=List[Service])
def list_services_endpoint(
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Daftar semua layanan. Membutuhkan autentikasi admin."""
    return get_services()

@router.get("/{service_id}", response_model=Service)
def get_service_endpoint(
    service_id: str,
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Ambil layanan tertentu berdasarkan ID. Membutuhkan autentikasi admin."""
    service = get_service(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.put("/{service_id}", response_model=Service)
def update_service_endpoint(
    service_id: str,
    service: ServiceUpdate,
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Perbarui layanan. Membutuhkan autentikasi admin."""
    updated = update_service(service_id, service)
    if not updated:
        raise HTTPException(status_code=404, detail="Service not found")
    return updated

@router.delete("/{service_id}", response_model=dict)
def delete_service_endpoint(
    service_id: str,
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Hapus layanan. Membutuhkan autentikasi admin."""
    success = delete_service(service_id)
    if not success:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"result": "success"}