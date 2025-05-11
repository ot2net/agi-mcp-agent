"""Example usage of the MCP (Multi-Cloud Platform) system."""

import asyncio
import logging
from datetime import datetime

from agi_mcp_agent.mcp.core import MasterControlProgram
from agi_mcp_agent.mcp.models import Agent, Task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Run the MCP example."""
    # Initialize MCP with database URL
    mcp = MasterControlProgram("postgresql://user:password@localhost:5432/mcp_db")

    # Create and register an agent
    agent = Agent(
        name="example_agent",
        type="llm",
        capabilities={
            "tasks": ["text_generation", "text_analysis"],
            "models": ["gpt-3.5-turbo", "gpt-4"]
        }
    )
    agent_id = await mcp.register_agent(agent)
    if not agent_id:
        logger.error("Failed to register agent")
        return

    # Create a task
    task = Task(
        name="example_task",
        description="Generate a summary of the given text",
        priority=7,
        input_data={
            "text": "This is an example text that needs to be summarized.",
            "max_length": 100
        }
    )
    task_id = await mcp.create_task(task)
    if not task_id:
        logger.error("Failed to create task")
        return

    # Start the MCP
    try:
        # Run the MCP for a few seconds
        mcp_task = asyncio.create_task(mcp.start())
        await asyncio.sleep(5)

        # Update task status
        await mcp.update_task_status(
            task_id,
            "completed",
            output_data={"summary": "Example text summary."}
        )

        # Get system status
        status = await mcp.get_system_status()
        if status:
            logger.info(f"System status: {status.dict()}")

        # Stop the MCP
        mcp.stop()
        await mcp_task

    except Exception as e:
        logger.error(f"Error running MCP: {e}")
        mcp.stop()


if __name__ == "__main__":
    asyncio.run(main()) 