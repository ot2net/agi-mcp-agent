"""FastAPI server for the AGI-MCP-Agent framework."""

import asyncio
import logging
import os
import uuid
import sys
import traceback
import threading
import time
from typing import Dict, List, Optional, Union, Any
from dotenv import load_dotenv
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agi_mcp_agent.agent.llm_agent import LLMAgent
from agi_mcp_agent.mcp.core import MasterControlProgram, Task
from agi_mcp_agent.mcp.llm_models import LLMProvider, LLMModel
from agi_mcp_agent.environment import (
    APIEnvironment,
    FileSystemEnvironment,
    MemoryEnvironment,
    WebEnvironment,
    DatabaseEnvironment,
    MCPEnvironment
)

# Configure logging
log_level = os.getenv("LOGLEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info(f"Setting log level to {log_level}")

# Load environment variables
logger.info("Loading environment variables from .env file")
load_dotenv()

# 改进API密钥的脱敏处理
def mask_sensitive_url(url: str) -> str:
    """Mask sensitive information in database URLs."""
    if '@' in url:
        parts = url.split('@')
        if len(parts) >= 2:
            # 保留协议和用户名，脱敏密码
            user_info = parts[0].split('//')[-1]
            if ':' in user_info:
                username = user_info.split(':')[0]
                return f"{url.split('//')[0]}//{username}:***@{parts[1]}"
    return url

# 获取数据库URL并脱敏日志
database_url = os.getenv("DATABASE_URL")
if not database_url:
    logger.error("DATABASE_URL environment variable is not set")
    raise ValueError("DATABASE_URL environment variable is not set")

# 改进日志输出，使用脱敏函数
logger.info(f"Using database URL: {mask_sensitive_url(database_url)}")

# 改进CORS配置，使其更安全和可配置
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
logger.info(f"Configured CORS origins: {ALLOWED_ORIGINS}")

# Create the FastAPI app
logger.info("Creating FastAPI application")
app = FastAPI(
    title="AGI-MCP-Agent API",
    description="API for interacting with the AGI-MCP-Agent framework",
    version="0.1.0",
)

# 更新CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global variables for MCP
mcp = None
mcp_task = None
environments = {}
is_mcp_running = False

# Create the MCP with database configuration
try:
    logger.info("Initializing Master Control Program")
    mcp = MasterControlProgram(database_url)
    logger.info("MCP initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize MCP: {str(e)}")
    logger.error(traceback.format_exc())
    raise

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests with improved error handling."""
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    
    logger.debug(f"Request: {request.method} {request.url.path} from {client_ip}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.debug(f"Response: {response.status_code} in {process_time:.3f}s")
        
        # 为响应添加处理时间头
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Request error after {process_time:.3f}s: {str(e)}")
        logger.error(traceback.format_exc())
        # 返回适当的错误响应而不是让异常向上传播
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)}
        )

def run_async_in_thread(async_func):
    """Run an async function in a separate thread."""
    loop = asyncio.new_event_loop()
    
    def run_in_thread():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_func)
        
    thread = threading.Thread(target=run_in_thread)
    thread.daemon = True
    thread.start()
    return thread

@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup."""
    global is_mcp_running
    logger.info("Server startup event triggered")
    try:
        logger.info("Starting Master Control Program in background thread")
        # Start MCP in a background thread to avoid blocking the server startup
        mcp_thread = run_async_in_thread(mcp.start())
        app.state.mcp_thread = mcp_thread
        
        is_mcp_running = True
        logger.info("MCP background thread started successfully")
    except Exception as e:
        logger.error(f"Failed to start MCP on startup: {str(e)}")
        logger.error(traceback.format_exc())
        is_mcp_running = False

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    global is_mcp_running
    logger.info("Server shutdown event triggered")
    try:
        # Stop the MCP
        await mcp.stop()
        is_mcp_running = False
        logger.info("MCP stopped successfully on server shutdown")
    except Exception as e:
        logger.error(f"Error stopping MCP on shutdown: {str(e)}")
        logger.error(traceback.format_exc())
        raise

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
    capabilities: Union[List[str], Dict[str, Any], Any] = Field(default_factory=list)


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
    system_load: float
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


# LLM model schema routes
class LLMProviderCreate(BaseModel):
    """Model for creating an LLM provider."""
    name: str  # e.g. 'openai', 'anthropic'
    type: str  # e.g. 'openai', 'anthropic', 'rest'
    api_key: Optional[str] = None
    models: List[str] = []
    metadata: Optional[Dict[str, Any]] = None


class LLMProviderResponse(BaseModel):
    """Model for LLM provider responses."""
    id: int
    name: str
    type: str
    status: str
    models_count: int
    created_at: Optional[str] = None


class LLMModelCreate(BaseModel):
    """Model for creating an LLM model."""
    provider_id: int
    model_name: str
    capability: str
    params: Dict[str, Any] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = None


class LLMModelResponse(BaseModel):
    """Model for LLM model responses."""
    id: int
    provider_id: int
    provider_name: str
    model_name: str
    capability: str
    status: str
    params: Dict[str, Any]
    created_at: Optional[str] = None


# Routes
@app.get("/")
async def read_root():
    """Get information about the API."""
    logger.debug("Handling request to root endpoint")
    return {
        "name": "AGI-MCP-Agent API",
        "version": "0.1.0",
        "description": "API for interacting with the AGI-MCP-Agent framework",
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.debug("Handling health check request")
    return {
        "status": "ok",
        "mcp_running": is_mcp_running,
        "timestamp": str(datetime.now())
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
    
    # 确保 capabilities 被正确处理
    capabilities = new_agent.capabilities
    if capabilities is None:
        capabilities = []
        
    return {
        "id": new_agent.id,
        "name": new_agent.name,
        "status": new_agent.status,
        "capabilities": capabilities,
    }


@app.get("/agents/", response_model=List[AgentResponse])
async def list_agents():
    """List all agents.

    Returns:
        List of agents
    """
    try:
        agents = await mcp.get_all_agents()
        
        agent_responses = []
        for agent in agents:
            # 确保 capabilities 被正确处理，如果是字典则保持原样
            capabilities = agent.capabilities
            if capabilities is None:
                capabilities = []
                
            agent_responses.append({
                "id": str(agent.id),
                "name": agent.name,
                "status": agent.status,
                "capabilities": capabilities,
            })
            
        return agent_responses
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error listing agents: {str(e)}"
        )


@app.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get an agent by ID.

    Args:
        agent_id: The ID of the agent to get

    Returns:
        The agent
    """
    try:
        # 尝试将ID转换为整数
        try:
            agent_id_int = int(agent_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid agent ID format")
            
        agent = mcp.repository.get_agent(agent_id_int)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # 确保 capabilities 被正确处理
        capabilities = agent.capabilities
        if capabilities is None:
            capabilities = []
            
        return {
            "id": str(agent.id),
            "name": agent.name,
            "status": agent.status,
            "capabilities": capabilities,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error getting agent: {str(e)}"
        )


@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent.

    Args:
        agent_id: The ID of the agent to delete

    Returns:
        Success message
    """
    try:
        # 尝试将ID转换为整数
        try:
            agent_id_int = int(agent_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid agent ID format")
            
        success = await mcp.unregister_agent(agent_id_int)
        
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found or could not be deleted")
        
        return {"message": f"Agent {agent_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting agent: {str(e)}"
        )


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
            input_data=task.metadata,
            dependencies=task.dependencies,
        )
        
        created_task = await mcp.add_task(new_task)
        
        if not created_task:
            raise HTTPException(
                status_code=500,
                detail="Failed to create task"
            )
        
        return {
            "id": str(created_task.id),
            "name": created_task.name,
            "description": created_task.description,
            "status": created_task.status,
            "agent_id": created_task.agent_id,
            "priority": created_task.priority,
            "created_at": created_task.created_at.isoformat(),
            "started_at": created_task.started_at.isoformat() if created_task.started_at else None,
            "completed_at": created_task.completed_at.isoformat() if created_task.completed_at else None,
        }
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        logger.error(traceback.format_exc())
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
        tasks = await mcp.get_all_tasks()
        
        return [
            {
                "id": str(task.id),
                "name": task.name,
                "description": task.description,
                "status": task.status,
                "agent_id": task.agent_id,
                "priority": task.priority,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            }
            for task in tasks
        ]
    except Exception as e:
        logger.error(f"Error listing tasks: {str(e)}")
        logger.error(traceback.format_exc())
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
        task = await mcp.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "id": str(task.id),
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
        logger.error(traceback.format_exc())
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
    status = await mcp.get_system_status()
    
    # 将SystemStatus对象转换为字典并处理timestamp
    response = {
        "running": mcp.running,
        "tasks": {
            "pending": status.pending_tasks,
            "running": status.running_tasks,
            "completed": status.completed_tasks,
            "failed": status.failed_tasks
        },
        "agents": {
            "total": status.total_agents,
            "active": status.active_agents
        },
        "system_load": status.system_load,
        "timestamp": status.timestamp.isoformat()
    }
    
    return response


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
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", "8000"))
    
    # Start the server
    uvicorn.run(
        "agi_mcp_agent.api.server:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )


# LLM model routes
@app.post("/llm/providers", response_model=LLMProviderResponse)
async def create_llm_provider(provider: LLMProviderCreate):
    """Create a new LLM provider.

    Args:
        provider: The LLM provider to create

    Returns:
        The created LLM provider
    """
    try:
        new_provider = LLMProvider(
            name=provider.name,
            type=provider.type,
            api_key=provider.api_key,
            models=provider.models,
            metadata=provider.metadata
        )
        
        provider_id = await mcp.register_llm_provider(new_provider)
        
        if not provider_id:
            raise HTTPException(status_code=500, detail="Failed to create LLM provider")
            
        return {
            "id": provider_id,
            "name": new_provider.name,
            "type": new_provider.type,
            "status": "enabled",
            "models_count": len(new_provider.models) if new_provider.models else 0,
            "created_at": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating LLM provider: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error creating LLM provider: {str(e)}")


@app.get("/llm/providers", response_model=List[LLMProviderResponse])
async def list_llm_providers():
    """Get all LLM providers.

    Returns:
        List of all LLM providers
    """
    try:
        providers = await mcp.llm_service.get_all_providers()
        
        if not providers:
            return []
            
        return [
            {
                "id": p.id,
                "name": p.name,
                "type": p.type,
                "status": p.status,
                "models_count": len(await mcp.llm_service.get_models_by_provider(p.id)),
                "created_at": datetime.now().isoformat()  # Assuming creation time
            }
            for p in providers
        ]
    except Exception as e:
        logger.error(f"Error listing LLM providers: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error listing LLM providers: {str(e)}")


@app.get("/llm/providers/{provider_id}", response_model=LLMProviderResponse)
async def get_llm_provider(provider_id: int):
    """Get a specific LLM provider.

    Args:
        provider_id: The provider ID

    Returns:
        The LLM provider
    """
    try:
        provider = await mcp.llm_service.get_provider(provider_id)
        
        if not provider:
            raise HTTPException(status_code=404, detail="LLM provider not found")
            
        return {
            "id": provider.id,
            "name": provider.name,
            "type": provider.type,
            "status": provider.status,
            "models_count": len(await mcp.llm_service.get_models_by_provider(provider.id)),
            "created_at": datetime.now().isoformat()  # Assuming creation time
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting LLM provider: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting LLM provider: {str(e)}")


@app.delete("/llm/providers/{provider_id}")
async def delete_llm_provider(provider_id: int):
    """Delete an LLM provider.

    Args:
        provider_id: The provider ID

    Returns:
        Success message
    """
    try:
        success = await mcp.llm_service.delete_provider(provider_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="LLM provider not found or could not be deleted")
            
        return {"message": f"LLM provider {provider_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting LLM provider: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error deleting LLM provider: {str(e)}")


# LLM models routes
@app.post("/llm/models", response_model=LLMModelResponse)
async def create_llm_model(model: LLMModelCreate):
    """Create a new LLM model.

    Args:
        model: The LLM model to create

    Returns:
        The created LLM model
    """
    try:
        new_model = LLMModel(
            provider_id=model.provider_id,
            model_name=model.model_name,
            capability=model.capability,
            params=model.params,
            metadata=model.metadata
        )
        
        model_id = await mcp.register_llm_model(new_model)
        
        if not model_id:
            raise HTTPException(status_code=500, detail="Failed to create LLM model")
            
        # Get provider information
        provider = await mcp.llm_service.get_provider(model.provider_id)
        
        if not provider:
            provider_name = "Unknown"
        else:
            provider_name = provider.name
            
        return {
            "id": model_id,
            "provider_id": new_model.provider_id,
            "provider_name": provider_name,
            "model_name": new_model.model_name,
            "capability": new_model.capability,
            "status": new_model.status,
            "params": new_model.params,
            "created_at": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating LLM model: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error creating LLM model: {str(e)}")


@app.get("/llm/models", response_model=List[LLMModelResponse])
async def list_llm_models():
    """Get all LLM models.

    Returns:
        List of all LLM models
    """
    try:
        # Get all models from MCP
        models = await mcp.llm_service.get_all_models()
        
        if not models:
            return []
            
        result = []
        for m in models:
            # Get provider information
            provider = await mcp.llm_service.get_provider(m.provider_id)
            
            if not provider:
                provider_name = "Unknown"
            else:
                provider_name = provider.name
                
            result.append({
                "id": m.id,
                "provider_id": m.provider_id,
                "provider_name": provider_name,
                "model_name": m.model_name,
                "capability": m.capability,
                "status": m.status,
                "params": m.params,
                "created_at": datetime.now().isoformat()  # Assuming creation time
            })
            
        return result
    except Exception as e:
        logger.error(f"Error listing LLM models: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error listing LLM models: {str(e)}")


@app.get("/llm/models/{model_id}", response_model=LLMModelResponse)
async def get_llm_model(model_id: int):
    """Get a specific LLM model.

    Args:
        model_id: The model ID

    Returns:
        The LLM model
    """
    try:
        model = await mcp.llm_service.get_model(model_id)
        
        if not model:
            raise HTTPException(status_code=404, detail="LLM model not found")
            
        # Get provider information
        provider = await mcp.llm_service.get_provider(model.provider_id)
        
        if not provider:
            provider_name = "Unknown"
        else:
            provider_name = provider.name
            
        return {
            "id": model.id,
            "provider_id": model.provider_id,
            "provider_name": provider_name,
            "model_name": model.model_name,
            "capability": model.capability,
            "status": model.status,
            "params": model.params,
            "created_at": datetime.now().isoformat()  # Assuming creation time
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting LLM model: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting LLM model: {str(e)}")


@app.delete("/llm/models/{model_id}")
async def delete_llm_model(model_id: int):
    """Delete an LLM model.

    Args:
        model_id: The model ID

    Returns:
        Success message
    """
    try:
        success = await mcp.llm_service.delete_model(model_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="LLM model not found or could not be deleted")
            
        return {"message": f"LLM model {model_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting LLM model: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error deleting LLM model: {str(e)}")


@app.get("/llm/providers/{provider_id}/models", response_model=List[LLMModelResponse])
async def get_provider_models(provider_id: int):
    """Get all models for a specific provider.

    Args:
        provider_id: The provider ID

    Returns:
        List of LLM models for the provider
    """
    try:
        # Check if provider exists
        provider = await mcp.llm_service.get_provider(provider_id)
        
        if not provider:
            raise HTTPException(status_code=404, detail="LLM provider not found")
            
        # Get models for this provider
        models = await mcp.llm_service.get_models_by_provider(provider_id)
        
        if not models:
            return []
            
        result = []
        for m in models:
            result.append({
                "id": m.id,
                "provider_id": m.provider_id,
                "provider_name": provider.name,
                "model_name": m.model_name,
                "capability": m.capability,
                "status": m.status,
                "params": m.params,
                "created_at": datetime.now().isoformat()  # Assuming creation time
            })
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting provider models: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting provider models: {str(e)}")


if __name__ == "__main__":
    start_server() 