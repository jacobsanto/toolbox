"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import { StatusBadge } from "@/components/status-badge";
import { Card } from "@/components/ui/card";
import { getRun } from "@/lib/api";
import { L } from "@/lib/labels";
import type { RunDetail } from "@/lib/types";

export default function RunDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [run, setRun] = useState<RunDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | undefined;
    let stopped = false;

    async function load() {
      try {
        const data = await getRun(id);
        if (stopped) return;
        setRun(data);
        setError(null);
        // Όσο τρέχει, κάνε poll κάθε 2s μέχρι τερματική κατάσταση
        if (data.status === "queued" || data.status === "running") {
          timer = setTimeout(load, 2000);
        }
      } catch {
        if (!stopped) setError(L.apiDown);
      }
    }
    load();
    return () => {
      stopped = true;
      if (timer) clearTimeout(timer);
    };
  }, [id]);

  if (error) return <p className="text-sm text-red-400">{error}</p>;
  if (!run) return <p className="text-sm text-zinc-500">…</p>;

  return (
    <div className="flex flex-col gap-4">
      <Link href="/runs" className="text-sm text-zinc-500 hover:text-zinc-300">
        {L.backToRuns}
      </Link>
      <Card>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="font-mono text-lg text-zinc-100">{run.id}</h1>
          <StatusBadge status={run.status} />
          <span className="text-sm text-zinc-400">{run.agent_id}</span>
          {run.duration_ms != null ? (
            <span className="text-sm text-zinc-500">{run.duration_ms} ms</span>
          ) : null}
          {run.exit_code != null ? (
            <span className="text-sm text-zinc-500">
              {L.exitCode}: {run.exit_code}
            </span>
          ) : null}
        </div>
        <p className="mt-2 text-sm text-zinc-300">{run.task}</p>
        {run.error ? <p className="mt-2 text-sm text-red-400">{run.error}</p> : null}
      </Card>
      <Card>
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-zinc-400">
          {L.log}
        </h2>
        <pre className="max-h-[60vh] overflow-auto whitespace-pre-wrap rounded bg-zinc-950 p-3 font-mono text-xs text-zinc-300">
          {run.log_tail || "—"}
        </pre>
      </Card>
    </div>
  );
}
