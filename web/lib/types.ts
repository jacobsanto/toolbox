export type RunStatus = "queued" | "running" | "done" | "error" | "cancelled";

export interface Agent {
  id: string;
  display_name: string;
  description: string | null;
  command_template: string;
  binary: string;
  model: string | null;
  models: string[];
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

export interface InboxItem {
  id: number;
  source: string;
  content: string;
  kind: string | null;
  reason: string | null;
  status: "new" | "triaged" | "done";
  created_at: string;
}

export interface BudgetUsage {
  scope: string;
  month_eur: number;
  monthly_limit_eur: number;
  today_runs: number;
  daily_limit_runs: number;
  level: "ok" | "warning" | "exceeded";
}

export interface Connector {
  name: string;
  display_name: string;
  description: string;
  binary: string;
  auth: string;
  actions: Record<string, string>;
  events: string[];
  available: boolean;
}

export interface AskSource {
  kind: string;
  ref: string;
  title: string;
  snippet: string;
  score: number;
}

export interface MemoryStatus {
  vault_dir: string;
  vault_exists: boolean;
  note_count: number;
  top_tags: { tag: string; count: number }[];
}

export interface MemoryResult {
  path: string;
  title: string;
  tags: string[];
  score: number;
  snippet: string;
}

export interface StandardsInfo {
  fixed: string[];
  learned: string[];
}

export interface Artifact {
  id: number;
  run_id: string;
  kind: string;
  path: string | null;
  meta: Record<string, unknown>;
  created_at: string;
  agent_id: string;
  task: string;
  run_status: string;
}

export interface RoomResponse {
  runs: Run[];
  skipped: { agent_id: string; reason: string }[];
}

export interface MCEvent {
  id: number;
  run_id: string | null;
  payload: Record<string, unknown>;
  created_at: string;
}
