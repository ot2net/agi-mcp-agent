# MCP Environment

The `MCPEnvironment` provides an interface for agents to interact with Model Control Protocol (MCP) servers, enabling tools discovery, invocation, and server lifecycle management.

## Overview

The Model Control Protocol (MCP) is a standardized interface for AI agents to access external tools and capabilities. The `MCPEnvironment` provides a unified way to:

- Manage MCP server lifecycles (start, stop, restart)
- Discover available tools on MCP servers
- Invoke tools with parameters and process results
- Monitor server status and health
- Configure server settings and capabilities

## Initialization

```python
from agi_mcp_agent.environment import MCPEnvironment

# Basic initialization
mcp_env = MCPEnvironment(
    name="example-mcp",
    servers={
        "filesystem": {
            "command": "python -m mcp.servers.filesystem --port 8080",
            "description": "MCP server for filesystem operations"
        },
        "web": {
            "command": "python -m mcp.servers.web --port 8081",
            "description": "MCP server for web operations"
        }
    }
)

# With advanced options
mcp_env = MCPEnvironment(
    name="advanced-mcp",
    servers={
        "filesystem": {
            "command": "python -m mcp.servers.filesystem --port 8080",
            "description": "MCP server for filesystem operations",
            "working_dir": "/path/to/workspace",
            "env_vars": {"DEBUG": "true"},
            "startup_timeout": 30
        }
    },
    auto_start=True,  # Start servers automatically
    startup_timeout=60,  # Global startup timeout
    shutdown_timeout=30  # Global shutdown timeout
)
```

## Basic Operations

### Managing Server Lifecycle

```python
# List all servers
result = mcp_env.execute_action({
    "operation": "list_servers"
})

# Access the server list
if result["success"]:
    servers = result["servers"]
    for server in servers:
        print(f"Server: {server['name']}, Status: {server['status']}")
else:
    print(f"Error: {result['error']}")

# Get a specific server's status
status_result = mcp_env.execute_action({
    "operation": "server_status",
    "server_name": "filesystem"
})
if status_result["success"]:
    status = status_result["status"]
    running = status_result["running"]
    print(f"Server 'filesystem' is {status} (Running: {running})")
```

### Starting and Stopping Servers

```python
# Start a server
start_result = mcp_env.execute_action({
    "operation": "start_server",
    "server_name": "filesystem"
})
if start_result["success"]:
    print(f"Server started with PID {start_result['pid']}")
else:
    print(f"Error starting server: {start_result['error']}")

# Stop a server
stop_result = mcp_env.execute_action({
    "operation": "stop_server",
    "server_name": "filesystem",
    "force": False  # Optional, true to force kill
})
if stop_result["success"]:
    print("Server stopped successfully")

# Restart a server
restart_result = mcp_env.execute_action({
    "operation": "restart_server",
    "server_name": "filesystem"
})
if restart_result["success"]:
    print(f"Server restarted with new PID {restart_result['pid']}")
```

### Discovering Tools

```python
# List all tools on a server
tools_result = mcp_env.execute_action({
    "operation": "list_tools",
    "server_name": "filesystem"
})

# Access the tool list
if tools_result["success"]:
    tools = tools_result["tools"]
    for tool in tools:
        print(f"Tool: {tool['name']}")
        print(f"  Description: {tool['description']}")
        print(f"  Parameters: {tool['parameters']}")
else:
    print(f"Error listing tools: {tools_result['error']}")

# Get details about a specific tool
tool_details = mcp_env.execute_action({
    "operation": "get_tool_details",
    "server_name": "filesystem",
    "tool_name": "read_file"
})
if tool_details["success"]:
    tool = tool_details["tool"]
    print(f"Tool: {tool['name']}")
    print(f"Description: {tool['description']}")
    print(f"Parameters:")
    for param in tool['parameters']:
        print(f"  {param['name']} ({param['type']}): {param['description']}")
```

### Invoking Tools

```python
# Invoke a tool on a server
invoke_result = mcp_env.execute_action({
    "operation": "invoke_tool",
    "server_name": "filesystem",
    "tool_name": "read_file",
    "parameters": {
        "path": "data/config.json",
        "encoding": "utf-8"
    }
})

# Process the tool result
if invoke_result["success"]:
    result = invoke_result["result"]
    print(f"Tool execution succeeded: {result}")
else:
    error = invoke_result["error"]
    print(f"Tool execution failed: {error}")

# Invoke with streaming response
stream_result = mcp_env.execute_action({
    "operation": "invoke_tool_streaming",
    "server_name": "web",
    "tool_name": "search",
    "parameters": {
        "query": "artificial intelligence",
        "num_results": 10
    }
})

# Process streaming results
if stream_result["success"]:
    for chunk in stream_result["chunks"]:
        print(f"Received chunk: {chunk}")
```

## Advanced Features

### Server Configuration

```python
# Update server configuration
config_result = mcp_env.execute_action({
    "operation": "update_server_config",
    "server_name": "filesystem",
    "config": {
        "root_dir": "/new/path",
        "max_file_size": 1024 * 1024 * 10  # 10MB
    }
})
if config_result["success"]:
    print("Server configuration updated")
```

