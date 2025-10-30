from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Cookie, HTTPException, Response

from app.schemas.user_chat_schemas import (ConversationHistoryResponse,
                                           NewSessionResponse, UserChatRequest,
                                           UserChatResponse)
from app.services.ai_config_service import get_active_rag_params
from app.services.llm_service import chat_with_rag_and_history
from app.services.rag_service import rag_pipeline
from app.services.session_service import (add_message_to_history,
                                          create_session,
                                          get_conversation_history,
                                          get_recent_context, get_session,
                                          get_session_info,
                                          update_session_activity)

router = APIRouter()


@router.post("/", response_model=UserChatResponse)
def user_chat_endpoint(
    request: UserChatRequest,
    response: Response,
    session_id: Optional[str] = Cookie(None, include_in_schema=False)
):
    """
    User chat endpoint dengan session & conversation history.
    - Otomatis buat session baru jika belum ada
    - Simpan history conversation (user + assistant)
    - Context aware (bisa referensi chat sebelumnya)
    - Session tersimpan di cookie (otomatis)
    """
    try:
        # 1. Get atau create session
        current_session_id = None
        
        if session_id:
            # Cek session exists
            session = get_session(UUID(session_id))
            if session and session.get("is_active"):
                current_session_id = UUID(session_id)
                # Update last activity
                update_session_activity(current_session_id)
        
        # Create new session jika belum ada atau invalid
        if not current_session_id:
            new_session = create_session()
            current_session_id = UUID(new_session["session_id"])
            # Set cookie untuk session
            response.set_cookie(
                key="session_id",
                value=str(current_session_id),
                httponly=True,
                max_age=86400 * 7,  # 7 days
                samesite="lax"
            )
        
        # 2. Ambil conversation context (5 message terakhir)
        conversation_context = get_recent_context(current_session_id, limit=5)
        
        # 3. Simpan user message ke history
        add_message_to_history(
            session_id=current_session_id,
            role="user",
            message=request.query
        )
        
        # 4. Get active RAG params dari AI config
        active_params = get_active_rag_params()
        
        # 5. RAG: Search similar services
        rag_result = rag_pipeline(
            user_query=request.query,
            top_k=active_params["top_k"],
            similarity_threshold=active_params["min_similarity"]
        )
        
        # 6. LLM: Generate response dengan history context
        chat_result = chat_with_rag_and_history(
            user_query=request.query,
            search_results=rag_result["search_results"],
            conversation_context=conversation_context
        )
        
        # 7. Simpan assistant response ke history
        add_message_to_history(
            session_id=current_session_id,
            role="assistant",
            message=chat_result["response"]
        )
        
        # 8. Return simple response (question + answer only, no session_id)
        return UserChatResponse(
            question=request.query,
            answer=chat_result["response"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=ConversationHistoryResponse)
def get_history_endpoint(
    session_id: Optional[str] = Cookie(None, include_in_schema=False),
    limit: int = 10
):
    """
    Get conversation history untuk session saat ini.
    Returns newest messages first.
    """
    if not session_id:
        raise HTTPException(status_code=400, detail="No active session found")
    
    try:
        session_uuid = UUID(session_id)
        
        # Verify session exists
        session = get_session(session_uuid)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get history
        history = get_conversation_history(session_uuid, limit)
        
        return ConversationHistoryResponse(
            session_id=session_uuid,
            history=history,
            total_messages=len(history)
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/new-session", response_model=NewSessionResponse)
def new_session_endpoint(response: Response):
    """
    Buat session baru (clear history, start fresh).
    """
    try:
        new_session = create_session()
        session_id = new_session["session_id"]
        
        # Set cookie
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            max_age=86400 * 7,  # 7 days
            samesite="lax"
        )
        
        return NewSessionResponse(
            session_id=UUID(session_id),
            message="New session created successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session")
def clear_session_endpoint(response: Response):
    """
    Clear session cookie (logout/reset).
    """
    response.delete_cookie(key="session_id")
    return {"message": "Session cleared successfully"}


@router.get("/session-info")
def get_session_info_endpoint(
    session_id: Optional[str] = Cookie(None, include_in_schema=False)
):
    """
    Get info tentang session saat ini.
    """
    if not session_id:
        raise HTTPException(status_code=400, detail="No active session found")
    
    try:
        session_uuid = UUID(session_id)
        info = get_session_info(session_uuid)
        
        if not info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return info
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
def health_check():
    """
    Health check endpoint untuk user chat service.
    """
    try:
        # Check if AI config is accessible
        params = get_active_rag_params()
        
        return {
            "status": "healthy",
            "service": "user_chat",
            "config_loaded": True,
            "rag_params": params
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "user_chat",
            "error": str(e)
        }
