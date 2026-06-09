"use client";

import { useState } from "react";
import { askOS } from "@/lib/api";
import type { AskSource } from "@/lib/types";
import { L2 } from "@/lib/labels";

const KIND_ICON: Record<string, string> = {
  memory: "🧠",
  inbox: "📥",
  run: "⚙️",
  default: "📄",
};

export default function AskPage() {
  const [query, setQuery] = useState("");
  const [synthesize, setSynthesize] = useState(false);
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<string | null | undefined>(undefined);
  const [sources, setSources] = useState<AskSource[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function handleAsk(e: React.FormEvent) {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    setLoading(true);
    setError(null);
    setAnswer(undefined);
    setSources([]);
    try {
      const data = await askOS(q, synthesize);
      setSources(data.sources);
      setAnswer(data.answer);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Σφάλμα.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-6 max-w-3xl">
      <h1 className="text-lg font-semibold text-zinc-100">🎙️ {L2.ask}</h1>

      <form onSubmit={handleAsk} className="flex flex-col gap-3">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={3}
          className="w-full rounded border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:border-indigo-500 focus:outline-none resize-none"
          placeholder={L2.askPlaceholder}
        />
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 text-xs text-zinc-400 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={synthesize}
              onChange={(e) => setSynthesize(e.target.checked)}
              className="h-3.5 w-3.5 rounded border-zinc-600 bg-zinc-800 accent-indigo-500"
            />
            {L2.synthesize}
          </label>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="rounded bg-indigo-600 px-5 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-40"
          >
            {loading ? L2.working : L2.askButton}
          </button>
        </div>
      </form>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {answer !== undefined && (
        <div className="flex flex-col gap-4">
          {/* AI Answer */}
          <div className="rounded-lg border border-indigo-800/60 bg-indigo-950/30 p-4">
            <p className="mb-2 text-xs font-medium text-indigo-400">{L2.answer}</p>
            {answer ? (
              <p className="text-sm text-zinc-100 leading-relaxed whitespace-pre-wrap">{answer}</p>
            ) : (
              <p className="text-sm text-zinc-500 italic">{L2.noAnswer}</p>
            )}
          </div>

          {/* Sources */}
          {sources.length > 0 && (
            <div>
              <p className="mb-2 text-xs font-medium text-zinc-400">{L2.sources}</p>
              <div className="flex flex-col gap-2">
                {sources.map((s, i) => (
                  <div
                    key={i}
                    className="rounded-lg border border-zinc-800 bg-zinc-900 p-3 flex flex-col gap-1"
                  >
                    <div className="flex items-center gap-2">
                      <span>{KIND_ICON[s.kind] ?? KIND_ICON.default}</span>
                      <span className="text-sm font-medium text-zinc-200">{s.title || s.ref}</span>
                      <span className="ml-auto text-xs text-zinc-500">
                        {(s.score * 100).toFixed(0)}%
                      </span>
                    </div>
                    {s.snippet && (
                      <p className="text-xs text-zinc-400 leading-relaxed line-clamp-3 ml-6">{s.snippet}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
