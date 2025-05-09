import os
import pytest
import asyncio
from typing import Dict, Any

from agi_mcp_agent.agent.llm_providers.base import (
    LLMProvider,
    ModelConfig,
    ModelResponse,
    ModelCapability
)
from agi_mcp_agent.agent.llm_providers.openai import OpenAIProvider
from agi_mcp_agent.agent.llm_providers.anthropic import AnthropicProvider
from agi_mcp_agent.agent.llm_providers.google import GoogleProvider
from agi_mcp_agent.agent.llm_providers.mistral import MistralProvider


@pytest.fixture
def providers():
    """Fixture to initialize LLM providers."""
    providers = {}
    
    # Load API keys from environment variables
    api_keys = {
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "google": os.getenv("GOOGLE_API_KEY"),
        "mistral": os.getenv("MISTRAL_API_KEY")
    }
    
    # Initialize providers with valid API keys
    if api_keys["openai"]:
        providers["openai"] = OpenAIProvider(api_key=api_keys["openai"])
    if api_keys["anthropic"]:
        providers["anthropic"] = AnthropicProvider(api_key=api_keys["anthropic"])
    if api_keys["google"]:
        providers["google"] = GoogleProvider(api_key=api_keys["google"])
    if api_keys["mistral"]:
        providers["mistral"] = MistralProvider(api_key=api_keys["mistral"])
    
    return providers


class TestLLMProviders:
    """Test suite for LLM providers."""
    
    @pytest.mark.asyncio
    async def test_provider_initialization(self, providers):
        """Test that providers are properly initialized."""
        for provider_name, provider in providers.items():
            assert isinstance(provider, LLMProvider)
            assert len(provider.available_models) > 0
            assert len(provider.capabilities) > 0
    
    @pytest.mark.asyncio
    async def test_model_capabilities(self, providers):
        """Test that model capabilities are properly defined."""
        for provider_name, provider in providers.items():
            for capability in provider.capabilities:
                assert isinstance(capability, ModelCapability)
                assert len(capability.supported_models) > 0
    
    @pytest.mark.asyncio
    async def test_text_generation(self, providers):
        """Test text generation for each provider."""
        test_prompt = "Write a short poem about artificial intelligence."
        
        for provider_name, provider in providers.items():
            # Get first available model for testing
            model_name = provider.available_models[0]["id"]
            
            config = ModelConfig(
                model_name=model_name,
                provider_name=provider_name,
                temperature=0.7,
                max_tokens=100
            )

            # Test regular completion
            response = await provider.generate_text(test_prompt, config)
            assert isinstance(response, ModelResponse)
            assert len(response.text) > 0
            assert response.model_name == model_name
            assert response.provider_name == provider_name

            # Test streaming completion
            async for chunk in provider.generate_text(test_prompt, config, stream=True):
                assert isinstance(chunk, ModelResponse)
                assert hasattr(chunk, 'text')
    
    @pytest.mark.asyncio
    async def test_chat_completion(self, providers):
        """Test chat completion for each provider."""
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ]

        for provider_name, provider in providers.items():
            if not provider.model_supports_capability(
                provider.available_models[0]["id"], 
                "chat_completion"
            ):
                continue

            config = ModelConfig(
                model_name=provider.available_models[0]["id"],
                provider_name=provider_name
            )

            response = await provider.generate_chat_completion(test_messages, config)
            assert isinstance(response, ModelResponse)
            assert "Paris" in response.text
    
    @pytest.mark.asyncio
    async def test_embeddings(self, providers):
        """Test embedding generation for each provider."""
        test_texts = ["Hello, world!", "This is a test."]

        for provider_name, provider in providers.items():
            if not provider.model_supports_capability(
                provider.available_models[0]["id"], 
                "embeddings"
            ):
                continue

            config = ModelConfig(
                model_name=provider.available_models[0]["id"],
                provider_name=provider_name
            )

            embeddings = await provider.generate_embeddings(test_texts, config)
            assert isinstance(embeddings, list)
            assert len(embeddings) == len(test_texts)
            assert all(isinstance(emb, list) for emb in embeddings)
    
    def test_api_key_validation(self, providers):
        """Test API key validation for each provider."""
        for provider_name, provider in providers.items():
            assert provider.validate_api_key()

        # Test with invalid API key
        with pytest.raises(Exception):
            OpenAIProvider(api_key="invalid_key").validate_api_key() 