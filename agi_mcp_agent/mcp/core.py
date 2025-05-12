"""Core Master Control Program implementation."""

import asyncio
import logging
import sys
import traceback
import time
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
        logger.info("Initializing MasterControlProgram")
        try:
            logger.debug(f"Creating MCPRepository with database URL: {database_url.split('@')[0]}@*****")
            self.repository = MCPRepository(database_url)
            logger.info("Repository initialized successfully")
            
            logger.debug("Initializing LLMService")
            start_time = time.time()
            self.llm_service = LLMService(self.repository)
            logger.info(f"LLMService initialized in {time.time() - start_time:.2f} seconds")
            
            self.running = False
            self._log_system_event("info", "MCP initialized")
            logger.info("MasterControlProgram initialization complete")
        except Exception as e:
            logger.error(f"Error during MCP initialization: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def _log_system_event(self, level: str, message: str, metadata: Optional[Dict] = None):
        """Log a system event.

        Args:
            level: The log level
            message: The log message
            metadata: Optional metadata to include
        """
        try:
            log = SystemLog(
                level=level,
                component="mcp",
                message=message,
                metadata=metadata or {}
            )
            self.repository.add_system_log(log)
            
            # Also log to application logger
            log_method = getattr(logger, level.lower(), logger.info)
            log_method(f"System event: {message}")
        except Exception as e:
            logger.error(f"Error logging system event: {str(e)}")
            logger.error(traceback.format_exc())

    async def register_agent(self, agent: Agent) -> Optional[int]:
        """Register an agent with the MCP.

        Args:
            agent: The agent to register

        Returns:
            The agent's ID if successful
        """
        logger.info(f"Registering agent: {agent.name}")
        try:
            created_agent = self.repository.create_agent(agent)
            if created_agent and created_agent.id:
                logger.info(f"Agent registered successfully with ID: {created_agent.id}")
                self._log_system_event(
                    "info",
                    f"Registered agent {created_agent.name}",
                    {"agent_id": created_agent.id}
                )
                return created_agent.id
            else:
                logger.warning(f"Failed to register agent: {agent.name}")
                return None
        except Exception as e:
            logger.error(f"Error registering agent: {str(e)}")
            logger.error(traceback.format_exc())
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

    async def add_task(self, task: Task) -> Optional[Task]:
        """Add a task to the system.

        Args:
            task: The task to add

        Returns:
            The task with ID if successful, None otherwise
        """
        logger.info(f"Adding task: {task.name}")
        try:
            created_task = self.repository.create_task(task)
            if created_task and created_task.id:
                logger.info(f"Task added successfully with ID: {created_task.id}")
                self._log_system_event(
                    "info", 
                    f"Added task {created_task.name}", 
                    {"task_id": created_task.id}
                )
                return created_task
            else:
                logger.warning(f"Failed to add task: {task.name}")
                return None
        except Exception as e:
            logger.error(f"Error adding task: {str(e)}")
            logger.error(traceback.format_exc())
            return None
            
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID.

        Args:
            task_id: The ID of the task to get

        Returns:
            The task if found, None otherwise
        """
        logger.info(f"Getting task with ID: {task_id}")
        try:
            # Convert string ID to integer
            try:
                task_id_int = int(task_id)
            except ValueError:
                logger.error(f"Invalid task ID format: {task_id}")
                return None
                
            task = self.repository.get_task(task_id_int)
            if task:
                logger.debug(f"Found task: {task.name} (ID: {task.id})")
                return task
            else:
                logger.warning(f"Task with ID {task_id} not found")
                return None
        except Exception as e:
            logger.error(f"Error getting task: {str(e)}")
            logger.error(traceback.format_exc())
            return None
            
    async def get_all_tasks(self) -> List[Task]:
        """Get all tasks.

        Returns:
            List of all tasks
        """
        logger.debug("Getting all tasks")
        try:
            tasks = self.repository.get_all_tasks()
            logger.debug(f"Retrieved {len(tasks)} tasks")
            return tasks
        except Exception as e:
            logger.error(f"Error getting all tasks: {str(e)}")
            logger.error(traceback.format_exc())
            return []

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
        logger.info("Starting MCP main loop")
        try:
            self.running = True
            self._log_system_event("info", "MCP started")

            logger.info("MCP entering main loop")
            while self.running:
                try:
                    # Get system status
                    logger.debug("Fetching system status")
                    status = await self.get_system_status()
                    if status:
                        # Log system status periodically
                        if status.running_tasks > 0 or status.pending_tasks > 0:
                            logger.debug(f"System status: {status.dict()}")
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
                    logger.error(f"Error in MCP main loop iteration: {str(e)}")
                    logger.error(traceback.format_exc())
                    self._log_system_event(
                        "error",
                        f"Error in MCP main loop: {str(e)}",
                        {"error": str(e), "traceback": traceback.format_exc()}
                    )
                    await asyncio.sleep(5)  # Wait before retrying
        except Exception as e:
            logger.error(f"Critical error in MCP start: {str(e)}")
            logger.error(traceback.format_exc())
            self._log_system_event(
                "error",
                f"Critical error in MCP start: {str(e)}",
                {"error": str(e), "traceback": traceback.format_exc()}
            )
            raise

    async def stop(self):
        """Stop the MCP."""
        logger.info("Stopping MCP")
        self.running = False
        self._log_system_event("info", "MCP stopped")
        logger.info("MCP has been stopped")

    async def get_all_agents(self) -> List[Agent]:
        """Get all agents.

        Returns:
            List of all agents
        """
        logger.debug("Getting all agents")
        try:
            agents = self.repository.get_all_agents()
            logger.debug(f"Retrieved {len(agents)} agents")
            return agents
        except Exception as e:
            logger.error(f"Error getting all agents: {str(e)}")
            logger.error(traceback.format_exc())
            return []

    async def unregister_agent(self, agent_id: int) -> bool:
        """Unregister an agent from the MCP.

        Args:
            agent_id: The ID of the agent to unregister

        Returns:
            Whether the unregistration was successful
        """
        logger.info(f"Unregistering agent with ID: {agent_id}")
        try:
            # 尝试获取 agent 以确认它存在
            agent = self.repository.get_agent(agent_id)
            if not agent:
                logger.warning(f"Cannot unregister agent {agent_id}: not found")
                return False
                
            # 从数据库中删除 agent
            success = self.repository.delete_agent(agent_id)
            if success:
                logger.info(f"Agent {agent_id} unregistered successfully")
                self._log_system_event(
                    "info",
                    f"Unregistered agent {agent.name}",
                    {"agent_id": agent_id}
                )
                return True
            else:
                logger.warning(f"Failed to unregister agent {agent_id}")
                return False
        except Exception as e:
            logger.error(f"Error unregistering agent: {str(e)}")
            logger.error(traceback.format_exc())
            return False 