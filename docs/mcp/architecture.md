# Architecture of MCP Agent Orchestration System

## High-Level Architecture Diagram

```mermaid
graph TD
    ConfigLoader --> AgentManager
    ConfigLoader --> ToolAggregator
    AgentManager -->|register| AgentClient
    AgentManager --> TaskScheduler
    TaskScheduler --> AgentClient
    ToolAggregator --> AgentClient
    UserAPI --> ToolAggregator
    UserAPI --> TaskScheduler
    AgentClient -->|invoke| ExternalService
```

## Module Descriptions

- **ConfigLoader**: Loads and validates agent/tool configuration from YAML/JSON. Supports hot-reload.
- **AgentManager**: Registers, initializes, and manages the lifecycle of all agent backends. Handles dynamic agent registration/unregistration.
- **AgentClient**: Abstract base for all agent integrations (e.g., Claude, ChatGPT, REST tools). Each agent type implements this interface.
- **TaskScheduler**: Manages task queue, prioritization, dependency resolution, and assignment to agents. Supports retries and timeouts.
- **ToolAggregator**: Aggregates all available tools from registered agents, exposes unified API for discovery and invocation.
- **UserAPI**: (Optional) REST/gRPC/WebSocket API for external clients to submit tasks, query status, and invoke tools.
- **ExternalService**: Any LLM API or custom tool backend (Claude, ChatGPT, etc.).

## Data Flow: Task Submission & Execution

1. User submits a task via UserAPI or direct call.
2. ConfigLoader ensures agent/tool config is loaded.
3. TaskScheduler queues the task, resolves dependencies and priority.
4. AgentManager selects or instantiates the appropriate AgentClient.
5. TaskScheduler assigns the task to AgentClient.
6. AgentClient invokes the external service/tool.
7. Result is returned to TaskScheduler, then to UserAPI.

## Sequence Diagram: Tool Invocation

```mermaid
sequenceDiagram
    participant User
    participant ToolAggregator
    participant AgentManager
    participant AgentClient
    participant ExternalService
    User->>ToolAggregator: call_tool(tool_name, args)
    ToolAggregator->>AgentManager: find_agent_for_tool(tool_name)
    AgentManager->>AgentClient: get_agent_instance()
    AgentClient->>ExternalService: invoke_tool(args)
    ExternalService-->>AgentClient: result
    AgentClient-->>ToolAggregator: result
    ToolAggregator-->>User: result
```

## State Transitions

- **Task**: pending → running → completed/failed
- **Agent**: registered → available/busy → error/unregistered

## Extensibility Points

- Add new agent types by subclassing AgentClient and updating config
- Add new tool types by extending ToolAggregator logic
- Support for new APIs by extending UserAPI

## Future Work / TODOs
- Distributed TaskScheduler for horizontal scaling
- Pluggable authentication and rate limiting
- Web dashboard for live monitoring
- Advanced scheduling algorithms (load, cost, capability-aware)
- Streaming and async tool invocation 