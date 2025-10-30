"""
Service untuk mengelola chat sessions dan conversation history.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from app.database.client import supabase


def create_session() -> dict:
    """
    Buat session baru untuk user.
    
    Returns:
        dict: Session data dengan session_id
    """
    response = supabase.table("chat_sessions").insert({
        "created_at": datetime.now().isoformat(),
        "last_activity": datetime.now().isoformat(),
        "is_active": True
    }).execute()
    
    if response.data and len(response.data) > 0:
        return response.data[0]
    raise Exception("Failed to create session")


def get_session(session_id: UUID) -> Optional[dict]:
    """
    Get session by ID.
    
    Args:
        session_id: UUID of session
        
    Returns:
        dict or None: Session data or None if not found
    """
    response = supabase.table("chat_sessions").select("*").eq("session_id", str(session_id)).execute()
    
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None


def update_session_activity(session_id: UUID) -> bool:
    """
    Update last_activity timestamp untuk session.
    
    Args:
        session_id: UUID of session
        
    Returns:
        bool: True if updated successfully
    """
    try:
        response = supabase.table("chat_sessions").update({
            "last_activity": datetime.now().isoformat()
        }).eq("session_id", str(session_id)).execute()
        
        return response.data is not None and len(response.data) > 0
    except Exception:
        return False


def add_message_to_history(session_id: UUID, role: str, message: str, metadata: Optional[dict] = None) -> dict:
    """
    Tambah pesan ke chat history.
    
    Args:
        session_id: UUID of session
        role: 'user' or 'assistant'
        message: Message content
        metadata: Optional metadata (e.g., retrieved services)
        
    Returns:
        dict: Inserted message data
    """
    data = {
        "session_id": str(session_id),
        "role": role,
        "message": message,
        "created_at": datetime.now().isoformat()
    }
    
    if metadata:
        data["metadata"] = metadata
    
    response = supabase.table("chat_history").insert(data).execute()
    
    if response.data and len(response.data) > 0:
        return response.data[0]
    raise Exception("Failed to add message to history")


def get_conversation_history(session_id: UUID, limit: int = 10) -> List[dict]:
    """
    Ambil conversation history untuk session (newest first).
    
    Args:
        session_id: UUID of session
        limit: Maximum number of messages to retrieve
        
    Returns:
        List[dict]: List of chat messages
    """
    response = supabase.table("chat_history").select("role, message, created_at").eq(
        "session_id", str(session_id)
    ).order("created_at", desc=True).limit(limit).execute()
    
    return response.data if response.data else []


def get_recent_context(session_id: UUID, limit: int = 5) -> str:
    """
    Ambil recent conversation context untuk LLM (format string).
    Returns messages in chronological order (oldest first) untuk context.
    
    Args:
        session_id: UUID of session
        limit: Number of recent messages to include
        
    Returns:
        str: Formatted conversation context
    """
    messages = get_conversation_history(session_id, limit)
    
    if not messages:
        return ""
    
    # Reverse untuk chronological order (oldest first)
    messages.reverse()
    
    context_lines = []
    for msg in messages:
        role_label = "Pengguna" if msg["role"] == "user" else "Asisten"
        context_lines.append(f"{role_label}: {msg['message']}")
    
    return "\n".join(context_lines)


def get_session_info(session_id: UUID) -> Optional[dict]:
    """
    Get session info with total messages count.
    
    Args:
        session_id: UUID of session
        
    Returns:
        dict or None: Session info with total_messages
    """
    session = get_session(session_id)
    if not session:
        return None
    
    # Count total messages
    response = supabase.table("chat_history").select("id", count="exact").eq(
        "session_id", str(session_id)
    ).execute()
    
    total_messages = response.count if response.count else 0
    
    return {
        **session,
        "total_messages": total_messages
    }


def cleanup_inactive_sessions() -> int:
    """
    Cleanup sessions yang tidak aktif lebih dari 24 jam.
    
    Returns:
        int: Number of sessions cleaned up
    """
    try:
        response = supabase.rpc("cleanup_inactive_sessions").execute()
        return response.data if response.data else 0
    except Exception:
        return 0
