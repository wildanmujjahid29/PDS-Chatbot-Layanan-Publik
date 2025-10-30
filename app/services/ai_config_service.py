from typing import Any, Dict, Optional

from app.database.client import supabase


def get_all_configs() -> Dict[str, str]:
    result = supabase.table("ai_config").select("config_key, config_value").execute()
    
    configs = {}
    if result.data:
        for item in result.data:
            configs[item["config_key"]] = item["config_value"]
    
    return configs


def get_config(key: str) -> Optional[str]:
    result = supabase.table("ai_config").select("config_value").eq("config_key", key).execute()
    
    if result.data and len(result.data) > 0:
        return result.data[0]["config_value"]
    
    return None


def update_config(key: str, value: str, updated_by: Optional[str] = None) -> bool:
    update_data = {
        "config_value": value,
        "updated_at": "now()"
    }
    
    if updated_by:
        update_data["updated_by"] = updated_by
    
    result = supabase.table("ai_config").update(update_data).eq("config_key", key).execute()
    
    return bool(result.data)


def get_ai_config_summary() -> Dict[str, Any]:
    configs = get_all_configs()
    
    # Mask API key for security (show only last 4 chars)
    api_key = configs.get("gemini_api_key", "")
    masked_key = f"***{api_key[-4:]}" if len(api_key) > 4 else "Not Set"
    
    return {
        "gemini_api_key": masked_key,
        "top_k": int(configs.get("top_k", 5)),
        "min_similarity": float(configs.get("min_similarity", 0.5)),
        "temperature": float(configs.get("temperature", 0.7)),
        "max_tokens": int(configs.get("max_tokens", 1024))
    }


def update_multiple_configs(updates: Dict[str, Any], updated_by: Optional[str] = None) -> Dict[str, bool]:
    results = {}
    
    for key, value in updates.items():
        # Convert value to string for storage
        str_value = str(value)
        success = update_config(key, str_value, updated_by)
        results[key] = success
    
    return results


def get_active_gemini_key() -> str:
    return get_config("gemini_api_key") or ""


def get_active_rag_params() -> Dict[str, Any]:
    configs = get_all_configs()
    
    return {
        "top_k": int(configs.get("top_k", 5)),
        "min_similarity": float(configs.get("min_similarity", 0.5))
    }
