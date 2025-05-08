"""
Example usage of the LLM provider system in AGI-MCP-Agent.

This script demonstrates how to:
1. List available providers and models
2. Generate text with different models
3. Compare responses from different models
4. Generate embeddings
5. Handle model fallbacks
"""

import asyncio
import logging
import os
import sys
import time
from typing import Dict, List

# Add the parent directory to the path to ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from agi_mcp_agent.agent.llm_providers.manager import model_manager
from agi_mcp_agent.agent.llm_agent import LLMAgent, MultiToolLLMAgent
from agi_mcp_agent.mcp.core import Task


async def list_providers_and_models():
    """List all available providers and their models."""
    providers = model_manager.list_providers()
    
    print("Available providers:")
    for provider in providers:
        print(f"- {provider}")
    
    print("\nAll models:")
    models = model_manager.list_models()
    for model in models:
        print(f"- {model['provider']}:{model['name']} - {model['description']}")
    
    print("\nCapabilities:")
    capabilities = model_manager.get_capabilities()
    for capability in capabilities:
        models = [f"{m['provider']}:{m['name']}" for m in model_manager.list_models_by_capability(capability.name)]
        print(f"- {capability.name}: {', '.join(models)}")


async def compare_model_responses():
    """Compare responses from different models for the same prompt."""
    prompt = "Explain quantum computing in simple terms."
    
    # Models to compare (adjust based on available providers)
    models_to_try = []
    
    # Try to get models from different providers
    for provider in ["openai", "anthropic", "google", "mistral"]:
        if provider in model_manager.list_providers():
            provider_models = model_manager.list_models_by_provider(provider)
            if provider_models:
                # Get the first model from this provider
                model_id = f"{provider}:{provider_models[0]['name']}"
                models_to_try.append(model_id)
    
    if not models_to_try:
        logger.error("No models available for comparison.")
        return
    
    print(f"\nComparing model responses for prompt: '{prompt}'")
    for model_id in models_to_try:
        try:
            start_time = time.time()
            response = await model_manager.generate_text(
                prompt=prompt,
                model_identifier=model_id,
                temperature=0.7,
                max_tokens=150,  # Limit to short responses for example
            )
            elapsed_time = time.time() - start_time
            
            print(f"\n--- {model_id} (took {elapsed_time:.2f}s) ---")
            print(f"Response: {response.text}")
            print(f"Usage: {response.usage.prompt_tokens} prompt tokens, {response.usage.completion_tokens} completion tokens")
            print(f"Cost: ${response.usage.total_cost:.6f}")
        
        except Exception as e:
            print(f"Error with {model_id}: {str(e)}")


async def generate_embeddings():
    """Generate embeddings for different texts and compare them."""
    texts = [
        "The quick brown fox jumps over the lazy dog.",
        "A fast red fox leaps above the sleeping hound.",
        "Artificial intelligence is transforming the world."
    ]
    
    # Find an embedding model
    embedding_models = model_manager.list_models_by_capability("embeddings")
    if not embedding_models:
        logger.error("No embedding models available.")
        return
    
    model_id = f"{embedding_models[0]['provider']}:{embedding_models[0]['name']}"
    print(f"\nGenerating embeddings with {model_id}")
    
    try:
        embeddings = await model_manager.generate_embeddings(
            texts=texts,
            model_identifier=model_id,
        )
        
        print(f"Generated {len(embeddings)} embeddings, each with dimension {len(embeddings[0])}")
        
        # Show a simple cosine similarity between the first two embeddings
        import numpy as np
        
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
        similarity_1_2 = cosine_similarity(embeddings[0], embeddings[1])
        similarity_1_3 = cosine_similarity(embeddings[0], embeddings[2])
        
        print(f"Similarity between text 1 and 2: {similarity_1_2:.4f}")
        print(f"Similarity between text 1 and 3: {similarity_1_3:.4f}")
        
    except Exception as e:
        print(f"Error generating embeddings: {str(e)}")


async def demonstrate_agent_usage():
    """Demonstrate using LLM agents with the provider system."""
    print("\nDemonstrating LLM agent usage:")
    
    # Create a standard LLM agent
    agent = LLMAgent(
        name="TestAgent",
        capabilities=["text-generation", "question-answering"],
        model_identifier="openai:gpt-3.5-turbo",  # This will fallback to other providers if needed
        temperature=0.7,
    )
    
    # Create a task for the agent
    task = Task(
        id="test-task-1",
        description="Answer a question about space",
        metadata={
            "prompt": "What are black holes and how are they formed?",
            "input_variables": {},
        }
    )
    
    # Execute the task
    agent.execute_task(task)
    
    # Wait for the task to complete
    while not agent.is_task_complete("test-task-1"):
        await asyncio.sleep(0.5)
        print(".", end="", flush=True)
    
    # Get the result
    result = agent.get_task_result("test-task-1")
    print(f"\nResult: {result}")


async def model_fallback_test():
    """Test the model fallback functionality."""
    print("\nTesting model fallback:")
    
    # Create a model list with a mix of valid and invalid models
    models = ["nonexistent:model", "openai:gpt-3.5-turbo"]
    
    prompt = "What is the capital of France?"
    
    # Try each model in sequence
    for model_id in models:
        try:
            print(f"Trying {model_id}...")
            response = await model_manager.generate_text(
                prompt=prompt,
                model_identifier=model_id,
                temperature=0.7,
            )
            print(f"Success with {model_id}: {response.text}")
            break
        except Exception as e:
            print(f"Error with {model_id}: {str(e)}")
            continue
    else:
        print("All models failed.")


async def main():
    """Run the example script."""
    print("=== LLM Provider System Examples ===\n")
    
    # Available providers and models
    await list_providers_and_models()
    
    # Compare model responses
    await compare_model_responses()
    
    # Generate embeddings
    await generate_embeddings()
    
    # Demonstrate agent usage
    await demonstrate_agent_usage()
    
    # Test model fallback
    await model_fallback_test()


if __name__ == "__main__":
    asyncio.run(main())