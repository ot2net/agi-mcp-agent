#!/usr/bin/env python3
"""Example of using the LLM provider database configuration system."""

import asyncio
import os
import sys
from typing import List, Dict

# Add the parent directory to sys.path to allow importing from the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agi_mcp_agent.agent.llm_providers.manager import ModelProviderManager
from agi_mcp_agent.repositories.llm_provider_repository import LLMProviderRepository
from agi_mcp_agent.models.llm_provider import LLMModelModel
from agi_mcp_agent.agent.llm_agent import LLMAgent
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


async def list_providers_and_models(db_url: str):
    """List all providers and models from the database.
    
    Args:
        db_url: Database URL
    """
    print("\n=== LLM Providers and Models ===")
    
    # Initialize model manager with the database URL
    manager = ModelProviderManager(db_url=db_url)
    
    # List all available providers
    providers = manager.list_providers()
    print(f"Available providers: {', '.join(providers)}")
    
    # List providers by region
    chinese_providers = manager.list_providers_by_region('cn')
    global_providers = manager.list_providers_by_region('global')
    
    print(f"Chinese providers: {', '.join(chinese_providers)}")
    print(f"Global providers: {', '.join(global_providers)}")
    
    # List all available models from all providers
    all_models = manager.list_models()
    print(f"\nTotal available models: {len(all_models)}")
    
    # Group models by provider
    models_by_provider = {}
    for model in all_models:
        provider = model['provider']
        if provider not in models_by_provider:
            models_by_provider[provider] = []
        models_by_provider[provider].append(model)
    
    # Print models by provider
    for provider, models in models_by_provider.items():
        print(f"\n{provider.upper()} models:")
        for model in models:
            print(f"  - {model['name']}: {model.get('description', 'No description')}")
    
    # List models by capability
    chat_models = manager.list_models_by_capability('chat-completion')
    print(f"\nChat-capable models: {len(chat_models)}")
    for model in chat_models[:5]:  # Print first 5 for brevity
        print(f"  - {model['provider']}:{model['name']}")
    
    # List models by region
    chinese_models = manager.list_models_by_region('cn')
    print(f"\nChinese models: {len(chinese_models)}")
    for model in chinese_models:
        print(f"  - {model['provider']}:{model['name']}")


async def demonstrate_text_generation(db_url: str):
    """Demonstrate text generation with different models.
    
    Args:
        db_url: Database URL
    """
    print("\n=== Text Generation with Different Models ===")
    
    # Initialize model manager with the database URL
    manager = ModelProviderManager(db_url=db_url)
    
    # Define prompt
    prompt = "Write a haiku about artificial intelligence."
    print(f"Prompt: {prompt}")
    
    # Try generating text with different models
    models_to_try = []
    
    # Add an OpenAI model if available
    if "openai" in manager.list_providers():
        models_to_try.append("openai:gpt-3.5-turbo")
    
    # Add a Chinese model if available
    chinese_providers = manager.list_providers_by_region('cn')
    if chinese_providers:
        chinese_provider = chinese_providers[0]
        provider_models = manager.list_models_by_provider(chinese_provider)
        if provider_models:
            models_to_try.append(f"{chinese_provider}:{provider_models[0]['name']}")
    
    # Add a fallback model
    fallback_model = manager.get_fallback_model(
        capability="text-completion",
        excluded_models=models_to_try
    )
    if fallback_model and fallback_model not in models_to_try:
        models_to_try.append(fallback_model)
    
    # Generate text with each model
    for model_id in models_to_try:
        try:
            print(f"\nGenerating with {model_id}...")
            response = await manager.generate_text(
                prompt=prompt,
                model_identifier=model_id,
                temperature=0.7,
                max_tokens=100
            )
            print(f"Response: {response.text}")
            print(f"Usage: {response.usage.prompt_tokens} prompt tokens, {response.usage.completion_tokens} completion tokens")
            print(f"Cost: ${response.usage.total_cost:.6f}")
        except Exception as e:
            print(f"Error with {model_id}: {str(e)}")


async def add_custom_model_to_database(db_url: str):
    """Add a custom model to the database.
    
    Args:
        db_url: Database URL
    """
    print("\n=== Adding Custom Model to Database ===")
    
    # Initialize the repository
    repo = LLMProviderRepository(db_url)
    
    # Find the DeepSeek provider
    deepseek_provider = repo.get_provider_by_name("deepseek")
    if not deepseek_provider:
        print("DeepSeek provider not found. Make sure database is initialized.")
        return
    
    # Create a custom model
    custom_model = LLMModelModel(
        provider_id=deepseek_provider.id,
        name="deepseek-custom",
        model_id="deepseek-custom",
        display_name="DeepSeek Custom Model",
        description="A custom DeepSeek model added for demonstration",
        model_type="chat",
        is_enabled=True,
        max_tokens=8192,
        supports_streaming=True,
        supports_function_calling=True,
        context_window=8192,
        pricing_input=0.000003,
        pricing_output=0.000006,
        capabilities=["text-completion", "chat-completion", "function-calling"],
        parameters={"top_p": 1.0}
    )
    
    # Check if model already exists
    existing_model = repo.get_model_by_name(deepseek_provider.id, "deepseek-custom")
    if existing_model:
        print("Model 'deepseek-custom' already exists, updating instead...")
        repo.update_model(
            existing_model.id, 
            description="A custom DeepSeek model updated through the API",
            supports_function_calling=True
        )
        print("Model updated successfully.")
    else:
        # Add model to the database
        success = repo.add_model(custom_model)
        if success:
            print("Model added successfully.")
        else:
            print("Failed to add model.")
    
    # Verify the model was added
    all_deepseek_models = repo.get_models_by_provider(deepseek_provider.id)
    print(f"\nDeepSeek models in database: {len(all_deepseek_models)}")
    for model in all_deepseek_models:
        print(f"  - {model.name}: {model.description}")


async def demonstrate_llm_agent_with_region(db_url: str):
    """Demonstrate using the LLMAgent with regional model selection.
    
    Args:
        db_url: Database URL
    """
    print("\n=== LLM Agent with Regional Model Selection ===")
    
    # Create an agent with global region preference
    global_agent = LLMAgent(
        name="GlobalAgent",
        region="global",
        db_url=db_url
    )
    
    # Create an agent with Chinese region preference
    chinese_agent = LLMAgent(
        name="ChineseAgent",
        region="cn",
        db_url=db_url
    )
    
    print(f"Global agent model: {global_agent.model_identifier}")
    print(f"Chinese agent model: {chinese_agent.model_identifier}")
    
    # Test an actual completion
    prompt = "What is the capital of France?"
    
    try:
        print("\nGenerating with global agent...")
        result = await global_agent._try_models_with_fallback(prompt, "test-global")
        print(f"Response: {result}")
    except Exception as e:
        print(f"Error with global agent: {str(e)}")
    
    try:
        print("\nGenerating with Chinese agent...")
        result = await chinese_agent._try_models_with_fallback(prompt, "test-chinese")
        print(f"Response: {result}")
    except Exception as e:
        print(f"Error with Chinese agent: {str(e)}")


async def main():
    """Main entry point."""
    # Get database URL from environment
    db_url = os.environ.get("DATABASE_URL", "sqlite:///./data/agi_mcp.db")
    
    # Run demonstrations
    await list_providers_and_models(db_url)
    await add_custom_model_to_database(db_url)
    await demonstrate_text_generation(db_url)
    await demonstrate_llm_agent_with_region(db_url)


if __name__ == "__main__":
    asyncio.run(main()) 