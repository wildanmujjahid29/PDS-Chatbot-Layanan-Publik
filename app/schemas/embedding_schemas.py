from pydantic import BaseModel
from typing import List
from uuid import UUID

class EmbeddingBase(BaseModel):
    service_id: UUID
    content: str
    embedding: List[float]