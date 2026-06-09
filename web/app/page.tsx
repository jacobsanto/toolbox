import { AgentCard } from "@/components/agent-card";
import { LiveFeed } from "@/components/live-feed";
import { NewRunForm } from "@/components/new-run-form";
import { NewAgentForm } from "@/components/new-agent-form";
import { getAgents } from "@/lib/api";
import { L, L2 } from "@/lib/labels";
import type { Agent } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function AgentsPage() {
  let agents: Agent[] = [];
  let apiDown = false;
  try {
    agents = await getAgents();
  } catch {
    apiDown = true;
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <section className="lg:col-span-2 flex flex-col gap-6">
        <div>
          <h1 className="mb-4 text-lg font-semibold text-zinc-100">{L.agents}</h1>
          {apiDown ? (
            <p className="text-sm text-red-400">{L.apiDown}</p>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {agents.map((a) => (
                <AgentCard key={a.id} agent={a} />
              ))}
            </div>
          )}
        </div>

        {!apiDown && (
          <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
            <h2 className="mb-4 text-sm font-semibold text-zinc-200">{L2.newAgent}</h2>
            <NewAgentForm />
          </div>
        )}
      </section>

      <aside className="flex flex-col gap-4">
        {!apiDown && agents.length > 0 ? <NewRunForm agents={agents} /> : null}
        <LiveFeed />
      </aside>
    </div>
  );
}
