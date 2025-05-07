"""FastAPI server for the AGI-MCP-Agent framework."""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agi_mcp_agent.agent.llm_agent import LLMAgent
from agi_mcp_agent.mcp.core import MasterControlProgram, Task

logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(
    title="AGI-MCP-Agent API",
    description="API for interacting with the AGI-MCP-Agent framework",
    version="0.1.0",
)

# Create the MCP
mcp = MasterControlProgram()

# Create a task to manage the MCP
mcp_task = None


# Models for API requests and responses
class AgentCreate(BaseModel):
    """Model for creating an agent."""

    name: str
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    capabilities: List[str] = Field(default_factory=list)


class AgentResponse(BaseModel):
    """Model for agent responses."""

    id: str
    name: str
    status: str
    capabilities: List[str]


class TaskCreate(BaseModel):
    """Model for creating a task."""

    name: str
    description: str
    priority: int = 5
    metadata: Dict = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)


class TaskResponse(BaseModel):
    """Model for task responses."""

    id: str
    name: str
    description: str
    status: str
    agent_id: Optional[str] = None
    priority: int
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class SystemStatusResponse(BaseModel):
    """Model for system status responses."""

    running: bool
    tasks: Dict
    agents: Dict
    timestamp: str


# Routes
@app.get("/")
async def read_root():
    """Get information about the API."""
    return {
        "name": "AGI-MCP-Agent API",
        "version": "0.1.0",
        "description": "API for interacting with the AGI-MCP-Agent framework",
    }


@app.post("/agents/", response_model=AgentResponse)
async def create_agent(agent: AgentCreate):
    """Create a new agent.

    Args:
        agent: The agent to create

    Returns:
        The created agent
    """
    new_agent = LLMAgent(
        name=agent.name,
        capabilities=agent.capabilities,
        model_name=agent.model_name,
        temperature=agent.temperature,
    )
    
    mcp.register_agent(new_agent)
    
    return {
        "id": new_agent.id,
        "name": new_agent.name,
        "status": new_agent.status,
        "capabilities": new_agent.capabilities,
    }


@app.get("/agents/", response_model=List[AgentResponse])
async def list_agents():
    """List all agents.

    Returns:
        List of agents
    """
    return [
        {
            "id": agent.id,
            "name": agent.name,
            "status": agent.status,
            "capabilities": agent.capabilities,
        }
        for agent in mcp.agents.values()
    ]


@app.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get an agent by ID.

    Args:
        agent_id: The ID of the agent to get

    Returns:
        The agent
    """
    if agent_id not in mcp.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = mcp.agents[agent_id]
    return {
        "id": agent.id,
        "name": agent.name,
        "status": agent.status,
        "capabilities": agent.capabilities,
    }


@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent.

    Args:
        agent_id: The ID of the agent to delete

    Returns:
        Success message
    """
    if agent_id not in mcp.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    mcp.unregister_agent(agent_id)
    return {"message": f"Agent {agent_id} deleted"}


@app.post("/tasks/", response_model=TaskResponse)
async def create_task(task: TaskCreate):
    """Create a new task.

    Args:
        task: The task to create

    Returns:
        The created task
    """
    new_task = Task(
        name=task.name,
        description=task.description,
        priority=task.priority,
        metadata=task.metadata,
        dependencies=task.dependencies,
    )
    
    mcp.add_task(new_task)
    
    return {
        "id": new_task.id,
        "name": new_task.name,
        "description": new_task.description,
        "status": new_task.status,
        "agent_id": new_task.agent_id,
        "priority": new_task.priority,
        "created_at": new_task.created_at.isoformat(),
        "started_at": new_task.started_at.isoformat() if new_task.started_at else None,
        "completed_at": new_task.completed_at.isoformat() if new_task.completed_at else None,
    }


@app.get("/tasks/", response_model=List[TaskResponse])
async def list_tasks():
    """List all tasks.

    Returns:
        List of tasks
    """
    return [
        {
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "status": task.status,
            "agent_id": task.agent_id,
            "priority": task.priority,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        }
        for task in mcp.tasks.values()
    ]


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get a task by ID.

    Args:
        task_id: The ID of the task to get

    Returns:
        The task
    """
    task = mcp.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "id": task.id,
        "name": task.name,
        "description": task.description,
        "status": task.status,
        "agent_id": task.agent_id,
        "priority": task.priority,
        "created_at": task.created_at.isoformat(),
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }


@app.get("/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get the system status.

    Returns:
        The system status
    """
    status = mcp.get_system_status()
    status["timestamp"] = status["timestamp"].isoformat()
    return status


@app.post("/system/start")
async def start_system():
    """Start the MCP.

    Returns:
        Success message
    """
    global mcp_task
    
    if mcp.running:
        return {"message": "System already running"}
    
    # Start the MCP in a separate task
    mcp_task = asyncio.create_task(mcp.start())
    
    return {"message": "System started"}


@app.post("/system/stop")
async def stop_system():
    """Stop the MCP.

    Returns:
        Success message
    """
    global mcp_task
    
    if not mcp.running:
        return {"message": "System not running"}
    
    # Stop the MCP
    mcp.stop()
    if mcp_task:
        await mcp_task
        mcp_task = None
    
    return {"message": "System stopped"}


def start_server():
    """Start the FastAPI server."""
    import uvicorn
    
    # Start the server
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    start_server() 