# API Environment

The `APIEnvironment` provides a standardized interface for agents to interact with external HTTP APIs, supporting both synchronous and asynchronous requests, authentication, and session management.

## Overview

Modern agents frequently need to interact with external services through REST APIs and other HTTP-based interfaces. The `APIEnvironment` provides a unified way to:

- Send HTTP requests using various methods (GET, POST, PUT, DELETE, etc.)
- Manage authentication and authorization
- Maintain session state and cookies
- Handle JSON and other content types
- Process and transform API responses
- Handle errors and retries gracefully

## Initialization

```python
from agi_mcp_agent.environment import APIEnvironment

# Basic initialization with defaults
api_env = APIEnvironment(
    name="example-api",
    base_url="https://api.example.com"
)

# With authentication and custom headers
api_env = APIEnvironment(
    name="secure-api",
    base_url="https://secure-api.example.com",
    auth={
        "type": "bearer",
        "token": "your-api-token"
    },
    default_headers={
        "User-Agent": "AGI-MCP-Agent/1.0",
        "Accept": "application/json"
    },
    timeout=30
)
```

## Basic Operations

### Sending GET Requests

```python
# Simple GET request
result = api_env.execute_action({
    "operation": "get",
    "url": "/users",
    "params": {
        "page": 1,
        "limit": 10
    }
})

# Access the response
if result["success"]:
    status_code = result["status_code"]
    content = result["content"]
    headers = result["headers"]
    
    # Process the data
    for user in content["data"]:
        print(f"User: {user['name']}")
else:
    print(f"Error: {result['error']}")
```

### Sending POST Requests

```python
# POST with JSON body
result = api_env.execute_action({
    "operation": "post",
    "url": "/users",
    "json": {
        "name": "John Doe",
        "email": "john@example.com",
        "role": "user"
    }
})

# POST with form data
result = api_env.execute_action({
    "operation": "post",
    "url": "/upload",
    "data": {
        "description": "Profile picture"
    },
    "files": {
        "image": {
            "path": "/path/to/image.jpg",
            "content_type": "image/jpeg"
        }
    }
})
```

### Using Other HTTP Methods

```python
# PUT request to update a resource
result = api_env.execute_action({
    "operation": "put",
    "url": "/users/42",
    "json": {
        "name": "John Updated",
        "email": "john.updated@example.com"
    }
})

# DELETE request to remove a resource
result = api_env.execute_action({
    "operation": "delete",
    "url": "/users/42"
})

# PATCH request for partial updates
result = api_env.execute_action({
    "operation": "patch",
    "url": "/users/42",
    "json": {
        "email": "new.email@example.com"
    }
})
```

## Advanced Features

### Session Management

The `APIEnvironment` maintains session state between requests:

```python
# Login to establish a session
login_result = api_env.execute_action({
    "operation": "post",
    "url": "/login",
    "json": {
        "username": "user",
        "password": "pass"
    }
})

# Subsequent requests will use the same session
profile_result = api_env.execute_action({
    "operation": "get",
    "url": "/profile"
})

# Explicitly clear the session if needed
api_env.execute_action({
    "operation": "clear_session"
})
```

### Asynchronous Requests

For non-blocking operations:

```python
# Start an asynchronous request
job_id = api_env.execute_action({
    "operation": "async_post",
    "url": "/long-running-job",
    "json": {"task": "process_data"}
})["job_id"]

# Check status later
status = api_env.execute_action({
    "operation": "check_async_status",
    "job_id": job_id
})

# Retrieve the result when ready
if status["status"] == "completed":
    result = api_env.execute_action({
        "operation": "get_async_result",
        "job_id": job_id
    })
```

### Error Handling and Retries

Configure automatic retries for transient failures:

```python
api_env = APIEnvironment(
    name="reliable-api",
    base_url="https://api.example.com",
    retry_options={
        "max_retries": 3,
        "retry_delay": 1,  # seconds
        "retry_backoff": 2,  # exponential backoff factor
        "retry_status_codes": [429, 500, 502, 503, 504]
    }
)
```

### Custom Authentication Flows

Support for various authentication methods:

```python
# OAuth2 Password Grant
api_env = APIEnvironment(
    name="oauth2-api",
    base_url="https://api.example.com",
    auth={
        "type": "oauth2",
        "token_url": "https://auth.example.com/token",
        "client_id": "client-id",
        "client_secret": "client-secret",
        "username": "user@example.com",
        "password": "secure-password",
        "scope": "read write"
    }
)

# API Key Authentication
api_env = APIEnvironment(
    name="apikey-api",
    base_url="https://api.example.com",
    auth={
        "type": "apikey",
        "key": "x-api-key",
        "value": "your-api-key",
        "location": "header"  # or "query"
    }
)
```

## Security Considerations

The `APIEnvironment` implements several security features:

- **Credential masking**: Sensitive information like passwords and tokens are masked in logs
- **URL validation**: Requests are restricted to the configured base URL domain
- **TLS verification**: HTTPS certificates are verified by default
- **Timeout enforcement**: All requests have configurable timeouts to prevent hanging operations
- **Content-type validation**: Responses are validated against expected content types

## Logging and Debugging

Enable detailed logging for debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

api_env = APIEnvironment(
    name="debug-api",
    base_url="https://api.example.com",
    debug=True  # Enable detailed request/response logging
)
```

## Testing

For testing purposes, you can initialize the `APIEnvironment` with a mock mode:

```python
api_env = APIEnvironment(
    name="test-api",
    base_url="https://api.example.com",
    mock_responses={
        "GET:/users": {
            "status_code": 200,
            "content": {"data": [{"id": 1, "name": "Test User"}]},
            "headers": {"Content-Type": "application/json"}
        }
    }
)
```

## Example Usage

Complete example of using the `APIEnvironment`:

```python
from agi_mcp_agent.environment import APIEnvironment

# Initialize the environment
api_env = APIEnvironment(
    name="httpbin-api",
    base_url="https://httpbin.org",
    default_headers={"User-Agent": "AGI-MCP-Agent Example"}
)

# Query parameters test
get_result = api_env.execute_action({
    "operation": "get",
    "url": "/get",
    "params": {
        "foo": "bar",
        "baz": "qux"
    }
})
print(f"GET Status: {get_result['status_code']}")
print(f"GET Response: {get_result['content']}")

# POST JSON data test
post_result = api_env.execute_action({
    "operation": "post",
    "url": "/post",
    "json": {
        "name": "John Doe",
        "age": 30
    }
})
print(f"POST Status: {post_result['status_code']}")
print(f"POST Response: {post_result['content']}")

# Clean up
api_env.close()
``` 