"""Core Master Control Program implementation."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from agi_mcp_agent.mcp.models import Agent, Task, SystemLog, SystemStatus
from agi_mcp_agent.mcp.repository import MCPRepository
from agi_mcp_agent.mcp.llm_service import LLMService
from agi_mcp_agent.mcp.llm_models import (
    LLMProvider, LLMModel, LLMRequest, LLMResponse,
    LLMEmbeddingRequest, LLMEmbeddingResponse
)

logger = logging.getLogger(__name__)


class MasterControlProgram:
    """Master Control Program for agent orchestration and task management."""

    def __init__(self, database_url: str):
        """Initialize the MCP.

        Args:
            database_url: The database connection URL
        """
        self.repository = MCPRepository(database_url)
        self.llm_service = LLMService(self.repository)
        self.running = False
        self._log_system_event("info", "MCP initialized")

    def _log_system_event(self, level: str, message: str, metadata: Optional[Dict] = None):
        """Log a system event.

        Args:
            level: The log level
            message: The log message
            metadata: Optional metadata to include
        """
        log = SystemLog(
            level=level,
            component="mcp",
            message=message,
            metadata=metadata
        )
        self.repository.add_system_log(log)

    async def register_agent(self, agent: Agent) -> Optional[int]:
        """Register an agent with the MCP.

        Args:
            agent: The agent to register

        Returns:
            The agent's ID if successful
        """
        created_agent = self.repository.create_agent(agent)
        if created_agent and created_agent.id:
            self._log_system_event(
                "info",
                f"Registered agent {created_agent.name}",
                {"agent_id": created_agent.id}
            )
            return created_agent.id
        return None

    async def create_task(self, task: Task) -> Optional[int]:
        """Create a new task.

        Args:
            task: The task to create

        Returns:
            The task's ID if successful
        """
        created_task = self.repository.create_task(task)
        if created_task and created_task.id:
            self._log_system_event(
                "info",
                f"Created task {created_task.name}",
                {"task_id": created_task.id}
            )
            return created_task.id
        return None

    async def update_task_status(self, task_id: int, status: str,
                               output_data: Optional[Dict] = None,
                               error_message: Optional[str] = None) -> bool:
        """Update a task's status.

        Args:
            task_id: The ID of the task to update
            status: The new status
            output_data: Optional output data
            error_message: Optional error message

        Returns:
            Whether the update was successful
        """
        success = self.repository.update_task_status(
            task_id, status, output_data, error_message
        )
        if success:
            self._log_system_event(
                "info",
                f"Updated task {task_id} status to {status}",
                {
                    "task_id": task_id,
                    "status": status,
                    "has_output": bool(output_data),
                    "has_error": bool(error_message)
                }
            )
        return success

    async def get_system_status(self) -> Optional[SystemStatus]:
        """Get the current system status.

        Returns:
            The current system status
        """
        return self.repository.get_system_status()

    # LLM-specific methods
    async def register_llm_provider(self, provider: LLMProvider) -> Optional[int]:
        """Register a new LLM provider.

        Args:
            provider: The provider configuration

        Returns:
            The provider's ID if successful
        """
        provider_id = await self.llm_service.create_provider(provider)
        if provider_id:
            self._log_system_event(
                "info",
                f"Registered LLM provider {provider.name}",
                {"provider_id": provider_id}
            )
        return provider_id

    async def register_llm_model(self, model: LLMModel) -> Optional[int]:
        """Register a new LLM model.

        Args:
            model: The model configuration

        Returns:
            The model's ID if successful
        """
        model_id = await self.llm_service.create_model(model)
        if model_id:
            self._log_system_event(
                "info",
                f"Registered LLM model {model.model_name}",
                {"model_id": model_id}
            )
        return model_id

    async def generate_completion(self, request: LLMRequest) -> Optional[LLMResponse]:
        """Generate a completion using the specified model.

        Args:
            request: The completion request

        Returns:
            The completion response if successful
        """
        response = await self.llm_service.generate_completion(request)
        if response:
            self._log_system_event(
                "info",
                f"Generated completion using model {request.model_id}",
                {
                    "request_id": response.request_id,
                    "model_id": request.model_id,
                    "usage": response.usage
                }
            )
        return response

    async def generate_embeddings(self, request: LLMEmbeddingRequest) -> Optional[LLMEmbeddingResponse]:
        """Generate embeddings using the specified model.

        Args:
            request: The embedding request

        Returns:
            The embedding response if successful
        """
        response = await self.llm_service.generate_embeddings(request)
        if response:
            self._log_system_event(
                "info",
                f"Generated embeddings using model {request.model_id}",
                {
                    "request_id": response.request_id,
                    "model_id": request.model_id,
                    "usage": response.usage
                }
            )
        return response

    async def start(self):
        """Start the MCP."""
        self.running = True
        self._log_system_event("info", "MCP started")

        while self.running:
            try:
                # Get system status
                status = await self.get_system_status()
                if status:
                    # Log system status periodically
                    if status.running_tasks > 0 or status.pending_tasks > 0:
                        self._log_system_event(
                            "debug",
                            "System status update",
                            status.dict()
                        )

                # TODO: Implement task scheduling and agent assignment logic
                # This would involve:
                # 1. Querying for pending tasks
                # 2. Finding available agents
                # 3. Matching tasks to agents based on capabilities
                # 4. Updating task status and agent assignments

                await asyncio.sleep(1)  # Prevent CPU overuse

            except Exception as e:
                self._log_system_event(
                    "error",
                    f"Error in MCP main loop: {str(e)}",
                    {"error": str(e)}
                )
                await asyncio.sleep(5)  # Wait before retrying

    def stop(self):
        """Stop the MCP."""
        self.running = False
        self._log_system_event("info", "MCP stopped") 