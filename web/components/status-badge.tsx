import { Badge } from "./ui/badge";
import { STATUS_LABELS } from "@/lib/labels";

const STYLES: Record<string, string> = {
  queued: "bg-amber-500/15 text-amber-400",
  running: "bg-violet-500/15 text-violet-400 animate-pulse",
  done: "bg-emerald-500/15 text-emerald-400",
  error: "bg-red-500/15 text-red-400",
  cancelled: "bg-zinc-500/15 text-zinc-400",
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <Badge className={STYLES[status] ?? "bg-zinc-500/15 text-zinc-400"}>
      {STATUS_LABELS[status] ?? status}
    </Badge>
  );
}
