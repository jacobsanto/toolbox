export type RunStatus = "queued" | "running" | "done" | "error" | "cancelled";

export interface Agent {
  id: string;
  display_name: string;
  description: string | null;
  command_template: string;
  binary: string;
  capabilities: string[];
  budget_scope: "arivia" | "titan" | "personal";
  cost_config: { currency?: string; est_per_run?: number };
  available: boolean;
  updated_at: string;
}

export interface Run {
  id: string;
  agent_id: string;
  task: string;
  status: RunStatus;
  exit_code: number | null;
  error: string | null;
  started_at: string | null;
  finished_at: string | null;
  duration_ms: number | null;
  log_path: string | null;
  created_at: string;
}

export interface RunDetail extends Run {
  log_tail: string;
}

export interface MCEvent {
  id: number;
  run_id: string | null;
  payload: Record<string, unknown>;
  created_at: string;
}
