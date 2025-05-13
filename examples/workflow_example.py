#!/usr/bin/env python3
"""
Example demonstrating the workflow engine in AGI-MCP-Agent.

This example shows how to:
1. Register environments and agents
2. Define and execute a workflow
3. Connect environments, agents, and tasks together
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agi_mcp_agent.workflow import WorkflowEngine, WorkflowStep, Workflow
from agi_mcp_agent.workflow.registry import EnvironmentRegistry, AgentRegistry
from agi_mcp_agent.environment import FileSystemEnvironment, MemoryEnvironment
from agi_mcp_agent.agent.llm_providers.manager import model_manager
from agi_mcp_agent.agent.llm_agent import LLMAgent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Run the workflow example."""
    logger.info("=== Workflow Engine Example ===")
    
    # Create environment and agent registries
    env_registry = EnvironmentRegistry()
    agent_registry = AgentRegistry()
    
    # Initialize and register environments
    try:
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        os.makedirs(data_dir, exist_ok=True)
        
        # File system environment
        fs_env = FileSystemEnvironment(
            name="file-system",
            root_dir=data_dir,
            sandbox=True
        )
        env_registry.register("fs", fs_env)
        
        # Memory environment
        memory_dir = os.path.join(data_dir, "memories")
        os.makedirs(memory_dir, exist_ok=True)
        mem_env = MemoryEnvironment(
            name="memory",
            storage_dir=memory_dir
        )
        env_registry.register("memory", mem_env)
        
        logger.info(f"Registered environments: {env_registry.list()}")
    except Exception as e:
        logger.error(f"Error initializing environments: {e}")
        return
    
    # Initialize and register agents
    try:
        # Simple LLM agent (the default model will depend on what you have configured)
        simple_agent = LLMAgent(
            name="text-agent",
            capabilities=["text-generation", "summarization"],
            model_identifier="openai:gpt-3.5-turbo",  # Will fall back if not available
            temperature=0.7
        )
        agent_registry.register("text", simple_agent)
        
        logger.info(f"Registered agents: {agent_registry.list()}")
    except Exception as e:
        logger.error(f"Error initializing agents: {e}")
        return
    
    # Initialize workflow engine
    workflow_engine = WorkflowEngine(env_registry, agent_registry)
    
    # Define a simple workflow
    workflow_definition = {
        "id": "document-processing",
        "name": "Document Processing Workflow",
        "description": "Process a document by writing it, reading it, and summarizing it",
        "steps": {
            "write_document": {
                "name": "Write Document",
                "type": "environment_action",
                "environment": "fs",
                "action": {
                    "operation": "write",
                    "path": "example_doc.txt",
                    "content": "# AGI-MCP-Agent\n\nThe AGI-MCP-Agent system provides a comprehensive framework for integrating large language models with external environments. It offers a flexible architecture for defining agents that can interact with file systems, memory stores, databases, and web services.\n\nThe system includes several key components:\n\n1. **Environments**: Interfaces to external systems like file storage, APIs, and databases\n2. **Agents**: Intelligent components powered by LLMs that can perform tasks\n3. **MCP**: The Multi-Cloud Platform that orchestrates agents and tasks\n4. **Workflow Engine**: A system to connect environments, agents, and tasks\n\nThis framework is designed to be extensible and modular, allowing for easy integration of new capabilities and models."
                },
                "output_key": "write_result"
            },
            "read_document": {
                "name": "Read Document",
                "type": "environment_action",
                "depends_on": ["write_document"],
                "environment": "fs",
                "action": {
                    "operation": "read",
                    "path": "example_doc.txt"
                },
                "output_key": "document_content"
            },
            "store_in_memory": {
                "name": "Store in Memory",
                "type": "environment_action",
                "depends_on": ["read_document"],
                "environment": "memory",
                "action": {
                    "operation": "store",
                    "key": "example_doc",
                    "data": "{{ document_content }}",
                    "tags": ["document", "example"]
                },
                "output_key": "memory_store_result"
            },
            "summarize": {
                "name": "Summarize Document",
                "type": "agent_task",
                "depends_on": ["read_document"],
                "agent": "text",
                "task_input": {
                    "prompt": "Summarize the following document in 2-3 sentences:\n\n{{ document_content }}",
                    "max_tokens": 150
                },
                "output_key": "summary"
            },
            "store_summary": {
                "name": "Store Summary",
                "type": "environment_action",
                "depends_on": ["summarize"],
                "environment": "memory",
                "action": {
                    "operation": "store",
                    "key": "example_doc_summary",
                    "data": "{{ summary }}",
                    "tags": ["summary", "example"]
                },
                "output_key": "summary_store_result"
            },
            "write_summary": {
                "name": "Write Summary",
                "type": "environment_action",
                "depends_on": ["summarize"],
                "environment": "fs",
                "action": {
                    "operation": "write",
                    "path": "example_summary.txt",
                    "content": "SUMMARY:\n\n{{ summary }}"
                },
                "output_key": "write_summary_result"
            }
        }
    }
    
    # Create and register the workflow
    try:
        workflow = workflow_engine.create_workflow_from_dict(workflow_definition)
        workflow_id = workflow_engine.register_workflow(workflow)
        logger.info(f"Registered workflow '{workflow.name}' with ID {workflow_id}")
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        return
    
    # Execute the workflow
    try:
        logger.info("Executing workflow...")
        result = await workflow_engine.execute_workflow(workflow_id)
        
        if result["status"] == "completed":
            logger.info(f"Workflow completed successfully in {result['duration']:.2f} seconds")
            
            # Display the summary
            summary = result["results"].get("summarize")
            if summary:
                logger.info("\nGenerated Summary:")
                logger.info("-----------------")
                logger.info(f"{summary}")
                logger.info("-----------------")
        else:
            logger.error(f"Workflow failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 