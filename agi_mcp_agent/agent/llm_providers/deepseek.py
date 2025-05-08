"""DeepSeek provider implementation."""

import asyncio
import logging
import time
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

import aiohttp
import json

from agi_mcp_agent.agent.llm_providers.base import (
    LLMProvider,
    ModelCapability,
    ModelConfig,
    ModelResponse,
    ModelUsage,
)

logger = logging.getLogger(__name__)


class DeepSeekProvider(LLMProvider):
    """Provider for DeepSeek models."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        api_base: Optional[str] = None,
        **kwargs
    ):
        """Initialize the DeepSeek provider.
        
        Args:
            api_key: DeepSeek API key
            api_base: Base URL for API requests
            **kwargs: Additional configuration
        """
        self.api_base = api_base or "https://api.deepseek.com/v1"
        
        super().__init__(api_key=api_key, **kwargs)
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available models from DeepSeek.
        
        Returns:
            List of model information dictionaries
        """
        # Default available models
        default_models = [
            {
                "id": "deepseek-chat",
                "name": "deepseek-chat",
                "description": "DeepSeek Chat - General purpose chat model",
                "max_tokens": 8192,
                "pricing": {"input": 0.0000025, "output": 0.000005}
            },
            {
                "id": "deepseek-coder",
                "name": "deepseek-coder",
                "description": "DeepSeek Coder - Specialized in code generation",
                "max_tokens": 8192,
                "pricing": {"input": 0.000002, "output": 0.000009}
            },
            {
                "id": "deepseek-chat-v2",
                "name": "deepseek-chat-v2",
                "description": "DeepSeek Chat v2 - Improved general purpose chat model",
                "max_tokens": 16384,
                "pricing": {"input": 0.000003, "output": 0.000006}
            },
            {
                "id": "deepseek-embedding",
                "name": "deepseek-embedding",
                "description": "DeepSeek Embedding - Text embeddings model",
                "max_tokens": 8192,
                "pricing": {"input": 0.0000001}
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
            logger.warning(f"Could not fetch models from DeepSeek API: {str(e)}")
            logger.warning("Using default model list")
            return default_models
    
    def _list_models_sync(self) -> List[Dict[str, Any]]:
        """Synchronous version of list_models for running in a thread.
        
        Note: DeepSeek API might not provide a list models endpoint, so this is a placeholder.
        """
        # This is a placeholder as DeepSeek might not have a list models endpoint
        # In a real implementation, you'd make the API call here
        return [
            {
                "id": "deepseek-chat",
                "name": "deepseek-chat",
                "description": "DeepSeek Chat - General purpose chat model",
                "max_tokens": 8192,
                "pricing": {"input": 0.0000025, "output": 0.000005}
            },
            {
                "id": "deepseek-coder",
                "name": "deepseek-coder",
                "description": "DeepSeek Coder - Specialized in code generation",
                "max_tokens": 8192,
                "pricing": {"input": 0.000002, "output": 0.000009}
            },
            {
                "id": "deepseek-chat-v2",
                "name": "deepseek-chat-v2",
                "description": "DeepSeek Chat v2 - Improved general purpose chat model",
                "max_tokens": 16384,
                "pricing": {"input": 0.000003, "output": 0.000006}
            },
            {
                "id": "deepseek-embedding",
                "name": "deepseek-embedding",
                "description": "DeepSeek Embedding - Text embeddings model",
                "max_tokens": 8192,
                "pricing": {"input": 0.0000001}
            },
        ]
    
    def get_capabilities(self) -> List[ModelCapability]:
        """Get the capabilities of DeepSeek models.
        
        Returns:
            List of model capabilities
        """
        # Define capabilities
        capabilities = [
            ModelCapability(
                name="text-completion",
                description="Generate text completions",
                supported_models=[
                    "deepseek-chat", "deepseek-chat-v2", "deepseek-coder",
                ],
            ),
            ModelCapability(
                name="chat-completion",
                description="Generate chat completions",
                supported_models=[
                    "deepseek-chat", "deepseek-chat-v2", "deepseek-coder",
                ],
            ),
            ModelCapability(
                name="embeddings",
                description="Generate embeddings for text",
                supported_models=[
                    "deepseek-embedding",
                ],
            ),
            ModelCapability(
                name="function-calling",
                description="Call functions defined by the user",
                supported_models=[
                    "deepseek-chat-v2",
                ],
            ),
        ]
        
        return capabilities
    
    def validate_api_key(self) -> bool:
        """Validate the API key.
        
        Returns:
            Whether the API key is valid
        """
        if not self.api_key:
            return False
            
        try:
            # Make a simple API call to validate the key
            # We'll just call the models endpoint which should be fast
            loop = asyncio.get_event_loop()
            response = loop.run_in_executor(None, self._validate_api_key_sync)
            return response
        except Exception as e:
            logger.error(f"Error validating DeepSeek API key: {str(e)}")
            return False
    
    def _validate_api_key_sync(self) -> bool:
        """Synchronous version of validate_api_key for running in a thread."""
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            # Simple API call to check if the key is valid
            response = requests.get(
                f"{self.api_base}/models",
                headers=headers,
                timeout=5,
            )
            
            return response.status_code == 200
        except Exception:
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
        # For DeepSeek, we'll convert this to a chat completion with a single user message
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        return await self.generate_chat_completion(
            messages=messages,
            model_config=model_config,
            stream=stream,
        )
    
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
        start_time = time.time()
        
        if stream:
            return self._stream_chat_completion(
                messages=messages,
                model_name=model_config.model_name,
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature,
                top_p=model_config.top_p,
                frequency_penalty=model_config.frequency_penalty,
                presence_penalty=model_config.presence_penalty,
                stop=model_config.stop_sequences,
                start_time=start_time,
            )
        
        url = f"{self.api_base}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": model_config.model_name,
            "messages": messages,
            "max_tokens": model_config.max_tokens,
            "temperature": model_config.temperature,
            "top_p": model_config.top_p,
            "frequency_penalty": model_config.frequency_penalty,
            "presence_penalty": model_config.presence_penalty,
        }
        
        if model_config.stop_sequences:
            payload["stop"] = model_config.stop_sequences
            
        # Add any additional config options
        for key, value in model_config.additional_config.items():
            if key not in payload:
                payload[key] = value
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"DeepSeek API error: {error_text}")
                        raise Exception(f"DeepSeek API returned {response.status}: {error_text}")
                    
                    data = await response.json()
                    
                    # Extract the completion text
                    completion_text = data["choices"][0]["message"]["content"]
                    
                    # Extract usage information
                    usage_data = data.get("usage", {})
                    usage = ModelUsage(
                        prompt_tokens=usage_data.get("prompt_tokens", 0),
                        completion_tokens=usage_data.get("completion_tokens", 0),
                        total_tokens=usage_data.get("total_tokens", 0),
                        input_cost=self._calculate_cost(model_config.model_name, "input", usage_data.get("prompt_tokens", 0)),
                        output_cost=self._calculate_cost(model_config.model_name, "output", usage_data.get("completion_tokens", 0)),
                    )
                    
                    # Calculate total cost
                    usage.total_cost = usage.input_cost + usage.output_cost
                    
                    return ModelResponse(
                        text=completion_text,
                        model_name=model_config.model_name,
                        provider_name=self.provider_name,
                        usage=usage,
                        finish_reason=data["choices"][0].get("finish_reason"),
                        raw_response=data,
                        response_ms=(time.time() - start_time) * 1000,
                    )
                    
        except Exception as e:
            logger.error(f"Error generating chat completion from DeepSeek: {str(e)}")
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
            temperature: Temperature for generation
            top_p: Top-p sampling parameter
            frequency_penalty: Frequency penalty
            presence_penalty: Presence penalty
            stop: List of stop sequences
            start_time: Start time for response timing
            
        Yields:
            Streaming model responses
        """
        if start_time is None:
            start_time = time.time()
            
        url = f"{self.api_base}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "stream": True,
        }
        
        if stop:
            payload["stop"] = stop
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"DeepSeek API error: {error_text}")
                        raise Exception(f"DeepSeek API returned {response.status}: {error_text}")
                    
                    # For streaming responses, we need to handle Server-Sent Events (SSE)
                    # Initialize variables for tracking the stream
                    buffer = ""
                    completion_text = ""
                    finish_reason = None
                    completion_tokens = 0
                    
                    async for line in response.content:
                        line = line.decode("utf-8")
                        
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            
                            # Check if it's the [DONE] message
                            if data_str == "[DONE]":
                                break
                                
                            try:
                                data = json.loads(data_str)
                                
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    
                                    # Only yield if there's content
                                    if "content" in delta and delta["content"]:
                                        completion_text += delta["content"]
                                        completion_tokens += 1
                                        
                                        # Create usage statistics - these are estimates during streaming
                                        prompt_tokens = 0
                                        for msg in messages:
                                            # Very rough token count estimate
                                            prompt_tokens += len(msg.get("content", "")) // 4
                                            
                                        usage = ModelUsage(
                                            prompt_tokens=prompt_tokens,
                                            completion_tokens=completion_tokens,
                                            total_tokens=prompt_tokens + completion_tokens,
                                            input_cost=self._calculate_cost(model_name, "input", prompt_tokens),
                                            output_cost=self._calculate_cost(model_name, "output", completion_tokens),
                                        )
                                        usage.total_cost = usage.input_cost + usage.output_cost
                                        
                                        yield ModelResponse(
                                            text=completion_text,
                                            model_name=model_name,
                                            provider_name=self.provider_name,
                                            usage=usage,
                                            finish_reason=None,  # Not available during streaming
                                            raw_response=data,
                                            response_ms=(time.time() - start_time) * 1000,
                                        )
                                    
                                    # Check for finish reason
                                    if "finish_reason" in data["choices"][0] and data["choices"][0]["finish_reason"]:
                                        finish_reason = data["choices"][0]["finish_reason"]
                                        
                            except json.JSONDecodeError:
                                pass  # Skip malformed JSON
                    
                    # Yield final response with complete token counts if available
                    if completion_text:
                        # Create usage statistics - these are still estimates
                        prompt_tokens = 0
                        for msg in messages:
                            # Very rough token count estimate
                            prompt_tokens += len(msg.get("content", "")) // 4
                            
                        usage = ModelUsage(
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            total_tokens=prompt_tokens + completion_tokens,
                            input_cost=self._calculate_cost(model_name, "input", prompt_tokens),
                            output_cost=self._calculate_cost(model_name, "output", completion_tokens),
                        )
                        usage.total_cost = usage.input_cost + usage.output_cost
                        
                        yield ModelResponse(
                            text=completion_text,
                            model_name=model_name,
                            provider_name=self.provider_name,
                            usage=usage,
                            finish_reason=finish_reason,
                            raw_response=None,
                            response_ms=(time.time() - start_time) * 1000,
                        )
                        
        except Exception as e:
            logger.error(f"Error streaming chat completion from DeepSeek: {str(e)}")
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
        url = f"{self.api_base}/embeddings"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # DeepSeek expects a list of texts
        payload = {
            "model": model_config.model_name,
            "input": texts,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"DeepSeek API error: {error_text}")
                        raise Exception(f"DeepSeek API returned {response.status}: {error_text}")
                    
                    data = await response.json()
                    
                    # Extract embeddings
                    embeddings = [item["embedding"] for item in data["data"]]
                    
                    return embeddings
                    
        except Exception as e:
            logger.error(f"Error generating embeddings from DeepSeek: {str(e)}")
            raise
    
    def _calculate_cost(self, model_name: str, type_: str, tokens: int) -> float:
        """Calculate the cost for token usage.
        
        Args:
            model_name: Name of the model
            type_: Type of tokens (input or output)
            tokens: Number of tokens
            
        Returns:
            Cost in USD
        """
        # Pricing per 1K tokens
        pricing_map = {
            "deepseek-chat": {"input": 0.0000025, "output": 0.000005},
            "deepseek-coder": {"input": 0.000002, "output": 0.000009},
            "deepseek-chat-v2": {"input": 0.000003, "output": 0.000006},
            "deepseek-embedding": {"input": 0.0000001},
        }
        
        # Get pricing for the model
        model_pricing = pricing_map.get(model_name)
        if not model_pricing:
            # Try partial matching
            for key, pricing in pricing_map.items():
                if key in model_name:
                    model_pricing = pricing
                    break
        
        # If still not found, use default pricing
        if not model_pricing:
            model_pricing = {"input": 0.000003, "output": 0.000006}
        
        # Calculate cost
        if type_ in model_pricing:
            return model_pricing[type_] * (tokens / 1000)
        else:
            return 0.0 