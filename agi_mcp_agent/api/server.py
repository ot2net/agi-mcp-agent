"""FastAPI server for the AGI-MCP-Agent framework."""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agi_mcp_agent.agent.llm_agent import LLMAgent
from agi_mcp_agent.mcp.core import MasterControlProgram, Task
from agi_mcp_agent.environment import (
    APIEnvironment,
    FileSystemEnvironment,
    MemoryEnvironment,
    WebEnvironment,
    DatabaseEnvironment,
    MCPEnvironment
)

logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(
    title="AGI-MCP-Agent API",
    description="API for interacting with the AGI-MCP-Agent framework",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许的前端域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)

# Create the MCP
mcp = MasterControlProgram()

# Create a task to manage the MCP
mcp_task = None

# Dictionary to store environments
environments = {}

# Flag to track if MCP is running
is_mcp_running = False

@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup."""
    global is_mcp_running
    try:
        # Start the MCP
        asyncio.create_task(mcp.start())
        is_mcp_running = True
        logger.info("MCP started successfully on server startup")
    except Exception as e:
        logger.error(f"Failed to start MCP on startup: {str(e)}")
        is_mcp_running = False

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    global is_mcp_running
    try:
        # Stop the MCP
        mcp.stop()
        is_mcp_running = False
        logger.info("MCP stopped successfully on server shutdown")
    except Exception as e:
        logger.error(f"Error stopping MCP on shutdown: {str(e)}")

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


class EnvironmentCreate(BaseModel):
    """Model for creating an environment."""
    
    name: str
    type: str
    config: Dict = Field(default_factory=dict)


class EnvironmentResponse(BaseModel):
    """Model for environment responses."""
    
    id: str
    name: str
    type: str
    status: str = "active"


class EnvironmentActionRequest(BaseModel):
    """Model for environment action requests."""
    
    action: Dict


class EnvironmentActionResponse(BaseModel):
    """Model for environment action responses."""
    
    success: bool
    result: Dict


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
    if not is_mcp_running:
        raise HTTPException(
            status_code=503,
            detail="MCP is not running. Please ensure the system is started."
        )

    try:
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
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating task: {str(e)}"
        )


@app.get("/tasks/", response_model=List[TaskResponse])
async def list_tasks():
    """List all tasks.

    Returns:
        List of tasks
    """
    if not is_mcp_running:
        raise HTTPException(
            status_code=503,
            detail="MCP is not running. Please ensure the system is started."
        )

    try:
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
    except Exception as e:
        logger.error(f"Error listing tasks: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing tasks: {str(e)}"
        )


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get a task by ID.

    Args:
        task_id: The ID of the task to get

    Returns:
        The task
    """
    if not is_mcp_running:
        raise HTTPException(
            status_code=503,
            detail="MCP is not running. Please ensure the system is started."
        )

    try:
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting task: {str(e)}"
        )


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


# Environment routes
@app.post("/environments/", response_model=EnvironmentResponse)
async def create_environment(env: EnvironmentCreate):
    """Create a new environment.
    
    Args:
        env: The environment to create
        
    Returns:
        The created environment
    """
    env_id = str(uuid.uuid4())
    
    try:
        if env.type == "api":
            new_env = APIEnvironment(
                name=env.name,
                base_url=env.config.get("base_url", ""),
                headers=env.config.get("headers", {})
            )
        elif env.type == "filesystem":
            new_env = FileSystemEnvironment(
                name=env.name,
                root_dir=env.config.get("root_dir", "./")
            )
        elif env.type == "memory":
            new_env = MemoryEnvironment(
                name=env.name,
                namespace=env.config.get("namespace", "default")
            )
        elif env.type == "web":
            new_env = WebEnvironment(
                name=env.name,
                user_agent=env.config.get("user_agent", "AGI-MCP-Agent WebEnvironment")
            )
        elif env.type == "database":
            new_env = DatabaseEnvironment(
                name=env.name,
                connection_string=env.config.get("connection_string", "sqlite:///:memory:"),
                engine_params=env.config.get("engine_params", {})
            )
        elif env.type == "mcp":
            new_env = MCPEnvironment(
                name=env.name,
                mcp=mcp
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown environment type: {env.type}")
        
        environments[env_id] = new_env
        
        return {
            "id": env_id,
            "name": new_env.name,
            "type": env.type,
            "status": "active"
        }
    except Exception as e:
        logger.error(f"Error creating environment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating environment: {str(e)}")


@app.get("/environments/", response_model=List[EnvironmentResponse])
async def list_environments():
    """List all environments.
    
    Returns:
        List of environments
    """
    return [
        {
            "id": env_id,
            "name": env.name,
            "type": get_environment_type(env),
            "status": "active"
        }
        for env_id, env in environments.items()
    ]


@app.get("/environments/{env_id}", response_model=EnvironmentResponse)
async def get_environment(env_id: str):
    """Get an environment by ID.
    
    Args:
        env_id: The ID of the environment to get
        
    Returns:
        The environment
    """
    if env_id not in environments:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    env = environments[env_id]
    return {
        "id": env_id,
        "name": env.name,
        "type": get_environment_type(env),
        "status": "active"
    }


@app.delete("/environments/{env_id}")
async def delete_environment(env_id: str):
    """Delete an environment.
    
    Args:
        env_id: The ID of the environment to delete
        
    Returns:
        Success message
    """
    if env_id not in environments:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    env = environments[env_id]
    env.close()  # Close the environment
    
    del environments[env_id]
    return {"message": f"Environment {env_id} deleted"}


@app.post("/environments/{env_id}/action", response_model=EnvironmentActionResponse)
async def execute_environment_action(env_id: str, action_request: EnvironmentActionRequest):
    """Execute an action in an environment.
    
    Args:
        env_id: The ID of the environment
        action_request: The action to execute
        
    Returns:
        The result of the action
    """
    if env_id not in environments:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    env = environments[env_id]
    
    try:
        result = env.execute_action(action_request.action)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        logger.error(f"Error executing action: {str(e)}")
        return {
            "success": False,
            "result": {"error": str(e)}
        }


@app.get("/environments/{env_id}/observation", response_model=Dict)
async def get_environment_observation(env_id: str):
    """Get an observation from an environment.
    
    Args:
        env_id: The ID of the environment
        
    Returns:
        The observation
    """
    if env_id not in environments:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    env = environments[env_id]
    
    try:
        observation = env.get_observation()
        return observation
    except Exception as e:
        logger.error(f"Error getting observation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting observation: {str(e)}")


@app.post("/environments/{env_id}/reset", response_model=Dict)
async def reset_environment(env_id: str):
    """Reset an environment.
    
    Args:
        env_id: The ID of the environment
        
    Returns:
        The initial observation
    """
    if env_id not in environments:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    env = environments[env_id]
    
    try:
        observation = env.reset()
        return observation
    except Exception as e:
        logger.error(f"Error resetting environment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error resetting environment: {str(e)}")


# Helper functions
def get_environment_type(env):
    """Get the type of an environment object.
    
    Args:
        env: The environment object
        
    Returns:
        The type as a string
    """
    if isinstance(env, APIEnvironment):
        return "api"
    elif isinstance(env, FileSystemEnvironment):
        return "filesystem"
    elif isinstance(env, MemoryEnvironment):
        return "memory"
    elif isinstance(env, WebEnvironment):
        return "web"
    elif isinstance(env, DatabaseEnvironment):
        return "database"
    elif isinstance(env, MCPEnvironment):
        return "mcp"
    else:
        return "unknown"
        

def start_server():
    """Start the FastAPI server."""
    import uvicorn
    
    # Start the server
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    start_server() 