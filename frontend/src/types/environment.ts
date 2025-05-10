export interface Environment {
  id: string;
  name: string;
  type: string;
  status: string;
  config?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
} 