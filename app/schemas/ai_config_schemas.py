from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class AIConfigBase(BaseModel):
    """Base schema untuk AI Configuration"""
    config_key: str
    config_value: str
    description: Optional[str] = None


class AIConfigUpdate(BaseModel):
    """Schema untuk update AI config"""
    config_value: str
    updated_by: Optional[str] = None
    
    @validator('config_value')
    def validate_config_value(cls, v, values):
        """Validate config value based on key"""
        # Add validation logic here if needed
        return v


class AIConfig(AIConfigBase):
    """Schema untuk AI Configuration response"""
    id: str
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class AIConfigSummary(BaseModel):
    """Summary of all AI configurations for easy access"""
    gemini_api_key: str = Field(..., description="Gemini API Key (masked)")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of documents to retrieve (1-20)")
    min_similarity: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum similarity threshold (0-1)")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="LLM temperature (0-1)")
    max_tokens: int = Field(default=1024, ge=100, le=4096, description="Maximum tokens (100-4096)")


class AIConfigUpdateRequest(BaseModel):
    """Request untuk update specific config"""
    gemini_api_key: Optional[str] = None
    top_k: Optional[int] = Field(None, ge=1, le=20)
    min_similarity: Optional[float] = Field(None, ge=0.0, le=1.0)
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(None, ge=100, le=4096)
