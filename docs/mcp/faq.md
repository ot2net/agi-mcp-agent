# FAQ: MCP Agent Orchestration System

## General

**Q: What is the MCP agent orchestration system?**
A: It is a unified platform for managing, scheduling, and invoking tasks across multiple LLM agent backends (Claude, ChatGPT, custom tools, etc.).

**Q: Where do I start?**
A: Read `agent_orchestration.md` for the main design and usage. See `README.md` for the document structure.

## Setup & Configuration

**Q: How do I add a new agent?**
A: Add it to your config file under `agents:` and, if custom, register its class in code. See `config.md` and `agent_plugin.md`.

**Q: How do I store secrets securely?**
A: Use environment variables or a secret manager. Never commit secrets to version control.

**Q: Can I reload config without restarting?**
A: Yes, the system supports hot-reload on config file changes.

## Troubleshooting

**Q: My agent is not responding. What should I check?**
A: Verify endpoint, credentials, and network. Use the agent's `health_check` method and check logs.

**Q: Task stuck in pending?**
A: Check for unresolved dependencies, agent availability, and queue length. See `task_scheduler.md`.

**Q: Tool invocation fails with permission error?**
A: Check your user/role permissions in the config. See `security.md`.

## Performance & Scaling

**Q: How do I handle high task volume?**
A: Tune `max_concurrent_tasks` per agent, use weighted/capability-aware scheduling, and monitor queue length.

**Q: Can I run the system distributed?**
A: Distributed scheduling is a planned feature. For now, run multiple instances with coordinated config.

## Extension & Best Practices

**Q: How do I add a new tool or agent type?**
A: Implement a new `AgentClient` subclass and update config. See `agent_plugin.md`.

**Q: How do I ensure security?**
A: Use HTTPS, rotate keys, enforce RBAC, and monitor logs. See `security.md`.

## Documentation Links
- [Main Design](agent_orchestration.md)
- [API Reference](api.md)
- [Configuration](config.md)
- [Plugin Development](agent_plugin.md)
- [Task Scheduling](task_scheduler.md)
 