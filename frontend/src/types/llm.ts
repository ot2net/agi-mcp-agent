export interface LLMProvider {
  id: number;
  name: string;
  type: string;
  status: string;
  models_count: number;
  created_at?: string;
}

export interface LLMModel {
  id: number;
  provider_id: number;
  provider_name: string;
  model_name: string;
  capability: string;
  status: string;
  params: Record<string, any>;
  created_at?: string;
}

export interface LLMProviderCreate {
  name: string;
  type: string;
  api_key?: string;
  models?: string[];
  metadata?: Record<string, any>;
}

export interface LLMModelCreate {
  provider_id: number;
  model_name: string;
  capability: string;
  params?: Record<string, any>;
  metadata?: Record<string, any>;
} 