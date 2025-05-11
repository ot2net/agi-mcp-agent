"""LLM (Large Language Model) configuration models for MCP."""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator


class LLMProvider(BaseModel):
    """LLM Provider configuration."""
    id: Optional[int] = None
    name: str  # e.g. 'openai', 'anthropic'
    type: str  # e.g. 'openai', 'anthropic', 'rest'
    api_key: str
    models: List[str]  # List of supported model names
    status: str = "enabled"
    metadata: Optional[Dict[str, Any]] = None

    @validator('type')
    def validate_type(cls, v):
        """Validate provider type."""
        valid_types = ['openai', 'anthropic', 'rest']
        if v not in valid_types:
            raise ValueError(f'Provider type must be one of {valid_types}')
        return v


class LLMModel(BaseModel):
    """LLM Model configuration."""
    id: Optional[int] = None
    provider_id: int
    model_name: str  # e.g. 'gpt-3.5-turbo'
    capability: str  # e.g. 'chat', 'embedding', 'completion'
    params: Dict[str, Any]  # Model-specific parameters
    status: str = "enabled"
    metadata: Optional[Dict[str, Any]] = None

    @validator('capability')
    def validate_capability(cls, v):
        """Validate model capability."""
        valid_capabilities = ['chat', 'embedding', 'completion']
        if v not in valid_capabilities:
            raise ValueError(f'Model capability must be one of {valid_capabilities}')
        return v


class LLMRequest(BaseModel):
    """LLM Request configuration."""
    model_id: int
    prompt: str
    max_tokens: Optional[int] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    stop: Optional[List[str]] = None
    stream: bool = False
    metadata: Optional[Dict[str, Any]] = None


class LLMResponse(BaseModel):
    """LLM Response model."""
    request_id: str
    model_id: int
    content: str
    usage: Dict[str, int]  # e.g. {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30}
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMEmbeddingRequest(BaseModel):
    """LLM Embedding Request configuration."""
    model_id: int
    input: Union[str, List[str]]
    metadata: Optional[Dict[str, Any]] = None


class LLMEmbeddingResponse(BaseModel):
    """LLM Embedding Response model."""
    request_id: str
    model_id: int
    embeddings: List[List[float]]
    usage: Dict[str, int]
    metadata: Optional[Dict[str, Any]] = None 