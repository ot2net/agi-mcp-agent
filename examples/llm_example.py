"""Example usage of the LLM functionality in MCP."""

import asyncio
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

from agi_mcp_agent.mcp.core import MasterControlProgram
from agi_mcp_agent.mcp.llm_models import (
    LLMProvider, LLMModel, LLMRequest, LLMEmbeddingRequest
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Run the LLM example."""
    # Load environment variables
    load_dotenv()
    
    # Initialize MCP with database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL environment variable is not set")
        return
        
    mcp = MasterControlProgram(database_url)

    # Get OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable is not set")
        return

    # Register OpenAI provider
    openai_provider = LLMProvider(
        name="openai",
        type="openai",  # Must be one of: 'openai', 'anthropic', 'rest'
        api_key=openai_api_key,
        models=["gpt-3.5-turbo", "gpt-4", "text-embedding-ada-002"],
        metadata={
            "organization": "your-org-id",
            "base_url": "https://api.openai.com/v1"
        }
    )
    provider_id = await mcp.register_llm_provider(openai_provider)
    if not provider_id:
        logger.error("Failed to register OpenAI provider")
        return

    # Register GPT-3.5 model
    gpt35_model = LLMModel(
        provider_id=provider_id,
        model_name="gpt-3.5-turbo",
        capability="chat",
        params={
            "max_tokens": 2000,
            "temperature": 0.7,
            "top_p": 1.0
        }
    )
    model_id = await mcp.register_llm_model(gpt35_model)
    if not model_id:
        logger.error("Failed to register GPT-3.5 model")
        return

    # Generate a completion
    completion_request = LLMRequest(
        model_id=model_id,
        prompt="Write a short poem about artificial intelligence.",
        max_tokens=100,
        temperature=0.8
    )
    completion_response = await mcp.generate_completion(completion_request)
    if completion_response:
        logger.info(f"Completion response: {completion_response.content}")
        logger.info(f"Token usage: {completion_response.usage}")

    # Register embedding model
    embedding_model = LLMModel(
        provider_id=provider_id,
        model_name="text-embedding-ada-002",
        capability="embedding",
        params={
            "dimensions": 1536
        }
    )
    embedding_model_id = await mcp.register_llm_model(embedding_model)
    if not embedding_model_id:
        logger.error("Failed to register embedding model")
        return

    # Generate embeddings
    embedding_request = LLMEmbeddingRequest(
        model_id=embedding_model_id,
        input="This is a test sentence for embedding generation."
    )
    embedding_response = await mcp.generate_embeddings(embedding_request)
    if embedding_response:
        logger.info(f"Generated {len(embedding_response.embeddings)} embeddings")
        logger.info(f"First embedding dimension: {len(embedding_response.embeddings[0])}")
        logger.info(f"Token usage: {embedding_response.usage}")

    # Get system status
    status = await mcp.get_system_status()
    if status:
        logger.info(f"System status: {status.dict()}")


if __name__ == "__main__":
    asyncio.run(main()) 