/**
 * API functions for workflow management
 */

import { Environment, Agent, Workflow } from '@/types/workflow';
import { ApiResponse } from '@/types/api';

// API配置
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// 通用的fetch封装函数
async function apiRequest<T>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return {
      success: true,
      data
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    if (process.env.NODE_ENV === 'development') {
      console.error(`API Error [${endpoint}]:`, error);
    }
    
    return {
      success: false,
      error: errorMessage
    };
  }
}

/**
 * Get all available environments
 */
export async function getEnvironments(): Promise<Environment[]> {
  // TODO: Replace with actual API call
  return Promise.resolve([
    { id: 'fs', name: 'File System', type: 'FileSystemEnvironment' },
    { id: 'memory', name: 'Memory Store', type: 'MemoryEnvironment' },
    { id: 'api', name: 'API Client', type: 'APIEnvironment' }
  ]);
}

/**
 * Get all available agents
 */
export async function getAgents(): Promise<Agent[]> {
  // TODO: Replace with actual API call
  return Promise.resolve([
    { id: 'text', name: 'Text Generator', type: 'LLMAgent' },
    { id: 'vision', name: 'Vision Agent', type: 'VisionAgent' }
  ]);
}

/**
 * Create a new workflow
 */
export async function createWorkflow(workflow: Omit<Workflow, 'id' | 'created_at' | 'updated_at'>): Promise<ApiResponse<Workflow>> {
  return apiRequest<Workflow>('/workflows', {
    method: 'POST',
    body: JSON.stringify(workflow),
  });
}

/**
 * Update an existing workflow
 */
export async function updateWorkflow(id: string, workflow: Partial<Workflow>): Promise<ApiResponse<Workflow>> {
  return apiRequest<Workflow>(`/workflows/${id}`, {
    method: 'PUT',
    body: JSON.stringify(workflow),
  });
}

/**
 * Get a workflow by ID
 */
export async function getWorkflow(id: string): Promise<Workflow | null> {
  const response = await apiRequest<Workflow>(`/workflows/${id}`);
  return response.success ? response.data : null;
}

/**
 * Save a workflow (create or update)
 */
export async function saveWorkflow(workflow: Workflow): Promise<ApiResponse<Workflow>> {
  if (workflow.id) {
    return updateWorkflow(workflow.id, workflow);
  } else {
    return createWorkflow(workflow);
  }
}

/**
 * Get all workflows
 */
export async function getWorkflows(): Promise<Workflow[]> {
  const response = await apiRequest<Workflow[]>('/workflows');
  return response.success ? response.data : [];
}

/**
 * Execute a workflow
 */
export async function executeWorkflow(
  workflowId: string, 
  input?: Record<string, any>
): Promise<ApiResponse<any>> {
  return apiRequest<any>(`/workflows/${workflowId}/execute`, {
    method: 'POST',
    body: JSON.stringify({ input: input || {} }),
  });
}

/**
 * Delete a workflow
 */
export async function deleteWorkflow(id: string): Promise<ApiResponse<boolean>> {
  const response = await apiRequest<{}>(`/workflows/${id}`, {
    method: 'DELETE',
  });
  
  return {
    success: response.success,
    data: response.success,
    error: response.error
  };
} 