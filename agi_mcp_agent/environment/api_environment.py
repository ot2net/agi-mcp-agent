"""API environment implementation for agent interactions with external APIs."""

import json
import logging
from typing import Any, Dict, List, Optional
import aiohttp
import asyncio
import requests

from agi_mcp_agent.environment.base import Environment

logger = logging.getLogger(__name__)


class APIEnvironment(Environment):
    """Environment that interfaces with external APIs."""

    def __init__(
        self, 
        name: str, 
        base_url: str, 
        headers: Dict[str, str] = None,
        timeout: int = 30,
        verify_ssl: bool = True
    ):
        """Initialize the API environment.

        Args:
            name: The name of the environment
            base_url: The base URL for API requests
            headers: The headers to use for API requests
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        super().__init__(name)
        self.base_url = base_url
        self.headers = headers or {}
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.state = {"last_response": None, "last_status": None}
        self.session = None
        logger.info(f"API Environment {self.name} initialized with base URL {base_url}")

    async def create_session(self):
        """Create an aiohttp session for async requests."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self.session

    async def close_session(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a synchronous API request.

        Args:
            action: The API request to execute with the following keys:
                - method: HTTP method (GET, POST, PUT, DELETE, etc.)
                - endpoint: API endpoint (will be appended to base_url)
                - params: Query parameters (optional)
                - data: Request body for POST/PUT (optional)
                - json: JSON data for POST/PUT (optional)
                - headers: Additional headers (optional)

        Returns:
            The response from the API
        """
        method = action.get("method", "GET").upper()
        endpoint = action.get("endpoint", "")
        params = action.get("params", {})
        data = action.get("data")
        json_data = action.get("json")
        headers = {**self.headers, **action.get("headers", {})}
        
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}" if endpoint else self.base_url
        
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=headers,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            
            # Update state with response info
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                try:
                    response_data = response.json()
                except json.JSONDecodeError:
                    response_data = response.text
            else:
                response_data = response.text
                
            self.state["last_response"] = response_data
            self.state["last_status"] = response.status_code
            
            result = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response_data,
                "success": 200 <= response.status_code < 300
            }
            
            logger.info(f"API request to {url} completed with status {response.status_code}")
            return result
            
        except Exception as e:
            logger.error(f"API request to {url} failed: {str(e)}")
            self.state["last_error"] = str(e)
            return {
                "status_code": 0,
                "error": str(e),
                "success": False
            }
    
    async def execute_action_async(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an asynchronous API request.

        Args:
            action: The API request to execute (same format as execute_action)

        Returns:
            The response from the API
        """
        method = action.get("method", "GET").upper()
        endpoint = action.get("endpoint", "")
        params = action.get("params", {})
        data = action.get("data")
        json_data = action.get("json")
        headers = {**self.headers, **action.get("headers", {})}
        
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}" if endpoint else self.base_url
        
        try:
            session = await self.create_session()
            
            async with session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=headers,
                ssl=self.verify_ssl
            ) as response:
                
                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    try:
                        response_data = await response.json()
                    except json.JSONDecodeError:
                        response_data = await response.text()
                else:
                    response_data = await response.text()
                
                self.state["last_response"] = response_data
                self.state["last_status"] = response.status
                
                result = {
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "content": response_data,
                    "success": 200 <= response.status < 300
                }
                
                logger.info(f"Async API request to {url} completed with status {response.status}")
                return result
                
        except Exception as e:
            logger.error(f"Async API request to {url} failed: {str(e)}")
            self.state["last_error"] = str(e)
            return {
                "status_code": 0,
                "error": str(e),
                "success": False
            }

    def get_observation(self) -> Dict[str, Any]:
        """Get the current state of the environment.

        Returns:
            The current state
        """
        return self.state

    def reset(self) -> Dict[str, Any]:
        """Reset the environment state.

        Returns:
            The initial state
        """
        self.state = {"last_response": None, "last_status": None}
        return self.state
    
    async def __aenter__(self):
        """Async context manager enter."""
        await self.create_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_session() 