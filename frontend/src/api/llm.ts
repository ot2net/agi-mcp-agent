import {
  LLMProvider,
  LLMModel,
  LLMProviderCreate,
  LLMModelCreate
} from '@/types/llm';

// 获取后端API基础URL
const API_BASE_URL = '/api/llm';

// 提供者API
export async function getProviders(): Promise<LLMProvider[]> {
  const response = await fetch(`${API_BASE_URL}/providers`);
  if (!response.ok) {
    throw new Error(`Failed to fetch providers: ${response.statusText}`);
  }
  return response.json();
}

export async function getProvider(id: number): Promise<LLMProvider> {
  const response = await fetch(`${API_BASE_URL}/providers/${id}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch provider ${id}: ${response.statusText}`);
  }
  return response.json();
}

export async function createProvider(provider: LLMProviderCreate): Promise<LLMProvider> {
  const response = await fetch(`${API_BASE_URL}/providers`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(provider),
  });
  if (!response.ok) {
    throw new Error(`Failed to create provider: ${response.statusText}`);
  }
  return response.json();
}

export async function deleteProvider(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/providers/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error(`Failed to delete provider ${id}: ${response.statusText}`);
  }
}

// 模型API
export async function getModels(): Promise<LLMModel[]> {
  const response = await fetch(`${API_BASE_URL}/models`);
  if (!response.ok) {
    throw new Error(`Failed to fetch models: ${response.statusText}`);
  }
  return response.json();
}

export async function getModel(id: number): Promise<LLMModel> {
  const response = await fetch(`${API_BASE_URL}/models/${id}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch model ${id}: ${response.statusText}`);
  }
  return response.json();
}

export async function createModel(model: LLMModelCreate): Promise<LLMModel> {
  const response = await fetch(`${API_BASE_URL}/models`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(model),
  });
  if (!response.ok) {
    throw new Error(`Failed to create model: ${response.statusText}`);
  }
  return response.json();
}

export async function deleteModel(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/models/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error(`Failed to delete model ${id}: ${response.statusText}`);
  }
}

export async function getProviderModels(providerId: number): Promise<LLMModel[]> {
  const response = await fetch(`${API_BASE_URL}/providers/${providerId}/models`);
  if (!response.ok) {
    throw new Error(`Failed to fetch models for provider ${providerId}: ${response.statusText}`);
  }
  return response.json();
} 