### Server Health Monitoring

```python
# Get server health metrics
health_result = mcp_env.execute_action({
    "operation": "server_health",
    "server_name": "filesystem"
})
if health_result["success"]:
    uptime = health_result["uptime"]
    memory_usage = health_result["memory_usage"]
    cpu_usage = health_result["cpu_usage"]
    request_count = health_result["request_count"]
    
    print(f"Server uptime: {uptime} seconds")
    print(f"Memory usage: {memory_usage} MB")
    print(f"CPU usage: {cpu_usage}%")
    print(f"Request count: {request_count}")
```

### Managing Multiple Servers

```python
# Start all servers
start_all_result = mcp_env.execute_action({
    "operation": "start_all_servers"
})
if start_all_result["success"]:
    print(f"Started {start_all_result['started_count']} servers")
    if start_all_result["failed_servers"]:
        print(f"Failed to start: {start_all_result['failed_servers']}")

# Stop all servers
stop_all_result = mcp_env.execute_action({
    "operation": "stop_all_servers"
})
if stop_all_result["success"]:
    print(f"Stopped {stop_all_result['stopped_count']} servers")
```

### Custom Server Registration

```python
# Register a new server at runtime
register_result = mcp_env.execute_action({
    "operation": "register_server",
    "server_name": "search",
    "server_config": {
        "command": "python -m mcp.servers.search --port 8082",
        "description": "MCP server for search operations",
        "auto_start": True
    }
})
if register_result["success"]:
    print("New server registered")

# Unregister a server
unregister_result = mcp_env.execute_action({
    "operation": "unregister_server",
    "server_name": "search"
})
if unregister_result["success"]:
    print("Server unregistered")
```

## Error Handling

The environment provides detailed error information:

```python
# Handle various error scenarios
result = mcp_env.execute_action({
    "operation": "invoke_tool",
    "server_name": "filesystem",
    "tool_name": "read_file",
    "parameters": {
        "path": "/nonexistent/file.txt"
    }
})

if not result["success"]:
    error_type = result.get("error_type", "unknown")
    error_message = result["error"]
    
    if error_type == "server_not_running":
        print(f"Server error: {error_message}")
        # Start the server
        mcp_env.execute_action({
            "operation": "start_server",
            "server_name": "filesystem"
        })
    elif error_type == "tool_not_found":
        print(f"Tool error: {error_message}")
    elif error_type == "invocation_error":
        print(f"Invocation error: {error_message}")
    else:
        print(f"Other error: {error_message}")
```

## Tool Schema Documentation

The `MCPEnvironment` can generate documentation for available tools:

```python
# Generate tool documentation
docs_result = mcp_env.execute_action({
    "operation": "generate_tool_docs",
    "server_name": "filesystem",
    "format": "markdown"
})
if docs_result["success"]:
    markdown_docs = docs_result["documentation"]
    print(markdown_docs)
    
    # Optionally save to a file
    with open("docs/filesystem_tools.md", "w") as f:
        f.write(markdown_docs)
```

## Example Usage

Complete example of using the `MCPEnvironment`:

```python
from agi_mcp_agent.environment import MCPEnvironment
import time

# Initialize the environment
mcp_env = MCPEnvironment(
    name="example-mcp",
    servers={
        "filesystem": {
            "command": "python -m mcp.servers.filesystem --port 8080",
            "description": "MCP server for filesystem operations"
        },
        "web": {
            "command": "python -m mcp.servers.web --port 8081",
            "description": "MCP server for web operations"
        }
    },
    auto_start=False  # Don't start automatically
)

try:
    # List the servers
    servers_result = mcp_env.execute_action({
        "operation": "list_servers"
    })
    print(f"Available servers: {len(servers_result['servers'])}")
    
    # Start the filesystem server
    mcp_env.execute_action({
        "operation": "start_server",
        "server_name": "filesystem"
    })
    
    # Wait for server to start
    time.sleep(2)
    
    # Check server status
    status_result = mcp_env.execute_action({
        "operation": "server_status",
        "server_name": "filesystem"
    })
    print(f"Server status: {status_result['status']}")
    
    # List available tools
    tools_result = mcp_env.execute_action({
        "operation": "list_tools",
        "server_name": "filesystem"
    })
    
    if tools_result["success"]:
        print(f"Available tools:")
        for tool in tools_result["tools"]:
            print(f"  - {tool['name']}: {tool['description']}")
    
    # Invoke a tool
    invoke_result = mcp_env.execute_action({
        "operation": "invoke_tool",
        "server_name": "filesystem",
        "tool_name": "list_directory",
        "parameters": {
            "path": "."
        }
    })
    
    if invoke_result["success"]:
        print(f"Directory contents: {invoke_result['result']}")
    else:
        print(f"Tool invocation failed: {invoke_result['error']}")
    
finally:
    # Clean up by stopping all servers
    mcp_env.execute_action({
        "operation": "stop_all_servers"
    })
    
    # Close the environment
    mcp_env.close()
``` 