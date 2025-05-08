"""LLM provider and model manager for AGI-MCP-Agent."""

import asyncio
import logging
import os
import random
from typing import Any, Dict, List, Optional, Set, Tuple, Union, AsyncGenerator

from agi_mcp_agent.agent.llm_providers.base import (
    LLMProvider,
    ModelCapability,
    ModelConfig,
    ModelResponse,
)
from agi_mcp_agent.utils.config import config
from agi_mcp_agent.repositories.llm_provider_repository import LLMProviderRepository

logger = logging.getLogger(__name__)


class ModelProviderManager:
    """Manager for LLM providers and models."""
    
    def __init__(self, db_url: Optional[str] = None):
        """Initialize the model provider manager.
        
        Args:
            db_url: Optional database URL for provider storage
        """
        self.providers: Dict[str, LLMProvider] = {}
        self.models_cache: Dict[str, Dict[str, Any]] = {}
        self.capabilities_cache: Dict[str, List[ModelCapability]] = {}
        
        # Initialize repository if database URL is provided
        self.repository = None
        self.db_url = db_url or os.environ.get("DATABASE_URL") or config.get("database_url")
        
        if self.db_url:
            try:
                self.repository = LLMProviderRepository(self.db_url)
                self.repository.create_tables()
                self.repository.initialize_default_data()
            except Exception as e:
                logger.error(f"Error initializing provider repository: {str(e)}")
        
        # Load providers from config and database
        self._load_providers()
        logger.info(f"Initialized ModelProviderManager with {len(self.providers)} providers")
    
    def _load_providers(self):
        """Load provider configurations from the global config and database."""
        # First try to load from database if available
        if self.repository:
            self._load_providers_from_database()
        
        # If no providers were loaded from database, fall back to environment variables
        if not self.providers:
            self._load_providers_from_config()
    
    def _load_providers_from_database(self):
        """Load provider configurations from the database."""
        try:
            # Get all enabled providers
            providers = self.repository.get_enabled_providers()
            
            for provider_model in providers:
                # Get provider settings
                settings_dict = self.repository.get_provider_settings_dict(provider_model.id)
                
                # Check if required settings are available (like API key)
                api_key = settings_dict.get("api_key")
                if not api_key:
                    logger.warning(f"Skipping provider {provider_model.name} because API key is missing")
                    continue
                
                # Import the provider class dynamically
                try:
                    module_path = provider_model.provider_module
                    class_name = provider_model.provider_class
                    
                    # Import module
                    module = __import__(module_path, fromlist=[class_name])
                    provider_class = getattr(module, class_name)
                    
                    # Initialize provider instance
                    provider_instance = provider_class(
                        api_key=api_key,
                        **{k: v for k, v in settings_dict.items() if k != "api_key"}
                    )
                    
                    # Add to providers dict
                    self.providers[provider_model.name] = provider_instance
                    logger.info(f"Loaded provider from database: {provider_model.name}")
                    
                except (ImportError, AttributeError) as e:
                    logger.error(f"Error loading provider {provider_model.name} from database: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error loading providers from database: {str(e)}")
    
    def _load_providers_from_config(self):
        """Load provider configurations from the global config."""
        # OpenAI is always included as default provider if key is available
        openai_api_key = os.environ.get("OPENAI_API_KEY") or config.get("openai_api_key")
        if openai_api_key:
            try:
                from agi_mcp_agent.agent.llm_providers.openai import OpenAIProvider
                self.providers["openai"] = OpenAIProvider(
                    api_key=openai_api_key,
                    organization_id=os.environ.get("OPENAI_ORG_ID") or config.get("openai_organization_id"),
                    api_base=os.environ.get("OPENAI_API_BASE") or config.get("openai_api_base"),
                )
                logger.info("Loaded OpenAI provider from environment")
            except ImportError:
                logger.warning("OpenAI provider package not installed, skipping")
        
        # Load Anthropic if available
        anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY") or config.get("anthropic_api_key")
        if anthropic_api_key:
            try:
                from agi_mcp_agent.agent.llm_providers.anthropic import AnthropicProvider
                self.providers["anthropic"] = AnthropicProvider(
                    api_key=anthropic_api_key,
                )
                logger.info("Loaded Anthropic provider from environment")
            except ImportError:
                logger.warning("Anthropic provider package not installed, skipping")
        
        # Load Google if available
        google_api_key = os.environ.get("GOOGLE_API_KEY") or config.get("google_api_key")
        if google_api_key:
            try:
                from agi_mcp_agent.agent.llm_providers.google import GoogleProvider
                self.providers["google"] = GoogleProvider(
                    api_key=google_api_key,
                    project_id=os.environ.get("GOOGLE_PROJECT_ID") or config.get("google_project_id"),
                )
                logger.info("Loaded Google provider from environment")
            except ImportError:
                logger.warning("Google provider package not installed, skipping")
        
        # Load Mistral if available
        mistral_api_key = os.environ.get("MISTRAL_API_KEY") or config.get("mistral_api_key")
        if mistral_api_key:
            try:
                from agi_mcp_agent.agent.llm_providers.mistral import MistralProvider
                self.providers["mistral"] = MistralProvider(
                    api_key=mistral_api_key,
                )
                logger.info("Loaded Mistral provider from environment")
            except ImportError:
                logger.warning("Mistral provider package not installed, skipping")
        
        # Load DeepSeek if available
        deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY") or config.get("deepseek_api_key")
        if deepseek_api_key:
            try:
                from agi_mcp_agent.agent.llm_providers.deepseek import DeepSeekProvider
                self.providers["deepseek"] = DeepSeekProvider(
                    api_key=deepseek_api_key,
                    api_base=os.environ.get("DEEPSEEK_API_BASE") or config.get("deepseek_api_base"),
                )
                logger.info("Loaded DeepSeek provider from environment")
            except ImportError:
                logger.warning("DeepSeek provider package not installed, skipping")
        
        # Load Qwen if available
        qwen_api_key = os.environ.get("QWEN_API_KEY") or config.get("qwen_api_key")
        if qwen_api_key:
            try:
                from agi_mcp_agent.agent.llm_providers.qwen import QwenProvider
                self.providers["qwen"] = QwenProvider(
                    api_key=qwen_api_key,
                    api_base=os.environ.get("QWEN_API_BASE") or config.get("qwen_api_base"),
                )
                logger.info("Loaded Qwen provider from environment")
            except ImportError:
                logger.warning("Qwen provider package not installed, skipping")
    
    def add_provider(self, provider_name: str, provider: LLMProvider) -> None:
        """Add a provider to the manager.
        
        Args:
            provider_name: Name of the provider
            provider: Provider instance
        """
        self.providers[provider_name] = provider
        logger.info(f"Added provider: {provider_name}")
        
        # Clear caches when adding a new provider
        self.models_cache = {}
        self.capabilities_cache = {}
        
        # Save to database if repository is available
        if self.repository:
            try:
                # Check if provider already exists
                provider_model = self.repository.get_provider_by_name(provider_name)
                
                if not provider_model:
                    # Import path and class name (best effort)
                    module_path = provider.__class__.__module__
                    class_name = provider.__class__.__name__
                    
                    # Create provider in database (this is simplified - you'd need appropriate DB models)
                    # This part depends on your actual database schema
                    pass
            except Exception as e:
                logger.error(f"Error saving provider to database: {str(e)}")
    
    def remove_provider(self, provider_name: str) -> bool:
        """Remove a provider from the manager.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Whether the provider was removed
        """
        if provider_name not in self.providers:
            return False
            
        del self.providers[provider_name]
        logger.info(f"Removed provider: {provider_name}")
        
        # Clear caches when removing a provider
        self.models_cache = {}
        self.capabilities_cache = {}
        
        return True
    
    def get_provider(self, provider_name: str) -> Optional[LLMProvider]:
        """Get a provider by name.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            The provider, if found
        """
        return self.providers.get(provider_name)
    
    def list_providers(self) -> List[str]:
        """List all available providers.
        
        Returns:
            List of provider names
        """
        return list(self.providers.keys())
    
    def list_providers_by_region(self, region: str) -> List[str]:
        """List providers by region.
        
        Args:
            region: Region code (e.g. 'cn', 'global')
            
        Returns:
            List of provider names in the specified region
        """
        if not self.repository:
            # Without repository, we can't filter by region reliably
            if region == 'cn':
                # Return Chinese models
                return [name for name in self.providers if name in ['deepseek', 'qwen']]
            else:
                # Return non-Chinese models
                return [name for name in self.providers if name not in ['deepseek', 'qwen']]
        else:
            # With repository, we can get accurate region info
            providers = self.repository.get_enabled_providers(region=region)
            return [p.name for p in providers if p.name in self.providers]
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all available models from all providers.
        
        Returns:
            List of model information dictionaries
        """
        if not self.models_cache:
            all_models = []
            
            for provider_name, provider in self.providers.items():
                try:
                    models = provider.list_available_models()
                    
                    # Add provider information to each model
                    for model in models:
                        model["provider"] = provider_name
                        all_models.append(model)
                except Exception as e:
                    logger.error(f"Error listing models for provider {provider_name}: {str(e)}")
            
            # Sort by provider and name
            all_models.sort(key=lambda m: (m["provider"], m["name"]))
            self.models_cache = {f"{m['provider']}:{m['name']}": m for m in all_models}
        
        return list(self.models_cache.values())
    
    def list_models_by_provider(self, provider_name: str) -> List[Dict[str, Any]]:
        """List all available models from a specific provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            List of model information dictionaries
        """
        provider = self.get_provider(provider_name)
        if not provider:
            return []
            
        try:
            models = provider.list_available_models()
            
            # Add provider information to each model
            for model in models:
                model["provider"] = provider_name
                
            return models
        except Exception as e:
            logger.error(f"Error listing models for provider {provider_name}: {str(e)}")
            return []
    
    def list_models_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """List all models that support a specific capability.
        
        Args:
            capability: Name of the capability
            
        Returns:
            List of model information dictionaries
        """
        all_models = self.list_models()
        capability_models = []
        
        for model in all_models:
            provider_name = model["provider"]
            model_name = model["name"]
            provider = self.get_provider(provider_name)
            
            if provider and provider.model_supports_capability(model_name, capability):
                capability_models.append(model)
        
        return capability_models
    
    def list_models_by_region(self, region: str) -> List[Dict[str, Any]]:
        """List all models in a specific region.
        
        Args:
            region: Region code (e.g. 'cn', 'global')
            
        Returns:
            List of model information dictionaries
        """
        # Get providers in the specified region
        provider_names = self.list_providers_by_region(region)
        
        # Get models from these providers
        models = []
        for provider_name in provider_names:
            models.extend(self.list_models_by_provider(provider_name))
            
        return models
    
    def get_capabilities(self) -> List[ModelCapability]:
        """Get all capabilities from all providers.
        
        Returns:
            List of unique capabilities
        """
        if not self.capabilities_cache:
            all_capabilities = []
            capability_names: Set[str] = set()
            
            for provider_name, provider in self.providers.items():
                try:
                    capabilities = provider.get_capabilities()
                    
                    for capability in capabilities:
                        if capability.name not in capability_names:
                            capability_names.add(capability.name)
                            all_capabilities.append(capability)
                except Exception as e:
                    logger.error(f"Error getting capabilities for provider {provider_name}: {str(e)}")
            
            self.capabilities_cache = all_capabilities
        
        return self.capabilities_cache
    
    def get_model_info(self, model_identifier: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model.
        
        Args:
            model_identifier: Model identifier in the format provider:model_name
            
        Returns:
            Model information, if found
        """
        # Ensure models are loaded
        if not self.models_cache:
            self.list_models()
            
        # Check if model exists in cache
        if model_identifier in self.models_cache:
            return self.models_cache[model_identifier]
            
        # If not found, try parsing the identifier
        try:
            provider_name, model_name = model_identifier.split(":", 1)
            
            # Try to get model from provider
            provider = self.get_provider(provider_name)
            if provider:
                models = provider.list_available_models()
                
                for model in models:
                    if model["name"] == model_name:
                        model["provider"] = provider_name
                        return model
        except ValueError:
            # Identifier doesn't contain a colon, might be a default or unregistered model
            pass
            
        return None
    
    def create_model_config(
        self, 
        model_identifier: str, 
        temperature: float = 0.7, 
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelConfig:
        """Create a model configuration for a specific model.
        
        Args:
            model_identifier: Model identifier in the format provider:model_name
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            **kwargs: Additional configuration parameters
            
        Returns:
            Model configuration
        """
        provider_name, model_name = model_identifier.split(":", 1)
        model_info = self.get_model_info(model_identifier)
        
        # Use default max tokens from model info if not provided
        if max_tokens is None and model_info and "max_tokens" in model_info:
            max_tokens = model_info["max_tokens"]
        elif max_tokens is None:
            max_tokens = 4096  # Default
        
        # Create model config
        return ModelConfig(
            model_name=model_name,
            provider_name=provider_name,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    async def generate_text(
        self,
        prompt: str,
        model_identifier: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[ModelResponse, AsyncGenerator[ModelResponse, None]]:
        """Generate text from a model.
        
        Args:
            prompt: Text prompt
            model_identifier: Model identifier in the format provider:model_name
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional model configuration parameters
            
        Returns:
            Model response or stream of responses
            
        Raises:
            ValueError: If the model identifier is invalid or the provider is not found
            Exception: If text generation fails
        """
        try:
            provider_name, model_name = model_identifier.split(":", 1)
        except ValueError:
            raise ValueError(f"Invalid model identifier: {model_identifier}. Must be in format 'provider:model_name'")
        
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider not found: {provider_name}")
        
        # Create model config
        model_config = self.create_model_config(
            model_identifier=model_identifier,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Generate text
        try:
            return await provider.generate_text(
                prompt=prompt,
                model_config=model_config,
                stream=stream,
            )
        except Exception as e:
            logger.error(f"Error generating text with {model_identifier}: {str(e)}")
            raise
    
    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model_identifier: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[ModelResponse, AsyncGenerator[ModelResponse, None]]:
        """Generate a chat completion from a model.
        
        Args:
            messages: List of chat messages in the format [{"role": "user", "content": "..."}]
            model_identifier: Model identifier in the format provider:model_name
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional model configuration parameters
            
        Returns:
            Model response or stream of responses
            
        Raises:
            ValueError: If the model identifier is invalid or the provider is not found
            Exception: If chat completion generation fails
        """
        try:
            provider_name, model_name = model_identifier.split(":", 1)
        except ValueError:
            raise ValueError(f"Invalid model identifier: {model_identifier}. Must be in format 'provider:model_name'")
        
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider not found: {provider_name}")
        
        # Create model config
        model_config = self.create_model_config(
            model_identifier=model_identifier,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Generate chat completion
        try:
            return await provider.generate_chat_completion(
                messages=messages,
                model_config=model_config,
                stream=stream,
            )
        except Exception as e:
            logger.error(f"Error generating chat completion with {model_identifier}: {str(e)}")
            raise
    
    async def generate_embeddings(
        self,
        texts: List[str],
        model_identifier: str,
        **kwargs
    ) -> List[List[float]]:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            model_identifier: Model identifier in the format provider:model_name
            **kwargs: Additional model configuration parameters
            
        Returns:
            List of embedding vectors
            
        Raises:
            ValueError: If the model identifier is invalid or the provider is not found
            Exception: If embedding generation fails
        """
        try:
            provider_name, model_name = model_identifier.split(":", 1)
        except ValueError:
            raise ValueError(f"Invalid model identifier: {model_identifier}. Must be in format 'provider:model_name'")
        
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider not found: {provider_name}")
        
        # Create model config
        model_config = self.create_model_config(
            model_identifier=model_identifier,
            **kwargs
        )
        
        # Generate embeddings
        try:
            return await provider.generate_embeddings(
                texts=texts,
                model_config=model_config,
            )
        except Exception as e:
            logger.error(f"Error generating embeddings with {model_identifier}: {str(e)}")
            raise
    
    def get_fallback_model(
        self,
        capability: str,
        preferred_providers: Optional[List[str]] = None,
        excluded_providers: Optional[List[str]] = None,
        excluded_models: Optional[List[str]] = None,
        region: Optional[str] = None,
    ) -> Optional[str]:
        """Get a fallback model with the specified capability.
        
        Args:
            capability: Required capability
            preferred_providers: List of preferred providers in order of preference
            excluded_providers: List of providers to exclude
            excluded_models: List of models to exclude
            region: Optional region filter
            
        Returns:
            Model identifier in the format provider:model_name, or None if no suitable model found
        """
        preferred_providers = preferred_providers or []
        excluded_providers = excluded_providers or []
        excluded_models = excluded_models or []
        
        # Get all models with the capability
        capability_models = self.list_models_by_capability(capability)
        
        # Apply region filter if specified
        if region:
            region_providers = self.list_providers_by_region(region)
            capability_models = [m for m in capability_models if m["provider"] in region_providers]
        
        # Filter out excluded providers and models
        filtered_models = [
            m for m in capability_models 
            if m["provider"] not in excluded_providers and f"{m['provider']}:{m['name']}" not in excluded_models
        ]
        
        if not filtered_models:
            return None
        
        # First try preferred providers
        for provider_name in preferred_providers:
            provider_models = [m for m in filtered_models if m["provider"] == provider_name]
            if provider_models:
                # Return first model from preferred provider
                return f"{provider_models[0]['provider']}:{provider_models[0]['name']}"
                
        # If no preferred provider models available, return a random one
        model = random.choice(filtered_models)
        return f"{model['provider']}:{model['name']}"


# Singleton instance
model_manager = ModelProviderManager() 