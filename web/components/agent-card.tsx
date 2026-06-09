import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { L, SCOPE_LABELS } from "@/lib/labels";
import type { Agent } from "@/lib/types";

const SCOPE_STYLES: Record<string, string> = {
  arivia: "bg-sky-500/15 text-sky-400",
  titan: "bg-orange-500/15 text-orange-400",
  personal: "bg-emerald-500/15 text-emerald-400",
};

export function AgentCard({ agent }: { agent: Agent }) {
  return (
    <Card className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-zinc-100">{agent.display_name}</h3>
        <Badge className={SCOPE_STYLES[agent.budget_scope] ?? ""}>
          {SCOPE_LABELS[agent.budget_scope] ?? agent.budget_scope}
        </Badge>
      </div>
      <p className="text-sm text-zinc-400">{agent.description}</p>
      <div className="flex flex-wrap gap-1">
        {agent.capabilities.map((c) => (
          <Badge key={c} className="bg-zinc-800 text-zinc-400">
            {c}
          </Badge>
        ))}
      </div>
      <div className="mt-auto flex items-center justify-between pt-2 text-xs text-zinc-500">
        <code className="text-zinc-500">{agent.command_template}</code>
        {agent.available ? (
          <span className="text-emerald-400">✓ {L.available}</span>
        ) : (
          <span className="text-red-400">✗ {L.notInstalled}</span>
        )}
      </div>
    </Card>
  );
}
