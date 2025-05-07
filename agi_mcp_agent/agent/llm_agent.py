"""LLM-powered agent implementation."""

import logging
import os
import time
from typing import Any, Dict, List, Optional

from langchain.callbacks.manager import CallbackManager
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

from agi_mcp_agent.agent.base import Agent
from agi_mcp_agent.mcp.core import Task

logger = logging.getLogger(__name__)


class LLMAgent(Agent):
    """Language Learning Model (LLM) powered agent."""

    def __init__(
        self,
        name: str,
        capabilities: List[str] = None,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
    ):
        """Initialize the LLM agent.

        Args:
            name: The name of the agent
            capabilities: List of capabilities this agent has
            model_name: The name of the LLM model to use
            temperature: The temperature to use for the LLM
        """
        if not capabilities:
            capabilities = ["text-generation", "question-answering", "summarization"]
        super().__init__(name, capabilities)
        
        # Ensure the API key is available
        if not os.environ.get("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY not found in environment variables")
        
        self.model_name = model_name
        self.temperature = temperature
        self.llm = OpenAI(
            model_name=model_name,
            temperature=temperature,
        )
        
        # Task tracking
        self.task_status: Dict[str, Dict[str, Any]] = {}
        logger.info(f"LLM Agent {self.name} initialized with model {model_name}")

    def execute_task(self, task: Task) -> None:
        """Execute a task using the LLM.

        Args:
            task: The task to execute
        """
        logger.info(f"Executing task {task.id} with LLM agent {self.id}")
        
        self.task_status[task.id] = {
            "status": "running",
            "start_time": time.time(),
            "result": None,
            "error": None,
        }
        
        # Process the task based on the metadata
        try:
            if "prompt" in task.metadata:
                prompt = task.metadata["prompt"]
                prompt_template = PromptTemplate.from_template(prompt)
                
                # Create a chain with the prompt and LLM
                chain = LLMChain(llm=self.llm, prompt=prompt_template)
                
                # Execute the chain with the input variables
                input_variables = task.metadata.get("input_variables", {})
                result = chain.run(**input_variables)
                
                # Store the result
                self.task_status[task.id]["result"] = result
                self.task_status[task.id]["status"] = "completed"
                logger.info(f"Task {task.id} completed successfully")
                
                # Store the result in memory for future reference
                self.store_in_memory(f"task:{task.id}:result", result)
                
                # Complete the task
                self.complete_task(task.id, result)
            else:
                error_msg = "Task metadata does not contain a prompt"
                logger.error(f"Error executing task {task.id}: {error_msg}")
                self.task_status[task.id]["error"] = error_msg
                self.task_status[task.id]["status"] = "failed"
                self.handle_error(task.id, error_msg)
                
        except Exception as e:
            logger.error(f"Error executing task {task.id}: {str(e)}")
            self.task_status[task.id]["error"] = str(e)
            self.task_status[task.id]["status"] = "failed"
            self.handle_error(task.id, str(e))

    def is_task_complete(self, task_id: str) -> bool:
        """Check if a task is complete.

        Args:
            task_id: The ID of the task to check

        Returns:
            Whether the task is complete
        """
        if task_id not in self.task_status:
            return False
        
        return self.task_status[task_id]["status"] in ["completed", "failed"]

    def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get the result of a completed task.

        Args:
            task_id: The ID of the task

        Returns:
            The task result, if available
        """
        if task_id not in self.task_status:
            logger.warning(f"Task {task_id} not found in agent {self.id}")
            return None
        
        if self.task_status[task_id]["status"] != "completed":
            logger.warning(f"Task {task_id} is not completed")
            return None
        
        return self.task_status[task_id]["result"]


class MultiToolLLMAgent(LLMAgent):
    """LLM agent with the ability to use multiple external tools."""
    
    def __init__(
        self,
        name: str,
        tools: List[Any] = None,
        capabilities: List[str] = None,
        model_name: str = "gpt-3.5-turbo-16k",
        temperature: float = 0.7,
    ):
        """Initialize the multi-tool LLM agent.

        Args:
            name: The name of the agent
            tools: List of tools this agent can use
            capabilities: List of capabilities this agent has
            model_name: The name of the LLM model to use
            temperature: The temperature to use for the LLM
        """
        # Add tool-specific capabilities
        if capabilities is None:
            capabilities = []
        
        # Add default capabilities for this type of agent
        if "tool-use" not in capabilities:
            capabilities.append("tool-use")
        
        super().__init__(name, capabilities, model_name, temperature)
        
        self.tools = tools or []
        logger.info(f"MultiToolLLMAgent {self.name} initialized with {len(self.tools)} tools")
    
    def add_tool(self, tool: Any) -> None:
        """Add a tool to the agent.

        Args:
            tool: The tool to add
        """
        self.tools.append(tool)
        logger.info(f"Added tool {tool.name} to agent {self.id}")
    
    def execute_task(self, task: Task) -> None:
        """Execute a task using the LLM and available tools.

        Args:
            task: The task to execute
        """
        logger.info(f"Executing task {task.id} with MultiToolLLMAgent {self.id}")
        
        self.task_status[task.id] = {
            "status": "running",
            "start_time": time.time(),
            "result": None,
            "error": None,
        }
        
        # Here, we would implement a more complex execution logic
        # that uses available tools to solve the task
        # For simplicity, we're just calling the parent method for now
        super().execute_task(task) 