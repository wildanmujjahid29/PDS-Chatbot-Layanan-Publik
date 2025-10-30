"""
Schemas untuk Admin Dashboard.
"""
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

# ============================================
# KNOWLEDGE BASE STATS
# ============================================

class ServiceCategoryStats(BaseModel):
    """Stats per kategori layanan"""
    category: str = Field(..., description="Kategori layanan (instansi)")
    count: int = Field(..., description="Jumlah layanan")
    percentage: float = Field(..., description="Persentase dari total")


class KnowledgeBaseStats(BaseModel):
    """Statistics knowledge base layanan"""
    total_services: int = Field(..., description="Total layanan di database")
    total_embedded: int = Field(..., description="Total layanan yang sudah di-embed")
    embedding_coverage: float = Field(..., description="Persentase coverage embedding")
    top_categories: List[ServiceCategoryStats] = Field(..., description="Top 10 kategori layanan")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")


# ============================================
# AI CONFIGURATION STATUS
# ============================================

class AIConfigStatus(BaseModel):
    """Current AI configuration status"""
    gemini_api_configured: bool = Field(..., description="Apakah Gemini API key sudah dikonfigurasi")
    top_k: int = Field(..., description="Current top_k parameter")
    min_similarity: float = Field(..., description="Current minimum similarity threshold")
    temperature: float = Field(..., description="LLM temperature setting")
    max_tokens: int = Field(..., description="Max tokens for LLM response")


# ============================================
# CHAT ANALYTICS
# ============================================

class ChatAnalytics(BaseModel):
    """Analytics untuk chat sessions dan messages"""
    total_sessions: int = Field(..., description="Total sessions created")
    active_sessions: int = Field(..., description="Sessions active dalam 24 jam terakhir")
    total_messages: int = Field(..., description="Total messages (user + assistant)")
    user_messages: int = Field(..., description="Total user messages")
    assistant_messages: int = Field(..., description="Total assistant messages")
    avg_messages_per_session: float = Field(..., description="Average messages per session")
    sessions_today: int = Field(..., description="New sessions created today")
    messages_today: int = Field(..., description="Messages sent today")


# ============================================
# SYSTEM HEALTH
# ============================================

class DatabaseHealth(BaseModel):
    """Database connection health"""
    status: str = Field(..., description="'healthy' or 'unhealthy'")
    response_time_ms: Optional[float] = Field(None, description="Database response time in ms")
    tables_accessible: bool = Field(..., description="Apakah semua tabel bisa diakses")
    error: Optional[str] = Field(None, description="Error message jika unhealthy")


class LLMHealth(BaseModel):
    """LLM service health"""
    status: str = Field(..., description="'healthy' or 'unhealthy'")
    api_key_configured: bool = Field(..., description="Apakah API key sudah dikonfigurasi")
    model_name: str = Field(..., description="Model yang digunakan")
    error: Optional[str] = Field(None, description="Error message jika unhealthy")


class SystemHealth(BaseModel):
    """Overall system health check"""
    overall_status: str = Field(..., description="'healthy', 'degraded', or 'unhealthy'")
    database: DatabaseHealth = Field(..., description="Database health status")
    llm: LLMHealth = Field(..., description="LLM service health status")
    embedding_service: str = Field(..., description="Embedding service status")
    uptime: Optional[str] = Field(None, description="System uptime")


# ============================================
# COMPLETE DASHBOARD
# ============================================

class AdminDashboard(BaseModel):
    """Complete admin dashboard response"""
    knowledge_base: KnowledgeBaseStats = Field(..., description="Knowledge base statistics")
    ai_config: AIConfigStatus = Field(..., description="Current AI configuration")
    chat_analytics: ChatAnalytics = Field(..., description="Chat analytics and metrics")
    system_health: SystemHealth = Field(..., description="System health status")
    generated_at: datetime = Field(default_factory=datetime.now, description="Dashboard generation timestamp")
