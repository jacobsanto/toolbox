import { getBudgets } from "@/lib/api";
import type { BudgetUsage } from "@/lib/types";
import { L2, SCOPE_LABELS } from "@/lib/labels";

export const dynamic = "force-dynamic";

const LEVEL_COLOR: Record<string, string> = {
  ok: "text-green-400",
  warning: "text-yellow-400",
  exceeded: "text-red-400",
};

const BAR_COLOR: Record<string, string> = {
  ok: "bg-green-600",
  warning: "bg-yellow-500",
  exceeded: "bg-red-600",
};

function UsageBar({ value, max, level }: { value: number; max: number; level: string }) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0;
  return (
    <div className="h-2 w-full rounded-full bg-zinc-700 overflow-hidden">
      <div
        className={`h-full rounded-full transition-all ${BAR_COLOR[level] ?? "bg-zinc-500"}`}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

export default async function BudgetsPage() {
  let budgets: BudgetUsage[] = [];
  let error = false;
  try {
    budgets = await getBudgets();
  } catch {
    error = true;
  }

  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      <h1 className="text-lg font-semibold text-zinc-100">💰 {L2.budgets}</h1>

      {error && (
        <p className="text-sm text-red-400">Αδυναμία φόρτωσης budgets.</p>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {budgets.map((b) => (
          <div
            key={b.scope}
            className="rounded-xl border border-zinc-800 bg-zinc-900 p-5 flex flex-col gap-4"
          >
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-zinc-100">
                {SCOPE_LABELS[b.scope] ?? b.scope}
              </h2>
              <span
                className={`text-xs font-medium uppercase tracking-wide ${LEVEL_COLOR[b.level] ?? "text-zinc-400"}`}
              >
                {b.level === "ok" ? "✓" : b.level === "warning" ? "⚠" : "✗"} {b.level}
              </span>
            </div>

            {/* Monthly spend */}
            <div className="flex flex-col gap-1.5">
              <div className="flex justify-between text-xs text-zinc-400">
                <span>{L2.monthSpend}</span>
                <span>
                  {b.month_eur.toFixed(2)} / {b.monthly_limit_eur.toFixed(2)} €
                </span>
              </div>
              <UsageBar value={b.month_eur} max={b.monthly_limit_eur} level={b.level} />
            </div>

            {/* Daily runs */}
            <div className="flex flex-col gap-1.5">
              <div className="flex justify-between text-xs text-zinc-400">
                <span>{L2.todayRuns}</span>
                <span>
                  {b.today_runs} / {b.daily_limit_runs}
                </span>
              </div>
              <UsageBar
                value={b.today_runs}
                max={b.daily_limit_runs}
                level={b.today_runs >= b.daily_limit_runs ? "exceeded" : b.today_runs >= b.daily_limit_runs * 0.8 ? "warning" : "ok"}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
