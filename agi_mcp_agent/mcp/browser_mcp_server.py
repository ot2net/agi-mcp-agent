"""Browser MCP Server implementation."""

import asyncio
import logging
import json
import os
import sys
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel

from agi_mcp_agent.environment.browser_mcp_environment import BrowserMCPEnvironment

logger = logging.getLogger(__name__)

class MCPRequest(BaseModel):
    """MCP request model."""
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[int] = None

class MCPResponse(BaseModel):
    """MCP response model."""
    jsonrpc: str = "2.0"
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[int] = None

class BrowserMCPServer:
    """MCP server for browser integration."""

    def __init__(self, name: str = "browser-mcp", port: int = 8080):
        """Initialize the browser MCP server.
        
        Args:
            name: The name of the server
            port: The port to listen on
        """
        self.name = name
        self.port = port
        self.environment = BrowserMCPEnvironment(name=name)
        self.app = FastAPI(title=f"{name} MCP Server")
        self.clients = set()
        self.setup_routes()
        
        logger.info(f"Browser MCP Server '{name}' initialized")
    
    def setup_routes(self):
        """Set up API routes."""
        @self.app.get("/")
        async def root():
            return {"message": f"Welcome to {self.name} MCP Server", "status": "running"}
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self.handle_websocket(websocket)
    
    async def handle_websocket(self, websocket: WebSocket):
        """Handle MCP WebSocket connections."""
        await websocket.accept()
        self.clients.add(websocket)
        
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    request = MCPRequest.parse_raw(data)
                    response = await self.handle_request(request)
                    await websocket.send_text(response.json())
                except Exception as e:
                    logger.error(f"Error handling request: {str(e)}")
                    error_response = MCPResponse(
                        jsonrpc="2.0",
                        error={"code": -32000, "message": f"Server error: {str(e)}"},
                        id=getattr(request, 'id', None)
                    )
                    await websocket.send_text(error_response.json())
        except WebSocketDisconnect:
            self.clients.remove(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
            self.clients.discard(websocket)
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle MCP requests.
        
        Args:
            request: The MCP request
            
        Returns:
            The MCP response
        """
        method = request.method
        params = request.params or {}
        
        try:
            if method == "initialize":
                result = await self.initialize(params)
                return MCPResponse(jsonrpc="2.0", result=result, id=request.id)
            elif method == "capabilities":
                result = self.get_capabilities()
                return MCPResponse(jsonrpc="2.0", result=result, id=request.id)
            elif method == "listTools":
                result = self.list_tools()
                return MCPResponse(jsonrpc="2.0", result=result, id=request.id)
            elif method == "executeTool":
                result = await self.execute_tool(params)
                return MCPResponse(jsonrpc="2.0", result=result, id=request.id)
            elif method == "shutdown":
                await self.shutdown()
                return MCPResponse(jsonrpc="2.0", result={"success": True}, id=request.id)
            else:
                logger.warning(f"Unknown method: {method}")
                return MCPResponse(
                    jsonrpc="2.0",
                    error={"code": -32601, "message": f"Method not found: {method}"},
                    id=request.id
                )
        except Exception as e:
            logger.error(f"Error handling method {method}: {str(e)}")
            return MCPResponse(
                jsonrpc="2.0",
                error={"code": -32000, "message": f"Server error: {str(e)}"},
                id=request.id
            )
    
    async def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the MCP server.
        
        Args:
            params: Initialization parameters
            
        Returns:
            Initialization result
        """
        logger.info(f"Initializing MCP server with params: {params}")
        return {"serverInfo": {"name": self.name, "version": "1.0.0"}}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities.
        
        Returns:
            Server capabilities
        """
        return {
            "protocols": {
                "mcp": {
                    "version": "2024-11-05"
                }
            }
        }
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools.
        
        Returns:
            Available tools
        """
        tools = [
            {
                "name": "google_search",
                "description": "Search Google for information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                },
                "returns": {
                    "type": "object",
                    "properties": {
                        "success": {
                            "type": "boolean"
                        },
                        "results": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "url": {"type": "string"},
                                    "snippet": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            {
                "name": "analyze_search_results",
                "description": "Analyze search results and provide recommendations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The original search query"
                        },
                        "criteria": {
                            "type": "array",
                            "description": "Analysis criteria",
                            "items": {"type": "string"},
                            "default": ["relevance", "authority", "recency"]
                        },
                        "count": {
                            "type": "integer",
                            "description": "Number of recommendations to generate",
                            "default": 3
                        }
                    },
                    "required": ["query"]
                },
                "returns": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "url": {"type": "string"},
                                    "snippet": {"type": "string"},
                                    "reason": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            {
                "name": "browse_webpage",
                "description": "Browse a specific webpage and extract its content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to browse"
                        },
                        "extract_content": {
                            "type": "boolean",
                            "description": "Whether to extract and analyze content",
                            "default": True
                        }
                    },
                    "required": ["url"]
                },
                "returns": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "title": {"type": "string"},
                        "content": {"type": "string"}
                    }
                }
            }
        ]
        
        return {"tools": tools}
    
    async def execute_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool.
        
        Args:
            params: Tool parameters
            
        Returns:
            Tool execution result
        """
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            raise ValueError("Tool name not specified")
        
        logger.info(f"Executing tool '{tool_name}' with arguments: {arguments}")
        
        if tool_name == "google_search":
            return await self._execute_google_search(arguments)
        elif tool_name == "analyze_search_results":
            return await self._execute_analyze_results(arguments)
        elif tool_name == "browse_webpage":
            return await self._execute_browse_webpage(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _execute_google_search(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Google search tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Search results
        """
        query = arguments.get("query")
        num_results = arguments.get("num_results", 10)
        
        if not query:
            raise ValueError("Query not specified")
        
        action = {
            "operation": "google_search",
            "query": query,
            "num_results": num_results
        }
        
        result = self.environment.execute_action(action)
        return result
    
    async def _execute_analyze_results(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute result analysis and recommendation tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Analysis and recommendations
        """
        query = arguments.get("query")
        criteria = arguments.get("criteria", ["relevance", "authority", "recency"])
        count = arguments.get("count", 3)
        
        if not query:
            raise ValueError("Query not specified")
        
        # First search
        search_action = {
            "operation": "google_search",
            "query": query,
            "num_results": max(10, count * 2)  # Get more results than needed for better recommendations
        }
        
        search_result = self.environment.execute_action(search_action)
        
        if not search_result.get("success", False):
            return search_result
        
        # Then analyze
        analyze_action = {
            "operation": "analyze_results",
            "query": query,
            "results": search_result.get("results", []),
            "criteria": criteria
        }
        
        analysis_result = self.environment.execute_action(analyze_action)
        
        if not analysis_result.get("success", False):
            return analysis_result
        
        # Generate recommendations
        recommend_action = {
            "operation": "generate_recommendations",
            "query": query,
            "results": search_result.get("results", []),
            "analysis": analysis_result.get("analysis", {}),
            "count": count
        }
        
        return self.environment.execute_action(recommend_action)
    
    async def _execute_browse_webpage(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute webpage browsing tool.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Webpage content
        """
        url = arguments.get("url")
        extract_content = arguments.get("extract_content", True)
        
        if not url:
            raise ValueError("URL not specified")
        
        action = {
            "operation": "browse_url",
            "url": url,
            "extract_content": extract_content
        }
        
        return self.environment.execute_action(action)
    
    async def shutdown(self):
        """Shutdown the MCP server."""
        logger.info(f"Shutting down MCP server '{self.name}'")
        for websocket in list(self.clients):
            try:
                await websocket.close()
            except Exception:
                pass
        self.clients.clear()
        self.environment.close()
    
    def start(self):
        """Start the MCP server."""
        import uvicorn
        logger.info(f"Starting MCP server '{self.name}' on port {self.port}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)


def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Browser MCP Server")
    parser.add_argument("--name", default="browser-mcp", help="Server name")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    args = parser.parse_args()
    
    # Start server
    server = BrowserMCPServer(name=args.name, port=args.port)
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down")
        asyncio.run(server.shutdown())
    except Exception as e:
        logger.error(f"Error running server: {str(e)}")
        asyncio.run(server.shutdown())
        sys.exit(1)


if __name__ == "__main__":
    main() 