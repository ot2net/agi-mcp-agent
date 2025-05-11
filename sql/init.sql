-- AGI MCP Agent Database Schema
-- This file contains all necessary database tables and extensions for the AGI MCP Agent system

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- MCP Core Schema
-- Table: mcp_agents
CREATE TABLE IF NOT EXISTS mcp_agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    type VARCHAR(64) NOT NULL,  -- e.g. 'llm', 'tool', 'orchestrator'
    capabilities JSONB NOT NULL, -- Array of capabilities this agent has
    status VARCHAR(16) DEFAULT 'active',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table: mcp_tasks
CREATE TABLE IF NOT EXISTS mcp_tasks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    description TEXT,
    status VARCHAR(16) DEFAULT 'pending', -- pending, running, completed, failed
    priority INTEGER DEFAULT 5,           -- 1-10 scale, 10 being highest
    agent_id INTEGER REFERENCES mcp_agents(id) ON DELETE SET NULL,
    parent_task_id INTEGER REFERENCES mcp_tasks(id) ON DELETE SET NULL,
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Table: mcp_task_dependencies
CREATE TABLE IF NOT EXISTS mcp_task_dependencies (
    task_id INTEGER REFERENCES mcp_tasks(id) ON DELETE CASCADE,
    dependency_id INTEGER REFERENCES mcp_tasks(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (task_id, dependency_id)
);

-- Table: mcp_agent_metrics
CREATE TABLE IF NOT EXISTS mcp_agent_metrics (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER REFERENCES mcp_agents(id) ON DELETE CASCADE,
    metric_name VARCHAR(64) NOT NULL,
    metric_value FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Table: mcp_system_logs
CREATE TABLE IF NOT EXISTS mcp_system_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(16) NOT NULL, -- info, warning, error, debug
    component VARCHAR(64) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- LLM Schema
-- Table: llm_providers
CREATE TABLE IF NOT EXISTS llm_providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL, -- e.g. 'openai', 'anthropic'
    type VARCHAR(32) NOT NULL,        -- e.g. 'openai', 'anthropic', 'rest'
    api_key TEXT NOT NULL,
    models TEXT[],                    -- List of supported model names
    status VARCHAR(16) DEFAULT 'enabled',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table: llm_models
CREATE TABLE IF NOT EXISTS llm_models (
    id SERIAL PRIMARY KEY,
    provider_id INTEGER REFERENCES llm_providers(id) ON DELETE CASCADE,
    model_name VARCHAR(128) NOT NULL, -- e.g. 'gpt-3.5-turbo'
    capability VARCHAR(64),           -- e.g. 'chat', 'embedding', 'completion'
    params JSONB,                     -- Model-specific parameters
    status VARCHAR(16) DEFAULT 'enabled',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(provider_id, model_name)
);

-- Table: llm_embeddings
CREATE TABLE IF NOT EXISTS llm_embeddings (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES llm_models(id) ON DELETE CASCADE,
    input_text TEXT NOT NULL,
    embedding vector(1536) NOT NULL,  -- Adjust dimension as needed
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table: llm_tasks (optional, for audit/logging)
CREATE TABLE IF NOT EXISTS llm_tasks (
    id SERIAL PRIMARY KEY,
    provider_id INTEGER REFERENCES llm_providers(id) ON DELETE SET NULL,
    model_id INTEGER REFERENCES llm_models(id) ON DELETE SET NULL,
    task_type VARCHAR(32),            -- e.g. 'completion', 'embedding', 'chat'
    input JSONB,
    output JSONB,
    status VARCHAR(16) DEFAULT 'pending',
    error TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_mcp_tasks_status ON mcp_tasks(status);
CREATE INDEX IF NOT EXISTS idx_mcp_tasks_agent_id ON mcp_tasks(agent_id);
CREATE INDEX IF NOT EXISTS idx_mcp_agent_metrics_agent_id ON mcp_agent_metrics(agent_id);
CREATE INDEX IF NOT EXISTS idx_mcp_system_logs_level ON mcp_system_logs(level);
CREATE INDEX IF NOT EXISTS idx_mcp_system_logs_component ON mcp_system_logs(component);
CREATE INDEX IF NOT EXISTS idx_llm_models_provider_id ON llm_models(provider_id);
CREATE INDEX IF NOT EXISTS idx_llm_embeddings_model_id ON llm_embeddings(model_id);
CREATE INDEX IF NOT EXISTS idx_llm_tasks_provider_id ON llm_tasks(provider_id);
CREATE INDEX IF NOT EXISTS idx_llm_tasks_model_id ON llm_tasks(model_id); 