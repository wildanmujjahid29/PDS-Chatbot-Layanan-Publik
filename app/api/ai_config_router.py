from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_admin
from app.schemas.ai_config_schemas import (AIConfigSummary,
                                           AIConfigUpdateRequest)
from app.schemas.auth_schemas import AdminUser
from app.services import ai_config_service

router = APIRouter()


@router.get("/", response_model=AIConfigSummary)
def get_ai_config(
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Ambil konfigurasi AI saat ini. Membutuhkan autentikasi admin.
    Kunci API akan disamarkan demi keamanan.

    Returns:
        Ringkasan konfigurasi AI yang aktif saat ini
    """
    try:
        config = ai_config_service.get_ai_config_summary()
        return AIConfigSummary(**config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/", response_model=dict)
def update_ai_config(
    updates: AIConfigUpdateRequest,
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Perbarui konfigurasi AI. Membutuhkan autentikasi admin.
    Hanya field yang disediakan yang akan diperbarui.

    Args:
        updates: AIConfigUpdateRequest berisi field yang ingin diubah

    Returns:
        Status hasil operasi pembaruan untuk tiap field
    """
    try:
        # Build update dictionary from provided fields
        update_dict = {}
        
        if updates.gemini_api_key is not None:
            update_dict["gemini_api_key"] = updates.gemini_api_key
        
        if updates.top_k is not None:
            update_dict["top_k"] = updates.top_k
        
        if updates.min_similarity is not None:
            update_dict["min_similarity"] = updates.min_similarity
        
        if updates.temperature is not None:
            update_dict["temperature"] = updates.temperature
        
        if updates.max_tokens is not None:
            update_dict["max_tokens"] = updates.max_tokens
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No fields provided for update")
        
        # Update configs (no updated_by for now)
        results = ai_config_service.update_multiple_configs(update_dict)
        
        # Check if all updates were successful
        all_success = all(results.values())
        
        return {
            "success": all_success,
            "message": "Configuration updated successfully" if all_success else "Some updates failed",
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test", response_model=dict)
def test_current_config():
    """
    Endpoint uji untuk menampilkan konfigurasi aktif saat ini untuk chatbot.
    Menampilkan nilai-nilai aktual yang digunakan sistem.

    Returns:
        Konfigurasi aktif saat ini
    """
    try:
        rag_params = ai_config_service.get_active_rag_params()
        all_configs = ai_config_service.get_all_configs()
        
        return {
            "rag_params": rag_params,
            "llm_params": {
                "temperature": float(all_configs.get("temperature", 0.7)),
                "max_tokens": int(all_configs.get("max_tokens", 1024))
            },
            "api_key_status": "Set" if ai_config_service.get_active_gemini_key() else "Not Set"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
