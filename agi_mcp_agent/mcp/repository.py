"""MCP (Multi-Cloud Platform) repository layer."""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import traceback

from agi_mcp_agent.mcp.models import Agent, Task, TaskDependency, AgentMetric, SystemLog, SystemStatus

logger = logging.getLogger(__name__)

# 添加一个JSON编码器来处理datetime对象
class DateTimeEncoder(json.JSONEncoder):
    """JSON编码器，用于处理datetime对象。"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def sanitize_for_json(obj):
    """Recursively convert any datetime objects to ISO format strings.
    
    Args:
        obj: The object to sanitize (dict, list, datetime, or other)
        
    Returns:
        The sanitized object, with all datetime objects converted to strings
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(sanitize_for_json(item) for item in obj)
    else:
        return obj


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
                # Sanitize data to handle datetime objects
                sanitized_capabilities = sanitize_for_json(agent.capabilities) if agent.capabilities else None
                sanitized_metadata = sanitize_for_json(agent.metadata) if agent.metadata else None
                
                # Convert Python lists and dicts to JSON
                capabilities_json = json.dumps(sanitized_capabilities) if sanitized_capabilities else None
                metadata_json = json.dumps(sanitized_metadata) if sanitized_metadata else None
                
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
                        "capabilities": capabilities_json,
                        "status": agent.status,
                        "metadata": metadata_json
                    }
                ).fetchone()
                session.commit()
                
                if result:
                    agent.id = result[0]
                    agent.created_at = result[1]
                    agent.updated_at = result[2]
                    return agent
        except Exception as e:
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
                    # Handle JSON serialization/deserialization
                    capabilities = result[3]
                    metadata = result[5]
                    
                    # Convert to Python if stored as JSON string
                    if isinstance(capabilities, str):
                        try:
                            capabilities = json.loads(capabilities)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to decode capabilities JSON for agent {agent_id}")
                            capabilities = {}
                    
                    if isinstance(metadata, str):
                        try:
                            metadata = json.loads(metadata)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to decode metadata JSON for agent {agent_id}")
                            metadata = {}
                            
                    return Agent(
                        id=result[0],
                        name=result[1],
                        type=result[2],
                        capabilities=capabilities,
                        status=result[4],
                        metadata=metadata,
                        created_at=result[6],
                        updated_at=result[7]
                    )
        except SQLAlchemyError as e:
            logger.error(f"Error getting agent: {e}")
        return None

    def delete_agent(self, agent_id: int) -> bool:
        """Delete an agent.

        Args:
            agent_id: The ID of the agent to delete

        Returns:
            Whether the deletion was successful
        """
        try:
            with self._get_session() as session:
                query = text("DELETE FROM mcp_agents WHERE id = :id")
                result = session.execute(query, {"id": agent_id})
                session.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting agent: {e}")
            return False

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
                # Sanitize data to handle datetime objects
                sanitized_input_data = sanitize_for_json(task.input_data) if task.input_data else None
                sanitized_output_data = sanitize_for_json(task.output_data) if task.output_data else None
                
                # Convert Python dicts to JSON
                input_data_json = json.dumps(sanitized_input_data) if sanitized_input_data else None
                output_data_json = json.dumps(sanitized_output_data) if sanitized_output_data else None
                
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
                        "input_data": input_data_json,
                        "output_data": output_data_json,
                        "error_message": task.error_message
                    }
                ).fetchone()
                session.commit()
                
                if result:
                    task.id = result[0]
                    task.created_at = result[1]
                    return task
        except Exception as e:
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
                # Sanitize output_data to handle datetime objects
                sanitized_output_data = sanitize_for_json(output_data) if output_data else None
                
                # Convert output_data dict to JSON string
                output_data_json = json.dumps(sanitized_output_data) if sanitized_output_data else None
                
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
                        "output_data": output_data_json,
                        "error_message": error_message
                    }
                )
                session.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            return False

    # System status operations
    def get_system_status(self) -> SystemStatus:
        """Get current system status.
        
        Returns:
            Current system status information
        """
        with Session(self.engine) as session:
            # Count tasks by status
            total_tasks = session.query(TaskDB).count()
            pending_tasks = session.query(TaskDB).filter(TaskDB.status == "pending").count()
            running_tasks = session.query(TaskDB).filter(TaskDB.status == "running").count()
            completed_tasks = session.query(TaskDB).filter(TaskDB.status == "completed").count()
            failed_tasks = session.query(TaskDB).filter(TaskDB.status == "failed").count()
            
            # Count agents by status
            total_agents = session.query(AgentDB).count()
            active_agents = session.query(AgentDB).filter(AgentDB.status == "active").count()
            idle_agents = session.query(AgentDB).filter(AgentDB.status == "idle").count()
            
            # 实现实际的系统负载计算
            system_load = self._calculate_system_load(session)
            
            return SystemStatus(
                total_tasks=total_tasks,
                pending_tasks=pending_tasks,
                running_tasks=running_tasks,
                completed_tasks=completed_tasks,
                failed_tasks=failed_tasks,
                total_agents=total_agents,
                active_agents=active_agents,
                idle_agents=idle_agents,
                system_load=system_load
            )

    def _calculate_system_load(self, session) -> float:
        """计算实际的系统负载"""
        try:
            import psutil
            
            # CPU使用率 (0-1)
            cpu_percent = psutil.cpu_percent(interval=0.1) / 100.0
            
            # 内存使用率 (0-1)  
            memory_percent = psutil.virtual_memory().percent / 100.0
            
            # 任务负载率 (运行中的任务数 / 活跃代理数)
            running_tasks = session.query(TaskDB).filter(TaskDB.status == "running").count()
            active_agents = session.query(AgentDB).filter(AgentDB.status == "active").count()
            
            task_load = running_tasks / max(active_agents, 1)  # 避免除零错误
            
            # 综合负载计算：CPU权重0.4，内存权重0.3，任务权重0.3
            system_load = (cpu_percent * 0.4) + (memory_percent * 0.3) + (min(task_load, 1.0) * 0.3)
            
            return round(system_load, 3)
            
        except ImportError:
            # 如果psutil不可用，使用简化的任务负载计算
            running_tasks = session.query(TaskDB).filter(TaskDB.status == "running").count()
            active_agents = session.query(AgentDB).filter(AgentDB.status == "active").count()
            
            return running_tasks / max(active_agents, 1)
        except Exception as e:
            logger.warning(f"Error calculating system load: {str(e)}")
            return 0.0

    def get_tasks_by_status(self, status: str) -> List[Task]:
        """获取指定状态的任务列表"""
        with Session(self.engine) as session:
            task_dbs = session.query(TaskDB).filter(TaskDB.status == status).all()
            return [self._db_task_to_model(task_db) for task_db in task_dbs]

    def get_available_agents(self) -> List[Agent]:
        """获取可用的代理列表"""
        with Session(self.engine) as session:
            agent_dbs = session.query(AgentDB).filter(
                AgentDB.status.in_(["active", "idle"])
            ).all()
            return [self._db_agent_to_model(agent_db) for agent_db in agent_dbs]

    def assign_task_to_agent(self, task_id: int, agent_id: int) -> bool:
        """将任务分配给代理"""
        try:
            with Session(self.engine) as session:
                # 更新任务状态和分配的代理
                task_db = session.query(TaskDB).filter(TaskDB.id == task_id).first()
                if not task_db:
                    return False
                
                task_db.agent_id = agent_id
                task_db.status = "assigned"
                task_db.started_at = datetime.utcnow()
                
                # 更新代理状态
                agent_db = session.query(AgentDB).filter(AgentDB.id == agent_id).first()
                if agent_db:
                    agent_db.status = "busy"
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error assigning task {task_id} to agent {agent_id}: {str(e)}")
            return False

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
                # First sanitize the metadata to handle datetime objects
                sanitized_metadata = sanitize_for_json(log.metadata) if log.metadata else None
                
                # Convert metadata dict to JSON string using custom encoder
                metadata_json = json.dumps(sanitized_metadata) if sanitized_metadata else None
                
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
                        "metadata": metadata_json
                    }
                )
                session.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding system log: {e}")
            return False

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID.

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            The task if found, None otherwise
        """
        try:
            with self._get_session() as session:
                query = text("""
                    SELECT id, name, description, status, priority, agent_id,
                           parent_task_id, input_data, output_data, error_message,
                           created_at, started_at, completed_at
                    FROM mcp_tasks
                    WHERE id = :id
                """)
                result = session.execute(query, {"id": task_id}).fetchone()
                
                if not result:
                    return None
                    
                # Convert JSON strings to Python dicts
                input_data = result[7]
                output_data = result[8]
                
                if input_data and isinstance(input_data, str):
                    try:
                        input_data = json.loads(input_data)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to decode input_data JSON for task {task_id}")
                        input_data = {}
                        
                if output_data and isinstance(output_data, str):
                    try:
                        output_data = json.loads(output_data)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to decode output_data JSON for task {task_id}")
                        output_data = {}
                
                return Task(
                    id=result[0],
                    name=result[1],
                    description=result[2],
                    status=result[3],
                    priority=result[4],
                    agent_id=result[5],
                    parent_task_id=result[6],
                    input_data=input_data,
                    output_data=output_data,
                    error_message=result[9],
                    created_at=result[10],
                    started_at=result[11],
                    completed_at=result[12]
                )
        except Exception as e:
            logger.error(f"Error getting task: {e}")
            logger.error(traceback.format_exc())
            return None
            
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks.

        Returns:
            List of all tasks
        """
        tasks = []
        try:
            with self._get_session() as session:
                query = text("""
                    SELECT id, name, description, status, priority, agent_id,
                           parent_task_id, input_data, output_data, error_message,
                           created_at, started_at, completed_at
                    FROM mcp_tasks
                    ORDER BY created_at DESC
                """)
                results = session.execute(query).fetchall()
                
                for result in results:
                    # Convert JSON strings to Python dicts
                    input_data = result[7]
                    output_data = result[8]
                    
                    if input_data and isinstance(input_data, str):
                        try:
                            input_data = json.loads(input_data)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to decode input_data JSON for task {result[0]}")
                            input_data = {}
                            
                    if output_data and isinstance(output_data, str):
                        try:
                            output_data = json.loads(output_data)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to decode output_data JSON for task {result[0]}")
                            output_data = {}
                    
                    task = Task(
                        id=result[0],
                        name=result[1],
                        description=result[2],
                        status=result[3],
                        priority=result[4],
                        agent_id=result[5],
                        parent_task_id=result[6],
                        input_data=input_data,
                        output_data=output_data,
                        error_message=result[9],
                        created_at=result[10],
                        started_at=result[11],
                        completed_at=result[12]
                    )
                    tasks.append(task)
                    
        except Exception as e:
            logger.error(f"Error getting all tasks: {e}")
            logger.error(traceback.format_exc())
        
        return tasks

    def get_all_agents(self) -> List[Agent]:
        """Get all agents.

        Returns:
            List of all agents
        """
        agents = []
        try:
            with self._get_session() as session:
                query = text("""
                    SELECT id, name, type, capabilities, status, metadata, created_at, updated_at
                    FROM mcp_agents
                    ORDER BY created_at DESC
                """)
                results = session.execute(query).fetchall()
                
                for result in results:
                    # Convert JSON strings to Python dicts
                    capabilities = result[3]
                    metadata = result[5]
                    
                    if capabilities and isinstance(capabilities, str):
                        try:
                            capabilities = json.loads(capabilities)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to decode capabilities JSON for agent {result[0]}")
                            capabilities = {}
                            
                    if metadata and isinstance(metadata, str):
                        try:
                            metadata = json.loads(metadata)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to decode metadata JSON for agent {result[0]}")
                            metadata = {}
                    
                    agent = Agent(
                        id=result[0],
                        name=result[1],
                        type=result[2],
                        capabilities=capabilities,
                        status=result[4],
                        metadata=metadata,
                        created_at=result[6],
                        updated_at=result[7]
                    )
                    agents.append(agent)
                    
        except Exception as e:
            logger.error(f"Error getting all agents: {e}")
            logger.error(traceback.format_exc())
        
        return agents 