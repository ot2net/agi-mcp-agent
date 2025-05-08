"""LLM-powered agent implementation."""

import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional

from agi_mcp_agent.agent.base import Agent
from agi_mcp_agent.agent.llm_providers.manager import ModelProviderManager
from agi_mcp_agent.mcp.core import Task
from agi_mcp_agent.utils.config import config

logger = logging.getLogger(__name__)

# Create a global model manager instance
model_manager = ModelProviderManager()


class LLMAgent(Agent):
    """Language Learning Model (LLM) powered agent."""
    
    def __init__(
        self,
        name: str,
        capabilities: List[str] = None,
        model_identifier: str = "openai:gpt-3.5-turbo",
        temperature: float = 0.7,
        fallback_models: List[str] = None,
        model_parameters: Dict[str, Any] = None,
        region: Optional[str] = None,
        db_url: Optional[str] = None,
    ):
        """Initialize the LLM agent.
        
        Args:
            name: The name of the agent
            capabilities: List of capabilities this agent has
            model_identifier: The model to use in format 'provider:model_name'
            temperature: The temperature to use for the LLM
            fallback_models: List of fallback models to try if the main model fails
            model_parameters: Additional parameters for the model
            region: Optional region preference (e.g., 'cn' for Chinese models)
            db_url: Optional database URL for model configuration
        """
        if not capabilities:
            capabilities = ["text-generation", "question-answering", "summarization"]
        super().__init__(name, capabilities)
        
        # Set up model parameters
        self.model_identifier = model_identifier
        self.temperature = temperature
        self.fallback_models = fallback_models or []
        self.model_parameters = model_parameters or {}
        self.region = region or os.environ.get("LLM_REGION") or config.get("llm_region")
        
        # Initialize model manager with database support if URL provided
        if db_url:
            self.model_manager = ModelProviderManager(db_url=db_url)
        else:
            # Use the global instance
            self.model_manager = model_manager
        
        # Task tracking
        self.task_status: Dict[str, Dict[str, Any]] = {}
        
        # Validate model identifier and check regional availability
        self._validate_model_identifier()
        
        logger.info(f"LLM Agent {self.name} initialized with model {self.model_identifier}")

    def _validate_model_identifier(self):
        """Validate the model identifier and check regional availability."""
        try:
            provider_name, model_name = self.model_identifier.split(":", 1)
        except ValueError:
            logger.warning(f"Invalid model identifier: {self.model_identifier}. Should be in format 'provider:model_name'")
            
            # If region is specified, try to find a suitable model from that region
            if self.region:
                region_providers = self.model_manager.list_providers_by_region(self.region)
                if region_providers:
                    provider_name = region_providers[0]
                    self.model_identifier = f"{provider_name}:default"
                    logger.warning(f"Using regional provider {provider_name} instead")
                    return
            
            # Otherwise, fall back to default model
            logger.warning("Falling back to openai:gpt-3.5-turbo")
            self.model_identifier = "openai:gpt-3.5-turbo"
            provider_name, model_name = self.model_identifier.split(":", 1)
        
        # Check if provider exists
        if provider_name not in self.model_manager.list_providers():
            logger.warning(f"Provider {provider_name} not available. Checking for alternative providers.")
            
            # If region is specified, try to find a provider from that region
            if self.region:
                region_providers = self.model_manager.list_providers_by_region(self.region)
                if region_providers:
                    logger.warning(f"Using regional provider {region_providers[0]} instead.")
                    self.model_identifier = f"{region_providers[0]}:{model_name}"
                    return
            
            # Otherwise, try any available provider
            available_providers = self.model_manager.list_providers()
            if available_providers:
                logger.warning(f"Using provider {available_providers[0]} instead.")
                # Try to find a similar model from the available provider
                self.model_identifier = f"{available_providers[0]}:{model_name}"
            else:
                logger.error("No LLM providers available. Agent will not function properly.")
                self.model_identifier = "none:none"

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
        asyncio.create_task(self._execute_task_async(task))
    
    async def _execute_task_async(self, task: Task) -> None:
        """Execute a task asynchronously.
        
        Args:
            task: The task to execute
        """
        try:
            if "prompt" in task.metadata:
                prompt = task.metadata["prompt"]
                
                # Execute the prompt with the configured model
                input_variables = task.metadata.get("input_variables", {})
                
                # Format the prompt with input variables
                formatted_prompt = prompt
                for key, value in input_variables.items():
                    formatted_prompt = formatted_prompt.replace(f"{{{key}}}", str(value))
                
                # Try the main model
                result = await self._try_models_with_fallback(formatted_prompt, task.id)
                
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
    
    async def _try_models_with_fallback(self, prompt: str, task_id: str) -> str:
        """Try the main model and fallback to others if it fails.
        
        Args:
            prompt: The prompt to process
            task_id: The task ID
            
        Returns:
            The model response
        """
        models_to_try = [self.model_identifier] + self.fallback_models
        
        # If fallback models not explicitly provided, add region-specific fallbacks
        if not self.fallback_models and self.region:
            capability = "text-completion"  # Default capability for text generation
            fallback = self.model_manager.get_fallback_model(
                capability=capability,
                excluded_models=[self.model_identifier],
                region=self.region
            )
            if fallback and fallback not in models_to_try:
                models_to_try.append(fallback)
        
        for i, model_id in enumerate(models_to_try):
            try:
                if i > 0:
                    logger.warning(f"Falling back to model {model_id} for task {task_id}")
                
                # Call the model
                response = await self.model_manager.generate_text(
                    prompt=prompt,
                    model_identifier=model_id,
                    temperature=self.temperature,
                    **self.model_parameters
                )
                
                # Return the response text
                return response.text
                
            except Exception as e:
                logger.error(f"Error with model {model_id} for task {task_id}: {str(e)}")
                if i == len(models_to_try) - 1:
                    # No more models to try
                    raise
        
        # This should not be reachable, but added for safety
        raise RuntimeError(f"All models failed for task {task_id}")

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
            logger.warning(f"Task {task_id} is not complete. Status: {self.task_status[task_id]['status']}")
            return None
        
        return self.task_status[task_id]["result"]
    
    def get_task_error(self, task_id: str) -> Optional[str]:
        """Get the error of a failed task.
        
        Args:
            task_id: The ID of the task
            
        Returns:
            The error message, if the task failed
        """
        if task_id not in self.task_status:
            logger.warning(f"Task {task_id} not found in agent {self.id}")
            return None
        
        if self.task_status[task_id]["status"] != "failed":
            logger.warning(f"Task {task_id} has not failed. Status: {self.task_status[task_id]['status']}")
            return None
        
        return self.task_status[task_id]["error"]


