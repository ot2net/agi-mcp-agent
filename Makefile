.PHONY: install install-dev format lint test clean run docker-build docker-run docker-stop help requirements

# Default python executable
PYTHON ?= python3
# Default poetry executable
POETRY ?= poetry

help:
	@echo "Makefile for the AGI-MCP-Agent project"
	@echo ""
	@echo "Usage:"
	@echo "  make install       Install production dependencies with Poetry"
	@echo "  make install-dev   Install development dependencies with Poetry"
	@echo "  make requirements  Generate requirements.txt from pyproject.toml"
	@echo "  make install-pip   Install dependencies using pip (for Docker)"
	@echo "  make format        Format code with Black and isort"
	@echo "  make lint          Run linters (flake8, mypy)"
	@echo "  make test          Run tests with pytest"
	@echo "  make clean         Remove Python file artifacts"
	@echo "  make run           Run the API server with Poetry"
	@echo "  make run-pip       Run the API server without Poetry (for Docker)"
	@echo "  make docker-build  Build the Docker image"
	@echo "  make docker-run    Run the Docker container"
	@echo "  make docker-stop   Stop the Docker container"
	@echo ""

install:
	$(POETRY) install --no-dev

install-dev:
	$(POETRY) install
	$(POETRY) run pre-commit install

requirements:
	$(PYTHON) generate_requirements.py

install-pip: requirements
	pip install -r requirements.txt

format:
	$(POETRY) run black agi_mcp_agent tests examples
	$(POETRY) run isort agi_mcp_agent tests examples

lint:
	$(POETRY) run flake8 agi_mcp_agent tests examples
	$(POETRY) run mypy agi_mcp_agent

test:
	$(POETRY) run pytest -v

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

run:
	$(POETRY) run python -m uvicorn agi_mcp_agent.api.server:app --host 0.0.0.0 --port 8000 --reload

run-pip:
	$(PYTHON) -m uvicorn agi_mcp_agent.api.server:app --host 0.0.0.0 --port 8000 --reload

docker-build:
	docker-compose build

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down 