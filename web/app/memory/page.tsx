"use client";

import { useEffect, useState } from "react";
import { generateMoc, getMemoryStatus, searchMemory } from "@/lib/api";
import type { MemoryResult, MemoryStatus } from "@/lib/types";
import { L2 } from "@/lib/labels";

export default function MemoryPage() {
  const [status, setStatus] = useState<MemoryStatus | null>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<MemoryResult[] | null>(null);
  const [searching, setSearching] = useState(false);
  const [generatingMoc, setGeneratingMoc] = useState(false);
  const [mocPath, setMocPath] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMemoryStatus()
      .then(setStatus)
      .catch(() => setError("Αδυναμία σύνδεσης με το vault."));
  }, []);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    setSearching(true);
    setError(null);
    try {
      const data = await searchMemory(q);
      setResults(data);
    } catch {
      setError("Σφάλμα κατά την αναζήτηση.");
    } finally {
      setSearching(false);
    }
  }

  async function handleMoc() {
    setGeneratingMoc(true);
    setError(null);
    try {
      const data = await generateMoc();
      setMocPath(data.path);
    } catch {
      setError("Σφάλμα κατά την ανανέωση MOC.");
    } finally {
      setGeneratingMoc(false);
    }
  }

  return (
    <div className="flex flex-col gap-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-zinc-100">🧠 {L2.memory}</h1>
        <button
          onClick={handleMoc}
          disabled={generatingMoc}
          className="rounded border border-zinc-700 px-3 py-1.5 text-xs text-zinc-300 hover:bg-zinc-800 disabled:opacity-40"
        >
          {generatingMoc ? L2.working : L2.regenMoc}
        </button>
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}
      {mocPath && (
        <p className="text-xs text-green-400">MOC ανανεώθηκε: {mocPath}</p>
      )}

      {/* Vault status */}
      {status && (
        <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4 flex flex-col gap-3">
          <div className="flex items-center gap-4 text-sm">
            <div>
              <p className="text-xs text-zinc-500">{L2.vault}</p>
              <p className="font-mono text-xs text-zinc-400 break-all">{status.vault_dir}</p>
            </div>
            <div className="ml-auto shrink-0 text-right">
              <p className="text-xs text-zinc-500">{L2.notes}</p>
              <p className="text-xl font-bold text-zinc-100">{status.note_count}</p>
            </div>
          </div>
          {status.top_tags.length > 0 && (
            <div>
              <p className="mb-1.5 text-xs text-zinc-500">{L2.topTags}</p>
              <div className="flex flex-wrap gap-1.5">
                {status.top_tags.map(({ tag, count }) => (
                  <span
                    key={tag}
                    className="cursor-pointer rounded bg-indigo-900/60 px-2 py-0.5 text-xs text-indigo-300 hover:bg-indigo-800/60"
                    onClick={() => { setQuery(tag); }}
                  >
                    #{tag} <span className="text-indigo-500">{count}</span>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Search */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 rounded border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:border-indigo-500 focus:outline-none"
          placeholder={L2.searchMemory}
        />
        <button
          type="submit"
          disabled={searching || !query.trim()}
          className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-40"
        >
          {searching ? "…" : L2.search}
        </button>
      </form>

      {/* Results */}
      {results !== null && (
        <div className="flex flex-col gap-2">
          {results.length === 0 ? (
            <p className="text-sm text-zinc-500">{L2.noResults}</p>
          ) : (
            results.map((r) => (
              <div key={r.path} className="rounded-lg border border-zinc-800 bg-zinc-900 p-4 flex flex-col gap-1.5">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-medium text-zinc-100">{r.title || r.path}</p>
                  <span className="shrink-0 text-xs text-zinc-500">
                    {(r.score * 100).toFixed(0)}%
                  </span>
                </div>
                {r.snippet && (
                  <p className="text-xs text-zinc-400 leading-relaxed line-clamp-3">{r.snippet}</p>
                )}
                <div className="flex flex-wrap gap-1 mt-0.5">
                  {r.tags.map((t) => (
                    <span key={t} className="rounded bg-zinc-800 px-1.5 py-0.5 text-xs text-zinc-400">
                      #{t}
                    </span>
                  ))}
                </div>
                <p className="font-mono text-xs text-zinc-600">{r.path}</p>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
