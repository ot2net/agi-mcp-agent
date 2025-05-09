export interface Task {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  model_identifier: string;
  prompt: string;
  created_at: string;
  completed_at?: string;
  result?: string;
  error?: string;
} 