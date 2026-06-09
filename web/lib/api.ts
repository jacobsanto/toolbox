import type {
  Agent,
  AskSource,
  BudgetUsage,
  Connector,
  InboxItem,
  MemoryResult,
  MemoryStatus,
  Run,
  RunDetail,
  StandardsInfo,
} from "./types";

export const API =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8777";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
  return res.json();
}

export const getAgents = () => get<Agent[]>("/api/agents");
export const getRuns = (limit = 50) => get<Run[]>(`/api/runs?limit=${limit}`);
export const getRun = (id: string) => get<RunDetail>(`/api/runs/${id}`);

export async function submitRun(agent_id: string, task: string): Promise<Run> {
  const res = await fetch(`${API}/api/runs`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ agent_id, task }),
  });
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json();
}

export const eventsUrl = () => `${API}/api/events`;

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new Error(detail?.detail ?? `API ${res.status}`);
  }
  return res.json();
}

export const getInbox = (status?: string) =>
  get<InboxItem[]>(`/api/inbox${status ? `?status=${status}` : ""}`);
export const addInboxItem = (content: string) =>
  post<InboxItem>("/api/inbox", { content });
export const triageInbox = (ai: boolean) =>
  post<InboxItem[]>("/api/inbox/triage", { ai });

export const getBudgets = () => get<BudgetUsage[]>("/api/budgets");
export const getConnectors = () => get<Connector[]>("/api/connectors");

export const getMemoryStatus = () => get<MemoryStatus>("/api/memory/status");
export const searchMemory = (q: string) =>
  get<MemoryResult[]>(`/api/memory/search?q=${encodeURIComponent(q)}&k=10`);
export const generateMoc = () => post<{ path: string }>("/api/memory/moc");

export const askOS = (q: string, synthesize: boolean) =>
  get<{ query: string; sources: AskSource[]; answer: string | null }>(
    `/api/ask?q=${encodeURIComponent(q)}&k=6&synthesize_answer=${synthesize}`,
  );

export const getStandards = () => get<StandardsInfo>("/api/standards");
export const detectStandards = () =>
  post<{
    patterns: { slug: string; statement: string; confidence: number; evidence: number }[];
    written: string[];
    min_confidence: number;
  }>("/api/standards/detect");

export const reflect = (period: "daily" | "weekly", ai: boolean) =>
  post<{ path: string; content: string }>(`/api/reflect/${period}`, { ai });

export const createAgent = (card: Record<string, unknown>) =>
  post<Agent>("/api/agents", card);
