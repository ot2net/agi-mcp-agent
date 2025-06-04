.PHONY: install install-dev format lint test clean run docker-build docker-run docker-stop help requirements check security update-deps

# Default python executable
PYTHON ?= python3
# Default poetry executable
POETRY ?= poetry

help:
	@echo "Makefile for the AGI-MCP-Agent project"
	@echo ""
	@echo "Installation:"
	@echo "  make install       Install production dependencies with Poetry"
	@echo "  make install-dev   Install development dependencies with Poetry"
	@echo "  make install-pip   Install dependencies using pip (for Docker)"
	@echo "  make requirements  Generate requirements.txt from pyproject.toml"
	@echo ""
	@echo "Development:"
	@echo "  make format        Format code with Black and isort"
	@echo "  make lint          Run linters (flake8, mypy)"
	@echo "  make test          Run tests with pytest"
	@echo "  make test-cov      Run tests with coverage report"
	@echo "  make check         Run all quality checks (format, lint, test)"
	@echo "  make security      Run security checks"
	@echo ""
	@echo "Running:"
	@echo "  make run           Run the API server with Poetry"
	@echo "  make run-pip       Run the API server without Poetry (for Docker)"
	@echo "  make run-dev       Run in development mode with hot reload"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  Build the Docker image"
	@echo "  make docker-run    Run the Docker container"
	@echo "  make docker-stop   Stop the Docker container"
	@echo "  make docker-logs   View Docker container logs"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean         Remove Python file artifacts"
	@echo "  make update-deps   Update dependencies to latest versions"
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
	$(POETRY) run black agi_mcp_agent tests examples scripts
	$(POETRY) run isort agi_mcp_agent tests examples scripts

lint:
	$(POETRY) run flake8 agi_mcp_agent tests examples scripts --max-line-length=88 --extend-ignore=E203,W503
	$(POETRY) run mypy agi_mcp_agent --ignore-missing-imports

test:
	$(POETRY) run pytest -v

test-cov:
	$(POETRY) run pytest -v --cov=agi_mcp_agent --cov-report=html --cov-report=term

check: format lint test
	@echo "All quality checks passed!"

security:
	$(POETRY) run bandit -r agi_mcp_agent -f json -o security-report.json || true
	$(POETRY) run safety check || true

update-deps:
	$(POETRY) update
	$(POETRY) export -f requirements.txt --output requirements.txt --without-hashes

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf security-report.json
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

run:
	$(POETRY) run python -m uvicorn agi_mcp_agent.api.server:app --host 0.0.0.0 --port 8000 --reload

run-pip:
	$(PYTHON) -m uvicorn agi_mcp_agent.api.server:app --host 0.0.0.0 --port 8000

run-dev:
	$(POETRY) run python -m uvicorn agi_mcp_agent.api.server:app --host 0.0.0.0 --port 8000 --reload --log-level debug

docker-build:
	docker-compose build

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

# 健康检查
health-check:
	@curl -f http://localhost:8000/health || echo "Health check failed"

# 数据库相关命令
db-init:
	$(POETRY) run alembic upgrade head

db-migrate:
	$(POETRY) run alembic revision --autogenerate -m "Auto migration"

db-upgrade:
	$(POETRY) run alembic upgrade head

db-downgrade:
	$(POETRY) run alembic downgrade -1 