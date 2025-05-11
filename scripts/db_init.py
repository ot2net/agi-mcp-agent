#!/usr/bin/env python
import os
import sys
import logging
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database and import schema."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        # Create engine
        engine = create_engine(database_url)
        
        # Get the path to init.sql
        project_root = Path(__file__).parent.parent
        sql_file = project_root / 'sql' / 'init.sql'
        
        if not sql_file.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_file}")
        
        # Read and execute SQL file
        logger.info("Reading SQL file...")
        with open(sql_file, 'r') as f:
            sql = f.read()
        
        logger.info("Executing SQL commands...")
        with engine.connect() as conn:
            # Split SQL file into individual commands
            commands = sql.split(';')
            for command in commands:
                if command.strip():
                    conn.execute(text(command))
            conn.commit()
        
        logger.info("Database initialization completed successfully!")
        
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    init_database() 