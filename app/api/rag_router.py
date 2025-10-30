from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_admin
from app.schemas.auth_schemas import AdminUser
from app.schemas.rag_schemas import RAGQueryRequest, RAGQueryResponse
from app.services.rag_service import rag_pipeline

router = APIRouter()


@router.post("/search", response_model=RAGQueryResponse, include_in_schema=False)
def search_services_endpoint(
    request: RAGQueryRequest,
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Endpoint internal RAG untuk pencarian (test admin). Membutuhkan autentikasi admin."""
    try:
        result = rag_pipeline(
            user_query=request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold
        )
        return RAGQueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
