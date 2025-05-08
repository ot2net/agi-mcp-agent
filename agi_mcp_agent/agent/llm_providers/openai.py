"""OpenAI provider implementation."""

import asyncio
import logging
import time
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

import openai
from openai import AsyncOpenAI

from agi_mcp_agent.agent.llm_providers.base import (
    LLMProvider,
    ModelCapability,
    ModelConfig,
    ModelResponse,
    ModelUsage,
)

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """Provider for OpenAI models."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        organization_id: Optional[str] = None,
        api_base: Optional[str] = None,
        api_version: Optional[str] = None,
        **kwargs
    ):
        """Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            organization_id: OpenAI organization ID
            api_base: Base URL for API requests
            api_version: API version
            **kwargs: Additional configuration
        """
        self.organization_id = organization_id
        self.api_base = api_base
        self.api_version = api_version
        
        # Initialize the client
        self.client = AsyncOpenAI(
            api_key=api_key,
            organization=organization_id,
            base_url=api_base,
        )
        
        super().__init__(api_key=api_key, **kwargs)
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available models from OpenAI.
        
        Returns:
            List of model information dictionaries
        """
        # Default available models if we can't fetch from API
        default_models = [
            {
                "id": "gpt-4o",
                "name": "gpt-4o",
                "description": "GPT-4 Omni - Most capable model for a wide range of tasks",
                "max_tokens": 128000,
                "pricing": {"input": 0.00001, "output": 0.00003}
            },
            {
                "id": "gpt-4-turbo",
                "name": "gpt-4-turbo",
                "description": "GPT-4 Turbo - Improved version with broader knowledge cutoff",
                "max_tokens": 128000,
                "pricing": {"input": 0.00001, "output": 0.00003}
            },
            {
                "id": "gpt-4",
                "name": "gpt-4",
                "description": "GPT-4 - Most capable model for complex tasks",
                "max_tokens": 8192,
                "pricing": {"input": 0.00003, "output": 0.00006}
            },
            {
                "id": "gpt-3.5-turbo",
                "name": "gpt-3.5-turbo",
                "description": "GPT-3.5 Turbo - Fast, capable, and cost-effective model",
                "max_tokens": 16384,
                "pricing": {"input": 0.0000015, "output": 0.000002}
            },
            {
                "id": "text-embedding-3-large",
                "name": "text-embedding-3-large",
                "description": "Text embedding large model for semantic search",
                "max_tokens": 8191,
                "pricing": {"input": 0.00000013}
            },
            {
                "id": "text-embedding-3-small",
                "name": "text-embedding-3-small",
                "description": "Text embedding small model for semantic search - efficient and cost-effective",
                "max_tokens": 8191,
                "pricing": {"input": 0.00000003}
            },
        ]
        
        try:
            # Try to get models from the API
            # This requires a synchronous call, which we'll run in a separate thread
            loop = asyncio.get_event_loop()
            response = loop.run_in_executor(None, self._list_models_sync)
            
            # If we get here, we've successfully fetched models from the API
            return response
            
        except Exception as e:
            logger.warning(f"Could not fetch models from OpenAI API: {str(e)}")
            logger.warning("Using default model list")
            return default_models
    
    def _list_models_sync(self) -> List[Dict[str, Any]]:
        """Synchronous version of list_models for running in a thread."""
        client = openai.OpenAI(
            api_key=self.api_key,
            organization=self.organization_id,
            base_url=self.api_base,
        )
        response = client.models.list()
        
        # Convert to our format
        models = []
        for model in response.data:
            # Skip deprecated or non-useful models
            if any(term in model.id for term in ['deprecated', 'instruct', '001', '002', '003']):
                continue
                
            models.append({
                "id": model.id,
                "name": model.id,
                "description": getattr(model, "description", "No description available"),
                "max_tokens": self._get_max_tokens_for_model(model.id),
                "pricing": self._get_pricing_for_model(model.id)
            })
            
        return models
    
    def _get_max_tokens_for_model(self, model_id: str) -> int:
        """Get the maximum tokens for a model.
        
        Args:
            model_id: The model ID
            
        Returns:
            Maximum tokens
        """
        # Default max tokens mapping
        max_tokens_map = {
            "gpt-4o": 128000,
            "gpt-4-turbo": 128000,
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-3.5-turbo": 16384,
            "gpt-3.5-turbo-16k": 16384,
            "text-embedding-3-large": 8191,
            "text-embedding-3-small": 8191,
            "text-embedding-ada-002": 8191,
        }
        
        # Check for exact match first
        if model_id in max_tokens_map:
            return max_tokens_map[model_id]
        
        # Check for partial matches
        for key, value in max_tokens_map.items():
            if key in model_id:
                return value
        
        # Default to 4096 if no match
        return 4096
    
    def _get_pricing_for_model(self, model_id: str) -> Dict[str, float]:
        """Get the pricing for a model.
        
        Args:
            model_id: The model ID
            
        Returns:
            Pricing information
        """
        # Default pricing per 1K tokens
        pricing_map = {
            "gpt-4o": {"input": 0.00001, "output": 0.00003},
            "gpt-4-turbo": {"input": 0.00001, "output": 0.00003},
            "gpt-4": {"input": 0.00003, "output": 0.00006},
            "gpt-4-32k": {"input": 0.00006, "output": 0.00012},
            "gpt-3.5-turbo": {"input": 0.0000015, "output": 0.000002},
            "text-embedding-3-large": {"input": 0.00000013},
            "text-embedding-3-small": {"input": 0.00000003},
            "text-embedding-ada-002": {"input": 0.0000001},
        }
        
        # Check for exact match first
        if model_id in pricing_map:
            return pricing_map[model_id]
        
        # Check for partial matches
        for key, value in pricing_map.items():
            if key in model_id:
                return value
        
        # Default pricing if no match
        return {"input": 0.000002, "output": 0.000002}
    
    def get_capabilities(self) -> List[ModelCapability]:
        """Get the capabilities of OpenAI models.
        
        Returns:
            List of model capabilities
        """
        # Define capabilities
        capabilities = [
            ModelCapability(
                name="text-completion",
                description="Generate text completions",
                supported_models=[
                    "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o", 
                ],
            ),
            ModelCapability(
                name="chat-completion",
                description="Generate chat completions",
                supported_models=[
                    "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o", 
                ],
            ),
            ModelCapability(
                name="embeddings",
                description="Generate embeddings for text",
                supported_models=[
                    "text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large",
                ],
            ),
            ModelCapability(
                name="function-calling",
                description="Call functions defined by the user",
                supported_models=[
                    "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o", 
                ],
            ),
        ]
        
        return capabilities
    
    def validate_api_key(self) -> bool:
        """Validate the OpenAI API key.
        
        Returns:
            Whether the API key is valid
        """
        try:
            # Try to list models as a simple validation
            self._list_models_sync()
            return True
        except Exception as e:
            logger.warning(f"API key validation failed: {str(e)}")
            return False
    
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
        # For OpenAI, we'll use the chat completion API for all text generation
        messages = [{"role": "user", "content": prompt}]
        return await self.generate_chat_completion(messages, model_config, stream)
    
    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model_config: ModelConfig,
        stream: bool = False,
    ) -> Union[ModelResponse, AsyncGenerator[ModelResponse, None]]:
        """Generate a chat completion from the model.
        
        Args:
            messages: List of chat messages
            model_config: Configuration for the model
            stream: Whether to stream the response
            
        Returns:
            Either a ModelResponse or an async generator of ModelResponses if streaming
        """
        # Prepare request parameters
        model_name = model_config.model_name
        max_tokens = model_config.max_tokens
        temperature = model_config.temperature
        top_p = model_config.top_p
        frequency_penalty = model_config.frequency_penalty
        presence_penalty = model_config.presence_penalty
        stop_sequences = model_config.stop_sequences or None
        
        # Record start time for response timing
        start_time = time.time()
        
        try:
            if stream:
                # Handle streaming
                return self._stream_chat_completion(
                    messages=messages,
                    model_name=model_name,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    stop=stop_sequences,
                    start_time=start_time,
                )
            else:
                # Non-streaming request
                response = await self.client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    stop=stop_sequences,
                )
                
                # Calculate response time
                response_time = (time.time() - start_time) * 1000  # ms
                
                # Extract text from the response
                completion_text = response.choices[0].message.content
                
                # Create usage information
                usage = ModelUsage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                    input_cost=self._calculate_cost(
                        model_name, "input", response.usage.prompt_tokens
                    ),
                    output_cost=self._calculate_cost(
                        model_name, "output", response.usage.completion_tokens
                    ),
                )
                usage.total_cost = usage.input_cost + usage.output_cost
                
                # Create and return the model response
                return ModelResponse(
                    text=completion_text,
                    model_name=model_name,
                    provider_name="OpenAI",
                    usage=usage,
                    finish_reason=response.choices[0].finish_reason,
                    raw_response=response.dict(),
                    response_ms=response_time,
                )
                
        except Exception as e:
            logger.error(f"Error in OpenAI completion: {str(e)}")
            raise
    
    async def _stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model_name: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        frequency_penalty: float,
        presence_penalty: float,
        stop: Optional[List[str]] = None,
        start_time: float = None,
    ) -> AsyncGenerator[ModelResponse, None]:
        """Stream a chat completion from the model.
        
        Args:
            messages: List of chat messages
            model_name: Name of the model
            max_tokens: Maximum tokens to generate
            temperature: Temperature for sampling
            top_p: Top P for sampling
            frequency_penalty: Frequency penalty
            presence_penalty: Presence penalty
            stop: Stop sequences
            start_time: Start time for response timing
            
        Yields:
            Model responses as they are generated
        """
        if start_time is None:
            start_time = time.time()
            
        try:
            # Start streaming response
            stream = await self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop,
                stream=True,
            )
            
            # Collect response chunks
            full_text = ""
            finish_reason = None
            usage = ModelUsage()
            
            async for chunk in stream:
                delta = chunk.choices[0].delta
                
                # Get the text from the delta if it exists
                if delta.content:
                    text_chunk = delta.content
                    full_text += text_chunk
                    
                    # Calculate response time
                    response_time = (time.time() - start_time) * 1000  # ms
                    
                    # Create partial usage (we'll update this with the final usage later)
                    # For streaming, we estimate token usage
                    chunk_usage = ModelUsage(
                        prompt_tokens=0,  # Will be updated at the end
                        completion_tokens=len(text_chunk) // 4,  # Rough estimate
                        total_tokens=0,  # Will be updated at the end
                    )
                    
                    # Yield the partial response
                    yield ModelResponse(
                        text=full_text,
                        model_name=model_name,
                        provider_name="OpenAI",
                        usage=chunk_usage,
                        finish_reason=None,  # Will be provided in the final chunk
                        raw_response=None,
                        response_ms=response_time,
                    )
                
                # Update finish reason if present
                if chunk.choices[0].finish_reason:
                    finish_reason = chunk.choices[0].finish_reason
            
            # After streaming is complete, estimate final usage
            # This is an estimate since we don't get exact usage from the API for streaming
            prompt_tokens = sum(len(m["content"]) // 4 for m in messages)  # Rough estimate
            completion_tokens = len(full_text) // 4  # Rough estimate
            total_tokens = prompt_tokens + completion_tokens
            
            usage = ModelUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                input_cost=self._calculate_cost(model_name, "input", prompt_tokens),
                output_cost=self._calculate_cost(model_name, "output", completion_tokens),
            )
            usage.total_cost = usage.input_cost + usage.output_cost
            
            # Calculate final response time
            response_time = (time.time() - start_time) * 1000  # ms
            
            # Yield the final response
            yield ModelResponse(
                text=full_text,
                model_name=model_name,
                provider_name="OpenAI",
                usage=usage,
                finish_reason=finish_reason,
                raw_response=None,
                response_ms=response_time,
            )
            
        except Exception as e:
            logger.error(f"Error in OpenAI streaming completion: {str(e)}")
            raise
    
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
        model_name = model_config.model_name
        
        try:
            response = await self.client.embeddings.create(
                model=model_name,
                input=texts,
            )
            
            # Extract embeddings
            embeddings = [data.embedding for data in response.data]
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error in OpenAI embeddings: {str(e)}")
            raise
    
    def _calculate_cost(self, model_name: str, type_: str, tokens: int) -> float:
        """Calculate the cost for a model call.
        
        Args:
            model_name: Name of the model
            type_: Type of tokens (input or output)
            tokens: Number of tokens
            
        Returns:
            Cost in USD
        """
        pricing = self._get_pricing_for_model(model_name)
        
        # If the model doesn't have separate input/output pricing, use the input pricing
        if type_ not in pricing:
            if "input" in pricing:
                price_per_token = pricing["input"]
            else:
                # Default price if unknown
                price_per_token = 0.000002
        else:
            price_per_token = pricing[type_]
        
        # Calculate cost per 1K tokens
        return (tokens / 1000) * price_per_token 