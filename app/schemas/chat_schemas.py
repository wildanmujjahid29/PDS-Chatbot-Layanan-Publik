from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Request schema untuk chatbot"""
    query: str
    # Note: top_k and similarity_threshold are taken from AI config in the database.


class ChatSource(BaseModel):
    """Source information for chat response"""
    service_id: str
    content: str
    similarity: float


class ChatMetrics(BaseModel):
    """Reference-free evaluation metrics based on embeddings"""
    faithfulness: Optional[float] = None
    relevance: Optional[float] = None
    context_precision: Optional[float] = None


class ChatResponse(BaseModel):
    """Response schema untuk chatbot"""
    query: str
    response: str
    num_sources: int
    sources: List[ChatSource]
    metrics: Optional[ChatMetrics] = None
