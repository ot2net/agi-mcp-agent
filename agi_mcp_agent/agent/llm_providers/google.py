"""Google provider implementation for Gemini models."""

import asyncio
import logging
import time
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from agi_mcp_agent.agent.llm_providers.base import (
    LLMProvider,
    ModelCapability,
    ModelConfig,
    ModelResponse,
    ModelUsage,
)

logger = logging.getLogger(__name__)


class GoogleProvider(LLMProvider):
    """Provider for Google Gemini models."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        project_id: Optional[str] = None,
        location: Optional[str] = "us-central1",
        **kwargs,
    ):
        """Initialize the Google Gemini provider.
        
        Args:
            api_key: Google API key
            project_id: Google Cloud project ID (for enterprise tier)
            location: Region for enterprise tier API
            **kwargs: Additional configuration
        """
        self.project_id = project_id
        self.location = location
        
        # Configure the client
        genai.configure(api_key=api_key)
        
        # Initialize clients for different model types
        self.genai = genai
        
        super().__init__(api_key=api_key, **kwargs)
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available models from Google.
        
        Returns:
            List of model information dictionaries
        """
        # Default model definitions in case we can't fetch from API
        default_models = [
            {
                "id": "gemini-1.5-pro",
                "name": "gemini-1.5-pro",
                "description": "Gemini 1.5 Pro - Most capable model for complex tasks",
                "max_tokens": 1000000,
                "pricing": {"input": 0.00000125, "output": 0.00000375}
            },
            {
                "id": "gemini-1.5-flash",
                "name": "gemini-1.5-flash",
                "description": "Gemini 1.5 Flash - Fast and efficient model with lower cost",
                "max_tokens": 1000000,
                "pricing": {"input": 0.0000005, "output": 0.0000015}
            },
            {
                "id": "gemini-1.0-pro",
                "name": "gemini-1.0-pro",
                "description": "Gemini 1.0 Pro - Balanced model for most tasks",
                "max_tokens": 32768,
                "pricing": {"input": 0.000001, "output": 0.000002}
            },
            {
                "id": "gemini-1.0-pro-vision",
                "name": "gemini-1.0-pro-vision",
                "description": "Gemini 1.0 Pro Vision - Specialized for visual tasks",
                "max_tokens": 32768,
                "pricing": {"input": 0.000001, "output": 0.000002}
            },
            {
                "id": "embedding-001",
                "name": "embedding-001",
                "description": "Text embedding model for semantic search",
                "max_tokens": 3072,
                "pricing": {"input": 0.0000002}
            },
        ]
        
        try:
            # Fetch models from the API
            loop = asyncio.get_event_loop()
            models_response = loop.run_in_executor(None, self._list_models_sync)
            
            # Process the results
            models = []
            for model in models_response:
                model_id = model.name
                models.append({
                    "id": model_id,
                    "name": model_id,
                    "description": getattr(model, "description", "No description available"),
                    "max_tokens": self._get_max_tokens_for_model(model_id),
                    "pricing": self._get_pricing_for_model(model_id)
                })
            
            return models
            
        except Exception as e:
            logger.warning(f"Could not fetch models from Google API: {str(e)}")
            logger.warning("Using default model list")
            return default_models
    
    def _list_models_sync(self) -> List[Any]:
        """Synchronous version of list_models for running in a thread."""
        return list(genai.list_models())
    
    def _get_max_tokens_for_model(self, model_id: str) -> int:
        """Get the maximum tokens for a model.
        
        Args:
            model_id: The model ID
            
        Returns:
            Maximum tokens
        """
        # Default max tokens mapping
        max_tokens_map = {
            "gemini-1.5-pro": 1000000,
            "gemini-1.5-flash": 1000000,
            "gemini-1.0-pro": 32768,
            "gemini-1.0-pro-vision": 32768,
            "embedding-001": 3072,
        }
        
        # Check for exact match first
        if model_id in max_tokens_map:
            return max_tokens_map[model_id]
        
        # Check for partial matches
        for key, value in max_tokens_map.items():
            if key in model_id:
                return value
        
        # Default to 32768 if no match
        return 32768
    
    def _get_pricing_for_model(self, model_id: str) -> Dict[str, float]:
        """Get the pricing for a model.
        
        Args:
            model_id: The model ID
            
        Returns:
            Pricing information
        """
        # Pricing per 1M tokens (converted to per token)
        pricing_map = {
            "gemini-1.5-pro": {"input": 0.00000125, "output": 0.00000375},
            "gemini-1.5-flash": {"input": 0.0000005, "output": 0.0000015},
            "gemini-1.0-pro": {"input": 0.000001, "output": 0.000002},
            "gemini-1.0-pro-vision": {"input": 0.000001, "output": 0.000002},
            "embedding-001": {"input": 0.0000002},
        }
        
        # Check for exact match first
        if model_id in pricing_map:
            return pricing_map[model_id]
        
        # Check for partial matches
        for key, value in pricing_map.items():
            if key in model_id:
                return value
        
        # Default pricing if no match
        return {"input": 0.000001, "output": 0.000002}
    
    def get_capabilities(self) -> List[ModelCapability]:
        """Get the capabilities of Google models.
        
        Returns:
            List of model capabilities
        """
        # Define capabilities
        capabilities = [
            ModelCapability(
                name="text-completion",
                description="Generate text completions",
                supported_models=[
                    "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro", 
                ],
            ),
            ModelCapability(
                name="chat-completion",
                description="Generate chat completions",
                supported_models=[
                    "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro", 
                ],
            ),
            ModelCapability(
                name="embeddings",
                description="Generate embeddings for text",
                supported_models=[
                    "embedding-001",
                ],
            ),
            ModelCapability(
                name="vision",
                description="Process images and generate descriptions",
                supported_models=[
                    "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro-vision",
                ],
            ),
            ModelCapability(
                name="function-calling",
                description="Call functions defined by the user",
                supported_models=[
                    "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro",
                ],
            ),
        ]
        
        return capabilities
    
    def validate_api_key(self) -> bool:
        """Validate the Google API key.
        
        Returns:
            Whether the API key is valid
        """
        try:
            # Try to list models as a simple validation
            models = self._list_models_sync()
            return len(models) > 0
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
        # For Google, we'll use the chat API for all text generation
        messages = [{"role": "user", "parts": [{"text": prompt}]}]
        return await self.generate_chat_completion(messages, model_config, stream)
    
    async def generate_chat_completion(
        self,
        messages: List[Dict[str, Any]],
        model_config: ModelConfig,
        stream: bool = False,
    ) -> Union[ModelResponse, AsyncGenerator[ModelResponse, None]]:
        """Generate a chat completion from the model.
        
        Args:
            messages: List of chat messages in Google format
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
        
        # Convert messages to Google format if needed
        google_messages = []
        for message in messages:
            role = message.get("role", "user")
            
            # Check if message is already in Google format
            if "parts" in message:
                google_messages.append(message)
                continue
                
            # Convert from OpenAI format
            content = message.get("content", "")
            google_role = "user" if role == "user" else "model"
            google_messages.append({
                "role": google_role,
                "parts": [{"text": content}]
            })
        
        # Create generation config
        generation_config = GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_tokens,
            # No direct equivalent for frequency_penalty and presence_penalty
        )
        
        # Record start time for response timing
        start_time = time.time()
        
        try:
            # Initialize the model
            loop = asyncio.get_event_loop()
            model = await loop.run_in_executor(
                None,
                lambda: genai.GenerativeModel(model_name=model_name)
            )
            
            if stream:
                # Handle streaming
                return self._stream_chat_completion(
                    model=model,
                    messages=google_messages,
                    generation_config=generation_config,
                    model_name=model_name,
                    start_time=start_time,
                )
            else:
                # Generate content (non-streaming)
                chat_session = await loop.run_in_executor(
                    None,
                    lambda: model.start_chat(history=google_messages[:-1])
                )
                
                # Send the last message
                last_message = google_messages[-1]
                response = await loop.run_in_executor(
                    None,
                    lambda: chat_session.send_message(
                        last_message["parts"][0]["text"],
                        generation_config=generation_config
                    )
                )
                
                # Calculate response time
                response_time = (time.time() - start_time) * 1000  # ms
                
                # Extract text from the response
                completion_text = response.text
                
                # Estimate token usage
                prompt_text = "\n".join([m.get("parts", [{}])[0].get("text", "") for m in google_messages])
                prompt_tokens = len(prompt_text.split()) * 1.3  # Rough estimate
                completion_tokens = len(completion_text.split()) * 1.3  # Rough estimate
                total_tokens = prompt_tokens + completion_tokens
                
                # Create usage information
                usage = ModelUsage(
                    prompt_tokens=int(prompt_tokens),
                    completion_tokens=int(completion_tokens),
                    total_tokens=int(total_tokens),
                    input_cost=self._calculate_cost(
                        model_name, "input", int(prompt_tokens)
                    ),
                    output_cost=self._calculate_cost(
                        model_name, "output", int(completion_tokens)
                    ),
                )
                usage.total_cost = usage.input_cost + usage.output_cost
                
                # Create response object
                return ModelResponse(
                    text=completion_text,
                    model_name=model_name,
                    provider_name="Google",
                    usage=usage,
                    finish_reason="stop",  # Google doesn't provide this directly
                    raw_response=response._result,
                    response_ms=response_time,
                )
                
        except Exception as e:
            logger.error(f"Error in Google completion: {str(e)}")
            raise
    
    async def _stream_chat_completion(
        self,
        model,
        messages: List[Dict[str, Any]],
        generation_config: GenerationConfig,
        model_name: str,
        start_time: float = None,
    ) -> AsyncGenerator[ModelResponse, None]:
        """Stream a chat completion from the model.
        
        Args:
            model: The Gemini model instance
            messages: List of chat messages
            generation_config: The generation configuration
            model_name: Name of the model
            start_time: Start time for response timing
            
        Yields:
            Model responses as they are generated
        """
        if start_time is None:
            start_time = time.time()
            
        try:
            loop = asyncio.get_event_loop()
            
            # Create chat session with history
            chat_session = await loop.run_in_executor(
                None,
                lambda: model.start_chat(history=messages[:-1])
            )
            
            # Start streaming response for the last message
            last_message = messages[-1]
            response_stream = await loop.run_in_executor(
                None,
                lambda: chat_session.send_message(
                    last_message["parts"][0]["text"],
                    generation_config=generation_config,
                    stream=True
                )
            )
            
            # Collect response chunks
            full_text = ""
            
            # Estimate token usage for the prompt
            prompt_text = "\n".join([m.get("parts", [{}])[0].get("text", "") for m in messages])
            prompt_tokens = int(len(prompt_text.split()) * 1.3)  # Rough estimate
            output_tokens = 0
            
            for chunk in response_stream:
                if hasattr(chunk, 'text') and chunk.text:
                    # Estimate token count for this chunk
                    chunk_tokens = int(len(chunk.text.split()) * 1.3)  # Rough estimate
                    output_tokens += chunk_tokens
                    
                    full_text += chunk.text
                    
                    # Calculate response time
                    response_time = (time.time() - start_time) * 1000  # ms
                    
                    # Create partial usage
                    chunk_usage = ModelUsage(
                        prompt_tokens=prompt_tokens,
                        completion_tokens=output_tokens,
                        total_tokens=prompt_tokens + output_tokens,
                        input_cost=self._calculate_cost(model_name, "input", prompt_tokens),
                        output_cost=self._calculate_cost(model_name, "output", output_tokens),
                    )
                    chunk_usage.total_cost = chunk_usage.input_cost + chunk_usage.output_cost
                    
                    # Yield the partial response
                    yield ModelResponse(
                        text=full_text,
                        model_name=model_name,
                        provider_name="Google",
                        usage=chunk_usage,
                        finish_reason=None,
                        raw_response=None,
                        response_ms=response_time,
                    )
            
            # Calculate final response time
            response_time = (time.time() - start_time) * 1000  # ms
            
            # Create final usage information
            usage = ModelUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=output_tokens,
                total_tokens=prompt_tokens + output_tokens,
                input_cost=self._calculate_cost(model_name, "input", prompt_tokens),
                output_cost=self._calculate_cost(model_name, "output", output_tokens),
            )
            usage.total_cost = usage.input_cost + usage.output_cost
            
            # Yield the final response
            yield ModelResponse(
                text=full_text,
                model_name=model_name,
                provider_name="Google",
                usage=usage,
                finish_reason="stop",  # Google doesn't provide this directly
                raw_response=None,
                response_ms=response_time,
            )
            
        except Exception as e:
            logger.error(f"Error in Google streaming completion: {str(e)}")
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
            # Initialize the embedding model
            loop = asyncio.get_event_loop()
            embedding_model = await loop.run_in_executor(
                None, 
                lambda: genai.get_embedding_model(model_name)
            )
            
            # Generate embeddings
            embeddings = []
            for text in texts:
                embedding = await loop.run_in_executor(
                    None,
                    lambda: embedding_model.embed_content(text)
                )
                embeddings.append(embedding.values)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error in Google embeddings: {str(e)}")
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
                price_per_token = 0.000001
        else:
            price_per_token = pricing[type_]
        
        # Calculate cost
        return (tokens / 1000) * price_per_token 