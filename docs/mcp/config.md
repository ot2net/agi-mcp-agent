# Configuration Reference for MCP Agent Orchestration

## Overview

This document describes the configuration schema and best practices for the MCP agent orchestration system. All agent, tool, and system settings are managed via a centralized YAML or JSON file.

> **Note:** For standard LLM providers (e.g., OpenAI, Anthropic, Google, Mistral, Qwen, DeepSeek), you only need to specify `type`, `api_key`, and `models`. The system handles endpoint routing internally via the LLMProviderManager. Only custom REST tools require an explicit `endpoint` field.

## Configuration Schema (YAML Example)

```yaml
agents:
  openai:
    type: openai
    api_key: "${OPENAI_API_KEY}"
    models: [gpt-3.5-turbo, gpt-4]
    timeout: 30
    max_concurrent_tasks: 5
  anthropic:
    type: anthropic
    api_key: "${ANTHROPIC_API_KEY}"
    models: [claude-3-opus, claude-3-sonnet]
    timeout: 30
    max_concurrent_tasks: 5
  custom_tool:
    type: rest
    endpoint: "https://my-custom-tool/api"
    auth_token: "..."
    timeout: 10
    max_concurrent_tasks: 2
system:
  log_level: INFO
  api_port: 8080
  enable_metrics: true
  allowed_origins:
    - "*"
```

## Parameter Descriptions

- **agents**: Top-level mapping of agent names to their configuration.
  - **type**: The agent type (e.g., `openai`, `anthropic`, `rest`).
  - **api_key**/**auth_token**: Credentials for the agent backend.
  - **models**: List of supported model names for this provider (required for LLM providers).
  - **endpoint**: (Only for custom REST tools) API endpoint for the tool.
  - **timeout**: (Optional) Request timeout in seconds.
  - **max_concurrent_tasks**: (Optional) Maximum parallel tasks for this agent.
- **system**: Global system settings.
  - **log_level**: Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`).
  - **api_port**: Port for the REST API server.
  - **enable_metrics**: Enable Prometheus or similar metrics endpoint.
  - **allowed_origins**: CORS whitelist for API access.

## Environment-Specific Config

- Use separate config files for dev, test, and prod (e.g., `mcp_agents.dev.yaml`).
- Support environment variable substitution (e.g., `${API_KEY}`) for secrets.

## Hot-Reload & Dynamic Update

- The system supports hot-reloading config on file change.
- Dynamic agent registration/unregistration is possible via API.
- Invalid config changes are logged and rejected.

## Best Practices
- Store secrets in environment variables or secret managers, not in plain text.
- Use version control for config files, but exclude secrets.
- Validate config before deployment using a schema validator.
- Document all agent/tool parameters for team reference.

## Example: Minimal Config

```yaml
agents:
  openai:
    type: openai
    api_key: "${OPENAI_API_KEY}"
    models: [gpt-3.5-turbo]
system:
  log_level: INFO
  api_port: 8080
``` 