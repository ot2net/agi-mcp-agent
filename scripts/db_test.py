#!/usr/bin/env python
import os
import sys
import logging
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_database():
    """Test database connection and schema."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        logger.info("Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.scalar()
            logger.info(f"Connected to PostgreSQL version: {version}")
        
        # Get inspector
        inspector = inspect(engine)
        
        # Test required tables
        required_tables = [
            'mcp_agents',
            'mcp_tasks',
            'mcp_task_dependencies',
            'mcp_agent_metrics',
            'mcp_system_logs',
            'llm_providers',
            'llm_models',
            'llm_embeddings',
            'llm_tasks'
        ]
        
        # Check tables
        logger.info("Checking database tables...")
        existing_tables = inspector.get_table_names()
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            logger.error(f"Missing tables: {', '.join(missing_tables)}")
            sys.exit(1)
        
        logger.info("All required tables exist!")
        
        # Test extensions
        logger.info("Checking required extensions...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT extname FROM pg_extension;"))
            extensions = [row[0] for row in result]
            
            required_extensions = ['vector', 'pgcrypto']
            missing_extensions = [ext for ext in required_extensions if ext not in extensions]
            
            if missing_extensions:
                logger.error(f"Missing extensions: {', '.join(missing_extensions)}")
                sys.exit(1)
            
            logger.info("All required extensions are installed!")
        
        # Test basic insert operations
        logger.info("Testing basic insert operations...")
        with engine.connect() as conn:
            # Test MCP agent insert
            conn.execute(text("""
                INSERT INTO mcp_agents (name, type, capabilities)
                VALUES ('test_agent', 'test', '{"test": true}'::jsonb)
                RETURNING id;
            """))
            
            # Test LLM provider insert
            conn.execute(text("""
                INSERT INTO llm_providers (name, type, api_key, models)
                VALUES ('test_provider', 'test', 'test_key', ARRAY['test_model'])
                RETURNING id;
            """))
            
            conn.commit()
            logger.info("Basic insert operations successful!")
        
        logger.info("Database test completed successfully!")
        
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_database() 