"""MCP environment implementation for agent interactions with MCP servers."""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Union

from agi_mcp_agent.environment.base import Environment

logger = logging.getLogger(__name__)


class MCPEnvironment(Environment):
    """Environment that provides access to Model Context Protocol (MCP) servers."""

    def __init__(
        self, 
        name: str, 
        server_configs: Dict[str, Dict[str, Any]],
        auto_start: bool = True,
        timeout: int = 30
    ):
        """Initialize the MCP environment.

        Args:
            name: The name of the environment
            server_configs: Dictionary mapping server names to server configurations
            auto_start: Whether to automatically start servers that aren't running
            timeout: Timeout in seconds for server operations
        """
        super().__init__(name)
        self.server_configs = server_configs
        self.auto_start = auto_start
        self.timeout = timeout
        self.running_servers = {}
        self.connections = {}
        
        self.state = {
            "servers": {},
            "last_error": None
        }
        
        # Initialize server states
        for server_name, config in self.server_configs.items():
            self.state["servers"][server_name] = {
                "status": "not_started",
                "config": config,
                "pid": None,
                "last_error": None
            }
        
        logger.info(f"MCP Environment {self.name} initialized with {len(server_configs)} servers") 

    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP server operation.

        Args:
            action: The operation to execute with the following keys:
                - operation: The operation to perform (start_server, stop_server, etc.)
                - additional operation-specific parameters

        Returns:
            The result of the operation
        """
        operation = action.get("operation", "").lower()
        
        try:
            if operation == "start_server":
                return self._start_server(
                    server_name=action.get("server_name", ""),
                    wait=action.get("wait", True)
                )
            elif operation == "stop_server":
                return self._stop_server(
                    server_name=action.get("server_name", "")
                )
            elif operation == "list_servers":
                return self._list_servers()
            elif operation == "server_status":
                return self._server_status(
                    server_name=action.get("server_name", "")
                )
            elif operation == "list_tools":
                return self._list_tools(
                    server_name=action.get("server_name", "")
                )
            elif operation == "call_tool":
                return self._call_tool(
                    server_name=action.get("server_name", ""),
                    tool_name=action.get("tool_name", ""),
                    arguments=action.get("arguments", {})
                )
            else:
                logger.warning(f"Unknown MCP operation: {operation}")
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            logger.error(f"Error in MCP operation {operation}: {str(e)}")
            self.state["last_error"] = str(e)
            return {"success": False, "error": str(e)} 

    def _start_server(self, server_name: str, wait: bool = True) -> Dict[str, Any]:
        """Start an MCP server.

        Args:
            server_name: The name of the server to start
            wait: Whether to wait for the server to be ready

        Returns:
            Server start status
        """
        if not server_name:
            return {"success": False, "error": "No server name provided"}
            
        if server_name not in self.server_configs:
            return {"success": False, "error": f"Server '{server_name}' not configured"}
            
        # Check if server is already running
        server_status = self._server_status(server_name)
        if server_status.get("running", False):
            return {"success": True, "already_running": True, "server_name": server_name}
            
        config = self.server_configs[server_name]
        command = config.get("command")
        args = config.get("args", [])
        env = {**os.environ, **(config.get("env", {}))}
        
        if not command:
            return {"success": False, "error": f"No command specified for server '{server_name}'"}
            
        try:
            # Start the server process
            process = subprocess.Popen(
                [command] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                start_new_session=True  # Create a new process group
            )
            
            # Update server state
            self.running_servers[server_name] = process
            self.state["servers"][server_name]["status"] = "starting"
            self.state["servers"][server_name]["pid"] = process.pid
            
            if wait:
                # Wait for server to be ready
                ready = False
                start_time = time.time()
                while time.time() - start_time < self.timeout:
                    # Check if process is still running
                    if process.poll() is not None:
                        # Process exited
                        stdout, stderr = process.communicate()
                        error_msg = f"Server process exited with code {process.returncode}: {stderr}"
                        logger.error(error_msg)
                        self.state["servers"][server_name]["status"] = "failed"
                        self.state["servers"][server_name]["last_error"] = error_msg
                        return {"success": False, "error": error_msg}
                    
                    # Try to connect to the server
                    try:
                        # For simplicity, we're just checking if the process is running
                        # In a real implementation, you'd check if the server is accepting connections
                        ready = True
                        break
                    except Exception:
                        # Not ready yet, wait a bit
                        time.sleep(0.5)
                
                if not ready:
                    # Timeout waiting for server
                    error_msg = f"Timeout waiting for server '{server_name}' to be ready"
                    logger.error(error_msg)
                    self._stop_server(server_name)  # Cleanup
                    self.state["servers"][server_name]["status"] = "failed"
                    self.state["servers"][server_name]["last_error"] = error_msg
                    return {"success": False, "error": error_msg}
            
            # Server started successfully
            self.state["servers"][server_name]["status"] = "running"
            logger.info(f"Started MCP server '{server_name}' (PID: {process.pid})")
            
            return {
                "success": True,
                "server_name": server_name,
                "pid": process.pid,
                "ready": wait
            }
            
        except Exception as e:
            error_msg = f"Error starting server '{server_name}': {str(e)}"
            logger.error(error_msg)
            self.state["servers"][server_name]["status"] = "failed"
            self.state["servers"][server_name]["last_error"] = error_msg
            return {"success": False, "error": error_msg}

    def _stop_server(self, server_name: str) -> Dict[str, Any]:
        """Stop an MCP server.

        Args:
            server_name: The name of the server to stop

        Returns:
            Server stop status
        """
        if not server_name:
            return {"success": False, "error": "No server name provided"}
            
        if server_name not in self.server_configs:
            return {"success": False, "error": f"Server '{server_name}' not configured"}
            
        # Check if server is running
        if server_name not in self.running_servers:
            return {"success": True, "already_stopped": True, "server_name": server_name}
            
        process = self.running_servers[server_name]
        
        try:
            # Try to terminate the process gracefully
            if process.poll() is None:  # Process is still running
                # Send SIGTERM to the process group
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                
                # Wait for process to exit
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't exit gracefully
                    logger.warning(f"Server '{server_name}' did not exit gracefully, force killing...")
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            
            # Clean up
            stdout, stderr = process.communicate()
            del self.running_servers[server_name]
            
            # Update server state
            self.state["servers"][server_name]["status"] = "stopped"
            self.state["servers"][server_name]["pid"] = None
            
            logger.info(f"Stopped MCP server '{server_name}'")
            
            return {
                "success": True,
                "server_name": server_name,
                "exit_code": process.returncode
            }
            
        except Exception as e:
            error_msg = f"Error stopping server '{server_name}': {str(e)}"
            logger.error(error_msg)
            self.state["servers"][server_name]["last_error"] = error_msg
            return {"success": False, "error": error_msg}

    def _list_servers(self) -> Dict[str, Any]:
        """List all configured MCP servers.

        Returns:
            List of servers with their status
        """
        servers = []
        for name, state in self.state["servers"].items():
            servers.append({
                "name": name,
                "status": state["status"],
                "pid": state["pid"],
                "description": self.server_configs[name].get("description", ""),
                "last_error": state["last_error"]
            })
        
        return {
            "success": True,
            "servers": servers,
            "count": len(servers)
        }

    def _server_status(self, server_name: str) -> Dict[str, Any]:
        """Get the status of an MCP server.

        Args:
            server_name: The name of the server

        Returns:
            Server status
        """
        if not server_name:
            return {"success": False, "error": "No server name provided"}
            
        if server_name not in self.server_configs:
            return {"success": False, "error": f"Server '{server_name}' not configured"}
            
        state = self.state["servers"].get(server_name, {})
        running = server_name in self.running_servers and self.running_servers[server_name].poll() is None
        
        # Update state if it's inconsistent
        if running and state.get("status") != "running":
            state["status"] = "running"
        elif not running and state.get("status") == "running":
            state["status"] = "stopped"
            state["pid"] = None
        
        return {
            "success": True,
            "server_name": server_name,
            "status": state.get("status", "unknown"),
            "running": running,
            "pid": state.get("pid"),
            "last_error": state.get("last_error")
        }

    def _list_tools(self, server_name: str) -> Dict[str, Any]:
        """List the tools available on an MCP server.

        Args:
            server_name: The name of the server

        Returns:
            List of available tools
        """
        if not server_name:
            return {"success": False, "error": "No server name provided"}
            
        try:
            connection = self._ensure_connection(server_name)
            
            # In a real implementation, you would call the server's list_tools method
            # For this example, we'll return simulated tools based on the server config
            config = self.server_configs[server_name]
            tools = config.get("tools", [])
            
            if not tools:
                # Simulate some default tools based on the server name
                if "file" in server_name.lower() or "fs" in server_name.lower():
                    tools = [
                        {"name": "read_file", "description": "Read a file from the filesystem"},
                        {"name": "write_file", "description": "Write content to a file"},
                        {"name": "list_directory", "description": "List contents of a directory"}
                    ]
                elif "web" in server_name.lower() or "fetch" in server_name.lower():
                    tools = [
                        {"name": "fetch", "description": "Fetch content from a URL"},
                        {"name": "search", "description": "Search the web for information"}
                    ]
                elif "db" in server_name.lower() or "database" in server_name.lower():
                    tools = [
                        {"name": "query", "description": "Execute a database query"},
                        {"name": "list_tables", "description": "List tables in the database"}
                    ]
            
            return {
                "success": True,
                "server_name": server_name,
                "tools": tools,
                "count": len(tools)
            }
            
        except Exception as e:
            error_msg = f"Error listing tools for server '{server_name}': {str(e)}"
            logger.error(error_msg)
            self.state["servers"][server_name]["last_error"] = error_msg
            return {"success": False, "error": error_msg}

    def _call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on an MCP server.

        Args:
            server_name: The name of the server
            tool_name: The name of the tool to call
            arguments: The arguments to pass to the tool

        Returns:
            The result of the tool call
        """
        if not server_name:
            return {"success": False, "error": "No server name provided"}
            
        if not tool_name:
            return {"success": False, "error": "No tool name provided"}
            
        try:
            connection = self._ensure_connection(server_name)
            
            # In a real implementation, you would call the server's call_tool method
            # For this example, we'll return a simulated response
            logger.info(f"Calling tool '{tool_name}' on server '{server_name}' with arguments: {arguments}")
            
            # Simulate tool execution based on tool name
            if tool_name == "read_file":
                filename = arguments.get("filename", "")
                if not filename:
                    return {"success": False, "error": "No filename provided"}
                    
                # Simulated response
                return {
                    "success": True,
                    "server_name": server_name,
                    "tool_name": tool_name,
                    "content": f"Simulated content of file {filename}",
                    "size": 100
                }
                
            elif tool_name == "fetch":
                url = arguments.get("url", "")
                if not url:
                    return {"success": False, "error": "No URL provided"}
                    
                # Simulated response
                return {
                    "success": True,
                    "server_name": server_name,
                    "tool_name": tool_name,
                    "url": url,
                    "content": f"Simulated content from {url}",
                    "status_code": 200
                }
                
            else:
                # Generic simulated response
                return {
                    "success": True,
                    "server_name": server_name,
                    "tool_name": tool_name,
                    "result": f"Simulated result for tool {tool_name}",
                    "arguments": arguments
                }
            
        except Exception as e:
            error_msg = f"Error calling tool '{tool_name}' on server '{server_name}': {str(e)}"
            logger.error(error_msg)
            self.state["servers"][server_name]["last_error"] = error_msg
            return {"success": False, "error": error_msg}

    def _ensure_connection(self, server_name: str):
        """Ensure a connection to the specified server exists.

        Args:
            server_name: The name of the server

        Returns:
            A connection object for the server

        Raises:
            ValueError: If the server is not configured
            RuntimeError: If the server is not running or the connection fails
        """
        if server_name not in self.server_configs:
            raise ValueError(f"Server '{server_name}' not configured")
            
        # Check if server is running
        status = self._server_status(server_name)
        if not status.get("running", False):
            if not self.auto_start:
                raise RuntimeError(f"Server '{server_name}' is not running")
                
            # Auto-start the server
            start_result = self._start_server(server_name)
            if not start_result.get("success", False):
                raise RuntimeError(f"Failed to auto-start server '{server_name}': {start_result.get('error')}")
        
        # In a real implementation, you would establish and maintain
        # actual connections to the MCP servers. For this example,
        # we'll just simulate it.
        if server_name not in self.connections:
            # Simulated connection
            self.connections[server_name] = {
                "server_name": server_name,
                "connected": True
            }
            
        return self.connections[server_name]

    def get_observation(self) -> Dict[str, Any]:
        """Get the current state of the MCP environment.

        Returns:
            The current state
        """
        # Count servers by status
        status_counts = {}
        for state in self.state["servers"].values():
            status = state.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
            
        return {
            "server_count": len(self.server_configs),
            "running_count": status_counts.get("running", 0),
            "status_counts": status_counts,
            "last_error": self.state["last_error"]
        }

    def reset(self) -> Dict[str, Any]:
        """Reset the environment state.

        Returns:
            The initial state
        """
        # Stop all running servers
        for server_name in list(self.running_servers.keys()):
            self._stop_server(server_name)
            
        # Reset connections
        self.connections = {}
        
        # Reset state
        for server_name in self.server_configs:
            self.state["servers"][server_name] = {
                "status": "not_started",
                "pid": None,
                "last_error": None
            }
            
        self.state["last_error"] = None
        
        return self.get_observation()
        
    def close(self) -> None:
        """Close all connections and stop all servers."""
        self.reset()
        logger.info(f"Closed MCP environment {self.name}")
        
    def __del__(self):
        """Destructor to ensure all servers are stopped."""
        self.close() 