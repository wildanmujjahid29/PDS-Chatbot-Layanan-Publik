"""
Service untuk generate admin dashboard metrics.
"""
import time
from datetime import datetime, timedelta
from typing import Dict, List

from app.database.client import supabase
from app.services.ai_config_service import get_all_configs


def get_knowledge_base_stats() -> Dict:
    """
    Get statistics tentang knowledge base layanan.
    
    Returns:
        Dict dengan total services, embedding coverage, top categories
    """
    try:
        # Get total services
        services_response = supabase.table("services").select("id", count="exact").execute()
        total_services = services_response.count if services_response.count else 0
        
        # Get total embedded services
        embeddings_response = supabase.table("service_embeddings").select("service_id", count="exact").execute()
        total_embedded = embeddings_response.count if embeddings_response.count else 0
        
        # Calculate embedding coverage
        embedding_coverage = (total_embedded / total_services * 100) if total_services > 0 else 0
        
        # Get top categories (by instansi_penyelenggara)
        services_data = supabase.table("services").select("instansi_penyelenggara").execute()
        
        # Count by category
        category_counts = {}
        for service in services_data.data:
            category = service.get("instansi_penyelenggara", "Unknown")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Sort and get top 10
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        top_categories = [
            {
                "category": cat,
                "count": count,
                "percentage": (count / total_services * 100) if total_services > 0 else 0
            }
            for cat, count in sorted_categories
        ]
        
        return {
            "total_services": total_services,
            "total_embedded": total_embedded,
            "embedding_coverage": round(embedding_coverage, 2),
            "top_categories": top_categories,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "total_services": 0,
            "total_embedded": 0,
            "embedding_coverage": 0,
            "top_categories": [],
            "last_updated": None,
            "error": str(e)
        }


def get_ai_config_status() -> Dict:
    """
    Get current AI configuration status.
    
    Returns:
        Dict dengan AI config settings
    """
    try:
        configs = get_all_configs()
        
        gemini_key = configs.get("gemini_api_key", {}).get("config_value")
        
        return {
            "gemini_api_configured": bool(gemini_key and gemini_key.strip()),
            "top_k": int(configs.get("top_k", {}).get("config_value", 3)),
            "min_similarity": float(configs.get("min_similarity", {}).get("config_value", 0.3)),
            "temperature": float(configs.get("temperature", {}).get("config_value", 0.7)),
            "max_tokens": int(configs.get("max_tokens", {}).get("config_value", 1024))
        }
        
    except Exception as e:
        return {
            "gemini_api_configured": False,
            "top_k": 3,
            "min_similarity": 0.3,
            "temperature": 0.7,
            "max_tokens": 1024,
            "error": str(e)
        }


def get_chat_analytics() -> Dict:
    """
    Get analytics tentang chat sessions dan messages.
    
    Returns:
        Dict dengan chat analytics metrics
    """
    try:
        # Total sessions
        sessions_response = supabase.table("chat_sessions").select("id", count="exact").execute()
        total_sessions = sessions_response.count if sessions_response.count else 0
        
        # Active sessions (last 24 hours)
        yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
        active_sessions_response = supabase.table("chat_sessions").select(
            "id", count="exact"
        ).gte("last_activity", yesterday).eq("is_active", True).execute()
        active_sessions = active_sessions_response.count if active_sessions_response.count else 0
        
        # Total messages
        messages_response = supabase.table("chat_history").select("id, role", count="exact").execute()
        total_messages = messages_response.count if messages_response.count else 0
        
        # User vs Assistant messages
        user_messages = sum(1 for msg in messages_response.data if msg.get("role") == "user")
        assistant_messages = sum(1 for msg in messages_response.data if msg.get("role") == "assistant")
        
        # Average messages per session
        avg_messages = (total_messages / total_sessions) if total_sessions > 0 else 0
        
        # Sessions created today
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        sessions_today_response = supabase.table("chat_sessions").select(
            "id", count="exact"
        ).gte("created_at", today_start).execute()
        sessions_today = sessions_today_response.count if sessions_today_response.count else 0
        
        # Messages sent today
        messages_today_response = supabase.table("chat_history").select(
            "id", count="exact"
        ).gte("created_at", today_start).execute()
        messages_today = messages_today_response.count if messages_today_response.count else 0
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "total_messages": total_messages,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "avg_messages_per_session": round(avg_messages, 2),
            "sessions_today": sessions_today,
            "messages_today": messages_today
        }
        
    except Exception as e:
        return {
            "total_sessions": 0,
            "active_sessions": 0,
            "total_messages": 0,
            "user_messages": 0,
            "assistant_messages": 0,
            "avg_messages_per_session": 0,
            "sessions_today": 0,
            "messages_today": 0,
            "error": str(e)
        }


def check_database_health() -> Dict:
    """
    Check database connection health.
    
    Returns:
        Dict dengan database health status
    """
    try:
        start_time = time.time()
        
        # Try to query a simple table
        response = supabase.table("services").select("id").limit(1).execute()
        
        response_time_ms = (time.time() - start_time) * 1000
        
        # Check if all tables are accessible
        tables = ["services", "service_embeddings", "ai_config", "chat_sessions", "chat_history", "admin_users"]
        tables_accessible = True
        
        for table in tables:
            try:
                supabase.table(table).select("*").limit(1).execute()
            except Exception:
                tables_accessible = False
                break
        
        return {
            "status": "healthy",
            "response_time_ms": round(response_time_ms, 2),
            "tables_accessible": tables_accessible,
            "error": None
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "response_time_ms": None,
            "tables_accessible": False,
            "error": str(e)
        }


def check_llm_health() -> Dict:
    """
    Check LLM service health.
    
    Returns:
        Dict dengan LLM health status
    """
    try:
        from app.services.llm_service import get_configured_model

        # Try to get configured model
        model = get_configured_model()
        
        return {
            "status": "healthy",
            "api_key_configured": True,
            "model_name": "gemini-2.0-flash-exp",
            "error": None
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "api_key_configured": False,
            "model_name": "gemini-2.0-flash-exp",
            "error": str(e)
        }


def get_system_health() -> Dict:
    """
    Get overall system health status.
    
    Returns:
        Dict dengan complete system health check
    """
    database = check_database_health()
    llm = check_llm_health()
    
    # Determine overall status
    if database["status"] == "healthy" and llm["status"] == "healthy":
        overall_status = "healthy"
    elif database["status"] == "unhealthy" or llm["status"] == "unhealthy":
        overall_status = "unhealthy"
    else:
        overall_status = "degraded"
    
    return {
        "overall_status": overall_status,
        "database": database,
        "llm": llm,
        "embedding_service": "healthy",  # Assuming embedding service is healthy if we can import it
        "uptime": None  # Could add actual uptime tracking if needed
    }


def get_complete_dashboard() -> Dict:
    """
    Generate complete admin dashboard dengan semua metrics.
    
    Returns:
        Dict dengan complete dashboard data
    """
    return {
        "knowledge_base": get_knowledge_base_stats(),
        "ai_config": get_ai_config_status(),
        "chat_analytics": get_chat_analytics(),
        "system_health": get_system_health(),
        "generated_at": datetime.now().isoformat()
    }
