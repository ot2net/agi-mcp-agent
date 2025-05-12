"""LLM (Large Language Model) service layer."""

import logging
import uuid
from typing import Dict, List, Optional, Any, Union
import openai
import anthropic
from sqlalchemy import text

from agi_mcp_agent.mcp.llm_models import (
    LLMProvider, LLMModel, LLMRequest, LLMResponse,
    LLMEmbeddingRequest, LLMEmbeddingResponse
)
from agi_mcp_agent.mcp.repository import MCPRepository

logger = logging.getLogger(__name__)


class LLMService:
    """Service for handling LLM operations."""

    def __init__(self, repository: MCPRepository):
        """Initialize the LLM service.

        Args:
            repository: The MCP repository instance
        """
        self.repository = repository
        self._providers: Dict[int, LLMProvider] = {}
        self._models: Dict[int, LLMModel] = {}
        self._load_providers_and_models()

    def _load_providers_and_models(self):
        """Load all providers and models from the database."""
        try:
            with self.repository._get_session() as session:
                # Load providers
                provider_query = text("""
                    SELECT id, name, type, api_key, models, status, metadata, display_name
                    FROM llm_providers 
                    WHERE status = 'enabled'
                """)
                providers = session.execute(provider_query).fetchall()
                for p in providers:
                    try:
                        # Convert models string to list if it's a string
                        models = p[4] if isinstance(p[4], list) else []
                        # Convert metadata to dict if it's not already
                        metadata = p[6] if isinstance(p[6], dict) else {}
                        
                        self._providers[p[0]] = LLMProvider(
                            id=p[0],
                            name=p[1],
                            type=p[2],
                            api_key=p[3],
                            models=models,
                            status=p[5],
                            metadata=metadata
                        )
                    except Exception as e:
                        logger.error(f"Error loading provider {p[1]}: {e}")
                        continue

                # Load models
                model_query = text("""
                    SELECT id, provider_id, model_name, capability, params, status, metadata
                    FROM llm_models 
                    WHERE status = 'enabled'
                """)
                models = session.execute(model_query).fetchall()
                for m in models:
                    try:
                        # Convert params to dict if it's not already
                        params = m[4] if isinstance(m[4], dict) else {}
                        # Convert metadata to dict if it's not already
                        metadata = m[6] if isinstance(m[6], dict) else {}
                        
                        self._models[m[0]] = LLMModel(
                            id=m[0],
                            provider_id=m[1],
                            model_name=m[2],
                            capability=m[3],
                            params=params,
                            status=m[5],
                            metadata=metadata
                        )
                    except Exception as e:
                        logger.error(f"Error loading model {m[2]}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error loading providers and models: {e}")

    async def create_provider(self, provider: LLMProvider) -> Optional[int]:
        """Create a new LLM provider.

        Args:
            provider: The provider configuration

        Returns:
            The provider ID if successful
        """
        try:
            with self.repository._get_session() as session:
                query = text("""
                    INSERT INTO llm_providers (name, type, api_key, models, status, metadata)
                    VALUES (:name, :type, :api_key, :models, :status, :metadata)
                    RETURNING id
                """)
                result = session.execute(
                    query,
                    {
                        "name": provider.name,
                        "type": provider.type,
                        "api_key": provider.api_key,
                        "models": provider.models,
                        "status": provider.status,
                        "metadata": provider.metadata
                    }
                ).fetchone()
                session.commit()
                
                if result:
                    provider.id = result[0]
                    self._providers[provider.id] = provider
                    return provider.id
        except Exception as e:
            logger.error(f"Error creating provider: {e}")
        return None

    async def create_model(self, model: LLMModel) -> Optional[int]:
        """Create a new LLM model.

        Args:
            model: The model configuration

        Returns:
            The model ID if successful
        """
        try:
            with self.repository._get_session() as session:
                query = text("""
                    INSERT INTO llm_models (provider_id, model_name, capability, params, status, metadata)
                    VALUES (:provider_id, :model_name, :capability, :params, :status, :metadata)
                    RETURNING id
                """)
                result = session.execute(
                    query,
                    {
                        "provider_id": model.provider_id,
                        "model_name": model.model_name,
                        "capability": model.capability,
                        "params": model.params,
                        "status": model.status,
                        "metadata": model.metadata
                    }
                ).fetchone()
                session.commit()
                
                if result:
                    model.id = result[0]
                    self._models[model.id] = model
                    return model.id
        except Exception as e:
            logger.error(f"Error creating model: {e}")
        return None

    async def generate_completion(self, request: LLMRequest) -> Optional[LLMResponse]:
        """Generate a completion using the specified model.

        Args:
            request: The completion request

        Returns:
            The completion response if successful
        """
        try:
            model = self._models.get(request.model_id)
            if not model:
                raise ValueError(f"Model {request.model_id} not found")

            provider = self._providers.get(model.provider_id)
            if not provider:
                raise ValueError(f"Provider for model {request.model_id} not found")

            if provider.type == "openai":
                openai.api_key = provider.api_key
                response = await openai.ChatCompletion.acreate(
                    model=model.model_name,
                    messages=[{"role": "user", "content": request.prompt}],
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    frequency_penalty=request.frequency_penalty,
                    presence_penalty=request.presence_penalty,
                    stop=request.stop,
                    stream=request.stream
                )
                
                return LLMResponse(
                    request_id=str(uuid.uuid4()),
                    model_id=request.model_id,
                    content=response.choices[0].message.content,
                    usage=response.usage,
                    finish_reason=response.choices[0].finish_reason,
                    metadata=request.metadata
                )

            elif provider.type == "anthropic":
                client = anthropic.Client(api_key=provider.api_key)
                response = await client.completion(
                    model=model.model_name,
                    prompt=request.prompt,
                    max_tokens_to_sample=request.max_tokens,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    stop_sequences=request.stop
                )
                
                return LLMResponse(
                    request_id=str(uuid.uuid4()),
                    model_id=request.model_id,
                    content=response.completion,
                    usage={"total_tokens": response.stop_reason},
                    finish_reason=response.stop_reason,
                    metadata=request.metadata
                )

            else:
                raise ValueError(f"Unsupported provider type: {provider.type}")

        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            return None

    async def generate_embeddings(self, request: LLMEmbeddingRequest) -> Optional[LLMEmbeddingResponse]:
        """Generate embeddings using the specified model.

        Args:
            request: The embedding request

        Returns:
            The embedding response if successful
        """
        try:
            model = self._models.get(request.model_id)
            if not model:
                raise ValueError(f"Model {request.model_id} not found")

            provider = self._providers.get(model.provider_id)
            if not provider:
                raise ValueError(f"Provider for model {request.model_id} not found")

            if provider.type == "openai":
                openai.api_key = provider.api_key
                response = await openai.Embedding.acreate(
                    model=model.model_name,
                    input=request.input
                )
                
                return LLMEmbeddingResponse(
                    request_id=str(uuid.uuid4()),
                    model_id=request.model_id,
                    embeddings=[data.embedding for data in response.data],
                    usage=response.usage,
                    metadata=request.metadata
                )

            else:
                raise ValueError(f"Unsupported provider type for embeddings: {provider.type}")

        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return None 