#!/usr/bin/env python3
"""Example demonstrating the use of various environments in AGI-MCP-Agent."""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agi_mcp_agent.environment import (
    Environment, 
    APIEnvironment, 
    FileSystemEnvironment, 
    WebEnvironment, 
    DatabaseEnvironment,
    MCPEnvironment,
    MemoryEnvironment
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_filesystem_environment():
    """Demonstrate the use of FileSystemEnvironment."""
    logger.info("=== FileSystemEnvironment Example ===")
    
    # Initialize the environment
    fs_env = FileSystemEnvironment(
        name="example-fs",
        root_dir="./data",
        sandbox=True
    )
    
    # Create a directory
    result = fs_env.execute_action({
        "operation": "mkdir",
        "path": "test_dir"
    })
    logger.info(f"Create directory result: {result}")
    
    # Write a file
    result = fs_env.execute_action({
        "operation": "write",
        "path": "test_dir/hello.txt",
        "content": "Hello, World!\nThis is a test file."
    })
    logger.info(f"Write file result: {result}")
    
    # List directory
    result = fs_env.execute_action({
        "operation": "list",
        "path": "test_dir"
    })
    logger.info(f"List directory result: {json.dumps(result, indent=2)}")
    
    # Read file
    result = fs_env.execute_action({
        "operation": "read",
        "path": "test_dir/hello.txt"
    })
    logger.info(f"Read file result: {json.dumps(result, indent=2)}")
    
    # Delete file
    result = fs_env.execute_action({
        "operation": "delete",
        "path": "test_dir/hello.txt"
    })
    logger.info(f"Delete file result: {result}")


def example_api_environment():
    """Demonstrate the use of APIEnvironment."""
    logger.info("=== APIEnvironment Example ===")
    
    # Initialize the environment
    api_env = APIEnvironment(
        name="example-api",
        base_url="https://httpbin.org",
        headers={"User-Agent": "AGI-MCP-Agent Example"}
    )
    
    # Make a GET request
    result = api_env.execute_action({
        "method": "GET",
        "endpoint": "/get",
        "params": {"foo": "bar", "baz": "qux"}
    })
    logger.info(f"GET request result: {json.dumps(result, indent=2)}")
    
    # Make a POST request
    result = api_env.execute_action({
        "method": "POST",
        "endpoint": "/post",
        "json": {"hello": "world"}
    })
    logger.info(f"POST request result status: {result['status_code']}")


async def example_web_environment():
    """Demonstrate the use of WebEnvironment."""
    logger.info("=== WebEnvironment Example ===")
    
    # Initialize the environment
    web_env = WebEnvironment(
        name="example-web",
        headers={"User-Agent": "AGI-MCP-Agent Example"}
    )
    
    # Visit a URL
    result = web_env.execute_action({
        "action_type": "visit",
        "url": "https://example.com"
    })
    logger.info(f"Visit URL result: Title = {result.get('title', 'N/A')}")
    
    # Extract content
    result = web_env.execute_action({
        "action_type": "extract",
        "selector": "p",
        "selector_type": "css"
    })
    logger.info(f"Extract content result: {json.dumps(result.get('results', []), indent=2)}")
    
    # Get links
    result = web_env.execute_action({
        "action_type": "get_links"
    })
    logger.info(f"Links count: {result.get('count', 0)}")
    
    # Clean up
    await web_env.close_session()


def example_memory_environment():
    """Demonstrate the use of MemoryEnvironment."""
    logger.info("=== MemoryEnvironment Example ===")
    
    # Create a memory directory if it doesn't exist
    memory_dir = os.path.join(os.path.dirname(__file__), "..", "data", "memories")
    os.makedirs(memory_dir, exist_ok=True)
    
    # Initialize the environment
    memory_env = MemoryEnvironment(
        name="example-memory",
        storage_dir=memory_dir
    )
    
    # Store user context
    result = memory_env.execute_action({
        "operation": "store",
        "key": "user_context",
        "data": {
            "name": "John Doe",
            "preferences": {
                "language": "en",
                "theme": "dark"
            },
            "last_interaction": "2025-04-01T12:00:00"
        },
        "tags": ["user", "preferences", "context"]
    })
    logger.info(f"Store user context result: {json.dumps(result, indent=2)}")
    
    # Retrieve the stored memory
    result = memory_env.execute_action({
        "operation": "retrieve",
        "key": "user_context"
    })
    logger.info(f"Retrieve user context result: {json.dumps(result, indent=2)}")
    
    # Store temporary data with expiration
    result = memory_env.execute_action({
        "operation": "store",
        "key": "session_token",
        "data": "abc123xyz789",
        "tags": ["session", "temporary"],
        "expires": 3600  # 1 hour expiry
    })
    logger.info(f"Store temporary data result: {json.dumps(result, indent=2)}")
    
    # List all memories
    result = memory_env.execute_action({
        "operation": "list",
        "limit": 5
    })
    logger.info(f"List memories result: {json.dumps(result, indent=2)}")


def example_mcp_environment():
    """Demonstrate the use of MCPEnvironment."""
    logger.info("=== MCPEnvironment Example ===")
    
    # Define server configurations
    server_configs = {
        "filesystem": {
            "command": "python",
            "args": ["-m", "mcp_server.filesystem"],
            "description": "MCP server for filesystem operations",
            "tools": [
                {"name": "read_file", "description": "Read a file from the filesystem"},
                {"name": "write_file", "description": "Write content to a file"},
                {"name": "list_directory", "description": "List contents of a directory"}
            ]
        },
        "web": {
            "command": "python",
            "args": ["-m", "mcp_server.web"],
            "description": "MCP server for web operations",
            "tools": [
                {"name": "fetch", "description": "Fetch content from a URL"},
                {"name": "search", "description": "Search the web for information"}
            ]
        }
    }
    
    # Initialize the environment
    mcp_env = MCPEnvironment(
        name="example-mcp",
        server_configs=server_configs,
        auto_start=False  # Don't actually start the servers in this example
    )
    
    # List servers
    result = mcp_env.execute_action({
        "operation": "list_servers"
    })
    logger.info(f"List servers result: {json.dumps(result, indent=2)}")
    
    # Get server status
    result = mcp_env.execute_action({
        "operation": "server_status",
        "server_name": "filesystem"
    })
    logger.info(f"Server status result: {json.dumps(result, indent=2)}")
    
    # Simulate listing tools
    result = mcp_env.execute_action({
        "operation": "list_tools",
        "server_name": "filesystem"
    })
    logger.info(f"List tools result: {json.dumps(result, indent=2)}")
    
    # Clean up
    mcp_env.close()


async def main():
    """Run all examples."""
    # Run examples
    example_filesystem_environment()
    example_api_environment()
    await example_web_environment()
    example_memory_environment()
    example_mcp_environment()


if __name__ == "__main__":
    asyncio.run(main()) 