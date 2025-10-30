from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class RAGQueryRequest(BaseModel):
    """Request schema untuk RAG query"""
    query: str
    top_k: int = 5
    similarity_threshold: float = 0.5


class ServiceSearchResult(BaseModel):
    """Single service search result"""
    service_id: str
    service: Dict[str, Any]
    content: str
    similarity: float


class RAGQueryResponse(BaseModel):
    """Response schema untuk RAG query"""
    query: str
    search_results: List[Dict[str, Any]]
    num_results: int
