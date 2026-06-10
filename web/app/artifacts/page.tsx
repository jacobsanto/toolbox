"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getArtifacts } from "@/lib/api";
import { ARTIFACT_KIND_LABELS, L2 } from "@/lib/labels";
import type { Artifact } from "@/lib/types";

const KINDS = ["log", "note", "file", "output"];

export default function ArtifactsPage() {
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [kind, setKind] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    getArtifacts(kind ?? undefined)
      .then(setArtifacts)
      .catch(() => setError("Αδυναμία φόρτωσης."))
      .finally(() => setLoading(false));
  }, [kind]);

  return (
    <div className="flex flex-col gap-6 max-w-4xl">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-zinc-100">🗂️ {L2.artifacts}</h1>
        <div className="flex gap-1.5">
          <button
            onClick={() => setKind(null)}
            className={`rounded-full border px-3 py-1 text-xs ${
              kind === null
                ? "border-indigo-500 bg-indigo-900/50 text-indigo-200"
                : "border-zinc-700 text-zinc-400 hover:border-zinc-500"
            }`}
          >
            {L2.allKinds}
          </button>
          {KINDS.map((k) => (
            <button
              key={k}
              onClick={() => setKind(k)}
              className={`rounded-full border px-3 py-1 text-xs ${
                kind === k
                  ? "border-indigo-500 bg-indigo-900/50 text-indigo-200"
                  : "border-zinc-700 text-zinc-400 hover:border-zinc-500"
              }`}
            >
              {ARTIFACT_KIND_LABELS[k] ?? k}
            </button>
          ))}
        </div>
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}
      {loading ? (
        <p className="text-sm text-zinc-500">Φόρτωση…</p>
      ) : artifacts.length === 0 ? (
        <p className="text-sm text-zinc-500">{L2.artifactsEmpty}</p>
      ) : (
        <div className="flex flex-col gap-2">
          {artifacts.map((a) => (
            <Link
              key={a.id}
              href={`/runs/${a.run_id}`}
              className="rounded-lg border border-zinc-800 bg-zinc-900 p-4 hover:border-zinc-600 transition-colors flex flex-col gap-1.5"
            >
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-zinc-200">
                  {ARTIFACT_KIND_LABELS[a.kind] ?? a.kind}
                </span>
                <span className="rounded bg-zinc-800 px-1.5 py-0.5 text-xs text-zinc-400">
                  {a.agent_id}
                </span>
                <span className="ml-auto text-xs text-zinc-500">
                  {new Date(a.created_at).toLocaleDateString("el-GR", {
                    day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit",
                  })}
                </span>
              </div>
              <p className="text-xs text-zinc-400 line-clamp-1">{a.task}</p>
              {a.path && <p className="font-mono text-xs text-zinc-600 break-all">{a.path}</p>}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
