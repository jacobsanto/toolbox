"use client";

import { useEffect, useRef, useState } from "react";
import { getAgents, getRun, submitRoom } from "@/lib/api";
import { StatusBadge } from "@/components/status-badge";
import { L2 } from "@/lib/labels";
import type { Agent, Run, RunDetail } from "@/lib/types";

const TERMINAL = new Set(["done", "error", "cancelled"]);
const POLL_MS = 2000;

export default function RoomPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [task, setTask] = useState("");
  const [starting, setStarting] = useState(false);
  const [runs, setRuns] = useState<Run[]>([]);
  const [details, setDetails] = useState<Record<string, RunDetail>>({});
  const [skipped, setSkipped] = useState<{ agent_id: string; reason: string }[]>([]);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    getAgents()
      .then(setAgents)
      .catch(() => setError("Ο server δεν είναι διαθέσιμος."));
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, []);

  function toggle(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  async function poll(runList: Run[]) {
    const updated: Record<string, RunDetail> = {};
    await Promise.all(
      runList.map(async (r) => {
        try {
          updated[r.id] = await getRun(r.id);
        } catch { /* προσωρινό σφάλμα — θα ξαναδοκιμάσει στο επόμενο poll */ }
      }),
    );
    setDetails((prev) => ({ ...prev, ...updated }));
    const all = runList.map((r) => updated[r.id]?.status).filter(Boolean);
    if (all.length === runList.length && all.every((s) => TERMINAL.has(s!))) {
      if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
    }
  }

  async function handleStart(e: React.FormEvent) {
    e.preventDefault();
    const t = task.trim();
    if (!t || selected.size < 2) return;
    setStarting(true);
    setError(null);
    setRuns([]);
    setDetails({});
    setSkipped([]);
    if (timerRef.current) clearInterval(timerRef.current);
    try {
      const res = await submitRoom(t, Array.from(selected));
      setRuns(res.runs);
      setSkipped(res.skipped);
      poll(res.runs);
      timerRef.current = setInterval(() => poll(res.runs), POLL_MS);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Σφάλμα.");
    } finally {
      setStarting(false);
    }
  }

  const cols = runs.length >= 3 ? "lg:grid-cols-3" : "lg:grid-cols-2";

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold text-zinc-100">🗣️ {L2.room}</h1>
        <p className="mt-1 text-sm text-zinc-400">{L2.roomHint}</p>
      </div>

      <form onSubmit={handleStart} className="flex flex-col gap-4 rounded-xl border border-zinc-800 bg-zinc-900 p-5 max-w-3xl">
        <div>
          <p className="mb-2 text-xs font-medium text-zinc-400">{L2.selectAgents}</p>
          <div className="flex flex-wrap gap-2">
            {agents.map((a) => (
              <button
                key={a.id}
                type="button"
                onClick={() => toggle(a.id)}
                disabled={!a.available}
                title={a.available ? "" : L2.installHint}
                className={`rounded-full border px-3 py-1.5 text-xs transition-colors disabled:opacity-30 ${
                  selected.has(a.id)
                    ? "border-indigo-500 bg-indigo-900/50 text-indigo-200"
                    : "border-zinc-700 text-zinc-400 hover:border-zinc-500"
                }`}
              >
                {a.display_name}
                {a.model ? <span className="ml-1 text-zinc-500">({a.model})</span> : null}
              </button>
            ))}
          </div>
        </div>
        <textarea
          value={task}
          onChange={(e) => setTask(e.target.value)}
          rows={3}
          className="w-full rounded border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:border-indigo-500 focus:outline-none resize-none"
          placeholder="Το task που θα πάρουν όλοι οι πράκτορες…"
        />
        {error && <p className="text-xs text-red-400">{error}</p>}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={starting || !task.trim() || selected.size < 2}
            className="rounded bg-indigo-600 px-5 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-40"
          >
            {starting ? L2.working : L2.startRoom}
          </button>
        </div>
      </form>

      {skipped.length > 0 && (
        <div className="rounded-lg border border-yellow-900/60 bg-yellow-950/30 p-3 text-xs text-yellow-300 max-w-3xl">
          <p className="font-medium">{L2.skippedAgents}:</p>
          {skipped.map((s) => (
            <p key={s.agent_id}>• {s.agent_id} — {s.reason}</p>
          ))}
        </div>
      )}

      {runs.length > 0 && (
        <div className={`grid gap-4 ${cols}`}>
          {runs.map((r) => {
            const d = details[r.id];
            return (
              <div key={r.id} className="flex flex-col rounded-xl border border-zinc-800 bg-zinc-900 overflow-hidden">
                <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-2.5">
                  <span className="text-sm font-semibold text-zinc-100">{r.agent_id}</span>
                  <StatusBadge status={d?.status ?? r.status} />
                </div>
                <pre className="flex-1 overflow-auto p-4 text-xs text-zinc-300 leading-relaxed whitespace-pre-wrap max-h-96 min-h-32">
                  {d?.log_tail || (d?.error ? `❌ ${d.error}` : "Αναμονή output…")}
                </pre>
                {d?.duration_ms != null && (
                  <div className="border-t border-zinc-800 px-4 py-2 text-xs text-zinc-500">
                    {(d.duration_ms / 1000).toFixed(1)}s
                    {d.exit_code != null ? ` · exit ${d.exit_code}` : ""}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
