# MCP-Style Agent Orchestration Framework

The `AgentOrchestrationFramework` provides a unified interface for managing, scheduling, and invoking tasks across multiple LLM agent backends (such as Claude, ChatGPT, and custom REST tools). Inspired by the Model Context Protocol (MCP), this framework is designed for extensibility, automation, and ease of integration.

## Overview

This framework enables:
- Centralized agent and tool configuration
- Automated agent registration and lifecycle management
- Task scheduling and prioritization
- Tool discovery and invocation across all registered agents
- Monitoring, logging, and health checks
- Extensible plugin system for new agent types

## Architecture

(see architecture.md for diagrams and details)

---

## LLM Provider Integration

The orchestration framework leverages a unified `ModelProviderManager` to manage all LLM providers and models. This manager abstracts away provider-specific details and exposes a consistent interface for model selection, capability discovery, and text/chat/embedding generation.

### Key Points
- **No need to specify HTTP endpoints in config**: Just declare provider name, API key, and available models. The manager handles endpoint routing internally.
- **Unified interface**: All model calls (text, chat, embedding) go through the manager, which selects the correct provider and model.
- **Dynamic provider loading**: Providers are loaded from config, environment, or database. New providers can be added without code changes.
- **Extensible**: To add a new provider, implement the LLMProvider interface and register it with the manager.

### Example Configuration

```yaml
agents:
  openai:
    type: openai
    api_key: ${OPENAI_API_KEY}
    models: [gpt-3.5-turbo, gpt-4]
  anthropic:
    type: anthropic
    api_key: ${ANTHROPIC_API_KEY}
    models: [claude-3-opus, claude-3-sonnet]
```

### Example Usage

```python
from agi_mcp_agent.agent.llm_providers.manager import ModelProviderManager

manager = ModelProviderManager()

# List all available models
models = manager.list_models()

# Generate text
response = await manager.generate_text(
    prompt="What is AGI?",
    model_identifier="openai:gpt-3.5-turbo"
)
print(response.text)

# Generate chat completion
response = await manager.generate_chat_completion(
    messages=[{"role": "user", "content": "Hello!"}],
    model_identifier="anthropic:claude-3-opus"
)
print(response.text)

# Generate embeddings
embeddings = await manager.generate_embeddings(
    texts=["AI is amazing!"],
    model_identifier="openai:gpt-3.5-turbo"
)
print(embeddings)
```

### Best Practices
- Always use the manager's unified interface for all model calls.
- Do not hardcode HTTP endpoints or provider-specific logic in orchestration code.
- Use model identifiers in the form `provider:model_name` for clarity and routing.
- To add new providers, implement the LLMProvider interface and update config—no orchestration code changes needed.

---

## Initialization

```python
from mcp.agent_orchestration import AgentOrchestrationFramework

# Basic initialization
framework = AgentOrchestrationFramework(
    config_path="mcp_agents.yaml"
)

# Or with direct config dict
framework = AgentOrchestrationFramework(
    config={
        "agents": {
            "claude": {
                "type": "claude",
                "api_key": "sk-...",
                "endpoint": "https://api.anthropic.com/v1/complete"
            },
            "chatgpt": {
                "type": "openai",
                "api_key": "sk-...",
                "endpoint": "https://api.openai.com/v1/chat/completions"
            }
        }
    }
)
```

## Configuration

Configuration is centralized in a YAML or JSON file. Example:

```yaml
agents:
  claude:
    type: claude
    api_key: "sk-..."
    endpoint: "https://api.anthropic.com/v1/complete"
  chatgpt:
    type: openai
    api_key: "sk-..."
    endpoint: "https://api.openai.com/v1/chat/completions"
  custom_tool:
    type: rest
    endpoint: "https://my-custom-tool/api"
    auth_token: "..."
```

## Core Operations

### Agent Registration & Lifecycle

```