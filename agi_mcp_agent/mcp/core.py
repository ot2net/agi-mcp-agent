"""Core Master Control Program implementation."""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field

from agi_mcp_agent.agent.base import Agent

logger = logging.getLogger(__name__)


class Task(BaseModel):
    """Task representation for the MCP scheduler."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    status: str = "pending"  # pending, running, completed, failed
    agent_id: Optional[str] = None
    priority: int = 5  # 1-10 scale, 10 being highest
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    dependencies: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MasterControlProgram:
    """Master Control Program for agent orchestration and task management."""

    def __init__(self):
        """Initialize the MCP."""
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.running = False
        logger.info("Master Control Program initialized")

    def register_agent(self, agent: Agent) -> str:
        """Register an agent with the MCP.

        Args:
            agent: The agent to register

        Returns:
            The agent's ID
        """
        if agent.id in self.agents:
            logger.warning(f"Agent {agent.id} already registered")
            return agent.id

        self.agents[agent.id] = agent
        logger.info(f"Registered agent {agent.id}")
        return agent.id

    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the MCP.

        Args:
            agent_id: The ID of the agent to unregister

        Returns:
            Whether the agent was successfully unregistered
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found")
            return False

        del self.agents[agent_id]
        logger.info(f"Unregistered agent {agent_id}")
        return True

    def add_task(self, task: Task) -> str:
        """Add a task to the MCP scheduler.

        Args:
            task: The task to add

        Returns:
            The task ID
        """
        self.tasks[task.id] = task
        logger.info(f"Added task {task.id}: {task.name}")
        return task.id

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID.

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            The task, if found
        """
        return self.tasks.get(task_id)

    def _get_next_task(self) -> Optional[Task]:
        """Get the next available task based on priority and dependencies.

        Returns:
            The next task to execute, if any
        """
        available_tasks = []
        for task in self.tasks.values():
            if task.status != "pending":
                continue

            # Check dependencies
            dependencies_met = True
            for dep_id in task.dependencies:
                dep_task = self.tasks.get(dep_id)
                if not dep_task or dep_task.status != "completed":
                    dependencies_met = False
                    break

            if dependencies_met:
                available_tasks.append(task)

        if not available_tasks:
            return None

        # Sort by priority (highest first)
        available_tasks.sort(key=lambda t: t.priority, reverse=True)
        return available_tasks[0]

    def _assign_task_to_agent(self, task: Task) -> bool:
        """Assign a task to an available agent.

        Args:
            task: The task to assign

        Returns:
            Whether the task was successfully assigned
        """
        # Simple round-robin assignment for now
        # This should be replaced with a more sophisticated algorithm
        # that considers agent capabilities, load, etc.
        for agent_id, agent in self.agents.items():
            if agent.is_available():
                task.agent_id = agent_id
                task.status = "running"
                task.started_at = datetime.now()
                agent.assign_task(task)
                logger.info(f"Assigned task {task.id} to agent {agent_id}")
                return True

        logger.warning(f"No available agents to handle task {task.id}")
        return False

    async def start(self):
        """Start the MCP."""
        self.running = True
        logger.info("Master Control Program started")

        while self.running:
            # Process scheduling
            next_task = self._get_next_task()
            if next_task and not self._assign_task_to_agent(next_task):
                # No agents available, wait a bit
                await asyncio.sleep(1)
                continue

            # Update task statuses
            for agent_id, agent in self.agents.items():
                if not agent.is_available() and agent.current_task_id:
                    task_id = agent.current_task_id
                    if task_id in self.tasks and self.tasks[task_id].status == "running":
                        if agent.is_task_complete(task_id):
                            self.tasks[task_id].status = "completed"
                            self.tasks[task_id].completed_at = datetime.now()
                            logger.info(f"Task {task_id} completed by agent {agent_id}")

            await asyncio.sleep(0.1)  # Prevent CPU overuse

    def stop(self):
        """Stop the MCP."""
        self.running = False
        logger.info("Master Control Program stopped")

    def get_system_status(self) -> Dict[str, Any]:
        """Get the current system status.

        Returns:
            A dictionary containing system status information
        """
        task_stats = {
            "pending": sum(1 for t in self.tasks.values() if t.status == "pending"),
            "running": sum(1 for t in self.tasks.values() if t.status == "running"),
            "completed": sum(1 for t in self.tasks.values() if t.status == "completed"),
            "failed": sum(1 for t in self.tasks.values() if t.status == "failed"),
        }

        agent_stats = {
            "total": len(self.agents),
            "available": sum(1 for a in self.agents.values() if a.is_available()),
            "busy": sum(1 for a in self.agents.values() if not a.is_available()),
        }

        return {
            "running": self.running,
            "tasks": task_stats,
            "agents": agent_stats,
            "timestamp": datetime.now(),
        } 