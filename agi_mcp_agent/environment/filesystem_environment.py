"""File system environment implementation for agent interactions with file system."""

import logging
import os
import shutil
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from agi_mcp_agent.environment.base import Environment

logger = logging.getLogger(__name__)


class FileSystemEnvironment(Environment):
    """Environment that provides access to the file system."""

    def __init__(self, name: str, root_dir: str, sandbox: bool = True):
        """Initialize the file system environment.

        Args:
            name: The name of the environment
            root_dir: The root directory for file operations
            sandbox: Whether to restrict operations to the root directory for safety
        """
        super().__init__(name)
        self.root_dir = os.path.abspath(root_dir)
        self.sandbox = sandbox
        self.state = {"current_dir": self.root_dir}
        
        # Create the root directory if it doesn't exist
        os.makedirs(self.root_dir, exist_ok=True)
        
        logger.info(f"FileSystem Environment {self.name} initialized with root dir {self.root_dir}")

    def _validate_path(self, path: str) -> str:
        """Validate and normalize a path.

        Args:
            path: The path to validate

        Returns:
            The normalized absolute path

        Raises:
            ValueError: If the path is outside the sandbox
        """
        # Handle relative paths
        if not os.path.isabs(path):
            path = os.path.join(self.state["current_dir"], path)
        
        # Normalize the path to resolve any .. or . components
        normalized_path = os.path.normpath(os.path.abspath(path))
        
        # Check if the path is within the sandbox
        if self.sandbox and not normalized_path.startswith(self.root_dir):
            logger.warning(f"Attempted to access path outside sandbox: {path}")
            raise ValueError(f"Path {path} is outside the sandbox directory {self.root_dir}")
        
        return normalized_path

    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a file system operation.

        Args:
            action: The operation to execute with the following keys:
                - operation: The operation to perform (read, write, list, etc.)
                - path: The path to operate on
                - additional operation-specific parameters

        Returns:
            The result of the operation
        """
        operation = action.get("operation", "").lower()
        path = action.get("path", "")
        
        try:
            if operation == "read":
                return self._read_file(path, action.get("encoding", "utf-8"))
            elif operation == "write":
                return self._write_file(
                    path, 
                    action.get("content", ""), 
                    action.get("mode", "w"), 
                    action.get("encoding", "utf-8")
                )
            elif operation == "append":
                return self._write_file(
                    path, 
                    action.get("content", ""), 
                    "a", 
                    action.get("encoding", "utf-8")
                )
            elif operation == "list":
                return self._list_directory(path)
            elif operation == "mkdir":
                return self._create_directory(path)
            elif operation == "delete":
                return self._delete_file_or_directory(path)
            elif operation == "move":
                return self._move_file_or_directory(path, action.get("destination", ""))
            elif operation == "copy":
                return self._copy_file_or_directory(path, action.get("destination", ""))
            elif operation == "exists":
                return self._check_exists(path)
            elif operation == "cd":
                return self._change_directory(path)
            elif operation == "cwd":
                return {"success": True, "current_dir": self.state["current_dir"]}
            else:
                logger.warning(f"Unknown file system operation: {operation}")
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            logger.error(f"Error in file system operation {operation}: {str(e)}")
            return {"success": False, "error": str(e)}

    def _read_file(self, path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Read a file.

        Args:
            path: The path to the file
            encoding: The encoding to use

        Returns:
            The file content
        """
        normalized_path = self._validate_path(path)
        
        if not os.path.exists(normalized_path):
            return {"success": False, "error": f"File {path} does not exist"}
        
        if not os.path.isfile(normalized_path):
            return {"success": False, "error": f"{path} is not a file"}
        
        try:
            # Detect if it's a binary file
            is_binary = False
            try:
                with open(normalized_path, 'r', encoding=encoding) as f:
                    sample = f.read(1024)  # Read a sample to check
            except UnicodeDecodeError:
                is_binary = True
            
            if is_binary:
                # For binary files, return base64 encoded content
                import base64
                with open(normalized_path, 'rb') as f:
                    content = base64.b64encode(f.read()).decode('ascii')
                return {"success": True, "content": content, "encoding": "base64", "is_binary": True}
            else:
                # For text files, return the content as-is
                with open(normalized_path, 'r', encoding=encoding) as f:
                    content = f.read()
                return {"success": True, "content": content, "encoding": encoding, "is_binary": False}
        except Exception as e:
            return {"success": False, "error": f"Error reading file {path}: {str(e)}"}

    def _write_file(self, path: str, content: str, mode: str = "w", encoding: str = "utf-8") -> Dict[str, Any]:
        """Write to a file.

        Args:
            path: The path to the file
            content: The content to write
            mode: The file mode ("w" for write, "a" for append)
            encoding: The encoding to use

        Returns:
            Success status
        """
        normalized_path = self._validate_path(path)
        
        # Create parent directories if they don't exist
        parent_dir = os.path.dirname(normalized_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        # Check if the content is base64 encoded
        is_base64 = False
        if isinstance(content, dict) and content.get("encoding") == "base64":
            is_base64 = True
            import base64
            try:
                binary_content = base64.b64decode(content.get("content", ""))
                with open(normalized_path, mode + "b") as f:
                    f.write(binary_content)
                return {"success": True, "path": path}
            except Exception as e:
                return {"success": False, "error": f"Error writing to file {path}: {str(e)}"}
        
        # Normal text content
        try:
            with open(normalized_path, mode, encoding=encoding) as f:
                f.write(content)
            return {"success": True, "path": path}
        except Exception as e:
            return {"success": False, "error": f"Error writing to file {path}: {str(e)}"}

    def _list_directory(self, path: str) -> Dict[str, Any]:
        """List the contents of a directory.

        Args:
            path: The path to the directory

        Returns:
            List of files and directories
        """
        normalized_path = self._validate_path(path or ".")
        
        if not os.path.exists(normalized_path):
            return {"success": False, "error": f"Directory {path} does not exist"}
        
        if not os.path.isdir(normalized_path):
            return {"success": False, "error": f"{path} is not a directory"}
        
        try:
            items = os.listdir(normalized_path)
            
            # Get detailed information about each item
            files = []
            directories = []
            
            for item in items:
                item_path = os.path.join(normalized_path, item)
                is_dir = os.path.isdir(item_path)
                
                if is_dir:
                    directories.append({
                        "name": item,
                        "type": "directory",
                        "path": os.path.relpath(item_path, self.root_dir)
                    })
                else:
                    files.append({
                        "name": item,
                        "type": "file",
                        "path": os.path.relpath(item_path, self.root_dir),
                        "size": os.path.getsize(item_path),
                        "modified": os.path.getmtime(item_path)
                    })
            
            return {
                "success": True, 
                "path": path,
                "items": items,
                "files": files,
                "directories": directories
            }
        except Exception as e:
            return {"success": False, "error": f"Error listing directory {path}: {str(e)}"}

    def _create_directory(self, path: str) -> Dict[str, Any]:
        """Create a directory.

        Args:
            path: The path to the directory

        Returns:
            Success status
        """
        normalized_path = self._validate_path(path)
        
        try:
            os.makedirs(normalized_path, exist_ok=True)
            return {"success": True, "path": path}
        except Exception as e:
            return {"success": False, "error": f"Error creating directory {path}: {str(e)}"}

    def _delete_file_or_directory(self, path: str) -> Dict[str, Any]:
        """Delete a file or directory.

        Args:
            path: The path to delete

        Returns:
            Success status
        """
        normalized_path = self._validate_path(path)
        
        if not os.path.exists(normalized_path):
            return {"success": False, "error": f"Path {path} does not exist"}
        
        try:
            if os.path.isdir(normalized_path):
                shutil.rmtree(normalized_path)
            else:
                os.remove(normalized_path)
            return {"success": True, "path": path}
        except Exception as e:
            return {"success": False, "error": f"Error deleting {path}: {str(e)}"}

    def _move_file_or_directory(self, source: str, destination: str) -> Dict[str, Any]:
        """Move a file or directory.

        Args:
            source: The source path
            destination: The destination path

        Returns:
            Success status
        """
        normalized_source = self._validate_path(source)
        normalized_destination = self._validate_path(destination)
        
        if not os.path.exists(normalized_source):
            return {"success": False, "error": f"Source {source} does not exist"}
        
        # Create parent directories if they don't exist
        parent_dir = os.path.dirname(normalized_destination)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        try:
            shutil.move(normalized_source, normalized_destination)
            return {"success": True, "source": source, "destination": destination}
        except Exception as e:
            return {"success": False, "error": f"Error moving {source} to {destination}: {str(e)}"}

    def _copy_file_or_directory(self, source: str, destination: str) -> Dict[str, Any]:
        """Copy a file or directory.

        Args:
            source: The source path
            destination: The destination path

        Returns:
            Success status
        """
        normalized_source = self._validate_path(source)
        normalized_destination = self._validate_path(destination)
        
        if not os.path.exists(normalized_source):
            return {"success": False, "error": f"Source {source} does not exist"}
        
        # Create parent directories if they don't exist
        parent_dir = os.path.dirname(normalized_destination)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        try:
            if os.path.isdir(normalized_source):
                shutil.copytree(normalized_source, normalized_destination)
            else:
                shutil.copy2(normalized_source, normalized_destination)
            return {"success": True, "source": source, "destination": destination}
        except Exception as e:
            return {"success": False, "error": f"Error copying {source} to {destination}: {str(e)}"}

    def _check_exists(self, path: str) -> Dict[str, Any]:
        """Check if a file or directory exists.

        Args:
            path: The path to check

        Returns:
            Existence status
        """
        try:
            normalized_path = self._validate_path(path)
            exists = os.path.exists(normalized_path)
            return {
                "success": True, 
                "exists": exists,
                "path": path,
                "is_file": os.path.isfile(normalized_path) if exists else False,
                "is_directory": os.path.isdir(normalized_path) if exists else False
            }
        except ValueError as e:
            # Path validation error (outside sandbox)
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Error checking existence of {path}: {str(e)}"}

    def _change_directory(self, path: str) -> Dict[str, Any]:
        """Change the current directory.

        Args:
            path: The directory to change to

        Returns:
            Success status
        """
        try:
            normalized_path = self._validate_path(path)
            
            if not os.path.exists(normalized_path):
                return {"success": False, "error": f"Directory {path} does not exist"}
            
            if not os.path.isdir(normalized_path):
                return {"success": False, "error": f"{path} is not a directory"}
            
            self.state["current_dir"] = normalized_path
            return {"success": True, "current_dir": normalized_path}
        except Exception as e:
            return {"success": False, "error": f"Error changing directory to {path}: {str(e)}"}

    def get_observation(self) -> Dict[str, Any]:
        """Get the current state of the file system.

        Returns:
            The current state
        """
        return {
            "current_dir": self.state["current_dir"],
            "root_dir": self.root_dir,
            "sandbox": self.sandbox
        }

    def reset(self) -> Dict[str, Any]:
        """Reset the environment state.

        Returns:
            The initial state
        """
        self.state = {"current_dir": self.root_dir}
        return self.get_observation() 