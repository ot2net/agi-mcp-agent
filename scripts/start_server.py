#!/usr/bin/env python
"""Script to start the AGI-MCP-Agent API server."""

import os
import logging
from dotenv import load_dotenv
from agi_mcp_agent.api.server import start_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Start the API server."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Check required environment variables
        required_vars = ["DATABASE_URL"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return
        
        # Start the server
        logger.info("Starting AGI-MCP-Agent API server...")
        start_server()
        
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        raise

if __name__ == "__main__":
    main() 