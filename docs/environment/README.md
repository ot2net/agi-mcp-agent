# AGI-MCP-Agent Environment Module

The Environment module provides interfaces for agents to interact with external systems, APIs, and data sources. Each environment implementation follows a consistent pattern and provides a unified interface for agent operations.

## Environment Architecture

All environment implementations inherit from the base `Environment` class and follow a common pattern:

- **Initialization**: Configure connection parameters and establish initial state
- **Execute Action**: Process operations through a standard request/response format
- **Cleanup**: Release resources and close connections when no longer needed

## Available Environments

The AGI-MCP-Agent provides several environment implementations:

### API Environment

The `APIEnvironment` enables agents to interact with HTTP APIs through a standard interface. Features include:

- Synchronous and asynchronous HTTP requests
- Session management and cookie persistence
- Authentication handling
- Error handling and retry mechanisms

[API Environment Documentation](./api_environment.md)

### Filesystem Environment

The `FileSystemEnvironment` provides a secure interface to the local filesystem:

- File and directory operations (read, write, list, delete)
- Path sandboxing to limit access to approved directories
- Permission handling
- Content encoding/decoding

[Filesystem Environment Documentation](./filesystem_environment.md)

### Web Environment

The `WebEnvironment` provides browser-like capabilities for web interaction:

- Web page navigation and content extraction
- Element selection via CSS/XPath selectors
- Link and image processing
- Form submission

[Web Environment Documentation](./web_environment.md)

### Database Environment

The `DatabaseEnvironment` offers a standardized interface for database operations:

- SQL query execution
- Connection pooling and management
- Transaction support
- Schema management
- Parameterized queries to prevent SQL injection

[Database Environment Documentation](./database_environment.md)

### Memory Environment

The `MemoryEnvironment` enables persistent storage for agent memory:

- Key-value storage with metadata and tagging
- Content and tag-based search capabilities
- Time-based expiration
- Data persistence across agent sessions

[Memory Environment Documentation](./memory_environment.md)

### MCP Environment

The `MCPEnvironment` manages Model Control Protocol (MCP) servers:

- Server lifecycle management (start, stop, restart)
- Tool discovery and invocation
- Status monitoring
- Server configuration

[MCP Environment Documentation](./mcp_environment.md)

## Common Patterns

All environments follow these common patterns:

1. **Initialization with configuration parameters**
2. **Action execution through the `execute_action` method**
3. **Standard response format with success/error indicators**
4. **Resource cleanup through the `close` method**

## Security Considerations

Environment implementations include various security measures:

- Path sandboxing for filesystem operations
- Parameterized queries for database operations
- Request validation for API calls
- Memory isolation between environments
- Timeout handling for external service calls

## Testing

Learn how to test the environment implementations through unit tests, integration tests, and example scripts.

[Testing Documentation](./testing.md) 