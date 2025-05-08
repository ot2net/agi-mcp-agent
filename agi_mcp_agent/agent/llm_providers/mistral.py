"""Mistral AI provider implementation."""

import asyncio
import logging
import time
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

import mistralai
from mistralai.async_client import MistralAsyncClient
from mistralai.models.chat_completion import ChatMessage

from agi_mcp_agent.agent.llm_providers.base import (
    LLMProvider,
    ModelCapability,
    ModelConfig,
    ModelResponse,
    ModelUsage,
)

logger = logging.getLogger(__name__)


class MistralProvider(LLMProvider):
    """Provider for Mistral AI models."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        **kwargs,
    ):
        """Initialize the Mistral provider.
        
        Args:
            api_key: Mistral API key
            **kwargs: Additional configuration
        """
        # Initialize the client
        self.client = MistralAsyncClient(api_key=api_key)
        
        super().__init__(api_key=api_key, **kwargs)
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available models from Mistral.
        
        Returns:
            List of model information dictionaries
        """
        # Define available models
        models = [
            {
                "id": "mistral-large-latest",
                "name": "mistral-large",
                "description": "Mistral Large - Most powerful model from Mistral AI",
                "max_tokens": 32768,
                "pricing": {"input": 0.00000381, "output": 0.00001143}
            },
            {
                "id": "mistral-medium-latest",
                "name": "mistral-medium",
                "description": "Mistral Medium - Balanced model for general use",
                "max_tokens": 32768,
                "pricing": {"input": 0.00000127, "output": 0.00000381}
            },
            {
                "id": "mistral-small-latest",
                "name": "mistral-small",
                "description": "Mistral Small - Cost-effective model",
                "max_tokens": 32768,
                "pricing": {"input": 0.00000064, "output": 0.00000190}
            },
            {
                "id": "open-mistral-7b",
                "name": "open-mistral-7b",
                "description": "Open Mistral 7B - Open-source 7B parameter model",
                "max_tokens": 32768,
                "pricing": {"input": 0.00000025, "output": 0.00000025}
            },
            {
                "id": "open-mixtral-8x7b",
                "name": "open-mixtral-8x7b",
                "description": "Open Mixtral 8x7B - Open-source mixture of experts model",
                "max_tokens": 32768,
                "pricing": {"input": 0.00000060, "output": 0.00000060}
            },
            {
                "id": "mistral-embed",
                "name": "mistral-embed",
                "description": "Mistral Embedding model for semantic search",
                "max_tokens": 8192,
                "pricing": {"input": 0.00000010}
            },
        ]
        
        try:
            # Try to get models from the API
            loop = asyncio.get_event_loop()
            response = loop.run_until_complete(self.client.list_models())
            
            # If successful, add any new models that might not be in our default list
            api_models = {model.id for model in response.data}
            default_models = {model["id"] for model in models}
            
            # Add any new models found in the API
            for model_id in api_models:
                if model_id not in default_models:
                    models.append({
                        "id": model_id,
                        "name": model_id,
                        "description": f"Mistral AI model: {model_id}",
                        "max_tokens": 32768,  # Default
                        "pricing": {"input": 0.000001, "output": 0.000002}  # Default pricing
                    })
            
            return models
            
        except Exception as e:
            logger.warning(f"Could not fetch models from Mistral API: {str(e)}")
            logger.warning("Using default model list")
            return models
    
    def get_capabilities(self) -> List[ModelCapability]:
        """Get the capabilities of Mistral models.
        
        Returns:
            List of model capabilities
        """
        # Define capabilities
        capabilities = [
            ModelCapability(
                name="text-completion",
                description="Generate text completions",
                supported_models=[
                    "mistral-large", "mistral-medium", "mistral-small",
                    "open-mistral-7b", "open-mixtral-8x7b"
                ],
            ),
            ModelCapability(
                name="chat-completion",
                description="Generate chat completions",
                supported_models=[
                    "mistral-large", "mistral-medium", "mistral-small",
                    "open-mistral-7b", "open-mixtral-8x7b"
                ],
            ),
            ModelCapability(
                name="embeddings",
                description="Generate embeddings for text",
                supported_models=[
                    "mistral-embed",
                ],
            ),
            ModelCapability(
                name="function-calling",
                description="Call functions defined by the user",
                supported_models=[
                    "mistral-large", "mistral-medium",
                ],
            ),
        ]
        
        return capabilities
    
    def validate_api_key(self) -> bool:
        """Validate the Mistral API key.
        
        Returns:
            Whether the API key is valid
        """
        try:
            # Try to list models as a simple validation
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.client.list_models())
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
        # For Mistral, we'll use chat completion for all text generation
        messages = [ChatMessage(role="user", content=prompt)]
        return await self.generate_chat_completion(messages, model_config, stream)
    
    async def generate_chat_completion(
        self,
        messages: List[Any],
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
        
        # Convert messages to Mistral format if needed
        mistral_messages = []
        for message in messages:
            if isinstance(message, ChatMessage):
                mistral_messages.append(message)
                continue
                
            # Handle dict format
            if isinstance(message, dict):
                role = message.get("role", "user")
                content = message.get("content", "")
                mistral_messages.append(ChatMessage(role=role, content=content))
        
        # Record start time for response timing
        start_time = time.time()
        
        try:
            if stream:
                # Handle streaming
                return self._stream_chat_completion(
                    messages=mistral_messages,
                    model_name=model_name,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    start_time=start_time,
                )
            else:
                # Non-streaming request
                response = await self.client.chat(
                    model=model_name,
                    messages=mistral_messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
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
                    provider_name="Mistral",
                    usage=usage,
                    finish_reason=response.choices[0].finish_reason,
                    raw_response=response.model_dump(),
                    response_ms=response_time,
                )
                
        except Exception as e:
            logger.error(f"Error in Mistral completion: {str(e)}")
            raise
    
    async def _stream_chat_completion(
        self,
        messages: List[ChatMessage],
        model_name: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        start_time: float = None,
    ) -> AsyncGenerator[ModelResponse, None]:
        """Stream a chat completion from the model.
        
        Args:
            messages: List of chat messages
            model_name: Name of the model
            max_tokens: Maximum tokens to generate
            temperature: Temperature for sampling
            top_p: Top P for sampling
            start_time: Start time for response timing
            
        Yields:
            Model responses as they are generated
        """
        if start_time is None:
            start_time = time.time()
            
        try:
            # Start streaming response
            stream = await self.client.chat_stream(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
            )
            
            # Collect response chunks
            full_text = ""
            finish_reason = None
            
            # Track token counts for final usage calculation
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0
            first_chunk = True
            
            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    text_chunk = delta.content
                    full_text += text_chunk
                    
                    # Update token counts if available in the first chunk
                    if first_chunk and hasattr(chunk, 'usage'):
                        prompt_tokens = chunk.usage.prompt_tokens
                        first_chunk = False
                    
                    # Estimate completion tokens based on text length (rough approximation)
                    chunk_tokens = len(text_chunk.split()) // 4 or 1
                    completion_tokens += chunk_tokens
                    
                    # Calculate response time
                    response_time = (time.time() - start_time) * 1000  # ms
                    
                    # Create partial usage
                    chunk_usage = ModelUsage(
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=prompt_tokens + completion_tokens,
                        input_cost=self._calculate_cost(model_name, "input", prompt_tokens),
                        output_cost=self._calculate_cost(model_name, "output", completion_tokens),
                    )
                    chunk_usage.total_cost = chunk_usage.input_cost + chunk_usage.output_cost
                    
                    # Yield the partial response
                    yield ModelResponse(
                        text=full_text,
                        model_name=model_name,
                        provider_name="Mistral",
                        usage=chunk_usage,
                        finish_reason=None,  # Will be provided in the final chunk
                        raw_response=None,
                        response_ms=response_time,
                    )
                
                # Update finish reason if present
                if chunk.choices[0].finish_reason:
                    finish_reason = chunk.choices[0].finish_reason
            
            # If we didn't get prompt tokens from the API, estimate them
            if prompt_tokens == 0:
                prompt_tokens = sum(len(m.content.split()) for m in messages) 
            
            total_tokens = prompt_tokens + completion_tokens
            
            # Create final usage information
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
                provider_name="Mistral",
                usage=usage,
                finish_reason=finish_reason,
                raw_response=None,
                response_ms=response_time,
            )
            
        except Exception as e:
            logger.error(f"Error in Mistral streaming completion: {str(e)}")
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
        model_name = model_config.model_name or "mistral-embed"
        
        try:
            # Generate embeddings
            response = await self.client.embeddings(
                model=model_name,
                input=texts,
            )
            
            # Extract embeddings
            embeddings = [data.embedding for data in response.data]
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error in Mistral embeddings: {str(e)}")
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
        # Pricing per token
        pricing_map = {
            "mistral-large": {"input": 0.00000381, "output": 0.00001143},
            "mistral-medium": {"input": 0.00000127, "output": 0.00000381},
            "mistral-small": {"input": 0.00000064, "output": 0.00000190},
            "open-mistral-7b": {"input": 0.00000025, "output": 0.00000025},
            "open-mixtral-8x7b": {"input": 0.00000060, "output": 0.00000060},
            "mistral-embed": {"input": 0.00000010},
        }
        
        # Get the base model name without version
        base_model = model_name.split("-latest")[0] if "-latest" in model_name else model_name
        
        # Check for exact match first
        if base_model in pricing_map:
            pricing = pricing_map[base_model]
        else:
            # Default pricing if no match
            logger.warning(f"Unknown model for pricing: {model_name}, using default pricing")
            pricing = {"input": 0.000001, "output": 0.000002}
        
        # If the model doesn't have separate input/output pricing, use the input pricing
        if type_ not in pricing:
            if "input" in pricing:
                price_per_token = pricing["input"]
            else:
                # Default price if unknown
                price_per_token = 0.000001
        else:
            price_per_token = pricing[type_]
        
        # Calculate cost
        return tokens * price_per_token