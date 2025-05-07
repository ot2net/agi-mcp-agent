"""Configuration utilities for AGI-MCP-Agent."""

import json
import logging
import os
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration manager for AGI-MCP-Agent."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the configuration manager.

        Args:
            config_path: Path to a configuration file
        """
        self.config: Dict[str, Any] = {}
        
        # Load config from file if provided
        if config_path:
            self.load_from_file(config_path)
            
        # Load config from environment variables
        self.load_from_env()
        
        logger.info("Configuration loaded")

    def load_from_file(self, config_path: str) -> None:
        """Load configuration from a file.

        Args:
            config_path: Path to the configuration file
        """
        if not os.path.exists(config_path):
            logger.warning(f"Configuration file {config_path} not found")
            return
        
        _, ext = os.path.splitext(config_path)
        try:
            with open(config_path, "r") as f:
                if ext.lower() == ".json":
                    file_config = json.load(f)
                elif ext.lower() in [".yml", ".yaml"]:
                    file_config = yaml.safe_load(f)
                else:
                    logger.warning(f"Unsupported configuration file format: {ext}")
                    return
                
                self.config.update(file_config)
                logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {str(e)}")

    def load_from_env(self) -> None:
        """Load configuration from environment variables with AGI_MCP_ prefix."""
        for key, value in os.environ.items():
            if key.startswith("AGI_MCP_"):
                config_key = key[8:].lower()
                self.config[config_key] = value
                
        logger.info("Loaded configuration from environment variables")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: The configuration key
            default: The default value to return if the key is not found

        Returns:
            The configuration value
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: The configuration key
            value: The configuration value
        """
        self.config[key] = value
        logger.info(f"Set configuration {key}")

    def save_to_file(self, config_path: str) -> bool:
        """Save configuration to a file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Whether the save was successful
        """
        try:
            _, ext = os.path.splitext(config_path)
            with open(config_path, "w") as f:
                if ext.lower() == ".json":
                    json.dump(self.config, f, indent=2)
                elif ext.lower() in [".yml", ".yaml"]:
                    yaml.dump(self.config, f)
                else:
                    logger.warning(f"Unsupported configuration file format: {ext}")
                    return False
                
            logger.info(f"Saved configuration to {config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration to {config_path}: {str(e)}")
            return False

    def __str__(self) -> str:
        """Get a string representation of the configuration.

        Returns:
            String representation
        """
        return str(self.config)


# Global configuration instance
config = Config() 