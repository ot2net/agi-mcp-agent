"""Base classes for LLM providers."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, AsyncGenerator

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ModelConfig(BaseModel):
    """Configuration for a language model."""
    
    model_name: str
    provider_name: str
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = []
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    api_version: Optional[str] = None
    organization_id: Optional[str] = None
    additional_config: Dict[str, Any] = {}


class ModelUsage(BaseModel):
    """Usage statistics for a model call."""
    
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    input_cost: float = 0.0
    output_cost: float = 0.0
    total_cost: float = 0.0


class ModelResponse(BaseModel):
    """Response from a language model."""
    
    text: str
    model_name: str
    provider_name: str
    usage: ModelUsage
    finish_reason: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    created_at: datetime = datetime.now()
    response_ms: float = 0.0


class ModelCapability(BaseModel):
    """Capability of a language model."""
    
    name: str
    description: str
    parameters: Dict[str, Any] = {}
    supported_models: List[str] = []


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize the provider.
        
        Args:
            api_key: API key for the provider
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.provider_name = self.__class__.__name__.replace('Provider', '')
        self.available_models = self.list_available_models()
        self.capabilities = self.get_capabilities()
        logger.info(f"Initialized {self.provider_name} provider with {len(self.available_models)} models")
    
    @abstractmethod
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available models from this provider.
        
        Returns:
            List of model information dictionaries
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[ModelCapability]:
        """Get the capabilities of this provider.
        
        Returns:
            List of model capabilities
        """
        pass
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate the API key.
        
        Returns:
            Whether the API key is valid
        """
        pass
    
    @abstractmethod
    async def generate_text(
        self, 
        prompt: str, 
        model_config: ModelConfig,
        stream: bool = False,
    ) -> Union[ModelResponse, AsyncGenerator[ModelResponse, None]]:
        """Generate text from the model.
        
        Args:
            prompt: The prompt to send to the model
            model_config: Configuration for the model
            stream: Whether to stream the response
            
        Returns:
            Either a ModelResponse or an async generator of ModelResponses if streaming
        """
        pass
    
    @abstractmethod
    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model_config: ModelConfig,
        stream: bool = False,
    ) -> Union[ModelResponse, AsyncGenerator[ModelResponse, None]]:
        """Generate a chat completion from the model.
        
        Args:
            messages: List of chat messages in the format [{"role": "user", "content": "..."}]
            model_config: Configuration for the model
            stream: Whether to stream the response
            
        Returns:
            Either a ModelResponse or an async generator of ModelResponses if streaming
        """
        pass
    
    @abstractmethod
    async def generate_embeddings(
        self,
        texts: List[str],
        model_config: ModelConfig,
    ) -> List[List[float]]:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            model_config: Configuration for the model
            
        Returns:
            List of embedding vectors
        """
        pass
    
    def model_supports_capability(self, model_name: str, capability_name: str) -> bool:
        """Check if a model supports a specific capability.
        
        Args:
            model_name: Name of the model
            capability_name: Name of the capability
            
        Returns:
            Whether the model supports the capability
        """
        for capability in self.capabilities:
            if capability.name == capability_name and model_name in capability.supported_models:
                return True
        return False
    
    def __str__(self) -> str:
        """Get a string representation of the provider.
        
        Returns:
            String representation
        """
        return f"{self.provider_name}Provider({len(self.available_models)} models)" 