"""
Example model selector component for AGI-MCP-Agent.

This is a simplified example of how to create a model selector component
that can be used to select models from different providers.

The component provides a simple API to:
1. List available providers
2. List models from a selected provider
3. Get details about a specific model
4. Create a model configuration

This is intended as a reference for building a more complete UI component
in your preferred frontend framework (React, Vue, etc.).
"""

import asyncio
from typing import Dict, List, Optional

from agi_mcp_agent.agent.llm_providers.manager import model_manager


class ModelSelectorComponent:
    """A simplified model selector component."""
    
    def __init__(self):
        """Initialize the model selector component."""
        # Ensure the model manager is initialized
        self.manager = model_manager
        
        # Cache for providers and models
        self._providers_cache: Optional[List[str]] = None
        self._models_by_provider: Dict[str, List[Dict]] = {}
        self._capabilities_cache: Optional[List[Dict]] = None
    
    def get_providers(self) -> List[str]:
        """Get the list of available providers.
        
        Returns:
            List of provider names
        """
        if self._providers_cache is None:
            self._providers_cache = self.manager.list_providers()
        return self._providers_cache
    
    def get_models_by_provider(self, provider_name: str) -> List[Dict]:
        """Get the list of models for a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            List of model information dictionaries
        """
        if provider_name not in self._models_by_provider:
            self._models_by_provider[provider_name] = self.manager.list_models_by_provider(provider_name)
        return self._models_by_provider[provider_name]
    
    def get_all_models(self) -> List[Dict]:
        """Get the list of all models from all providers.
        
        Returns:
            List of model information dictionaries
        """
        return self.manager.list_models()
    
    def get_capabilities(self) -> List[Dict]:
        """Get the list of all available capabilities.
        
        Returns:
            List of capability information dictionaries
        """
        if self._capabilities_cache is None:
            capabilities = self.manager.get_capabilities()
            self._capabilities_cache = [cap.dict() for cap in capabilities]
        return self._capabilities_cache
    
    def get_models_by_capability(self, capability: str) -> List[Dict]:
        """Get the list of models that support a capability.
        
        Args:
            capability: Name of the capability
            
        Returns:
            List of model information dictionaries
        """
        return self.manager.list_models_by_capability(capability)
    
    def get_model_info(self, model_identifier: str) -> Optional[Dict]:
        """Get information about a specific model.
        
        Args:
            model_identifier: Model identifier (provider:model_name)
            
        Returns:
            Model information dictionary, or None if not found
        """
        return self.manager.get_model_info(model_identifier)
    
    def create_model_config(
        self, 
        model_identifier: str, 
        temperature: float = 0.7, 
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict:
        """Create a model configuration.
        
        Args:
            model_identifier: Model identifier (provider:model_name)
            temperature: Model temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional configuration parameters
            
        Returns:
            Model configuration dictionary
        """
        config = self.manager.create_model_config(
            model_identifier=model_identifier,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return config.dict()


async def example_usage():
    """Example usage of the model selector component."""
    # Create the component
    selector = ModelSelectorComponent()
    
    # Get available providers
    providers = selector.get_providers()
    print(f"Available providers: {providers}")
    
    if not providers:
        print("No providers available. Please configure your API keys.")
        return
    
    # Get models from the first provider
    provider = providers[0]
    models = selector.get_models_by_provider(provider)
    print(f"\nModels from {provider}:")
    for model in models:
        print(f"  - {model['name']}: {model['description']}")
    
    # Get models that support a specific capability
    capability = "chat-completion"
    capable_models = selector.get_models_by_capability(capability)
    print(f"\nModels that support {capability}:")
    for model in capable_models:
        print(f"  - {model['provider']}:{model['name']}")
    
    # Select a model and create a configuration
    if capable_models:
        model_id = f"{capable_models[0]['provider']}:{capable_models[0]['name']}"
        config = selector.create_model_config(
            model_identifier=model_id,
            temperature=0.8,
            max_tokens=500
        )
        print(f"\nCreated configuration for {model_id}:")
        for key, value in config.items():
            print(f"  {key}: {value}")
        
        # Get model information
        model_info = selector.get_model_info(model_id)
        if model_info:
            print(f"\nModel information for {model_id}:")
            for key, value in model_info.items():
                if key != "pricing":  # Skip pricing details for brevity
                    print(f"  {key}: {value}")
            
            # Print pricing information
            if "pricing" in model_info:
                print("  Pricing:")
                for price_type, price in model_info["pricing"].items():
                    print(f"    {price_type}: ${price} per token")


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_usage()) 