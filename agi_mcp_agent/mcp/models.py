"""MCP (Multi-Cloud Platform) models."""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class Agent(BaseModel):
    """MCP Agent model."""
    id: Optional[int] = None
    name: str
    type: str
    capabilities: Dict[str, Any]
    status: str = "active"
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Task(BaseModel):
    """MCP Task model."""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    status: str = "pending"
    priority: int = Field(default=5, ge=1, le=10)
    agent_id: Optional[int] = None
    parent_task_id: Optional[int] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TaskDependency(BaseModel):
    """MCP Task Dependency model."""
    task_id: int
    dependency_id: int
    created_at: Optional[datetime] = None


class AgentMetric(BaseModel):
    """MCP Agent Metric model."""
    id: Optional[int] = None
    agent_id: int
    metric_name: str
    metric_value: float
    timestamp: Optional[datetime] = None


class SystemLog(BaseModel):
    """MCP System Log model."""
    id: Optional[int] = None
    level: str
    component: str
    message: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None


class SystemStatus(BaseModel):
    """MCP System Status model."""
    total_agents: int
    active_agents: int
    pending_tasks: int
    running_tasks: int
    completed_tasks: int
    failed_tasks: int
    system_load: float
    timestamp: datetime = Field(default_factory=datetime.now) 