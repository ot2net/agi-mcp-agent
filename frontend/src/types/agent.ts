export interface Agent {
  id?: number;
  name: string;
  type: string;
  capabilities: Record<string, any>;
  status: string;
  metadata?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
} 