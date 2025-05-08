"""Anthropic (Claude) provider implementation."""

import asyncio
import logging
import time
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

import anthropic

from agi_mcp_agent.agent.llm_providers.base import (
    LLMProvider,
    ModelCapability,
    ModelConfig,
    ModelResponse,
    ModelUsage,
)

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """Provider for Anthropic Claude models."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        **kwargs,
    ):
        """Initialize the Anthropic provider.
        
        Args:
            api_key: Anthropic API key
            **kwargs: Additional configuration
        """
        # Initialize the client
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        
        super().__init__(api_key=api_key, **kwargs)
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available models from Anthropic.
        
        Returns:
            List of model information dictionaries
        """
        # Define available models (Anthropic doesn't have a list models API)
        models = [
            {
                "id": "claude-3-opus-20240229",
                "name": "claude-3-opus",
                "description": "Claude 3 Opus - Most powerful model in the Claude 3 family",
                "max_tokens": 200000,
                "pricing": {"input": 0.00003, "output": 0.00015}
            },
            {
                "id": "claude-3-sonnet-20240229",
                "name": "claude-3-sonnet",
                "description": "Claude 3 Sonnet - Balanced model for quality and speed",
                "max_tokens": 200000,
                "pricing": {"input": 0.000003, "output": 0.000015}
            },
            {
                "id": "claude-3-haiku-20240307",
                "name": "claude-3-haiku",
                "description": "Claude 3 Haiku - Fast and cost-effective model",
                "max_tokens": 200000,
                "pricing": {"input": 0.00000025, "output": 0.00000125}
            },
            {
                "id": "claude-2.1",
                "name": "claude-2.1",
                "description": "Claude 2.1 - Previous generation model",
                "max_tokens": 100000,
                "pricing": {"input": 0.000008, "output": 0.000024}
            },
            {
                "id": "claude-2.0",
                "name": "claude-2.0",
                "description": "Claude 2.0 - Previous generation model",
                "max_tokens": 100000,
                "pricing": {"input": 0.000008, "output": 0.000024}
            },
            {
                "id": "claude-instant-1.2",
                "name": "claude-instant-1.2",
                "description": "Claude Instant 1.2 - Fast, cost-effective legacy model",
                "max_tokens": 100000,
                "pricing": {"input": 0.0000008, "output": 0.0000024}
            },
        ]
        
        return models
    
    def get_capabilities(self) -> List[ModelCapability]:
        """Get the capabilities of Anthropic models.
        
        Returns:
            List of model capabilities
        """
        # Define capabilities
        capabilities = [
            ModelCapability(
                name="text-completion",
                description="Generate text completions",
                supported_models=[
                    "claude-3-opus", "claude-3-sonnet", "claude-3-haiku",
                    "claude-2.1", "claude-2.0", "claude-instant-1.2"
                ],
            ),
            ModelCapability(
                name="chat-completion",
                description="Generate chat completions",
                supported_models=[
                    "claude-3-opus", "claude-3-sonnet", "claude-3-haiku",
                    "claude-2.1", "claude-2.0", "claude-instant-1.2"
                ],
            ),
            ModelCapability(
                name="vision",
                description="Analyze and describe images",
                supported_models=[
                    "claude-3-opus", "claude-3-sonnet", "claude-3-haiku",
                ],
            ),
            ModelCapability(
                name="tool-use",
                description="Use tools provided by the user",
                supported_models=[
                    "claude-3-opus", "claude-3-sonnet", "claude-3-haiku",
                ],
            ),
        ]
        
        return capabilities
    
    def validate_api_key(self) -> bool:
        """Validate the Anthropic API key.
        
        Returns:
            Whether the API key is valid
        """
        try:
            # Create a synchronous client for validation
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # Send a minimal request to validate the API key
            response = client.messages.create(
                model="claude-3-haiku",
                max_tokens=1,
                messages=[
                    {"role": "user", "content": "Hello"}
                ],
                system="This is a test message for API key validation."
            )
            
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
        # Anthropic doesn't have a separate text completion API,
        # so we'll use the messages API for all text generation
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
        stop_sequences = model_config.stop_sequences or None
        system = model_config.additional_config.get("system", "")
        
        # Map messages to Anthropic format
        claude_messages = []
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            # Anthropic only supports user and assistant roles
            if role == "system":
                system = content
                continue
                
            claude_messages.append({
                "role": "user" if role == "user" else "assistant",
                "content": content
            })
        
        # Record start time for response timing
        start_time = time.time()
        
        try:
            if stream:
                # Handle streaming
                return self._stream_chat_completion(
                    messages=claude_messages,
                    system=system,
                    model_name=model_name,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    stop=stop_sequences,
                    start_time=start_time,
                )
            else:
                # Non-streaming request
                response = await self.client.messages.create(
                    model=model_name,
                    messages=claude_messages,
                    system=system,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    stop_sequences=stop_sequences,
                )
                
                # Calculate response time
                response_time = (time.time() - start_time) * 1000  # ms
                
                # Extract text from the response
                completion_text = response.content[0].text
                
                # Create usage information
                usage = ModelUsage(
                    prompt_tokens=response.usage.input_tokens,
                    completion_tokens=response.usage.output_tokens,
                    total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                    input_cost=self._calculate_cost(
                        model_name, "input", response.usage.input_tokens
                    ),
                    output_cost=self._calculate_cost(
                        model_name, "output", response.usage.output_tokens
                    ),
                )
                usage.total_cost = usage.input_cost + usage.output_cost
                
                # Create and return the model response
                return ModelResponse(
                    text=completion_text,
                    model_name=model_name,
                    provider_name="Anthropic",
                    usage=usage,
                    finish_reason=response.stop_reason,
                    raw_response=response.dict(),
                    response_ms=response_time,
                )
                
        except Exception as e:
            logger.error(f"Error in Anthropic completion: {str(e)}")
            raise
    
    async def _stream_chat_completion(
        self,
        messages: List[Dict[str, Any]],
        system: str,
        model_name: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        stop: Optional[List[str]] = None,
        start_time: float = None,
    ) -> AsyncGenerator[ModelResponse, None]:
        """Stream a chat completion from the model.
        
        Args:
            messages: List of chat messages
            system: System message
            model_name: Name of the model
            max_tokens: Maximum tokens to generate
            temperature: Temperature for sampling
            top_p: Top P for sampling
            stop: Stop sequences
            start_time: Start time for response timing
            
        Yields:
            Model responses as they are generated
        """
        if start_time is None:
            start_time = time.time()
            
        try:
            # Start streaming response
            stream = await self.client.messages.create(
                model=model_name,
                messages=messages,
                system=system,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop_sequences=stop,
                stream=True,
            )
            
            # Collect response chunks
            full_text = ""
            finish_reason = None
            
            # Track token counts for final usage calculation
            input_token_count = None
            output_token_count = 0
            
            async for chunk in stream:
                if chunk.type == "content_block_delta":
                    delta = chunk.delta
                    if delta.text:
                        # Estimate token count (very rough approximation)
                        output_token_count += len(delta.text) // 4
                        
                        full_text += delta.text
                        
                        # Calculate response time
                        response_time = (time.time() - start_time) * 1000  # ms
                        
                        # Create partial usage
                        chunk_usage = ModelUsage(
                            prompt_tokens=0,  # Will be updated at the end
                            completion_tokens=output_token_count,
                            total_tokens=0,  # Will be updated at the end
                        )
                        
                        # Yield the partial response
                        yield ModelResponse(
                            text=full_text,
                            model_name=model_name,
                            provider_name="Anthropic",
                            usage=chunk_usage,
                            finish_reason=None,  # Will be provided in the final message
                            raw_response=None,
                            response_ms=response_time,
                        )
                
                elif chunk.type == "message_stop":
                    finish_reason = chunk.message.stop_reason
                    
                    # Get input token count from the final message usage
                    input_token_count = chunk.message.usage.input_tokens
            
            # After streaming is complete, calculate final usage
            if input_token_count is None:
                # If for some reason we didn't get the input token count,
                # estimate it based on the input length
                input_token_count = sum(len(str(m)) for m in messages) // 4
            
            total_tokens = input_token_count + output_token_count
            
            usage = ModelUsage(
                prompt_tokens=input_token_count,
                completion_tokens=output_token_count,
                total_tokens=total_tokens,
                input_cost=self._calculate_cost(model_name, "input", input_token_count),
                output_cost=self._calculate_cost(model_name, "output", output_token_count),
            )
            usage.total_cost = usage.input_cost + usage.output_cost
            
            # Calculate final response time
            response_time = (time.time() - start_time) * 1000  # ms
            
            # Yield the final response
            yield ModelResponse(
                text=full_text,
                model_name=model_name,
                provider_name="Anthropic",
                usage=usage,
                finish_reason=finish_reason,
                raw_response=None,
                response_ms=response_time,
            )
            
        except Exception as e:
            logger.error(f"Error in Anthropic streaming completion: {str(e)}")
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
        # Anthropic doesn't currently have a dedicated embeddings API
        # In a real implementation, we might want to use a wrapper that
        # extracts embeddings from Claude, but for now we'll raise an exception
        raise NotImplementedError("Anthropic does not currently provide an embeddings API")
    
    def _calculate_cost(self, model_name: str, type_: str, tokens: int) -> float:
        """Calculate the cost for a model call.
        
        Args:
            model_name: Name of the model
            type_: Type of tokens (input or output)
            tokens: Number of tokens
            
        Returns:
            Cost in USD
        """
        # Pricing per 1M tokens (convert to per token)
        pricing_map = {
            "claude-3-opus": {"input": 0.00003, "output": 0.00015},
            "claude-3-sonnet": {"input": 0.000003, "output": 0.000015},
            "claude-3-haiku": {"input": 0.00000025, "output": 0.00000125},
            "claude-2.1": {"input": 0.000008, "output": 0.000024},
            "claude-2.0": {"input": 0.000008, "output": 0.000024},
            "claude-instant-1.2": {"input": 0.0000008, "output": 0.0000024},
        }
        
        # Get the base model name without version
        base_model = model_name.split("-20")[0] if "-20" in model_name else model_name
        
        # Check for exact match first
        if base_model in pricing_map:
            price_per_token = pricing_map[base_model][type_]
        else:
            # Default price if unknown
            logger.warning(f"Unknown model for pricing: {model_name}, using default pricing")
            price_per_token = 0.000015 if type_ == "output" else 0.000003
        
        # Calculate cost
        return (tokens / 1000) * price_per_token 