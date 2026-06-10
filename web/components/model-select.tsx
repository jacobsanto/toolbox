"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { updateAgentModel } from "@/lib/api";
import { L2 } from "@/lib/labels";

export function ModelSelect({
  agentId,
  model,
  models,
}: {
  agentId: string;
  model: string;
  models: string[];
}) {
  const router = useRouter();
  const [current, setCurrent] = useState(model);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleChange(next: string) {
    const prev = current;
    setCurrent(next);
    setSaving(true);
    setError(null);
    try {
      await updateAgentModel(agentId, next);
      router.refresh();
    } catch (err: unknown) {
      setCurrent(prev);
      setError(err instanceof Error ? err.message : "Σφάλμα.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-2">
        <span className="text-xs text-zinc-500">{L2.model}</span>
        <select
          value={current}
          disabled={saving}
          onChange={(e) => handleChange(e.target.value)}
          className="flex-1 rounded border border-zinc-700 bg-zinc-800 px-2 py-1 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none disabled:opacity-50"
        >
          {models.map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
        {saving && <span className="text-xs text-zinc-500">…</span>}
      </div>
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}
