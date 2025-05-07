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

- Python 3.8 or later
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management (optional)
- OpenAI API key (for LLM-based agents)
- Docker and Docker Compose (optional, for containerized deployment)

### Local Development Setup

#### With Poetry (Recommended for Development)

1. Clone the repository
   ```bash
   git clone https://github.com/ot2net/agi-mcp-agent.git
   cd agi-mcp-agent
   ```

2. Install dependencies using Poetry
   ```bash
   poetry install
   ```

3. Set up environment variables
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

4. Run the development server
   ```bash
   poetry run python -m uvicorn agi_mcp_agent.api.server:app --host 0.0.0.0 --port 8000 --reload
   ```

#### Without Poetry (Simplified Approach)

1. Clone the repository
   ```bash
   git clone https://github.com/ot2net/agi-mcp-agent.git
   cd agi-mcp-agent
   ```

2. Generate and install dependencies
   ```bash
   python generate_requirements.py
   pip install -r requirements.txt
   ```

3. Set up environment variables
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

4. Run the development server
   ```bash
   python -m uvicorn agi_mcp_agent.api.server:app --host 0.0.0.0 --port 8000 --reload
   ```

### Using the Makefile

The project includes a Makefile with useful commands:
```bash
make help          # Show available commands
make install-dev   # Install development dependencies with Poetry
make install-pip   # Install dependencies with pip (without Poetry)
make requirements  # Generate requirements.txt from pyproject.toml
make format        # Format code with Black and isort
make lint          # Run linters
make test          # Run tests
make run           # Run server with Poetry
make run-pip       # Run server with pip (without Poetry)
make docker-build  # Build Docker image
make docker-run    # Run Docker container
make docker-stop   # Stop Docker container
```

### Using Docker

#### Quick Start with Docker Compose

1. Build and run with Docker Compose
   ```bash
   docker-compose up --build
   ```

2. Access the API at http://localhost:8000

3. Stop the containers when done
   ```bash
   docker-compose down
   ```

#### Custom Docker Configuration

The project includes two Dockerfiles:
- `Dockerfile` - For the backend API
- `Dockerfile.frontend` - For the frontend Next.js application

The Docker setup automatically extracts dependencies from `pyproject.toml` and doesn't require Poetry to be installed in the container.

To customize the Docker build:
1. Edit environment variables in `docker-compose.yml`
2. Build the images: `docker-compose build`
3. Run the containers: `docker-compose up -d`

## Contributing

We welcome contributions from the community! Please check our [Contributing Guidelines](CONTRIBUTING.md) to get started.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Connect with Us

- [OT2.net](https://ot2.net)
- [GitHub Organization](https://github.com/ot2net)

Join our community to discuss ideas, collaborate on development, and help shape the future of intelligent agent systems! 