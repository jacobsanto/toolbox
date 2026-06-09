"use client";

import { useState } from "react";
import { reflect } from "@/lib/api";
import { L2 } from "@/lib/labels";

export default function JournalPage() {
  const [result, setResult] = useState<{ path: string; content: string } | null>(null);
  const [loading, setLoading] = useState<"daily" | "weekly" | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleReflect(period: "daily" | "weekly", ai: boolean) {
    setLoading(period);
    setError(null);
    setResult(null);
    try {
      const data = await reflect(period, ai);
      setResult(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Σφάλμα.");
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="flex flex-col gap-6 max-w-3xl">
      <h1 className="text-lg font-semibold text-zinc-100">📔 {L2.journal}</h1>

      <div className="flex flex-wrap gap-3">
        {(["daily", "weekly"] as const).map((period) => (
          <div key={period} className="flex gap-2">
            <button
              disabled={loading !== null}
              onClick={() => handleReflect(period, false)}
              className="rounded border border-zinc-700 px-4 py-2 text-sm text-zinc-300 hover:bg-zinc-800 disabled:opacity-40"
            >
              {period === "daily" ? L2.dailyRecap : L2.weeklyReview}
            </button>
            <button
              disabled={loading !== null}
              onClick={() => handleReflect(period, true)}
              className="rounded border border-indigo-700 px-4 py-2 text-sm text-indigo-300 hover:bg-indigo-900/40 disabled:opacity-40"
            >
              {loading === period
                ? L2.working
                : `${period === "daily" ? L2.dailyRecap : L2.weeklyReview} ${L2.triageAI}`}
            </button>
          </div>
        ))}
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {result && (
        <div className="flex flex-col gap-3">
          <p className="font-mono text-xs text-zinc-500">{result.path}</p>
          <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
            <pre className="text-sm text-zinc-200 whitespace-pre-wrap leading-relaxed">
              {result.content}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
