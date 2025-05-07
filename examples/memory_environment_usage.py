#!/usr/bin/env python3
"""Example demonstrating the use of the MemoryEnvironment in AGI-MCP-Agent."""

import json
import logging
import os
import sys
from typing import Dict, Any

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agi_mcp_agent.environment import MemoryEnvironment

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Demonstrate the use of MemoryEnvironment."""
    logger.info("=== MemoryEnvironment Example ===")
    
    # Create a memory directory if it doesn't exist
    memory_dir = os.path.join(os.path.dirname(__file__), "..", "data", "memories")
    os.makedirs(memory_dir, exist_ok=True)
    
    # Initialize the environment
    memory_env = MemoryEnvironment(
        name="example-memory",
        storage_dir=memory_dir,
        max_history=100
    )
    
    # Store some memories
    store_result = memory_env.execute_action({
        "operation": "store",
        "key": "user_preferences",
        "data": {
            "theme": "dark",
            "language": "en",
            "notifications": True
        },
        "tags": ["preferences", "user", "settings"]
    })
    logger.info(f"Store result: {json.dumps(store_result, indent=2)}")
    
    # Store another memory with expiration
    store_result = memory_env.execute_action({
        "operation": "store",
        "key": "temp_data",
        "data": "This memory will expire in 60 seconds",
        "tags": ["temporary"],
        "expires": 60  # 60 seconds from now
    })
    logger.info(f"Store temporary data result: {json.dumps(store_result, indent=2)}")
    
    # Store information about a conversation
    store_result = memory_env.execute_action({
        "operation": "store",
        "key": "conversation:12345",
        "data": {
            "summary": "User asked about travel recommendations for Japan",
            "sentiment": "positive",
            "topics": ["travel", "Japan", "recommendations"]
        },
        "tags": ["conversation", "travel", "Japan"]
    })
    logger.info(f"Store conversation result: {json.dumps(store_result, indent=2)}")
    
    # Retrieve a memory
    retrieve_result = memory_env.execute_action({
        "operation": "retrieve",
        "key": "user_preferences"
    })
    logger.info(f"Retrieve result: {json.dumps(retrieve_result, indent=2)}")
    
    # Search for memories
    search_result = memory_env.execute_action({
        "operation": "search",
        "query": "Japan",
        "limit": 5
    })
    logger.info(f"Search result: {json.dumps(search_result, indent=2)}")
    
    # Retrieve by tag
    tag_result = memory_env.execute_action({
        "operation": "retrieve_by_tag",
        "tag": "travel",
        "limit": 5
    })
    logger.info(f"Tag search result: {json.dumps(tag_result, indent=2)}")
    
    # List all memories
    list_result = memory_env.execute_action({
        "operation": "list",
        "limit": 10
    })
    logger.info(f"List result: {json.dumps(list_result, indent=2)}")
    
    # Delete a memory
    delete_result = memory_env.execute_action({
        "operation": "delete",
        "key": "temp_data"
    })
    logger.info(f"Delete result: {json.dumps(delete_result, indent=2)}")
    
    # List all memories after deletion
    list_result = memory_env.execute_action({
        "operation": "list",
        "limit": 10
    })
    logger.info(f"List after deletion: {json.dumps(list_result, indent=2)}")
    
    # Advanced usage: Store structured agent context
    store_result = memory_env.execute_action({
        "operation": "store",
        "key": "agent:context:12345",
        "data": {
            "tasks": [
                {"id": "task1", "description": "Research Tokyo attractions", "completed": True},
                {"id": "task2", "description": "Book hotel in Kyoto", "completed": False}
            ],
            "user_id": "user123",
            "session_start": "2025-04-01T10:00:00",
            "conversation_summary": "Planning trip to Japan in May, focusing on Tokyo and Kyoto"
        },
        "tags": ["agent", "context", "Japan", "travel", "task_list"]
    })
    logger.info(f"Store agent context result: {json.dumps(store_result, indent=2)}")
    
    logger.info("Memory environment demonstration completed")


if __name__ == "__main__":
    main() 