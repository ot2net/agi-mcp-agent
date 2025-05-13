"""Workflow engine for orchestrating environments, agents, and tasks."""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable

from pydantic import BaseModel, Field

from agi_mcp_agent.workflow.registry import EnvironmentRegistry, AgentRegistry
from agi_mcp_agent.mcp.models import Task

logger = logging.getLogger(__name__)


class StepStatus(str, Enum):
    """Status of a workflow step."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStepType(str, Enum):
    """Types of workflow steps."""
    ENVIRONMENT_ACTION = "environment_action"
    AGENT_TASK = "agent_task"
    CONDITIONAL = "conditional"
    PARALLEL = "parallel"


class WorkflowStep(BaseModel):
    """A step in a workflow."""
    
    id: str
    name: str
    type: WorkflowStepType
    depends_on: List[str] = Field(default_factory=list)
    
    # For environment actions
    environment: Optional[str] = None
    action: Optional[Dict[str, Any]] = None
    
    # For agent tasks
    agent: Optional[str] = None
    task_input: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    
    # For conditionals
    condition: Optional[str] = None
    if_true: Optional[str] = None
    if_false: Optional[str] = None
    
    # For parallel steps
    parallel_steps: List[str] = Field(default_factory=list)
    
    # Common fields
    timeout: Optional[int] = None
    output_key: Optional[str] = None
    retry_count: int = 0
    retry_delay: int = 5
    status: StepStatus = StepStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    

class Workflow(BaseModel):
    """A workflow definition."""
    
    id: str
    name: str
    description: Optional[str] = None
    steps: Dict[str, WorkflowStep]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowEngine:
    """Engine for executing workflows."""
    
    def __init__(
        self, 
        environment_registry: EnvironmentRegistry, 
        agent_registry: AgentRegistry
    ):
        """Initialize the workflow engine.
        
        Args:
            environment_registry: Registry of available environments
            agent_registry: Registry of available agents
        """
        self.environments = environment_registry
        self.agents = agent_registry
        self.workflows: Dict[str, Workflow] = {}
        self.running_workflows: Dict[str, Dict[str, Any]] = {}
        self.template_context_handlers: Dict[str, Callable] = {}
        
    def register_workflow(self, workflow: Workflow) -> str:
        """Register a workflow with the engine.
        
        Args:
            workflow: The workflow to register
            
        Returns:
            The ID of the registered workflow
        """
        workflow_id = workflow.id
        self.workflows[workflow_id] = workflow
        logger.info(f"Registered workflow '{workflow.name}' with ID {workflow_id}")
        return workflow_id
        
    def register_template_handler(self, name: str, handler: Callable) -> None:
        """Register a template context handler function.
        
        Args:
            name: The name of the handler
            handler: The handler function
        """
        self.template_context_handlers[name] = handler
        logger.debug(f"Registered template handler '{name}'")
    
    async def execute_workflow(
        self, 
        workflow_id: str, 
        input_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute a workflow by ID.
        
        Args:
            workflow_id: The ID of the workflow to execute
            input_data: Initial input data for the workflow
            
        Returns:
            The workflow execution result including step outputs
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow with ID '{workflow_id}' not found")
            
        workflow = self.workflows[workflow_id]
        
        # Generate execution ID and set up execution context
        execution_id = str(uuid.uuid4())
        context = {
            "workflow_id": workflow_id,
            "execution_id": execution_id,
            "input": input_data or {},
            "results": {},
            "start_time": time.time(),
            "status": "running"
        }
        
        self.running_workflows[execution_id] = context
        
        try:
            logger.info(f"Starting workflow execution {execution_id} for workflow '{workflow.name}'")
            
            # Track which steps have completed
            completed_steps = set()
            all_steps = set(workflow.steps.keys())
            
            # Until all steps are completed
            while completed_steps != all_steps:
                # Find steps that can be executed
                runnable_steps = []
                
                for step_id, step in workflow.steps.items():
                    if step_id in completed_steps:
                        continue
                        
                    # Check if dependencies are met
                    dependencies_met = all(dep in completed_steps for dep in step.depends_on)
                    
                    if dependencies_met:
                        runnable_steps.append(step)
                
                if not runnable_steps:
                    # If there are still steps but none can run, we have a circular dependency
                    if len(completed_steps) < len(all_steps):
                        remaining = all_steps - completed_steps
                        raise ValueError(f"Possible circular dependency among steps: {remaining}")
                    break
                
                # Execute steps in parallel
                tasks = [self._execute_step(step, context) for step in runnable_steps]
                await asyncio.gather(*tasks)
                
                # Mark completed steps
                for step in runnable_steps:
                    if step.status in (StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.SKIPPED):
                        completed_steps.add(step.id)
            
            # Workflow completed
            context["status"] = "completed"
            context["end_time"] = time.time()
            context["duration"] = context["end_time"] - context["start_time"]
            
            logger.info(
                f"Workflow '{workflow.name}' completed in {context['duration']:.2f}s. "
                f"Execution ID: {execution_id}"
            )
            
            return {
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "status": "completed",
                "results": context["results"],
                "duration": context["duration"]
            }
            
        except Exception as e:
            logger.error(f"Error executing workflow '{workflow.name}': {str(e)}")
            context["status"] = "failed"
            context["error"] = str(e)
            context["end_time"] = time.time()
            context["duration"] = context["end_time"] - context["start_time"]
            
            return {
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "status": "failed",
                "error": str(e),
                "results": context.get("results", {}),
                "duration": context["duration"]
            }
            
    async def _execute_step(self, step: WorkflowStep, context: Dict[str, Any]) -> None:
        """Execute a single workflow step.
        
        Args:
            step: The step to execute
            context: The workflow execution context
        """
        step.status = StepStatus.RUNNING
        step_start_time = time.time()
        
        logger.info(f"Executing step '{step.name}' (ID: {step.id}) of type {step.type}")
        
        try:
            if step.type == WorkflowStepType.ENVIRONMENT_ACTION:
                step.result = await self._execute_environment_action(step, context)
                
            elif step.type == WorkflowStepType.AGENT_TASK:
                step.result = await self._execute_agent_task(step, context)
                
            elif step.type == WorkflowStepType.CONDITIONAL:
                step.result = await self._execute_conditional(step, context)
                
            elif step.type == WorkflowStepType.PARALLEL:
                step.result = await self._execute_parallel(step, context)
                
            else:
                raise ValueError(f"Unknown step type: {step.type}")
                
            step.status = StepStatus.COMPLETED
            duration = time.time() - step_start_time
            logger.info(f"Step '{step.name}' completed in {duration:.2f}s")
            
            # Store result in context
            context["results"][step.id] = step.result
            
            # If output_key is specified, store under that key too
            if step.output_key:
                context[step.output_key] = step.result
                
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error = str(e)
            duration = time.time() - step_start_time
            logger.error(f"Step '{step.name}' failed after {duration:.2f}s: {str(e)}")
    
    async def _execute_environment_action(
        self, 
        step: WorkflowStep, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an environment action step.
        
        Args:
            step: The step to execute
            context: The workflow execution context
            
        Returns:
            The result of the environment action
        """
        if not step.environment or not step.action:
            raise ValueError(f"Environment action step '{step.id}' missing environment or action")
            
        # Resolve any template variables in the action
        resolved_action = self._resolve_templates(step.action, context)
        
        # Get the environment
        environment = self.environments.get(step.environment)
        if not environment:
            raise ValueError(f"Environment '{step.environment}' not found for step '{step.id}'")
            
        # Execute the action
        result = environment.execute_action(resolved_action)
        
        return result
    
    async def _execute_agent_task(
        self, 
        step: WorkflowStep, 
        context: Dict[str, Any]
    ) -> Any:
        """Execute an agent task step.
        
        Args:
            step: The step to execute
            context: The workflow execution context
            
        Returns:
            The result of the agent task
        """
        if not step.agent or not step.task_input:
            raise ValueError(f"Agent task step '{step.id}' missing agent or task_input")
            
        # Resolve any template variables in the task input
        resolved_input = self._resolve_templates(step.task_input, context)
        
        # Get the agent
        agent = self.agents.get(step.agent)
        if not agent:
            raise ValueError(f"Agent '{step.agent}' not found for step '{step.id}'")
            
        # Create a unique task ID
        task_id = f"{context['execution_id']}_{step.id}"
        
        # Create and execute the task
        task = Task(
            id=task_id,
            name=step.name, 
            description=step.description or step.name,
            priority=5,  # Default priority
            input_data=resolved_input,
            agent_id=None  # The agent framework will handle this
        )
        
        # Submit the task to the agent
        agent.execute_task(task)
        
        # Wait for the task to complete
        max_wait = step.timeout or 300  # Default 5 minute timeout
        wait_time = 0
        check_interval = 0.5  # Check every 0.5 seconds
        
        while wait_time < max_wait:
            if agent.is_task_complete(task_id):
                # Get the result
                result = agent.get_task_result(task_id)
                return result
                
            await asyncio.sleep(check_interval)
            wait_time += check_interval
            
        # If we reached here, the task timed out
        raise TimeoutError(f"Agent task '{step.id}' timed out after {max_wait} seconds")
    
    async def _execute_conditional(
        self, 
        step: WorkflowStep, 
        context: Dict[str, Any]
    ) -> Any:
        """Execute a conditional step.
        
        Args:
            step: The step to execute
            context: The workflow execution context
            
        Returns:
            The result of the chosen branch
        """
        if not step.condition or (not step.if_true and not step.if_false):
            raise ValueError(f"Conditional step '{step.id}' missing condition or branches")
            
        # Evaluate the condition
        condition_result = self._evaluate_condition(step.condition, context)
        
        # Execute the appropriate branch
        if condition_result and step.if_true:
            branch_step = self.workflows[context["workflow_id"]].steps.get(step.if_true)
            if not branch_step:
                raise ValueError(f"Branch step '{step.if_true}' not found")
                
            await self._execute_step(branch_step, context)
            return context["results"].get(branch_step.id)
            
        elif not condition_result and step.if_false:
            branch_step = self.workflows[context["workflow_id"]].steps.get(step.if_false)
            if not branch_step:
                raise ValueError(f"Branch step '{step.if_false}' not found")
                
            await self._execute_step(branch_step, context)
            return context["results"].get(branch_step.id)
            
        return None
    
    async def _execute_parallel(
        self, 
        step: WorkflowStep, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute parallel steps.
        
        Args:
            step: The step to execute
            context: The workflow execution context
            
        Returns:
            Dictionary of results from all parallel steps
        """
        if not step.parallel_steps:
            raise ValueError(f"Parallel step '{step.id}' has no substeps defined")
            
        # Get all the parallel steps
        parallel_steps = []
        for step_id in step.parallel_steps:
            if step_id not in self.workflows[context["workflow_id"]].steps:
                raise ValueError(f"Parallel substep '{step_id}' not found in workflow")
                
            parallel_steps.append(self.workflows[context["workflow_id"]].steps[step_id])
            
        # Execute all steps in parallel
        tasks = [self._execute_step(s, context) for s in parallel_steps]
        await asyncio.gather(*tasks)
        
        # Collect all results
        results = {}
        for s in parallel_steps:
            results[s.id] = context["results"].get(s.id)
            
        return results
    
    def _resolve_templates(self, obj: Any, context: Dict[str, Any]) -> Any:
        """Recursively resolve template variables in an object.
        
        Args:
            obj: The object containing templates to resolve
            context: The context containing values for templates
            
        Returns:
            The object with templates resolved
        """
        if isinstance(obj, str):
            # Check if this is a template string
            if "{{" in obj and "}}" in obj:
                return self._resolve_template_string(obj, context)
            return obj
            
        elif isinstance(obj, dict):
            return {k: self._resolve_templates(v, context) for k, v in obj.items()}
            
        elif isinstance(obj, list):
            return [self._resolve_templates(item, context) for item in obj]
            
        # For other types, just return as-is
        return obj
    
    def _resolve_template_string(self, template: str, context: Dict[str, Any]) -> Any:
        """Resolve a template string using the context.
        
        Args:
            template: The template string
            context: The context to resolve variables from
            
        Returns:
            The resolved value
        """
        # Handle special case where the entire string is a template
        if template.strip().startswith("{{") and template.strip().endswith("}}"):
            # Extract the variable path
            var_path = template.strip()[2:-2].strip()
            
            # Check for function calls or handlers
            if "(" in var_path and ")" in var_path:
                func_name = var_path.split("(")[0].strip()
                if func_name in self.template_context_handlers:
                    # Extract arguments
                    args_str = var_path[var_path.index("(")+1:var_path.rindex(")")]
                    # Parse arguments - this is a simplified version
                    args = [arg.strip() for arg in args_str.split(",")]
                    
                    # Call the handler
                    handler = self.template_context_handlers[func_name]
                    return handler(context, *args)
            
            # Handle dotted paths
            parts = var_path.split(".")
            current = context
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    # If the path doesn't exist, return the raw template
                    return template
                    
            return current
        
        # For more complex templates with embedded variables
        # This is a simplified version that only handles simple replacements
        import re
        
        def replace_var(match):
            var_path = match.group(1).strip()
            parts = var_path.split(".")
            current = context
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return match.group(0)  # Return the original template placeholder
                    
            # Convert result to string for embedding in the template
            if not isinstance(current, (str, int, float, bool)):
                return json.dumps(current)
                
            return str(current)
            
        # Replace all {{var}} occurrences
        return re.sub(r"{{(.*?)}}", replace_var, template)
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a condition expression.
        
        Args:
            condition: The condition expression
            context: The context with variables
            
        Returns:
            The boolean result of the condition
        """
        # This is a simplified condition evaluator
        # In a real implementation, you would want a more robust solution
        
        # Check if it's a template reference
        if condition.strip().startswith("{{") and condition.strip().endswith("}}"):
            resolved = self._resolve_template_string(condition, context)
            if isinstance(resolved, bool):
                return resolved
            
            # Try to convert to boolean
            if isinstance(resolved, str):
                return resolved.lower() in ("true", "yes", "1")
            
            # Non-empty/non-zero values are true
            return bool(resolved)
            
        # Otherwise, evaluate it as Python (unsafe, but simple for demo)
        # WARNING: In production, you should use a safer evaluation method!
        condition_context = {**context}
        
        # Add helper functions
        condition_context["len"] = len
        condition_context["str"] = str
        condition_context["int"] = int
        condition_context["float"] = float
        condition_context["bool"] = bool
        
        try:
            return bool(eval(condition, {"__builtins__": {}}, condition_context))
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False
            
    def create_workflow_from_dict(self, workflow_dict: Dict[str, Any]) -> Workflow:
        """Create a workflow from a dictionary definition.
        
        Args:
            workflow_dict: The workflow definition as a dictionary
            
        Returns:
            The created workflow
        """
        workflow_id = workflow_dict.get("id") or str(uuid.uuid4())
        steps = {}
        
        # Convert step dictionaries to WorkflowStep objects
        for step_id, step_dict in workflow_dict.get("steps", {}).items():
            step_type = WorkflowStepType(step_dict["type"])
            
            step = WorkflowStep(
                id=step_id,
                name=step_dict.get("name", f"Step {step_id}"),
                type=step_type,
                depends_on=step_dict.get("depends_on", []),
                environment=step_dict.get("environment"),
                action=step_dict.get("action"),
                agent=step_dict.get("agent"),
                task_input=step_dict.get("task_input"),
                description=step_dict.get("description"),
                condition=step_dict.get("condition"),
                if_true=step_dict.get("if_true"),
                if_false=step_dict.get("if_false"),
                parallel_steps=step_dict.get("parallel_steps", []),
                timeout=step_dict.get("timeout"),
                output_key=step_dict.get("output_key"),
                retry_count=step_dict.get("retry_count", 0),
                retry_delay=step_dict.get("retry_delay", 5)
            )
            
            steps[step_id] = step
            
        # Create and return the workflow
        workflow = Workflow(
            id=workflow_id,
            name=workflow_dict.get("name", f"Workflow {workflow_id}"),
            description=workflow_dict.get("description"),
            steps=steps,
            metadata=workflow_dict.get("metadata", {})
        )
        
        return workflow 