"""Component registry classes for the workflow system."""

import logging
from typing import Dict, Optional, Any, Type

from agi_mcp_agent.environment.base import Environment
from agi_mcp_agent.agent.llm_agent import LLMAgent

logger = logging.getLogger(__name__)


class EnvironmentRegistry:
    """Registry for environment instances."""

    def __init__(self):
        """Initialize the environment registry."""
        self.environments: Dict[str, Environment] = {}

    def register(self, name: str, environment: Environment) -> bool:
        """Register an environment with the registry.
        
        Args:
            name: The name to register the environment under
            environment: The environment instance
            
        Returns:
            True if registration was successful, False otherwise
        """
        if name in self.environments:
            logger.warning(f"Environment with name '{name}' already exists. Overwriting.")
            
        self.environments[name] = environment
        logger.info(f"Registered environment '{name}' of type {type(environment).__name__}")
        return True
    
    def get(self, name: str) -> Optional[Environment]:
        """Get an environment by name.
        
        Args:
            name: The name of the environment to retrieve
            
        Returns:
            The environment if found, None otherwise
        """
        if name not in self.environments:
            logger.error(f"Environment '{name}' not found in registry")
            return None
            
        return self.environments[name]
    
    def list(self) -> Dict[str, str]:
        """List all registered environments.
        
        Returns:
            Dict mapping environment names to their types
        """
        return {name: type(env).__name__ for name, env in self.environments.items()}
    
    def remove(self, name: str) -> bool:
        """Remove an environment from the registry.
        
        Args:
            name: The name of the environment to remove
            
        Returns:
            True if removal was successful, False otherwise
        """
        if name not in self.environments:
            logger.warning(f"Cannot remove: Environment '{name}' not found in registry")
            return False
            
        # Close the environment before removing it
        try:
            self.environments[name].close()
        except Exception as e:
            logger.error(f"Error closing environment '{name}': {e}")
            
        del self.environments[name]
        logger.info(f"Removed environment '{name}'")
        return True


class AgentRegistry:
    """Registry for agent instances."""

    def __init__(self):
        """Initialize the agent registry."""
        self.agents: Dict[str, LLMAgent] = {}
        
    def register(self, name: str, agent: LLMAgent) -> bool:
        """Register an agent with the registry.
        
        Args:
            name: The name to register the agent under
            agent: The agent instance
            
        Returns:
            True if registration was successful, False otherwise
        """
        if name in self.agents:
            logger.warning(f"Agent with name '{name}' already exists. Overwriting.")
            
        self.agents[name] = agent
        logger.info(f"Registered agent '{name}' of type {type(agent).__name__}")
        return True
    
    def get(self, name: str) -> Optional[LLMAgent]:
        """Get an agent by name.
        
        Args:
            name: The name of the agent to retrieve
            
        Returns:
            The agent if found, None otherwise
        """
        if name not in self.agents:
            logger.error(f"Agent '{name}' not found in registry")
            return None
            
        return self.agents[name]
    
    def list(self) -> Dict[str, str]:
        """List all registered agents.
        
        Returns:
            Dict mapping agent names to their types
        """
        return {name: type(agent).__name__ for name, agent in self.agents.items()}
    
    def remove(self, name: str) -> bool:
        """Remove an agent from the registry.
        
        Args:
            name: The name of the agent to remove
            
        Returns:
            True if removal was successful, False otherwise
        """
        if name not in self.agents:
            logger.warning(f"Cannot remove: Agent '{name}' not found in registry")
            return False
            
        del self.agents[name]
        logger.info(f"Removed agent '{name}'")
        return True 