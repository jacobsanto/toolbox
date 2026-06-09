import { RunsTable } from "@/components/runs-table";
import { getRuns } from "@/lib/api";
import { L } from "@/lib/labels";
import type { Run } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function RunsPage() {
  let runs: Run[] = [];
  let apiDown = false;
  try {
    runs = await getRuns();
  } catch {
    apiDown = true;
  }

  return (
    <div>
      <h1 className="mb-4 text-lg font-semibold text-zinc-100">{L.runs}</h1>
      {apiDown ? <p className="text-sm text-red-400">{L.apiDown}</p> : <RunsTable runs={runs} />}
    </div>
  );
}
