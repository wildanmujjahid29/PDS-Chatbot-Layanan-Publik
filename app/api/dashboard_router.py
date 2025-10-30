"""
Router untuk Admin Dashboard.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_admin
from app.schemas.auth_schemas import AdminUser
from app.schemas.dashboard_schemas import (AdminDashboard, AIConfigStatus,
                                           ChatAnalytics, KnowledgeBaseStats,
                                           SystemHealth)
from app.services.dashboard_service import (get_ai_config_status,
                                            get_chat_analytics,
                                            get_complete_dashboard,
                                            get_knowledge_base_stats,
                                            get_system_health)

router = APIRouter()


@router.get("/", response_model=AdminDashboard)
def get_dashboard(
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Ambil dashboard admin lengkap beserta semua metrik.
    Membutuhkan autentikasi admin.

    Returns:
        - Statistik Knowledge Base
        - Status Konfigurasi AI
        - Analitik Chat
        - Pemeriksaan Kesehatan Sistem
    """
    try:
        dashboard_data = get_complete_dashboard()
        return AdminDashboard(**dashboard_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard: {str(e)}")


@router.get("/knowledge-base", response_model=KnowledgeBaseStats)
def get_knowledge_base_stats_endpoint(
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Ambil statistik knowledge base saja.
    Membutuhkan autentikasi admin.
    """
    try:
        stats = get_knowledge_base_stats()
        return KnowledgeBaseStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-config", response_model=AIConfigStatus)
def get_ai_config_status_endpoint(
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Ambil status konfigurasi AI saja.
    Membutuhkan autentikasi admin.
    """
    try:
        status = get_ai_config_status()
        return AIConfigStatus(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat-analytics", response_model=ChatAnalytics)
def get_chat_analytics_endpoint(
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Ambil analitik chat saja.
    Membutuhkan autentikasi admin.
    """
    try:
        analytics = get_chat_analytics()
        return ChatAnalytics(**analytics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-health", response_model=SystemHealth)
def get_system_health_endpoint(
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Ambil status kesehatan sistem saja.
    Membutuhkan autentikasi admin.
    """
    try:
        health = get_system_health()
        return SystemHealth(**health)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
