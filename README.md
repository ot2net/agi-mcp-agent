[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/ot2net-agi-mcp-agent-badge.png)](https://mseep.ai/app/ot2net-agi-mcp-agent)

# AGI-MCP-Agent

[![GitHub Stars](https://img.shields.io/github/stars/ot2net/agi-mcp-agent?style=social)](https://github.com/ot2net/agi-mcp-agent)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Join the community](https://img.shields.io/badge/join-ot2.net-orange)](https://ot2.net)

## Overview

AGI-MCP-Agent is an open-source intelligent agent framework designed to explore and implement advanced agent capabilities through a Master Control Program (MCP) architecture. This project aims to create a flexible, extensible platform for autonomous agents that can perform complex tasks, learn from interactions, and coordinate multi-agent systems.

Visit [OT2.net](https://ot2.net) to learn more about our ecosystem and join our community!

## Vision

Our vision is to build a foundational framework for intelligent agents that can:

1. Operate autonomously to solve complex problems
2. Learn and adapt through interactions with the environment and other agents
3. Integrate with various tools, APIs, and data sources
4. Support multi-agent coordination and communication
5. Provide researchers and developers with a flexible platform for AI experimentation

## Architecture

The AGI-MCP-Agent architecture consists of several key components:

### Master Control Program (MCP)
The central coordination system that:
- Manages agent lifecycles
- Schedules and prioritizes tasks
- Monitors performance and system health
- Provides orchestration of multi-agent systems

### Agent Framework
The core agent capabilities:
- Cognitive processing (planning, reasoning, decision-making)
- Memory management (short-term and long-term)
- Tool/API integrations
- Perception modules
- Action generation
- Self-monitoring and reflection

### Environment Interface
- Standardized APIs for interacting with external systems
- Data ingestion pipelines
- Output formatting and delivery
- Sandboxed execution for security

### Multi-Agent Coordination
- Communication protocols between agents
- Role definition and assignment
- Collaborative problem-solving mechanisms
- Conflict resolution strategies

## Roadmap

### Phase 1: Foundation (Current)
- Core MCP implementation
- Basic agent capabilities
- Environment interface design
- Initial documentation and examples

### Phase 2: Expansion
- Advanced cognitive models
- Memory optimization
- Tool integration framework
- Performance benchmarks

### Phase 3: Multi-Agent
- Agent communication protocols
- Collaborative task solving
- Specialization and role assignment
- Swarm intelligence capabilities

### Phase 4: Applications
- Domain-specific agent templates
- Real-world use case implementations
- User-friendly interfaces
- Enterprise integration options

## Technical Stack

- **Backend**: Python
  - FastAPI for API interfaces
  - Pydantic for data validation
  - SQLAlchemy for database interactions
  - LangChain for LLM orchestration

- **Frontend**: React
  - Next.js framework
  - TypeScript for type safety
  - Tailwind CSS for styling
  - Redux for state management

- **DevOps**:
  - Docker for containerization
  - GitHub Actions for CI/CD
  - Pytest for testing

## Getting Started

### Prerequisites

- Python 3.9 or later
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management (recommended)
- PostgreSQL 12+ (or SQLite for development)
- OpenAI API key (for LLM-based agents)
- Docker and Docker Compose (optional, for containerized deployment)

### Quick Start with Docker (Recommended)

The fastest way to get started is using Docker Compose:

1. Clone the repository
   ```bash
   git clone https://github.com/ot2net/agi-mcp-agent.git
   cd agi-mcp-agent
   ```

2. Copy and configure environment variables
   ```bash
   cp example.env .env
   # Edit .env with your API keys and configuration
   ```

3. Start the services
   ```bash
   # Start backend with database
   docker-compose up -d
   
   # Or start with frontend included
   docker-compose --profile frontend up -d
   ```

4. Access the application
   - API: http://localhost:8000
   - Frontend (if enabled): http://localhost:3000
   - API Documentation: http://localhost:8000/docs

### Local Development Setup

#### With Poetry (Recommended for Development)

1. Clone the repository
   ```bash
   git clone https://github.com/ot2net/agi-mcp-agent.git
   cd agi-mcp-agent
   ```

2. Install dependencies using Poetry
   ```bash
   make install-dev
   # or manually: poetry install
   ```

3. Set up environment variables
   ```bash
   cp example.env .env
   # Edit .env with your configuration
   ```

4. Initialize the database
   ```bash
   make db-init
   ```

5. Run the development server
   ```bash
   make run-dev
   # or manually: poetry run python -m uvicorn agi_mcp_agent.api.server:app --host 0.0.0.0 --port 8000 --reload
   ```

#### Without Poetry (Simplified Approach)

1. Clone the repository
   ```bash
   git clone https://github.com/ot2net/agi-mcp-agent.git
   cd agi-mcp-agent
   ```

2. Generate and install dependencies
   ```bash
   make requirements
   pip install -r requirements.txt
   ```

3. Set up environment variables
   ```bash
   cp example.env .env
   # Edit .env with your configuration
   ```

4. Run the development server
   ```bash
   make run-pip
   ```

### Using the Makefile

The project includes a comprehensive Makefile with useful commands:

```bash
# Development commands
make help          # Show all available commands
make install-dev   # Install development dependencies
make format        # Format code with Black and isort
make lint          # Run linters (flake8, mypy)
make test          # Run tests
make test-cov      # Run tests with coverage report
make check         # Run all quality checks
make security      # Run security checks

# Running commands
make run           # Run server with Poetry
make run-dev       # Run in development mode with hot reload
make run-pip       # Run server with pip (without Poetry)

# Docker commands
make docker-build  # Build Docker image
make docker-run    # Run Docker container
make docker-stop   # Stop Docker container
make docker-logs   # View container logs

# Database commands
make db-init       # Initialize database
make db-migrate    # Create new migration
make db-upgrade    # Apply migrations

# Maintenance commands
make clean         # Remove build artifacts
make update-deps   # Update dependencies
make health-check  # Check if server is running
```

## Contributing

We welcome contributions from the community! Please check our [Contributing Guidelines](CONTRIBUTING.md) to get started.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Connect with Us

- [OT2.net](https://ot2.net)
- [GitHub Organization](https://github.com/ot2net)

Join our community to discuss ideas, collaborate on development, and help shape the future of intelligent agent systems! 