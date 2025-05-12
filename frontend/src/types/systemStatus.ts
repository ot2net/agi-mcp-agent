export interface SystemStatus {
  running: boolean;
  agents: {
    total: number;
    active: number;
  };
  tasks: {
    pending: number;
    running: number;
    completed: number;
    failed: number;
  };
  system_load?: number;
  timestamp: string;
} 