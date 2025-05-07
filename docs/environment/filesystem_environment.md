# Filesystem Environment

The `FileSystemEnvironment` provides a secure and controlled interface for agents to interact with the local filesystem, with path sandboxing and permission management.

## Overview

File operations are essential for many agent tasks, from data processing to configuration management. The `FileSystemEnvironment` provides a secure way to:

- Read and write files with proper encoding
- List and navigate directory contents
- Create and delete files and directories
- Check file existence and properties
- Perform path operations with security boundaries

## Initialization

```python
from agi_mcp_agent.environment import FileSystemEnvironment

# Basic initialization with root directory
fs_env = FileSystemEnvironment(
    name="example-fs",
    root_dir="/path/to/workspace"
)

# With additional options
fs_env = FileSystemEnvironment(
    name="secure-fs",
    root_dir="/path/to/workspace",
    allowed_extensions=[".txt", ".csv", ".json"],
    max_file_size=10 * 1024 * 1024,  # 10MB
    read_only=False
)
```

## Basic Operations

### Reading Files

```python
# Read a text file
result = fs_env.execute_action({
    "operation": "read_file",
    "path": "data/config.json",
    "encoding": "utf-8"  # Optional, defaults to utf-8
})

# Access the content
if result["success"]:
    content = result["content"]
    encoding = result["encoding"]
    is_binary = result["is_binary"]
    print(f"File content: {content}")
else:
    print(f"Error: {result['error']}")

# Read a binary file
binary_result = fs_env.execute_action({
    "operation": "read_file",
    "path": "images/logo.png",
    "binary": True
})
```

### Writing Files

```python
# Write a text file
write_result = fs_env.execute_action({
    "operation": "write_file",
    "path": "output/report.txt",
    "content": "This is a sample report.\nLine 2 of the report.",
    "encoding": "utf-8",  # Optional
    "mode": "w"  # 'w' for overwrite, 'a' for append
})

# Write a binary file
binary_write = fs_env.execute_action({
    "operation": "write_file",
    "path": "output/image.jpg",
    "content": binary_data,  # bytes object
    "binary": True
})

# Write with automatic directory creation
write_with_dirs = fs_env.execute_action({
    "operation": "write_file",
    "path": "new/nested/dirs/file.txt",
    "content": "This creates parent directories if needed.",
    "create_dirs": True
})
```

### Directory Operations

```python
# List directory contents
list_result = fs_env.execute_action({
    "operation": "list_dir",
    "path": "data"
})

# Access the directory contents
if list_result["success"]:
    files = list_result["files"]  # List of file objects
    directories = list_result["directories"]  # List of directory objects
    
    print(f"Files in directory:")
    for file in files:
        print(f"  {file['name']} - {file['size']} bytes")
        
    print(f"Subdirectories:")
    for directory in directories:
        print(f"  {directory['name']}")
else:
    print(f"Error: {list_result['error']}")

# Create a directory
mkdir_result = fs_env.execute_action({
    "operation": "create_dir",
    "path": "output/reports",
    "parents": True  # Create parent directories if needed
})

# Remove a directory
rmdir_result = fs_env.execute_action({
    "operation": "delete_dir",
    "path": "temp",
    "recursive": True  # Remove subdirectories and files
})
```

### File Management

```python
# Delete a file
delete_result = fs_env.execute_action({
    "operation": "delete_file",
    "path": "temp/old_data.txt"
})

# Check if a file exists
exists_result = fs_env.execute_action({
    "operation": "file_exists",
    "path": "config.json"
})
if exists_result["success"] and exists_result["exists"]:
    print("The file exists")

# Get file information
info_result = fs_env.execute_action({
    "operation": "file_info",
    "path": "data/dataset.csv"
})
if info_result["success"]:
    size = info_result["size"]
    modified = info_result["modified"]
    file_type = info_result["type"]
    print(f"File size: {size} bytes")
    print(f"Last modified: {modified}")
    print(f"File type: {file_type}")
```

