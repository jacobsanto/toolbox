import Link from "next/link";
import { StatusBadge } from "./status-badge";
import { L } from "@/lib/labels";
import type { Run } from "@/lib/types";

function fmtDuration(ms: number | null): string {
  if (ms == null) return "—";
  return ms < 10_000 ? `${ms} ms` : `${(ms / 1000).toFixed(1)} s`;
}

function fmtTime(iso: string): string {
  return new Date(iso).toLocaleString("el-GR", { hour12: false });
}

export function RunsTable({ runs }: { runs: Run[] }) {
  if (runs.length === 0) {
    return <p className="text-sm text-zinc-500">{L.noRuns}</p>;
  }
  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b border-zinc-800 text-left text-xs uppercase tracking-wide text-zinc-500">
          <th className="py-2 pr-3">ID</th>
          <th className="py-2 pr-3">{L.agent}</th>
          <th className="py-2 pr-3">{L.statusLabel}</th>
          <th className="py-2 pr-3 text-right">{L.duration}</th>
          <th className="py-2 pr-3">{L.createdAt}</th>
          <th className="py-2">{L.task}</th>
        </tr>
      </thead>
      <tbody>
        {runs.map((r) => (
          <tr key={r.id} className="border-b border-zinc-900 hover:bg-zinc-900/50">
            <td className="py-2 pr-3">
              <Link href={`/runs/${r.id}`} className="font-mono text-sky-400 hover:underline">
                {r.id}
              </Link>
            </td>
            <td className="py-2 pr-3 text-zinc-300">{r.agent_id}</td>
            <td className="py-2 pr-3">
              <StatusBadge status={r.status} />
            </td>
            <td className="py-2 pr-3 text-right font-mono text-zinc-400">
              {fmtDuration(r.duration_ms)}
            </td>
            <td className="py-2 pr-3 text-zinc-500">{fmtTime(r.created_at)}</td>
            <td className="max-w-xs truncate py-2 text-zinc-400" title={r.task}>
              {r.task}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
