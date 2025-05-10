# API Design for MCP Agent Orchestration

## Overview

This document describes the REST API for interacting with the MCP agent orchestration system. The API enables external clients to manage agents, submit and monitor tasks, and discover/invoke tools.

## Authentication & Authorization
- All endpoints require an API key via `Authorization: Bearer <token>` header.
- Role-based access control can be enabled per endpoint.

## Error Handling
- All errors return JSON with `error_code`, `message`, and optional `details`.
- HTTP status codes follow REST conventions (200, 201, 400, 401, 403, 404, 409, 500).

Example error response:
```json
{
  "error_code": "AGENT_NOT_FOUND",
  "message": "Agent 'claude' does not exist.",
  "details": {}
}
```

## Endpoints

### Agent Management

#### List Agents
`GET /api/agents`
```json
[
  {"name": "claude", "type": "claude", "status": "available"},
  {"name": "chatgpt", "type": "openai", "status": "busy"}
]
```

#### Register Agent
`POST /api/agents`
```json
{
  "name": "my_agent",
  "type": "rest",
  "endpoint": "https://my-agent/api",
  "api_key": "sk-..."
}
```
Response: 201 Created

#### Unregister Agent
`DELETE /api/agents/{name}`
Response: 204 No Content

### Task Management

#### Submit Task
`POST /api/tasks`
```json
{
  "agent_name": "chatgpt",
  "tool_name": "chat_completion",
  "arguments": {"prompt": "Hello!"},
  "priority": 5
}
```
Response:
```json
{"task_id": "abc123"}
```

#### Get Task Status
`GET /api/tasks/{task_id}`
```json
{"status": "running", "result": null}
```

#### List Tasks
`GET /api/tasks?agent=chatgpt&status=completed`
```json
[
  {"task_id": "abc123", "status": "completed", "result": "..."}
]
```

### Tool Discovery & Invocation

#### List Tools
`GET /api/tools`
```json
[
  {"name": "chat_completion", "agent": "chatgpt", "description": "..."}
]
```

#### Get Tool Details
`GET /api/tools/{agent}/{tool_name}`
```json
{
  "name": "chat_completion",
  "agent": "chatgpt",
  "parameters": [
    {"name": "prompt", "type": "string", "required": true}
  ],
  "description": "..."
}
```

#### Invoke Tool
`POST /api/tools/{agent}/{tool_name}/invoke`
```json
{
  "arguments": {"prompt": "Explain quantum computing."}
}
Response:
```json
{"result": "Quantum computing is..."}
```

## Extensibility
- gRPC and WebSocket APIs can be added for streaming and real-time updates.
- API versioning via `/api/v1/` prefix.

## Best Practices
- Use pagination for large lists.
- Support idempotency for task submission.
- Log all API calls for audit.
- Validate all input and sanitize output. 