## Advanced Features

### Path Operations

```python
# Get absolute path (still within sandbox)
abs_path_result = fs_env.execute_action({
    "operation": "absolute_path",
    "path": "relative/path/file.txt"
})
if abs_path_result["success"]:
    abs_path = abs_path_result["path"]
    print(f"Absolute path: {abs_path}")

# Join paths securely
join_result = fs_env.execute_action({
    "operation": "join_paths",
    "base": "data",
    "paths": ["2023", "q1", "reports"]
})
if join_result["success"]:
    joined_path = join_result["path"]
    print(f"Joined path: {joined_path}")
```

### File Searching

```python
# Find files by pattern
find_result = fs_env.execute_action({
    "operation": "find_files",
    "path": "data",
    "pattern": "*.csv",
    "recursive": True
})
if find_result["success"]:
    matched_files = find_result["files"]
    print(f"Found {len(matched_files)} CSV files:")
    for file in matched_files:
        print(f"  {file['path']}")
```

### File Copying and Moving

```python
# Copy a file
copy_result = fs_env.execute_action({
    "operation": "copy_file",
    "source": "data/original.txt",
    "destination": "backup/original.txt",
    "create_dirs": True  # Create destination directory if needed
})

# Move/rename a file
move_result = fs_env.execute_action({
    "operation": "move_file",
    "source": "temp/draft.txt",
    "destination": "final/report.txt"
})
```

## Security Features

The `FileSystemEnvironment` incorporates several security measures:

- **Path sandboxing**: All operations are restricted to the configured root directory
- **Path normalization**: Prevents directory traversal attacks using `..` or symbolic links
- **Extension filtering**: Can restrict operations to specific file types
- **Size limits**: Prevents reading or writing excessively large files
- **Read-only mode**: Optionally prevent any write operations
- **Permission checks**: Validates appropriate permissions before operations

### Sandbox Operation

The environment enforces a strict sandbox that contains all file operations:

```python
# This will fail with a sandbox violation error
result = fs_env.execute_action({
    "operation": "read_file",
    "path": "/etc/passwd"  # Path outside the sandbox
})
# This will also fail with a sandbox violation error
result = fs_env.execute_action({
    "operation": "read_file",
    "path": "../../../etc/passwd"  # Attempted directory traversal
})
```

## Working with Temporary Files

```python
# Create a temporary file
temp_result = fs_env.execute_action({
    "operation": "create_temp_file",
    "prefix": "data_",
    "suffix": ".tmp",
    "content": "Temporary content"
})
if temp_result["success"]:
    temp_path = temp_result["path"]
    print(f"Created temporary file: {temp_path}")
    
    # Use the temporary file...
    
    # Delete when done
    fs_env.execute_action({
        "operation": "delete_file",
        "path": temp_path
    })
```

## Example Usage

Complete example of using the `FileSystemEnvironment`:

```python
from agi_mcp_agent.environment import FileSystemEnvironment
import os

# Create a test directory
test_dir = os.path.join(os.getcwd(), "test_fs_env")
os.makedirs(test_dir, exist_ok=True)

# Initialize the environment
fs_env = FileSystemEnvironment(
    name="example-fs",
    root_dir=test_dir
)

# Create a directory
fs_env.execute_action({
    "operation": "create_dir",
    "path": "test_dir"
})

# Write a file
fs_env.execute_action({
    "operation": "write_file",
    "path": "test_dir/hello.txt",
    "content": "Hello, World!\nThis is a test file."
})

# List directory contents
list_result = fs_env.execute_action({
    "operation": "list_dir",
    "path": "test_dir"
})
print(f"Directory contents: {list_result}")

# Read the file
read_result = fs_env.execute_action({
    "operation": "read_file",
    "path": "test_dir/hello.txt"
})
print(f"File content: {read_result['content']}")

# Delete the file
fs_env.execute_action({
    "operation": "delete_file",
    "path": "test_dir/hello.txt"
})

# Clean up
fs_env.close()
``` 