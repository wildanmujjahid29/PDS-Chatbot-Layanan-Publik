from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_admin
from app.schemas.auth_schemas import AdminUser
from app.schemas.chat_schemas import ChatRequest, ChatResponse
from app.services.ai_config_service import get_active_rag_params
from app.services.embedding_service import (generate_embedding,
                                            normalize_vector, preprocess_text)
from app.services.llm_service import chat_with_rag
from app.services.rag_service import rag_pipeline

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest,
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Endpoint uji chat untuk admin. Membutuhkan autentikasi admin.
    Parameter RAG (top_k, min_similarity) diambil dari konfigurasi AI yang tersimpan
    di database; tidak diambil dari request.
    """
    try:
        # Get active RAG params from AI config
        active_params = get_active_rag_params()

        # Use RAG params from AI config stored in database (do not accept from request)
        top_k = active_params["top_k"]
        min_similarity = active_params["min_similarity"]
        # 1. RAG: Search similar services
        rag_result = rag_pipeline(
            user_query=request.query,
            top_k=top_k,
            similarity_threshold=min_similarity
        )
        
        # 2. LLM: Generate response dengan Gemini
        chat_result = chat_with_rag(
            user_query=request.query,
            search_results=rag_result["search_results"]
        )

        # 3. Compute lightweight reference-free metrics using embeddings (if possible)
        #   - faithfulness: similarity between answer and concatenated context
        #   - relevance: similarity between answer and question
        #   - context_precision: fraction of sources with answer-source sim >= threshold
        try:
            generated = chat_result.get("response")
            question = request.query
            sources = rag_result.get("search_results", [])

            if generated and question:
                # embeddings: preprocess + generate + normalize
                q_emb = normalize_vector(generate_embedding(preprocess_text(question)))
                a_emb = normalize_vector(generate_embedding(preprocess_text(generated)))

                # cosine helper
                def cos(u, v):
                    return sum(x * y for x, y in zip(u, v)) if u and v and len(u) == len(v) else 0.0

                relevance = float(cos(a_emb, q_emb))

                # context concat
                if sources:
                    concat = " ".join([s.get("content", "") for s in sources])
                    concat_emb = normalize_vector(generate_embedding(preprocess_text(concat)))
                    faithfulness = float(cos(a_emb, concat_emb))

                    # per-source sims
                    thr = 0.65
                    count_relevant = 0
                    for s in sources:
                        s_content = s.get("content") or ""
                        s_emb = normalize_vector(generate_embedding(preprocess_text(s_content)))
                        sim = cos(a_emb, s_emb)
                        if sim >= thr:
                            count_relevant += 1
                    context_precision = count_relevant / len(sources) if sources else 0.0
                else:
                    faithfulness = None
                    context_precision = None

                metrics = {
                    "faithfulness": round(faithfulness, 4) if faithfulness is not None else None,
                    "relevance": round(relevance, 4),
                    "context_precision": round(context_precision, 4) if context_precision is not None else None,
                }
            else:
                metrics = None
        except Exception:
            metrics = None

        # Attach metrics into response payload
        try:
            chat_result["metrics"] = metrics
        except Exception:
            pass

        return ChatResponse(**chat_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
