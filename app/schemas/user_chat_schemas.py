"""
Schemas untuk user chat dengan session & conversation history.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

# ============================================
# USER CHAT REQUEST/RESPONSE
# ============================================

class UserChatRequest(BaseModel):
    """Request untuk user chat (hanya query)"""
    query: str = Field(..., min_length=1, description="User's question")


class ChatMessage(BaseModel):
    """Single chat message (user or assistant)"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    message: str = Field(..., description="Message content")
    created_at: datetime = Field(..., description="Message timestamp")


class UserChatResponse(BaseModel):
    """Response untuk user chat (question & answer only, no session_id)"""
    question: str = Field(..., description="User's question")
    answer: str = Field(..., description="Assistant's answer")


# ============================================
# CONVERSATION HISTORY
# ============================================

class ConversationHistoryResponse(BaseModel):
    """Response untuk get conversation history"""
    session_id: UUID = Field(..., description="Session ID")
    history: List[ChatMessage] = Field(..., description="Chat history (newest first)")
    total_messages: int = Field(..., description="Total messages in history")


# ============================================
# SESSION MANAGEMENT
# ============================================

class SessionInfo(BaseModel):
    """Session information"""
    session_id: UUID
    created_at: datetime
    last_activity: datetime
    is_active: bool
    total_messages: int


class NewSessionResponse(BaseModel):
    """Response ketika membuat session baru"""
    session_id: UUID = Field(..., description="New session ID")
    message: str = Field(default="New session created")
