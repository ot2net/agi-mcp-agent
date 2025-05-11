"""MCP (Multi-Cloud Platform) repository layer."""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from agi_mcp_agent.mcp.models import Agent, Task, TaskDependency, AgentMetric, SystemLog, SystemStatus

logger = logging.getLogger(__name__)


class MCPRepository:
    """Repository for MCP database operations."""

    def __init__(self, database_url: str):
        """Initialize the repository.

        Args:
            database_url: The database connection URL
        """
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)

    def _get_session(self):
        """Get a new database session."""
        return self.Session()

    # Agent operations
    def create_agent(self, agent: Agent) -> Optional[Agent]:
        """Create a new agent.

        Args:
            agent: The agent to create

        Returns:
            The created agent with ID, if successful
        """
        try:
            with self._get_session() as session:
                query = text("""
                    INSERT INTO mcp_agents (name, type, capabilities, status, metadata)
                    VALUES (:name, :type, :capabilities, :status, :metadata)
                    RETURNING id, created_at, updated_at
                """)
                result = session.execute(
                    query,
                    {
                        "name": agent.name,
                        "type": agent.type,
                        "capabilities": agent.capabilities,
                        "status": agent.status,
                        "metadata": agent.metadata
                    }
                ).fetchone()
                session.commit()
                
                if result:
                    agent.id = result[0]
                    agent.created_at = result[1]
                    agent.updated_at = result[2]
                    return agent
        except SQLAlchemyError as e:
            logger.error(f"Error creating agent: {e}")
            return None

    def get_agent(self, agent_id: int) -> Optional[Agent]:
        """Get an agent by ID.

        Args:
            agent_id: The ID of the agent to retrieve

        Returns:
            The agent, if found
        """
        try:
            with self._get_session() as session:
                query = text("SELECT * FROM mcp_agents WHERE id = :id")
                result = session.execute(query, {"id": agent_id}).fetchone()
                if result:
                    return Agent(
                        id=result[0],
                        name=result[1],
                        type=result[2],
                        capabilities=result[3],
                        status=result[4],
                        metadata=result[5],
                        created_at=result[6],
                        updated_at=result[7]
                    )
        except SQLAlchemyError as e:
            logger.error(f"Error getting agent: {e}")
        return None

    # Task operations
    def create_task(self, task: Task) -> Optional[Task]:
        """Create a new task.

        Args:
            task: The task to create

        Returns:
            The created task with ID, if successful
        """
        try:
            with self._get_session() as session:
                query = text("""
                    INSERT INTO mcp_tasks (
                        name, description, status, priority, agent_id,
                        parent_task_id, input_data, output_data, error_message
                    )
                    VALUES (
                        :name, :description, :status, :priority, :agent_id,
                        :parent_task_id, :input_data, :output_data, :error_message
                    )
                    RETURNING id, created_at
                """)
                result = session.execute(
                    query,
                    {
                        "name": task.name,
                        "description": task.description,
                        "status": task.status,
                        "priority": task.priority,
                        "agent_id": task.agent_id,
                        "parent_task_id": task.parent_task_id,
                        "input_data": task.input_data,
                        "output_data": task.output_data,
                        "error_message": task.error_message
                    }
                ).fetchone()
                session.commit()
                
                if result:
                    task.id = result[0]
                    task.created_at = result[1]
                    return task
        except SQLAlchemyError as e:
            logger.error(f"Error creating task: {e}")
            return None

    def update_task_status(self, task_id: int, status: str, 
                          output_data: Optional[Dict] = None,
                          error_message: Optional[str] = None) -> bool:
        """Update a task's status and related fields.

        Args:
            task_id: The ID of the task to update
            status: The new status
            output_data: Optional output data to store
            error_message: Optional error message to store

        Returns:
            Whether the update was successful
        """
        try:
            with self._get_session() as session:
                query = text("""
                    UPDATE mcp_tasks
                    SET status = :status,
                        output_data = COALESCE(:output_data, output_data),
                        error_message = COALESCE(:error_message, error_message),
                        completed_at = CASE 
                            WHEN :status IN ('completed', 'failed') THEN NOW()
                            ELSE completed_at
                        END
                    WHERE id = :id
                """)
                session.execute(
                    query,
                    {
                        "id": task_id,
                        "status": status,
                        "output_data": output_data,
                        "error_message": error_message
                    }
                )
                session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error updating task status: {e}")
            return False

    # System status operations
    def get_system_status(self) -> Optional[SystemStatus]:
        """Get the current system status.

        Returns:
            The current system status
        """
        try:
            with self._get_session() as session:
                # Get agent counts
                agent_query = text("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(CASE WHEN status = 'active' THEN 1 END) as active
                    FROM mcp_agents
                """)
                agent_stats = session.execute(agent_query).fetchone()

                # Get task counts
                task_query = text("""
                    SELECT 
                        COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                        COUNT(CASE WHEN status = 'running' THEN 1 END) as running,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed
                    FROM mcp_tasks
                """)
                task_stats = session.execute(task_query).fetchone()

                return SystemStatus(
                    total_agents=agent_stats[0],
                    active_agents=agent_stats[1],
                    pending_tasks=task_stats[0],
                    running_tasks=task_stats[1],
                    completed_tasks=task_stats[2],
                    failed_tasks=task_stats[3],
                    system_load=0.0  # TODO: Implement actual system load calculation
                )
        except SQLAlchemyError as e:
            logger.error(f"Error getting system status: {e}")
            return None

    # Logging operations
    def add_system_log(self, log: SystemLog) -> bool:
        """Add a system log entry.

        Args:
            log: The log entry to add

        Returns:
            Whether the log was successfully added
        """
        try:
            with self._get_session() as session:
                query = text("""
                    INSERT INTO mcp_system_logs (level, component, message, metadata)
                    VALUES (:level, :component, :message, :metadata)
                """)
                session.execute(
                    query,
                    {
                        "level": log.level,
                        "component": log.component,
                        "message": log.message,
                        "metadata": log.metadata
                    }
                )
                session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error adding system log: {e}")
            return False 