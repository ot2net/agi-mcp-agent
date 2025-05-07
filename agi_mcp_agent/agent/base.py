"""Base agent class definitions."""

import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Agent(ABC):
    """Base abstract agent class that all agents should inherit from."""

    def __init__(self, name: str, capabilities: List[str] = None):
        """Initialize the agent.

        Args:
            name: The name of the agent
            capabilities: List of capabilities this agent has
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.capabilities = capabilities or []
        self.current_task_id: Optional[str] = None
        self.status = "idle"  # idle, busy, error
        self.memory: Dict[str, Any] = {}
        logger.info(f"Agent {self.name} ({self.id}) initialized")

    def is_available(self) -> bool:
        """Check if the agent is available to take on a new task.

        Returns:
            Whether the agent is available
        """
        return self.status == "idle"

    def assign_task(self, task: Any) -> bool:
        """Assign a task to the agent.

        Args:
            task: The task to assign

        Returns:
            Whether the task was successfully assigned
        """
        if not self.is_available():
            logger.warning(f"Agent {self.id} is not available")
            return False

        self.current_task_id = task.id
        self.status = "busy"
        logger.info(f"Task {task.id} assigned to agent {self.id}")
        
        # Start task execution
        try:
            self.execute_task(task)
            return True
        except Exception as e:
            logger.error(f"Error executing task {task.id}: {str(e)}")
            self.status = "error"
            return False

    @abstractmethod
    def execute_task(self, task: Any) -> None:
        """Execute a task.

        Args:
            task: The task to execute
        """
        pass

    @abstractmethod
    def is_task_complete(self, task_id: str) -> bool:
        """Check if a task is complete.

        Args:
            task_id: The ID of the task to check

        Returns:
            Whether the task is complete
        """
        pass

    def complete_task(self, task_id: str, result: Optional[Any] = None) -> None:
        """Mark a task as complete.

        Args:
            task_id: The ID of the task to complete
            result: The result of the task execution
        """
        if self.current_task_id != task_id:
            logger.warning(f"Task {task_id} is not assigned to agent {self.id}")
            return

        self.current_task_id = None
        self.status = "idle"
        logger.info(f"Task {task_id} completed by agent {self.id}")

    def handle_error(self, task_id: str, error: str) -> None:
        """Handle an error that occurred during task execution.

        Args:
            task_id: The ID of the task that encountered an error
            error: The error message
        """
        if self.current_task_id != task_id:
            logger.warning(f"Task {task_id} is not assigned to agent {self.id}")
            return

        self.status = "error"
        logger.error(f"Error in task {task_id} executed by agent {self.id}: {error}")

    def add_capability(self, capability: str) -> None:
        """Add a capability to the agent.

        Args:
            capability: The capability to add
        """
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            logger.info(f"Added capability {capability} to agent {self.id}")

    def has_capability(self, capability: str) -> bool:
        """Check if the agent has a specific capability.

        Args:
            capability: The capability to check for

        Returns:
            Whether the agent has the specified capability
        """
        return capability in self.capabilities

    def store_in_memory(self, key: str, value: Any) -> None:
        """Store a value in the agent's memory.

        Args:
            key: The key to store the value under
            value: The value to store
        """
        self.memory[key] = value

    def retrieve_from_memory(self, key: str) -> Optional[Any]:
        """Retrieve a value from the agent's memory.

        Args:
            key: The key to retrieve

        Returns:
            The stored value, if found
        """
        return self.memory.get(key)

    def clear_memory(self) -> None:
        """Clear the agent's memory."""
        self.memory.clear()
        logger.info(f"Memory cleared for agent {self.id}")

    def __str__(self) -> str:
        """Get a string representation of the agent.

        Returns:
            String representation
        """
        return f"Agent(id={self.id}, name={self.name}, status={self.status})" 