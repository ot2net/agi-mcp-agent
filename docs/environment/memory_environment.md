# Memory Environment

The `MemoryEnvironment` provides persistent storage capabilities for agent memories, preferences, and context. It implements a key-value store with metadata, tagging, and search capabilities.

## Overview

Memory is a critical component for intelligent agents to maintain context between interactions, remember user preferences, and accumulate knowledge over time. The `MemoryEnvironment` addresses these needs by providing:

- Persistent storage of structured data
- Metadata tagging for organization and retrieval
- Content-based search capabilities
- Automatic expiration for temporary memories
- On-disk persistence for durability

## Initialization

```python
from agi_mcp_agent.environment import MemoryEnvironment

# Initialize with a storage directory
memory_env = MemoryEnvironment(
    name="agent-memory",
    storage_dir="/path/to/storage",
    max_history=100,  # Optional: limit the number of memories
    memory_format="json"  # Optional: storage format
)
```

## Basic Operations

### Storing Memories

Store structured data with optional tags and expiration:

```python
# Store user preferences
result = memory_env.execute_action({
    "operation": "store",
    "key": "user_preferences",
    "data": {
        "theme": "dark",
        "language": "en",
        "notifications": True
    },
    "tags": ["preferences", "user", "settings"]
})

# Store temporary session data (expires in 1 hour)
result = memory_env.execute_action({
    "operation": "store",
    "key": "session_token",
    "data": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "tags": ["session", "temporary"],
    "expires": 3600  # seconds
})
```

### Retrieving Memories

Retrieve stored memories by key:

```python
result = memory_env.execute_action({
    "operation": "retrieve",
    "key": "user_preferences"
})

# Access the data and metadata
if result["success"]:
    preferences = result["data"]
    metadata = result["metadata"]
    print(f"User theme preference: {preferences['theme']}")
    print(f"Last accessed: {metadata['last_accessed']}")
    print(f"Access count: {metadata['access_count']}")
```

### Searching Memories

Search for memories by content:

```python
# Search for memories related to Japan
result = memory_env.execute_action({
    "operation": "search",
    "query": "japan"
})

# Process search results
if result["success"]:
    for match in result["matches"]:
        print(f"Found memory: {match['key']}")
        print(f"Content: {match['data']}")
```

### Searching by Tags

Retrieve memories with specific tags:

```python
# Find all memories tagged as "conversation"
result = memory_env.execute_action({
    "operation": "retrieve_by_tag",
    "tag": "conversation"
})

# Process matching memories
if result["success"]:
    for match in result["matches"]:
        print(f"Conversation: {match['key']}")
```

### Listing Memories

List all available memories:

```python
# List all memories with pagination
result = memory_env.execute_action({
    "operation": "list",
    "limit": 10,
    "offset": 0
})

# Process the memory list
if result["success"]:
    print(f"Found {result['count']} memories")
    for memory in result["memories"]:
        print(f"Key: {memory['key']}")
        print(f"Created: {memory['created']}")
        print(f"Tags: {', '.join(memory['tags'])}")
```

### Deleting Memories

Remove memories that are no longer needed:

```python
result = memory_env.execute_action({
    "operation": "delete",
    "key": "session_token"
})
```

## Automatic Memory Management

The `MemoryEnvironment` provides automatic handling of:

- **Memory expiration**: Temporary memories are automatically removed after their expiration time
- **Access tracking**: Each memory tracks access count and last access time
- **Persistence**: Memories are automatically saved to disk for durability
- **Metadata**: Creation time, access patterns, and tags are managed automatically

## Use Cases

### Conversation History

Store conversation history for context retention:

```python
memory_env.execute_action({
    "operation": "store",
    "key": f"conversation:{conversation_id}",
    "data": {
        "summary": "User asked about travel recommendations for Japan",
        "sentiment": "positive",
        "topics": ["travel", "Japan", "recommendations"]
    },
    "tags": ["conversation", "travel", "Japan"]
})
```

### Agent Context

Maintain agent task state between sessions:

```python
memory_env.execute_action({
    "operation": "store",
    "key": f"agent:context:{agent_id}",
    "data": {
        "current_tasks": [
            {"id": "task1", "status": "in_progress", "description": "Research Japan travel"},
            {"id": "task2", "status": "pending", "description": "Book flight tickets"}
        ],
        "last_focus": "task1",
        "knowledge_gaps": ["Japan visa requirements", "COVID restrictions"]
    },
    "tags": ["agent", "context", "Japan", "travel", "task_list"]
})
```

## Implementation Details

The `MemoryEnvironment` stores memories as JSON files on disk, with an in-memory index for fast retrieval and searching. Key features of the implementation include:

- **Thread-safety**: Memory operations are thread-safe for concurrent access
- **Atomic operations**: Storage and retrieval operations are atomic to prevent data corruption
- **Lazy loading**: Memories are loaded from disk on demand to minimize memory usage
- **Periodic cleanup**: Expired memories are periodically cleaned up to free resources

## Testing

The `MemoryEnvironment` can be tested using the provided unit tests:

```bash
# Run the memory environment tests
python -m unittest tests.environment.test_memory_environment
```

The tests cover:

1. Basic store and retrieve operations
2. Memory expiration
3. Tag-based searches
4. Text-based content searches
5. Memory persistence

## Example

A complete example demonstrating the `MemoryEnvironment` is available at:

```bash
# Run the memory environment example
python examples/memory_environment_usage.py
``` 