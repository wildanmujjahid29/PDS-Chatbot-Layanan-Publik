from typing import List, Optional

from app.database.client import supabase
from app.schemas.mpp_service_schemas import (Service, ServiceCreate,
                                             ServiceUpdate)
from app.services.embedding_service import pipeline_embedding


def create_service(service: ServiceCreate) -> Service:
    # Insert ke tabel services
    result = supabase.table("services").insert(service.dict()).execute()
    data = result.data[0]

    # Jalankan pipeline embedding
    content, embedding = pipeline_embedding(Service(**data))

    # Insert ke tabel service_embeddings
    embedding_data = {
        "service_id": data["id"],
        "content": content,
        "embedding": embedding
    }
    supabase.table("service_embeddings").insert(embedding_data).execute()

    return Service(**data)

def create_services(services: List[ServiceCreate]) -> List[Service]:
    """
    Insert banyak services sekaligus (bulk insert).
    """
    # Insert semua services ke tabel services
    services_data = [service.dict() for service in services]
    result = supabase.table("services").insert(services_data).execute()
    
    # Generate embeddings untuk semua services
    embedding_data_list = []
    created_services = []
    
    for data in result.data:
        service_obj = Service(**data)
        created_services.append(service_obj)
        
        # Jalankan pipeline embedding
        content, embedding = pipeline_embedding(service_obj)
        
        embedding_data_list.append({
            "service_id": data["id"],
            "content": content,
            "embedding": embedding
        })
    
    # Bulk insert ke tabel service_embeddings
    if embedding_data_list:
        supabase.table("service_embeddings").insert(embedding_data_list).execute()
    
    return created_services

def get_service(service_id: str) -> Optional[Service]:
    result = supabase.table("services").select("*").eq("id", service_id).execute()
    if result.data:
        return Service(**result.data[0])
    return None

def get_services() -> List[Service]:
    result = supabase.table("services").select("*").execute()
    return [Service(**item) for item in result.data]

def update_service(service_id: str, service: ServiceUpdate) -> Optional[Service]:
    # Update data di tabel services
    result = supabase.table("services").update(service.dict(exclude_unset=True)).eq("id", service_id).execute()
    
    if result.data:
        updated_service = Service(**result.data[0])
        
        # Re-generate embedding untuk data yang diupdate
        content, embedding = pipeline_embedding(updated_service)
        
        # Update embedding di tabel service_embeddings
        embedding_data = {
            "content": content,
            "embedding": embedding
        }
        supabase.table("service_embeddings").update(embedding_data).eq("service_id", service_id).execute()
        
        return updated_service
    
    return None

def delete_service(service_id: str) -> bool:
    result = supabase.table("services").delete().eq("id", service_id).execute()
    return bool(result.data)