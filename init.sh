#!/bin/bash

# AGI-MCP-Agent initialization script
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Initializing AGI-MCP-Agent project...${NC}"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${YELLOW}Poetry not found. Installing Poetry...${NC}"
    curl -sSL https://install.python-poetry.org | python3 -
    echo -e "${GREEN}Poetry installed successfully!${NC}"
fi

# Install dependencies using Poetry
echo -e "${GREEN}Installing dependencies with Poetry...${NC}"
poetry install
echo -e "${GREEN}Dependencies installed successfully!${NC}"

# Install pre-commit hooks
echo -e "${GREEN}Installing pre-commit hooks...${NC}"
poetry run pre-commit install
echo -e "${GREEN}Pre-commit hooks installed successfully!${NC}"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cat > .env << EOF
# API Settings
AGI_MCP_API_HOST=0.0.0.0
AGI_MCP_API_PORT=8000
AGI_MCP_LOG_LEVEL=INFO

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
EOF
    echo -e "${YELLOW}Please edit the .env file and set your OPENAI_API_KEY${NC}"
else
    echo -e "${GREEN}.env file already exists. Skipping creation.${NC}"
fi

# Check if data directory exists, if not create it
if [ ! -d "data" ]; then
    echo -e "${GREEN}Creating data directory...${NC}"
    mkdir -p data
fi

echo -e "${GREEN}Initialization complete!${NC}"
echo -e "${YELLOW}To run the development server:${NC}"
echo -e "  poetry run python -m uvicorn agi_mcp_agent.api.server:app --host 0.0.0.0 --port 8000 --reload"
echo -e "${YELLOW}Or use the Makefile:${NC}"
echo -e "  make run"
echo -e "${YELLOW}To run with Docker:${NC}"
echo -e "  docker-compose up --build" 