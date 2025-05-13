/**
 * Workflow related type definitions
 */

/**
 * Environment type
 */
export interface Environment {
  id: string;
  name: string;
  type: string;
  description?: string;
  config?: Record<string, any>;
}

/**
 * Agent type
 */
export interface Agent {
  id: string;
  name: string;
  type: string;
  capabilities?: string[];
  model_id?: string;
  description?: string;
  config?: Record<string, any>;
}

/**
 * Step types in a workflow
 */
export enum WorkflowStepType {
  EnvironmentAction = 'environment_action',
  AgentTask = 'agent_task',
  Conditional = 'conditional',
  Parallel = 'parallel'
}

/**
 * Workflow step status
 */
export enum StepStatus {
  Pending = 'pending',
  Running = 'running',
  Completed = 'completed',
  Failed = 'failed',
  Skipped = 'skipped'
}

/**
 * Base workflow step
 */
export interface WorkflowStepBase {
  id: string;
  name: string;
  type: WorkflowStepType;
  depends_on?: string[];
  timeout?: number;
  output_key?: string;
  retry_count?: number;
  retry_delay?: number;
  status?: StepStatus;
  result?: any;
  error?: string;
}

/**
 * Environment action step
 */
export interface EnvironmentActionStep extends WorkflowStepBase {
  type: WorkflowStepType.EnvironmentAction;
  environment: string;
  action: {
    operation: string;
    [key: string]: any;
  };
}

/**
 * Agent task step
 */
export interface AgentTaskStep extends WorkflowStepBase {
  type: WorkflowStepType.AgentTask;
  agent: string;
  task_input: Record<string, any>;
  description?: string;
}

/**
 * Conditional step
 */
export interface ConditionalStep extends WorkflowStepBase {
  type: WorkflowStepType.Conditional;
  condition: string;
  if_true?: string;
  if_false?: string;
}

/**
 * Parallel step
 */
export interface ParallelStep extends WorkflowStepBase {
  type: WorkflowStepType.Parallel;
  parallel_steps: string[];
}

/**
 * Union type for all step types
 */
export type WorkflowStep = 
  | EnvironmentActionStep 
  | AgentTaskStep 
  | ConditionalStep 
  | ParallelStep;

/**
 * Workflow definition
 */
export interface Workflow {
  id: string;
  name: string;
  description?: string;
  steps: Record<string, WorkflowStep>;
  metadata?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
  owner_id?: string;
}

/**
 * Workflow execution
 */
export interface WorkflowExecution {
  id: string;
  workflow_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  start_time: string;
  end_time?: string;
  results?: Record<string, any>;
  error?: string;
} 