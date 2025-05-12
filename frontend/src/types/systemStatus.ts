export interface SystemStatus {
  total_agents: number;
  active_agents: number;
  pending_tasks: number;
  running_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  system_load: number;
  timestamp?: string;
} 