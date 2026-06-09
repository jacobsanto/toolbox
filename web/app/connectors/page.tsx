import { getConnectors } from "@/lib/api";
import type { Connector } from "@/lib/types";
import { L, L2 } from "@/lib/labels";

export const dynamic = "force-dynamic";

export default async function ConnectorsPage() {
  let connectors: Connector[] = [];
  let error = false;
  try {
    connectors = await getConnectors();
  } catch {
    error = true;
  }

  return (
    <div className="flex flex-col gap-6 max-w-4xl">
      <h1 className="text-lg font-semibold text-zinc-100">🔌 {L2.connectors}</h1>

      {error && (
        <p className="text-sm text-red-400">Αδυναμία φόρτωσης connectors.</p>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        {connectors.map((c) => (
          <div
            key={c.name}
            className="rounded-xl border border-zinc-800 bg-zinc-900 p-5 flex flex-col gap-3"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2 className="font-semibold text-zinc-100">{c.display_name}</h2>
                <p className="mt-0.5 text-xs text-zinc-400">{c.description}</p>
              </div>
              <span
                className={`shrink-0 rounded px-2 py-0.5 text-xs font-medium ${
                  c.available
                    ? "bg-green-900 text-green-300"
                    : "bg-zinc-700 text-zinc-400"
                }`}
              >
                {c.available ? L.available : L.notInstalled}
              </span>
            </div>

            <div className="text-xs text-zinc-500">
              <span className="font-mono">{c.binary}</span>
              {c.auth && c.auth !== "none" && (
                <span className="ml-2 rounded bg-zinc-800 px-1.5 py-0.5">{c.auth}</span>
              )}
            </div>

            {Object.keys(c.actions).length > 0 && (
              <div>
                <p className="mb-1.5 text-xs font-medium text-zinc-400">Actions</p>
                <div className="flex flex-wrap gap-1.5">
                  {Object.entries(c.actions).map(([key, desc]) => (
                    <span
                      key={key}
                      title={desc}
                      className="rounded bg-zinc-800 px-2 py-0.5 text-xs text-zinc-300"
                    >
                      {key}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {c.events.length > 0 && (
              <div>
                <p className="mb-1.5 text-xs font-medium text-zinc-400">Events</p>
                <div className="flex flex-wrap gap-1.5">
                  {c.events.map((ev) => (
                    <span
                      key={ev}
                      className="rounded bg-zinc-800 px-2 py-0.5 text-xs text-zinc-400"
                    >
                      {ev}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
