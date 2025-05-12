"""LLM (Large Language Model) service layer."""

import logging
import uuid
import traceback
import sys
import time
import json
from typing import Dict, List, Optional, Any, Union
import openai
import anthropic
from sqlalchemy import text
from datetime import datetime
from pydantic import BaseModel

from agi_mcp_agent.mcp.llm_models import (
    LLMProvider, LLMModel, LLMRequest, LLMResponse,
    LLMEmbeddingRequest, LLMEmbeddingResponse
)
from agi_mcp_agent.mcp.repository import MCPRepository, sanitize_for_json

logger = logging.getLogger(__name__)

# 添加JSON编码器用于处理datetime对象
class DateTimeEncoder(json.JSONEncoder):
    """JSON编码器，用于处理datetime对象。"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class LLMService:
    """Service for handling LLM operations."""

    def __init__(self, repository: MCPRepository):
        """Initialize the LLM service.

        Args:
            repository: The MCP repository instance
        """
        logger.info("Initializing LLMService")
        start_time = time.time()
        
        self.repository = repository
        self._providers: Dict[int, LLMProvider] = {}
        self._models: Dict[int, LLMModel] = {}
        
        # Try to initialize providers and models
        try:
            logger.info("Loading providers and models from database")
            self._load_providers_and_models()
            logger.info(f"Initialized LLMService in {time.time() - start_time:.2f} seconds")
            logger.info(f"Loaded {len(self._providers)} providers and {len(self._models)} models")
        except Exception as e:
            logger.error(f"Failed to initialize LLMService: {str(e)}")
            logger.error(traceback.format_exc())
            # Continue with empty collections
            self._providers = {}
            self._models = {}

    def _load_providers_and_models(self):
        """Load all providers and models from the database."""
        with self.repository._get_session() as session:
            try:
                logger.debug("Querying for enabled providers")
                providers_query = text("""
                    SELECT id, name, type, api_key, models, status, metadata
                    FROM llm_providers
                    WHERE status = 'enabled' OR COALESCE(is_enabled, true) = true
                """)
                providers = session.execute(providers_query).fetchall()
                logger.debug(f"Found {len(providers)} providers")
                
                for p in providers:
                    try:
                        # Extract fields
                        provider_id = p[0]
                        provider_name = p[1]
                        provider_type = p[2]
                        api_key = p[3]
                        models_data = p[4]
                        status = p[5]
                        metadata = p[6]
                        
                        logger.debug(f"Processing provider: {provider_name} (ID: {provider_id})")
                        
                        # Handle models field (could be PostgreSQL array, JSON string, Python list, or None)
                        provider_models = []
                        if models_data:
                            logger.debug(f"Models data type: {type(models_data)}")
                            # PostgreSQL array comes as a list
                            if isinstance(models_data, list):
                                provider_models = models_data
                                logger.debug(f"Using PostgreSQL array directly: {provider_models}")
                            # JSON string needs parsing
                            elif isinstance(models_data, str):
                                try:
                                    # Try to parse as JSON
                                    provider_models = json.loads(models_data)
                                    logger.debug(f"Parsed models from JSON string: {provider_models}")
                                except json.JSONDecodeError as e:
                                    logger.warning(f"Failed to parse models JSON for provider {provider_id}: {e}")
                                    # Treat as list with one model
                                    provider_models = [models_data]
                            else:
                                logger.warning(f"Unexpected models data type: {type(models_data)} for provider {provider_id}")
                        
                        # Handle metadata field (could be JSON string, dict, or None)
                        provider_metadata = {}
                        if metadata:
                            logger.debug(f"Metadata type: {type(metadata)}")
                            if isinstance(metadata, str):
                                try:
                                    # Try to parse as JSON
                                    provider_metadata = json.loads(metadata)
                                except json.JSONDecodeError:
                                    logger.warning(f"Failed to parse metadata JSON for provider {provider_id}")
                            elif isinstance(metadata, dict):
                                provider_metadata = metadata
                        
                        # Create provider object
                        self._providers[provider_id] = LLMProvider(
                            id=provider_id,
                            name=provider_name,
                            type=provider_type,
                            api_key=api_key,
                            models=provider_models,
                            status=status,
                            metadata=provider_metadata
                        )
                        logger.debug(f"Added provider {provider_name} to service")
                    except Exception as e:
                        logger.error(f"Error loading provider: {str(e)}")
                        logger.error(traceback.format_exc())
                        continue
                
                logger.debug(f"Loaded {len(self._providers)} providers, now loading models")
                
                # Query for models
                models_query = text("""
                    SELECT 
                        id, provider_id, model_name, capability, params, status, metadata
                    FROM llm_models
                    WHERE status = 'enabled' OR COALESCE(is_enabled, true) = true
                """)
                models = session.execute(models_query).fetchall()
                logger.debug(f"Found {len(models)} models")
                
                for m in models:
                    try:
                        # Extract fields
                        model_id = m[0]
                        provider_id = m[1]
                        model_name = m[2]
                        capability = m[3]
                        params_data = m[4]
                        status = m[5]
                        metadata = m[6]
                        
                        logger.debug(f"Processing model: {model_name} (ID: {model_id})")
                        
                        # Skip if provider doesn't exist
                        if provider_id not in self._providers:
                            logger.warning(f"Skipping model {model_name}: provider {provider_id} not found")
                            continue
                        
                        # Handle params field (could be JSON string, dict, or None)
                        model_params = {}
                        if params_data:
                            logger.debug(f"Params data type: {type(params_data)}")
                            if isinstance(params_data, str):
                                try:
                                    # Try to parse as JSON
                                    model_params = json.loads(params_data)
                                except json.JSONDecodeError:
                                    logger.warning(f"Failed to parse params JSON for model {model_id}")
                            elif isinstance(params_data, dict):
                                model_params = params_data
                        
                        # Handle metadata field (could be JSON string, dict, or None)
                        model_metadata = {}
                        if metadata:
                            logger.debug(f"Metadata type: {type(metadata)}")
                            if isinstance(metadata, str):
                                try:
                                    # Try to parse as JSON
                                    model_metadata = json.loads(metadata)
                                except json.JSONDecodeError:
                                    logger.warning(f"Failed to parse metadata JSON for model {model_id}")
                            elif isinstance(metadata, dict):
                                model_metadata = metadata
                        
                        # Create model object
                        self._models[model_id] = LLMModel(
                            id=model_id,
                            provider_id=provider_id,
                            model_name=model_name,
                            capability=capability,
                            params=model_params,
                            status=status,
                            metadata=model_metadata
                        )
                        logger.debug(f"Added model {model_name} to service")
                    except Exception as e:
                        logger.error(f"Error loading model: {str(e)}")
                        logger.error(traceback.format_exc())
                        continue
                
                logger.info(f"Loaded {len(self._providers)} providers and {len(self._models)} models")
                
            except Exception as e:
                logger.error(f"Error loading providers and models: {str(e)}")
                logger.error(traceback.format_exc())
                # Don't let initialization failure crash the service
                # Just continue with empty collections
                self._providers = {}
                self._models = {}

    def _convert_list_to_pg_array(self, python_list: List) -> str:
        """Convert a Python list to a PostgreSQL array literal.
        
        Args:
            python_list: The Python list to convert
            
        Returns:
            A string in PostgreSQL array literal format
        """
        if not python_list:
            return "{}"
            
        # Create PostgreSQL array literal
        pg_array = "{"
        for i, item in enumerate(python_list):
            if i > 0:
                pg_array += ","
            # Escape item if needed
            item_str = str(item)
            if '"' in item_str or '\\' in item_str or ',' in item_str:
                # Double backslashes and double quotes for PostgreSQL
                escaped_item = item_str.replace('\\', '\\\\').replace('"', '\\"')
                pg_array += f'"{escaped_item}"'
            else:
                pg_array += f'"{item_str}"'
        pg_array += "}"
        
        return pg_array

    async def create_provider(self, provider: LLMProvider) -> Optional[int]:
        """Create a new LLM provider.

        Args:
            provider: The provider configuration to create

        Returns:
            The provider's ID, if successful
        """
        try:
            with self.repository._get_session() as session:
                # Convert models to PostgreSQL array format if models is not None
                models_array = self._convert_list_to_pg_array(provider.models) if provider.models else None
                
                # Sanitize metadata to handle datetime objects
                sanitized_metadata = sanitize_for_json(provider.metadata) if provider.metadata else None
                
                # Convert metadata to JSON
                metadata_json = json.dumps(sanitized_metadata) if sanitized_metadata else None
                
                # Use text format for direct parameters
                query = text("""
                    INSERT INTO llm_providers (name, type, api_key, models, status, metadata)
                    VALUES (:name, :type, :api_key, :models, :status, :metadata)
                    RETURNING id
                """)
                
                # Execute with parameter mapping
                result = session.execute(
                    query,
                    {
                        "name": provider.name,
                        "type": provider.type,
                        "api_key": provider.api_key,
                        "models": models_array,
                        "status": provider.status,
                        "metadata": metadata_json
                    }
                ).fetchone()
                session.commit()
                
                if result:
                    provider.id = result[0]
                    self._providers[provider.id] = provider
                    return provider.id
        except Exception as e:
            logger.error(f"Error creating provider: {e}")
            logger.error(traceback.format_exc())
        return None

    async def create_model(self, model: LLMModel) -> Optional[int]:
        """Create a new LLM model.

        Args:
            model: The model configuration to create

        Returns:
            The model's ID, if successful
        """
        try:
            with self.repository._get_session() as session:
                # Sanitize data to handle datetime objects
                sanitized_params = sanitize_for_json(model.params) if model.params else None
                sanitized_metadata = sanitize_for_json(model.metadata) if model.metadata else None
                
                # Convert params and metadata to JSON
                params_json = json.dumps(sanitized_params) if sanitized_params else None
                metadata_json = json.dumps(sanitized_metadata) if sanitized_metadata else None
                
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
                        "params": params_json,
                        "status": model.status,
                        "metadata": metadata_json
                    }
                ).fetchone()
                session.commit()
                
                if result:
                    model.id = result[0]
                    self._models[model.id] = model
                    return model.id
        except Exception as e:
            logger.error(f"Error creating model: {e}")
            logger.error(traceback.format_exc())
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
            logger.error(traceback.format_exc())
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
            logger.error(traceback.format_exc())
            return None 