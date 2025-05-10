# Agent Plugin Development Guide

## Overview

This guide explains how to develop and integrate new agent plugins for the MCP agent orchestration system. Plugins allow the framework to support new LLM APIs, custom tools, or external services.

## Plugin Interface & Lifecycle

- All plugins must subclass `AgentClient` and implement required methods:
  - `list_tools(self)`: Return a list of available tools/functions.
  - `invoke_tool(self, tool_name, arguments)`: Execute a tool with given arguments.
  - (Optional) `health_check(self)`: Return agent health status.
- Plugins are registered at startup via config or at runtime via API.
- Plugins can be hot-reloaded if config changes.

## Implementing a New AgentClient

```python
from mcp.agent_orchestration import AgentClient

class MyRestAgent(AgentClient):
    def __init__(self, endpoint, api_key, **kwargs):
        self.endpoint = endpoint
        self.api_key = api_key

    def list_tools(self):
        # Example: fetch tool list from REST API
        resp = requests.get(f"{self.endpoint}/tools", headers={"Authorization": f"Bearer {self.api_key}"})
        return resp.json()

    def invoke_tool(self, tool_name, arguments):
        resp = requests.post(f"{self.endpoint}/tools/{tool_name}/invoke", json={"arguments": arguments}, headers={"Authorization": f"Bearer {self.api_key}"})
        return resp.json()

    def health_check(self):
        resp = requests.get(f"{self.endpoint}/health")
        return resp.status_code == 200
```

## Registration & Configuration

- Add the new agent to your config file:

```yaml
agents:
  my_rest:
    type: my_rest
    endpoint: "https://my-rest-api"
    api_key: "sk-..."
```

- Register the class in code:

```python
framework.register_agent_class("my_rest", MyRestAgent)
```

## Best Practices
- Handle all network errors and timeouts gracefully.
- Never log sensitive credentials.
- Validate and sanitize all input/output.
- Implement `health_check` for monitoring.
- Document all supported tools and parameters.

## Example: Minimal REST API Plugin

```python
class EchoAgent(AgentClient):
    def list_tools(self):
        return [{"name": "echo", "description": "Echo input text", "parameters": [{"name": "text", "type": "string"}]}]
    def invoke_tool(self, tool_name, arguments):
        if tool_name == "echo":
            return {"result": arguments["text"]}
        raise Exception("Unknown tool")
```

## Testing & Debugging
- Use unit tests to cover all plugin methods.
- Test with both valid and invalid input.
- Use the framework's logging to trace plugin activity.
- Use the API to list tools and invoke them for end-to-end testing. 