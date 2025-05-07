"""Base environment interface for agent interactions."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Environment(ABC):
    """Abstract base class for environments that agents can interact with."""

    def __init__(self, name: str):
        """Initialize the environment.

        Args:
            name: The name of the environment
        """
        self.name = name
        logger.info(f"Environment {self.name} initialized")

    @abstractmethod
    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action in the environment.

        Args:
            action: The action to execute

        Returns:
            The result of the action
        """
        pass

    @abstractmethod
    def get_observation(self) -> Dict[str, Any]:
        """Get an observation from the environment.

        Returns:
            The observation
        """
        pass

    @abstractmethod
    def reset(self) -> Dict[str, Any]:
        """Reset the environment to its initial state.

        Returns:
            The initial observation
        """
        pass

    def __str__(self) -> str:
        """Get a string representation of the environment.

        Returns:
            String representation
        """
        return f"Environment(name={self.name})"


class APIEnvironment(Environment):
    """Environment that interfaces with external APIs."""

    def __init__(self, name: str, base_url: str, headers: Dict[str, str] = None):
        """Initialize the API environment.

        Args:
            name: The name of the environment
            base_url: The base URL for API requests
            headers: The headers to use for API requests
        """
        super().__init__(name)
        self.base_url = base_url
        self.headers = headers or {}
        self.state = {}
        logger.info(f"API Environment {self.name} initialized with base URL {base_url}")

    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an API request.

        Args:
            action: The API request to execute

        Returns:
            The response from the API
        """
        # This would normally use requests or a similar library
        # to make the actual API call
        logger.info(f"Executing API request: {action}")
        return {"status": "not_implemented"}

    def get_observation(self) -> Dict[str, Any]:
        """Get the current state of the environment.

        Returns:
            The current state
        """
        return self.state

    def reset(self) -> Dict[str, Any]:
        """Reset the environment state.

        Returns:
            The initial state
        """
        self.state = {}
        return self.state


class FileSystemEnvironment(Environment):
    """Environment that provides access to the file system."""

    def __init__(self, name: str, root_dir: str):
        """Initialize the file system environment.

        Args:
            name: The name of the environment
            root_dir: The root directory for file operations
        """
        super().__init__(name)
        self.root_dir = root_dir
        self.state = {"current_dir": root_dir}
        logger.info(f"FileSystem Environment {self.name} initialized with root dir {root_dir}")

    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a file system operation.

        Args:
            action: The operation to execute

        Returns:
            The result of the operation
        """
        # This would normally implement various file operations
        # such as read, write, list, etc.
        logger.info(f"Executing file system operation: {action}")
        return {"status": "not_implemented"}

    def get_observation(self) -> Dict[str, Any]:
        """Get the current state of the file system.

        Returns:
            The current state
        """
        return self.state

    def reset(self) -> Dict[str, Any]:
        """Reset the environment state.

        Returns:
            The initial state
        """
        self.state = {"current_dir": self.root_dir}
        return self.state 