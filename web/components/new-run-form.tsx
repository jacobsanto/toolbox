"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { submitRun } from "@/lib/api";
import { L } from "@/lib/labels";
import { Card } from "./ui/card";
import type { Agent } from "@/lib/types";

export function NewRunForm({ agents }: { agents: Agent[] }) {
  const [agentId, setAgentId] = useState(agents.find((a) => a.available)?.id ?? "");
  const [task, setTask] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!agentId || !task.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const run = await submitRun(agentId, task.trim());
      setTask("");
      router.push(`/runs/${run.id}`);
    } catch {
      setError(L.apiDown);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card>
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-zinc-400">
        {L.newRun}
      </h2>
      <form onSubmit={onSubmit} className="flex flex-col gap-2">
        <select
          value={agentId}
          onChange={(e) => setAgentId(e.target.value)}
          className="rounded-md border border-zinc-800 bg-zinc-900 px-2 py-1.5 text-sm text-zinc-200"
        >
          {agents.map((a) => (
            <option key={a.id} value={a.id} disabled={!a.available}>
              {a.display_name}
              {a.available ? "" : ` (${L.notInstalled})`}
            </option>
          ))}
        </select>
        <textarea
          value={task}
          onChange={(e) => setTask(e.target.value)}
          placeholder={L.task + "…"}
          rows={3}
          className="rounded-md border border-zinc-800 bg-zinc-900 px-2 py-1.5 text-sm text-zinc-200 placeholder:text-zinc-600"
        />
        <button
          type="submit"
          disabled={busy || !task.trim() || !agentId}
          className="rounded-md bg-violet-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-violet-500 disabled:opacity-40"
        >
          {busy ? "…" : `▶ ${L.submit}`}
        </button>
        {error ? <p className="text-xs text-red-400">{error}</p> : null}
      </form>
    </Card>
  );
}