class MultiToolLLMAgent(LLMAgent):
    """LLM agent with the ability to use multiple external tools."""
    
    def __init__(
        self,
        name: str,
        tools: List[Any] = None,
        capabilities: List[str] = None,
        model_identifier: str = "openai:gpt-4",
        temperature: float = 0.7,
        fallback_models: List[str] = None,
        model_parameters: Dict[str, Any] = None,
    ):
        """Initialize the multi-tool LLM agent.

        Args:
            name: The name of the agent
            tools: List of tools this agent can use
            capabilities: List of capabilities this agent has
            model_identifier: The model to use in format 'provider:model_name'
            temperature: The temperature to use for the LLM
            fallback_models: List of fallback models to try if the main model fails
            model_parameters: Additional parameters for the model
        """
        # Add tool-specific capabilities
        if capabilities is None:
            capabilities = []
        
        # Add default capabilities for this type of agent
        if "tool-use" not in capabilities:
            capabilities.append("tool-use")
        
        # Set default fallback models for the multi-tool agent if not provided
        if fallback_models is None:
            # Try to find capable fallback models
            fallback_models = []
            for provider in ["openai", "anthropic", "google", "mistral"]:
                if provider != model_identifier.split(":")[0]:  # Don't include the main provider
                    capable_models = model_manager.list_models_by_capability("function-calling")
                    for model in capable_models:
                        if model["provider"] == provider:
                            fallback_models.append(f"{provider}:{model['name']}")
                            break
        
        super().__init__(
            name=name, 
            capabilities=capabilities, 
            model_identifier=model_identifier,
            temperature=temperature,
            fallback_models=fallback_models,
            model_parameters=model_parameters,
        )
        
        self.tools = tools or []
        logger.info(f"MultiToolLLMAgent {self.name} initialized with {len(self.tools)} tools")
    
    def add_tool(self, tool: Any) -> None:
        """Add a tool to the agent.

        Args:
            tool: The tool to add
        """
        self.tools.append(tool)
        logger.info(f"Added tool {tool.name} to agent {self.id}")
    
    async def _execute_task_async(self, task: Task) -> None:
        """Execute a task using the LLM and available tools.

        Args:
            task: The task to execute
        """
        try:
            if "prompt" in task.metadata:
                prompt = task.metadata["prompt"]
                input_variables = task.metadata.get("input_variables", {})
                
                # Format the prompt with input variables
                formatted_prompt = prompt
                for key, value in input_variables.items():
                    formatted_prompt = formatted_prompt.replace(f"{{{key}}}", str(value))
                
                # Analyze the task to determine needed tools
                task_analysis = await self._analyze_task(formatted_prompt, task.id)
                
                # Select appropriate tools based on analysis
                tools_to_use = self._select_tools(task_analysis)
                
                # Create messages for function calling
                messages = [
                    {"role": "system", "content": self._create_system_prompt(tools_to_use)},
                    {"role": "user", "content": formatted_prompt}
                ]
                
                # Execute with function calling
                if tools_to_use:
                    # Use chat completion for function calling
                    result = await self._execute_with_tools(messages, tools_to_use, task.id)
                else:
                    # No tools needed, use standard completion
                    result = await self._try_models_with_fallback(formatted_prompt, task.id)
                
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
    
    async def _analyze_task(self, prompt: str, task_id: str) -> Dict[str, Any]:
        """Analyze a task to determine which tools might be needed.
        
        Args:
            prompt: The task prompt
            task_id: The task ID
            
        Returns:
            Analysis with recommended tools and approach
        """
        # Create an analysis prompt
        analysis_prompt = f"""
        You are an AI assistant specialized in task analysis. Your job is to analyze a given task and determine:
        1. What tools might be needed to solve the task
        2. What approach should be taken to solve the task
        3. What sub-tasks need to be completed
        
        Here is the task:
        
        {prompt}
        
        Available tools:
        {self._format_tools_description()}
        
        Return a JSON object with the following fields:
        - needed_tools: List of tool names that will be needed (empty list if none)
        - approach: String describing the approach to take
        - sub_tasks: List of sub-tasks to complete
        """
        
        try:
            # Use a simpler model for analysis to save cost
            analysis_model = "openai:gpt-3.5-turbo"
            for provider in model_manager.list_providers():
                models = model_manager.list_models_by_provider(provider)
                if models:
                    analysis_model = f"{provider}:{models[0]['name']}"
                    break
            
            # Get analysis from a simpler model
            analysis_response = await model_manager.generate_text(
                prompt=analysis_prompt,
                model_identifier=analysis_model,
                temperature=0.2,  # Low temperature for more deterministic response
                max_tokens=1000,
            )
            
            # Try to parse the response as JSON
            import json
            try:
                analysis = json.loads(analysis_response.text)
                return analysis
            except json.JSONDecodeError:
                logger.warning(f"Could not parse analysis as JSON for task {task_id}")
                # Return a simple analysis if parsing fails
                return {
                    "needed_tools": [],
                    "approach": "Use direct completion",
                    "sub_tasks": ["Complete the task directly"]
                }
                
        except Exception as e:
            logger.error(f"Error analyzing task {task_id}: {str(e)}")
            # Return a simple analysis if an error occurs
            return {
                "needed_tools": [],
                "approach": "Use direct completion",
                "sub_tasks": ["Complete the task directly"]
            }
    
    def _select_tools(self, analysis: Dict[str, Any]) -> List[Any]:
        """Select tools based on task analysis.
        
        Args:
            analysis: Task analysis
            
        Returns:
            List of tools to use
        """
        needed_tool_names = analysis.get("needed_tools", [])
        selected_tools = []
        
        for tool in self.tools:
            if tool.name in needed_tool_names:
                selected_tools.append(tool)
                
        return selected_tools
    
    def _format_tools_description(self) -> str:
        """Format tools for description.
        
        Returns:
            Formatted tools description
        """
        if not self.tools:
            return "No tools available."
            
        descriptions = []
        for tool in self.tools:
            desc = f"- {tool.name}: {tool.description}"
            descriptions.append(desc)
            
        return "\n".join(descriptions)
    
    def _create_system_prompt(self, tools: List[Any]) -> str:
        """Create a system prompt for function calling.
        
        Args:
            tools: List of tools to include
            
        Returns:
            System prompt
        """
        system_prompt = f"""
        You are a helpful AI assistant with the ability to use tools to solve complex tasks.
        Your goal is to help the user by using the tools available to you when appropriate.
        
        Available tools:
        {self._format_tools_description()}
        
        When you need to use a tool, respond with a JSON format specifying the tool and parameters.
        For example:
        {{
            "tool": "tool_name",
            "parameters": {{
                "param1": "value1",
                "param2": "value2"
            }}
        }}
        
        Always think step-by-step. First decide if you need to use a tool. If yes, which tool and with what parameters.
        After getting the result from the tool, incorporate it into your response.
        """
        
        return system_prompt
    
    async def _execute_with_tools(self, messages: List[Dict[str, str]], tools: List[Any], task_id: str) -> str:
        """Execute a task using function calling.
        
        Args:
            messages: List of chat messages
            tools: List of tools to use
            task_id: The task ID
            
        Returns:
            Final result
        """
        models_to_try = [self.model_identifier] + self.fallback_models
        
        for i, model_id in enumerate(models_to_try):
            try:
                if i > 0:
                    logger.warning(f"Falling back to model {model_id} for task {task_id}")
                
                max_iterations = 10  # Prevent infinite loops
                conversation = messages.copy()
                final_result = ""
                
                # Function calling loop
                for iteration in range(max_iterations):
                    # Call the model
                    response = await model_manager.generate_chat_completion(
                        messages=conversation,
                        model_identifier=model_id,
                        temperature=self.temperature,
                        **self.model_parameters
                    )
                    
                    response_text = response.text
                    
                    # Check if the response contains a function call
                    import json
                    import re
                    
                    # Try to extract JSON with a pattern
                    tool_calls = []
                    json_pattern = r'```json\s*(.*?)\s*```|{(?:[^{}]|{(?:[^{}]|{[^{}]*})*})*}'
                    matches = re.findall(json_pattern, response_text, re.DOTALL)
                    
                    for match in matches:
                        match = match.strip()
                        if not match:
                            continue
                            
                        try:
                            # Try to parse the JSON
                            tool_call = json.loads(match)
                            if "tool" in tool_call and "parameters" in tool_call:
                                tool_calls.append(tool_call)
                        except json.JSONDecodeError:
                            continue
                    
                    if tool_calls:
                        # Execute tool calls
                        for tool_call in tool_calls:
                            tool_name = tool_call["tool"]
                            params = tool_call["parameters"]
                            
                            # Find the tool
                            tool = next((t for t in tools if t.name == tool_name), None)
                            if tool:
                                # Execute the tool
                                try:
                                    tool_result = await tool.execute(**params)
                                    # Add tool result to conversation
                                    conversation.append({"role": "assistant", "content": response_text})
                                    conversation.append({
                                        "role": "user", 
                                        "content": f"Tool result: {json.dumps(tool_result)}\n\nPlease continue with your analysis and provide the next step or final answer."
                                    })
                                except Exception as e:
                                    # Add error to conversation
                                    conversation.append({"role": "assistant", "content": response_text})
                                    conversation.append({
                                        "role": "user", 
                                        "content": f"Error executing tool {tool_name}: {str(e)}\n\nPlease try a different approach or provide your best answer without using this tool."
                                    })
                            else:
                                # Tool not found
                                conversation.append({"role": "assistant", "content": response_text})
                                conversation.append({
                                    "role": "user", 
                                    "content": f"Tool {tool_name} not found. Available tools: {', '.join(t.name for t in tools)}\n\nPlease try a different approach or provide your best answer without using this tool."
                                })
                    else:
                        # No tool calls, we have our final result
                        final_result = response_text
                        break
                
                # Return the final result
                return final_result
                
            except Exception as e:
                logger.error(f"Error with model {model_id} for task {task_id}: {str(e)}")
                if i == len(models_to_try) - 1:
                    # No more models to try
                    raise
        
        # This should not be reachable, but added for safety
        raise RuntimeError(f"All models failed for task {task_id}") 