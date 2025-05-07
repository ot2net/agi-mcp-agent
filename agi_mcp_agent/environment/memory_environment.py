"""Memory environment implementation for agent persistent memory capabilities."""

import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from agi_mcp_agent.environment.base import Environment

logger = logging.getLogger(__name__)


class MemoryEnvironment(Environment):
    """Environment that provides persistent memory storage for agents."""

    def __init__(
        self, 
        name: str, 
        storage_dir: str,
        max_history: int = 100,
        memory_format: str = "json"
    ):
        """Initialize the memory environment.

        Args:
            name: The name of the environment
            storage_dir: Directory to store memory files
            max_history: Maximum number of historical memories to store
            memory_format: Format to store memories ('json' or 'vector')
        """
        super().__init__(name)
        self.storage_dir = os.path.abspath(storage_dir)
        self.max_history = max_history
        self.memory_format = memory_format.lower()
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize state
        self.state = {
            "memories": {},
            "last_access": {},
            "memory_count": 0
        }
        
        # Load existing memories
        self._load_memories()
        
        logger.info(f"Memory Environment {self.name} initialized with storage in {self.storage_dir}")

    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a memory operation.

        Args:
            action: The operation to execute with the following keys:
                - operation: The operation to perform (store, retrieve, etc.)
                - additional operation-specific parameters

        Returns:
            The result of the operation
        """
        operation = action.get("operation", "").lower()
        
        try:
            if operation == "store":
                return self._store_memory(
                    key=action.get("key", ""),
                    data=action.get("data", {}),
                    tags=action.get("tags", []),
                    expires=action.get("expires", None)
                )
            elif operation == "retrieve":
                return self._retrieve_memory(
                    key=action.get("key", ""),
                    default=action.get("default", None)
                )
            elif operation == "retrieve_by_tag":
                return self._retrieve_by_tag(
                    tag=action.get("tag", ""),
                    limit=action.get("limit", 10)
                )
            elif operation == "search":
                return self._search_memories(
                    query=action.get("query", ""),
                    limit=action.get("limit", 10)
                )
            elif operation == "delete":
                return self._delete_memory(
                    key=action.get("key", "")
                )
            elif operation == "list":
                return self._list_memories(
                    limit=action.get("limit", 10),
                    offset=action.get("offset", 0)
                )
            elif operation == "clear":
                return self._clear_memories()
            else:
                logger.warning(f"Unknown memory operation: {operation}")
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            logger.error(f"Error in memory operation {operation}: {str(e)}")
            return {"success": False, "error": str(e)}

    def _store_memory(self, key: str, data: Any, tags: List[str] = None, expires: int = None) -> Dict[str, Any]:
        """Store a memory.

        Args:
            key: The memory key
            data: The data to store
            tags: Optional tags for categorization and retrieval
            expires: Optional expiry time in seconds from now

        Returns:
            Status of the operation
        """
        if not key:
            return {"success": False, "error": "No memory key provided"}
            
        # Generate a timestamp for this memory
        timestamp = time.time()
        expiry = timestamp + expires if expires else None
        
        # Create the memory object
        memory = {
            "key": key,
            "data": data,
            "tags": tags or [],
            "timestamp": timestamp,
            "created": datetime.fromtimestamp(timestamp).isoformat(),
            "expires": expiry,
            "access_count": 0
        }
        
        # Store in memory and update state
        self.state["memories"][key] = memory
        self.state["last_access"][key] = timestamp
        self.state["memory_count"] = len(self.state["memories"])
        
        # Save to disk
        self._save_memories()
        
        return {
            "success": True,
            "key": key,
            "timestamp": timestamp
        }

    def _retrieve_memory(self, key: str, default: Any = None) -> Dict[str, Any]:
        """Retrieve a memory by key.

        Args:
            key: The memory key
            default: Default value to return if key not found

        Returns:
            The retrieved memory
        """
        if not key:
            return {"success": False, "error": "No memory key provided"}
            
        memory = self.state["memories"].get(key)
        
        if not memory:
            return {
                "success": False,
                "key": key,
                "error": f"Memory not found for key: {key}",
                "default": default
            }
            
        # Check if expired
        if memory.get("expires") and memory["expires"] < time.time():
            self._delete_memory(key)
            return {
                "success": False,
                "key": key,
                "error": "Memory has expired",
                "default": default
            }
            
        # Update access information
        memory["access_count"] += 1
        self.state["last_access"][key] = time.time()
        
        return {
            "success": True,
            "key": key,
            "data": memory["data"],
            "metadata": {
                "created": memory["created"],
                "tags": memory["tags"],
                "access_count": memory["access_count"]
            }
        }

    def _retrieve_by_tag(self, tag: str, limit: int = 10) -> Dict[str, Any]:
        """Retrieve memories by tag.

        Args:
            tag: The tag to search for
            limit: Maximum number of results to return

        Returns:
            Matching memories
        """
        if not tag:
            return {"success": False, "error": "No tag provided"}
            
        matches = []
        
        for key, memory in self.state["memories"].items():
            # Skip expired memories
            if memory.get("expires") and memory["expires"] < time.time():
                continue
                
            if tag in memory.get("tags", []):
                matches.append({
                    "key": key,
                    "data": memory["data"],
                    "created": memory["created"],
                    "tags": memory["tags"]
                })
                
                if len(matches) >= limit:
                    break
                    
        return {
            "success": True,
            "tag": tag,
            "matches": matches,
            "count": len(matches)
        }

    def _search_memories(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search memories by simple text match.

        Args:
            query: The text to search for
            limit: Maximum number of results to return

        Returns:
            Matching memories
        """
        if not query:
            return {"success": False, "error": "No search query provided"}
            
        matches = []
        query = query.lower()
        
        for key, memory in self.state["memories"].items():
            # Skip expired memories
            if memory.get("expires") and memory["expires"] < time.time():
                continue
                
            # Simple text search in the memory key and serialized data
            memory_text = key.lower()
            
            # If data is a string, include it in the search
            if isinstance(memory["data"], str):
                memory_text += " " + memory["data"].lower()
            elif isinstance(memory["data"], dict):
                # For dictionaries, include values that are strings
                for value in memory["data"].values():
                    if isinstance(value, str):
                        memory_text += " " + value.lower()
            
            # Also include tags in the search
            for tag in memory.get("tags", []):
                memory_text += " " + tag.lower()
                
            if query in memory_text:
                matches.append({
                    "key": key,
                    "data": memory["data"],
                    "created": memory["created"],
                    "tags": memory["tags"]
                })
                
                if len(matches) >= limit:
                    break
                    
        return {
            "success": True,
            "query": query,
            "matches": matches,
            "count": len(matches)
        }

    def _delete_memory(self, key: str) -> Dict[str, Any]:
        """Delete a memory.

        Args:
            key: The memory key

        Returns:
            Status of the operation
        """
        if not key:
            return {"success": False, "error": "No memory key provided"}
            
        if key not in self.state["memories"]:
            return {"success": False, "error": f"Memory not found for key: {key}"}
            
        # Delete the memory
        del self.state["memories"][key]
        if key in self.state["last_access"]:
            del self.state["last_access"][key]
            
        self.state["memory_count"] = len(self.state["memories"])
        
        # Save changes to disk
        self._save_memories()
        
        return {
            "success": True,
            "key": key
        }

    def _list_memories(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List stored memories.

        Args:
            limit: Maximum number of memories to return
            offset: Starting offset for pagination

        Returns:
            List of memories
        """
        memories = []
        
        # Sort keys by last access time (most recent first)
        sorted_keys = sorted(
            self.state["last_access"].keys(),
            key=lambda k: self.state["last_access"].get(k, 0),
            reverse=True
        )
        
        # Apply pagination
        page_keys = sorted_keys[offset:offset + limit]
        
        for key in page_keys:
            if key in self.state["memories"]:
                memory = self.state["memories"][key]
                
                # Skip expired memories
                if memory.get("expires") and memory["expires"] < time.time():
                    continue
                    
                memories.append({
                    "key": key,
                    "created": memory["created"],
                    "tags": memory["tags"],
                    "access_count": memory["access_count"]
                })
                
        return {
            "success": True,
            "memories": memories,
            "count": len(memories),
            "total": self.state["memory_count"],
            "has_more": (offset + limit) < self.state["memory_count"]
        }

    def _clear_memories(self) -> Dict[str, Any]:
        """Clear all stored memories.

        Returns:
            Status of the operation
        """
        old_count = self.state["memory_count"]
        
        self.state["memories"] = {}
        self.state["last_access"] = {}
        self.state["memory_count"] = 0
        
        # Save the empty state to disk
        self._save_memories()
        
        return {
            "success": True,
            "cleared_count": old_count
        }

    def _load_memories(self) -> None:
        """Load memories from storage."""
        memory_file = os.path.join(self.storage_dir, f"{self.name}_memories.json")
        
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r') as f:
                    stored_data = json.load(f)
                    
                self.state["memories"] = stored_data.get("memories", {})
                self.state["last_access"] = stored_data.get("last_access", {})
                self.state["memory_count"] = len(self.state["memories"])
                
                # Clean up expired memories
                self._cleanup_expired()
                
                logger.info(f"Loaded {self.state['memory_count']} memories for environment {self.name}")
            except Exception as e:
                logger.error(f"Error loading memories: {str(e)}")
                # Initialize with empty state
                self.state["memories"] = {}
                self.state["last_access"] = {}
                self.state["memory_count"] = 0

    def _save_memories(self) -> None:
        """Save memories to storage."""
        memory_file = os.path.join(self.storage_dir, f"{self.name}_memories.json")
        
        try:
            with open(memory_file, 'w') as f:
                json.dump({
                    "memories": self.state["memories"],
                    "last_access": self.state["last_access"]
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving memories: {str(e)}")

    def _cleanup_expired(self) -> None:
        """Clean up expired memories."""
        current_time = time.time()
        expired_keys = []
        
        for key, memory in self.state["memories"].items():
            if memory.get("expires") and memory["expires"] < current_time:
                expired_keys.append(key)
                
        for key in expired_keys:
            del self.state["memories"][key]
            if key in self.state["last_access"]:
                del self.state["last_access"][key]
                
        if expired_keys:
            self.state["memory_count"] = len(self.state["memories"])
            logger.info(f"Cleaned up {len(expired_keys)} expired memories")

    def get_observation(self) -> Dict[str, Any]:
        """Get the current state of the memory environment.

        Returns:
            The current state
        """
        return {
            "memory_count": self.state["memory_count"],
            "storage_dir": self.storage_dir
        }

    def reset(self) -> Dict[str, Any]:
        """Reset the environment state.

        Returns:
            The initial state
        """
        # Reload memories from storage, don't clear them
        self._load_memories()
        return self.get_observation() 