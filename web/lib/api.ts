import type { Agent, Run, RunDetail } from "./types";

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
