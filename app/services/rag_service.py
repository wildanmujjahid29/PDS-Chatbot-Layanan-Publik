from typing import Any, Dict, List

from app.database.client import supabase
from app.services.embedding_service import (generate_embedding,
                                            normalize_vector, preprocess_text)


def search_similar_services(
    query: str,
    top_k: int = 5,
    similarity_threshold: float = 0.5
) -> List[Dict[str, Any]]:
    # 1. Preprocess dan generate embedding untuk query user
    processed_query = preprocess_text(query)
    query_embedding = generate_embedding(processed_query)
    query_embedding_norm = normalize_vector(query_embedding)

    result = supabase.rpc(
        'match_service_embeddings',
        {
            'query_embedding': query_embedding_norm,
            'match_threshold': 1 - similarity_threshold,  # Convert similarity to distance
            'match_count': top_k
        }
    ).execute()
    
    simplified_results = []
    if result.data:
        for item in result.data:
            simplified_results.append({
                "service_id": item.get("service_id"),
                "content": item.get("content"),
                "similarity": item.get("similarity")
            })
    
    return simplified_results


def rag_pipeline(
    user_query: str,
    top_k: int = 5,
    similarity_threshold: float = 0.5
) -> Dict[str, Any]:
    # Search similar services
    search_results = search_similar_services(
        query=user_query,
        top_k=top_k,
        similarity_threshold=similarity_threshold
    )
    
    return {
        "query": user_query,
        "search_results": search_results,
        "num_results": len(search_results)
    }
