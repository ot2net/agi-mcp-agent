"""Qwen provider implementation for Alibaba Cloud Qwen models."""

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


class QwenProvider(LLMProvider):
    """Provider for Alibaba Cloud Qwen models."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        api_base: Optional[str] = None,
        **kwargs
    ):
        """Initialize the Qwen provider.
        
        Args:
            api_key: Qwen API key (DashScope API key)
            api_base: Base URL for API requests
            **kwargs: Additional configuration
        """
        self.api_base = api_base or "https://dashscope.aliyuncs.com/api/v1"
        
        super().__init__(api_key=api_key, **kwargs)
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available models from Qwen.
        
        Returns:
            List of model information dictionaries
        """
        # Default available models
        default_models = [
            {
                "id": "qwen-turbo",
                "name": "qwen-turbo",
                "description": "Qwen Turbo - Fast and cost-effective general purpose model",
                "max_tokens": 6000,
                "pricing": {"input": 0.000002, "output": 0.000002}
            },
            {
                "id": "qwen-plus",
                "name": "qwen-plus",
                "description": "Qwen Plus - Higher quality general purpose model",
                "max_tokens": 30000,
                "pricing": {"input": 0.000003, "output": 0.000005}
            },
            {
                "id": "qwen-max",
                "name": "qwen-max",
                "description": "Qwen Max - Most powerful model with advanced reasoning",
                "max_tokens": 30000,
                "pricing": {"input": 0.000005, "output": 0.00001}
            },
            {
                "id": "qwen-max-longcontext",
                "name": "qwen-max-longcontext",
                "description": "Qwen Max with extended context window",
                "max_tokens": 64000,
                "pricing": {"input": 0.000005, "output": 0.00001}
            },
            {
                "id": "qwen-embedding-v1",
                "name": "qwen-embedding-v1",
                "description": "Qwen Embedding - Text embeddings model",
                "max_tokens": 2048,
                "pricing": {"input": 0.0000002}
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
            logger.warning(f"Could not fetch models from Qwen API: {str(e)}")
            logger.warning("Using default model list")
            return default_models
    
    def _list_models_sync(self) -> List[Dict[str, Any]]:
        """Synchronous version of list_models for running in a thread.
        
        Note: DashScope API might not provide a list models endpoint, so this is a placeholder.
        """
        # Using predefined models as DashScope API may not have a model listing endpoint
        return [
            {
                "id": "qwen-turbo",
                "name": "qwen-turbo",
                "description": "Qwen Turbo - Fast and cost-effective general purpose model",
                "max_tokens": 6000,
                "pricing": {"input": 0.000002, "output": 0.000002}
            },
            {
                "id": "qwen-plus",
                "name": "qwen-plus",
                "description": "Qwen Plus - Higher quality general purpose model",
                "max_tokens": 30000,
                "pricing": {"input": 0.000003, "output": 0.000005}
            },
            {
                "id": "qwen-max",
                "name": "qwen-max",
                "description": "Qwen Max - Most powerful model with advanced reasoning",
                "max_tokens": 30000,
                "pricing": {"input": 0.000005, "output": 0.00001}
            },
            {
                "id": "qwen-max-longcontext",
                "name": "qwen-max-longcontext",
                "description": "Qwen Max with extended context window",
                "max_tokens": 64000,
                "pricing": {"input": 0.000005, "output": 0.00001}
            },
            {
                "id": "qwen-embedding-v1",
                "name": "qwen-embedding-v1",
                "description": "Qwen Embedding - Text embeddings model",
                "max_tokens": 2048,
                "pricing": {"input": 0.0000002}
            },
        ]
    
    def get_capabilities(self) -> List[ModelCapability]:
        """Get the capabilities of Qwen models.
        
        Returns:
            List of model capabilities
        """
        # Define capabilities
        capabilities = [
            ModelCapability(
                name="text-completion",
                description="Generate text completions",
                supported_models=[
                    "qwen-turbo", "qwen-plus", "qwen-max", "qwen-max-longcontext",
                ],
            ),
            ModelCapability(
                name="chat-completion",
                description="Generate chat completions",
                supported_models=[
                    "qwen-turbo", "qwen-plus", "qwen-max", "qwen-max-longcontext",
                ],
            ),
            ModelCapability(
                name="embeddings",
                description="Generate embeddings for text",
                supported_models=[
                    "qwen-embedding-v1",
                ],
            ),
            ModelCapability(
                name="function-calling",
                description="Call functions defined by the user",
                supported_models=[
                    "qwen-plus", "qwen-max", "qwen-max-longcontext",
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
            loop = asyncio.get_event_loop()
            response = loop.run_in_executor(None, self._validate_api_key_sync)
            return response
        except Exception as e:
            logger.error(f"Error validating Qwen API key: {str(e)}")
            return False
    
    def _validate_api_key_sync(self) -> bool:
        """Synchronous version of validate_api_key for running in a thread."""
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            # For DashScope, we can use a simple model check endpoint or make a minimal request
            # This is a minimal request to test if the API key works
            response = requests.post(
                f"{self.api_base}/services/aigc/text-generation/generation",
                headers=headers,
                json={
                    "model": "qwen-turbo",
                    "input": {
                        "messages": [
                            {"role": "user", "content": "Hello"}
                        ]
                    },
                    "parameters": {
                        "max_tokens": 1
                    }
                },
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
        # For Qwen, we'll convert this to a chat completion with a single user message
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
        
        url = f"{self.api_base}/services/aigc/text-generation/generation"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # Qwen API (DashScope) expects a different format
        payload = {
            "model": model_config.model_name,
            "input": {
                "messages": messages
            },
            "parameters": {
                "max_tokens": model_config.max_tokens,
                "temperature": model_config.temperature,
                "top_p": model_config.top_p,
                "result_format": "message",
            }
        }
        
        # Map frequency and presence penalties
        if model_config.frequency_penalty:
            payload["parameters"]["repetition_penalty"] = 1.0 + model_config.frequency_penalty
            
        if model_config.stop_sequences:
            payload["parameters"]["stop"] = model_config.stop_sequences
            
        # Add any additional config options
        for key, value in model_config.additional_config.items():
            if key not in payload["parameters"]:
                payload["parameters"][key] = value
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Qwen API error: {error_text}")
                        raise Exception(f"Qwen API returned {response.status}: {error_text}")
                    
                    data = await response.json()
                    
                    # Extract the completion text
                    output = data.get("output", {})
                    choices = output.get("choices", [{}])
                    
                    if len(choices) == 0 or "message" not in choices[0]:
                        raise Exception("Unexpected response format from Qwen API")
                        
                    completion_text = choices[0]["message"].get("content", "")
                    
                    # Extract usage information
                    usage_data = output.get("usage", {})
                    usage = ModelUsage(
                        prompt_tokens=usage_data.get("input_tokens", 0),
                        completion_tokens=usage_data.get("output_tokens", 0),
                        total_tokens=usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0),
                        input_cost=self._calculate_cost(model_config.model_name, "input", usage_data.get("input_tokens", 0)),
                        output_cost=self._calculate_cost(model_config.model_name, "output", usage_data.get("output_tokens", 0)),
                    )
                    
                    # Calculate total cost
                    usage.total_cost = usage.input_cost + usage.output_cost
                    
                    return ModelResponse(
                        text=completion_text,
                        model_name=model_config.model_name,
                        provider_name=self.provider_name,
                        usage=usage,
                        finish_reason=choices[0].get("finish_reason"),
                        raw_response=data,
                        response_ms=(time.time() - start_time) * 1000,
                    )
                    
        except Exception as e:
            logger.error(f"Error generating chat completion from Qwen: {str(e)}")
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
            
        url = f"{self.api_base}/services/aigc/text-generation/generation"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-SSE": "enable",  # Enable server-sent events for streaming
        }
        
        # Qwen API (DashScope) expects a different format
        payload = {
            "model": model_name,
            "input": {
                "messages": messages
            },
            "parameters": {
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "result_format": "message",
                "incremental_output": True,  # Enable streaming
            }
        }
        
        # Map frequency and presence penalties
        if frequency_penalty:
            payload["parameters"]["repetition_penalty"] = 1.0 + frequency_penalty
            
        if stop:
            payload["parameters"]["stop"] = stop
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Qwen API error: {error_text}")
                        raise Exception(f"Qwen API returned {response.status}: {error_text}")
                    
                    # For streaming responses, we need to handle Server-Sent Events (SSE)
                    # Initialize variables for tracking the stream
                    completion_text = ""
                    finish_reason = None
                    prompt_tokens = 0
                    completion_tokens = 0
                    
                    # Simple token count estimate for prompt
                    for msg in messages:
                        # Very rough token count estimate
                        prompt_tokens += len(msg.get("content", "")) // 4
                    
                    async for line in response.content:
                        line = line.decode("utf-8").strip()
                        
                        if not line or not line.startswith("data: "):
                            continue
                            
                        data_str = line[6:].strip()
                        
                        try:
                            data = json.loads(data_str)
                            output = data.get("output", {})
                            
                            # Check for error
                            if "error" in data:
                                error = data.get("error", {})
                                logger.error(f"Qwen API error: {error}")
                                break
                            
                            if "choices" in output and len(output["choices"]) > 0:
                                choice = output["choices"][0]
                                
                                # Extract message content
                                if "message" in choice and "content" in choice["message"]:
                                    new_content = choice["message"]["content"]
                                    
                                    # Check if this is incremental or complete text
                                    if data.get("is_end", False):
                                        # Complete response, use it directly
                                        completion_text = new_content
                                    else:
                                        # Incremental response, append to existing text
                                        incremental_content = new_content.replace(completion_text, "")
                                        if incremental_content:
                                            completion_text = new_content
                                            completion_tokens += len(incremental_content) // 4  # Rough estimate
                                        
                                            # Create usage statistics - these are estimates
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
                                if "finish_reason" in choice and choice["finish_reason"]:
                                    finish_reason = choice["finish_reason"]
                                    
                                # Check for token usage in final message
                                if data.get("is_end", False) and "usage" in output:
                                    usage_data = output["usage"]
                                    prompt_tokens = usage_data.get("input_tokens", prompt_tokens)
                                    completion_tokens = usage_data.get("output_tokens", completion_tokens)
                            
                        except json.JSONDecodeError:
                            pass  # Skip malformed JSON
                    
                    # Yield final response if we have content and haven't yielded with this content yet
                    if completion_text:
                        # Create usage statistics with actual numbers if available
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
            logger.error(f"Error streaming chat completion from Qwen: {str(e)}")
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
        url = f"{self.api_base}/services/embeddings/text-embedding/text-embedding"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # DashScope embedding API format
        payload = {
            "model": model_config.model_name,
            "input": {
                "texts": texts
            },
            "parameters": {}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Qwen API error: {error_text}")
                        raise Exception(f"Qwen API returned {response.status}: {error_text}")
                    
                    data = await response.json()
                    
                    # Extract embeddings
                    output = data.get("output", {})
                    embeddings = [item["embedding"] for item in output.get("embeddings", [])]
                    
                    if len(embeddings) != len(texts):
                        logger.warning(f"Expected {len(texts)} embeddings but got {len(embeddings)}")
                    
                    return embeddings
                    
        except Exception as e:
            logger.error(f"Error generating embeddings from Qwen: {str(e)}")
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
        # Pricing per 1K tokens (approximate prices for Alibaba Cloud DashScope)
        pricing_map = {
            "qwen-turbo": {"input": 0.000002, "output": 0.000002},
            "qwen-plus": {"input": 0.000003, "output": 0.000005},
            "qwen-max": {"input": 0.000005, "output": 0.00001},
            "qwen-max-longcontext": {"input": 0.000005, "output": 0.00001},
            "qwen-embedding-v1": {"input": 0.0000002},
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
            model_pricing = {"input": 0.000003, "output": 0.000005}
        
        # Calculate cost
        if type_ in model_pricing:
            return model_pricing[type_] * (tokens / 1000)
        else:
            return 0.0 