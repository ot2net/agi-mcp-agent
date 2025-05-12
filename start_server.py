#!/usr/bin/env python
"""Server starter script that directly runs the original app with minimal changes."""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("server_starter")

# Set modules to debug
for module in ["agi_mcp_agent.mcp.core", "agi_mcp_agent.mcp.repository", 
               "agi_mcp_agent.mcp.llm_service", "agi_mcp_agent.api.server"]:
    logging.getLogger(module).setLevel(logging.DEBUG)

def main():
    """Main function that starts the server."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Set log level via environment variable before importing server
        os.environ["AGI_MCP_LOG_LEVEL"] = "DEBUG"
        
        # Get database URL
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("DATABASE_URL environment variable not set")
            sys.exit(1)
            
        logger.info(f"Using database URL: {database_url.split('@')[0]}@*****")
        
        # Get port from environment or use default
        port = int(os.getenv("PORT", "8000"))
        logger.info(f"Starting server on port {port}")
        
        # Run the server with the original app
        import uvicorn
        
        logger.info("Starting server with original app")
        uvicorn.run(
            "agi_mcp_agent.api.server:app",
            host="0.0.0.0",
            port=port,
            log_level="debug",
            reload=True
        )
        
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 