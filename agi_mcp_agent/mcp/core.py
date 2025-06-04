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
        """Start the MCP.

        This will start background tasks for:
        - Task scheduling and agent assignment
        - System monitoring and health checks
        - Resource management
        """
        if self.running:
            logger.warning("MCP is already running")
            return

        logger.info("Starting Master Control Program")
        self.running = True

        # Log startup event
        self._log_system_event("info", "MCP started")

        try:
            # 实现基本的任务调度循环
            while self.running:
                await self._process_task_queue()
                await self._monitor_system_health()
                await asyncio.sleep(1)  # 调度间隔为1秒
                
        except asyncio.CancelledError:
            logger.info("MCP task loop cancelled")
        except Exception as e:
            logger.error(f"Error in MCP main loop: {str(e)}")
            logger.error(traceback.format_exc())
            self._log_system_event("error", f"MCP main loop error: {str(e)}")
        finally:
            self.running = False
            self._log_system_event("info", "MCP stopped")

    async def _process_task_queue(self):
        """处理任务队列，实现任务调度和代理分配逻辑"""
        try:
            # 获取待处理的任务
            pending_tasks = self.repository.get_tasks_by_status("pending")
            if not pending_tasks:
                return

            # 获取可用的代理
            available_agents = self.repository.get_available_agents()
            if not available_agents:
                logger.debug("No available agents for task assignment")
                return

            # 简单的轮询调度算法
            for i, task in enumerate(pending_tasks[:len(available_agents)]):
                agent = available_agents[i % len(available_agents)]
                
                # 分配任务给代理
                success = self.repository.assign_task_to_agent(task.id, agent.id)
                if success:
                    logger.info(f"Assigned task {task.id} to agent {agent.id}")
                    self._log_system_event(
                        "info", 
                        f"Task assigned: {task.name} to agent {agent.name}",
                        {"task_id": task.id, "agent_id": agent.id}
                    )
                else:
                    logger.warning(f"Failed to assign task {task.id} to agent {agent.id}")

        except Exception as e:
            logger.error(f"Error in task queue processing: {str(e)}")
            logger.error(traceback.format_exc())

    async def _monitor_system_health(self):
        """监控系统健康状态"""
        try:
            # 检查代理状态
            agents = self.repository.get_all_agents()
            active_agents = [agent for agent in agents if agent.status == "active"]
            
            # 检查任务状态
            all_tasks = self.repository.get_all_tasks()
            running_tasks = [task for task in all_tasks if task.status == "running"]
            
            # 计算系统负载（简单实现）
            if active_agents:
                system_load = len(running_tasks) / len(active_agents)
            else:
                system_load = 0.0

            # 如果系统负载过高，记录警告
            if system_load > 5.0:  # 每个代理平均超过5个任务
                self._log_system_event(
                    "warning", 
                    f"High system load detected: {system_load:.2f}",
                    {"system_load": system_load, "active_agents": len(active_agents), "running_tasks": len(running_tasks)}
                )

        except Exception as e:
            logger.error(f"Error in system health monitoring: {str(e)}")
            logger.error(traceback.format_exc())

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
            # Try to get the agent to confirm it exists
            agent = self.repository.get_agent(agent_id)
            if not agent:
                logger.warning(f"Cannot unregister agent {agent_id}: not found")
                return False
                
            # Delete the agent from the database
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