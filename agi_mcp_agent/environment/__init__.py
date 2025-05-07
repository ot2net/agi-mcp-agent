"""Environment module for AGI-MCP-Agent.

This module provides interfaces for agents to interact with
external systems, APIs, and data sources.
"""

from agi_mcp_agent.environment.base import Environment
from agi_mcp_agent.environment.api_environment import APIEnvironment
from agi_mcp_agent.environment.filesystem_environment import FileSystemEnvironment
from agi_mcp_agent.environment.web_environment import WebEnvironment
from agi_mcp_agent.environment.database_environment import DatabaseEnvironment
from agi_mcp_agent.environment.mcp_environment import MCPEnvironment
from agi_mcp_agent.environment.memory_environment import MemoryEnvironment

__all__ = [
    "Environment",
    "APIEnvironment",
    "FileSystemEnvironment",
    "WebEnvironment",
    "DatabaseEnvironment",
    "MCPEnvironment",
    "MemoryEnvironment"
] 