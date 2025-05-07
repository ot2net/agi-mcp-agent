# Contributing to AGI-MCP-Agent

Thank you for considering contributing to AGI-MCP-Agent! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to uphold our Code of Conduct (to be established). Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

- Check if the bug has already been reported in the Issues section
- Use the bug report template when creating a new issue
- Include detailed steps to reproduce the bug
- Provide information about your environment (OS, Python version, etc.)

### Suggesting Features

- Check if the feature has already been suggested in the Issues section
- Use the feature request template when creating a new issue
- Clearly describe the feature and its potential benefits
- If possible, outline how the feature might be implemented

### Pull Requests

1. Fork the repository
2. Create a new branch for your changes
3. Make your changes
4. Run tests and ensure they pass
5. Submit a pull request

## Development Setup

1. Clone the repository
   ```bash
   git clone https://github.com/ot2net/agi-mcp-agent.git
   cd agi-mcp-agent
   ```

2. Install Poetry if you haven't already
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Install dependencies using Poetry
   ```bash
   poetry install
   ```

4. Install pre-commit hooks
   ```bash
   poetry run pre-commit install
   ```

5. Create a .env file for environment variables
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Docker Development

If you prefer to use Docker for development:

1. Build the development image
   ```bash
   docker-compose build
   ```

2. Run the development server
   ```bash
   docker-compose up
   ```

3. Run tests in the container
   ```bash
   docker-compose exec backend poetry run pytest
   ```

## Coding Standards

- Follow PEP 8 style guidelines for Python code
- Write descriptive commit messages
- Include docstrings for all functions, classes, and modules
- Write tests for new features and bug fixes
- We use Black and isort for code formatting, which you can run with `poetry run black .` and `poetry run isort .`

## Project Structure

```
agi-mcp-agent/
├── agi_mcp_agent/       # Main package
│   ├── agent/           # Agent implementation
│   ├── mcp/             # Master Control Program
│   ├── environment/     # Environment interfaces
│   └── utils/           # Utility functions
├── frontend/            # React frontend (if applicable)
├── tests/               # Test suite
├── examples/            # Example use cases
└── docs/                # Documentation
```

## Testing

Run tests using pytest through Poetry:

```bash
poetry run pytest
```

Or use the Makefile:

```bash
make test
```

## Documentation

- Update documentation for any changes to APIs or functionality
- Follow Google's Python Style Guide for docstrings

## Questions?

Feel free to ask questions by creating an issue labeled "question".

Visit [OT2.net](https://ot2.net) to join our community! 