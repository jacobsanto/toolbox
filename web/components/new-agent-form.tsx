"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { createAgent } from "@/lib/api";
import { L2 } from "@/lib/labels";

const SCOPES = ["arivia", "titan", "personal"] as const;

export function NewAgentForm() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [description, setDescription] = useState("");
  const [binary, setBinary] = useState("");
  const [command, setCommand] = useState("");
  const [scope, setScope] = useState<string>("personal");
  const [capabilities, setCapabilities] = useState("");
  const [estPerRun, setEstPerRun] = useState("");
  const [injectContext, setInjectContext] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    setError(null);
    setSuccess(false);
    try {
      const caps = capabilities.trim()
        ? capabilities.split(",").map((c) => c.trim()).filter(Boolean)
        : [];
      const costConfig: Record<string, unknown> = { currency: "EUR" };
      const parsed = parseFloat(estPerRun);
      if (!isNaN(parsed) && parsed > 0) costConfig.est_per_run = parsed;
      await createAgent({
        name: name.trim(),
        display_name: displayName.trim() || name.trim(),
        description: description.trim() || null,
        binary: binary.trim(),
        command_template: command.trim(),
        budget_scope: scope,
        capabilities: caps,
        cost_config: costConfig,
        inject_context: injectContext,
      });
      setSuccess(true);
      // Reset form
      setName(""); setDisplayName(""); setDescription(""); setBinary("");
      setCommand(""); setCapabilities(""); setEstPerRun("");
      setScope("personal"); setInjectContext(false);
      router.refresh();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Σφάλμα κατά τη δημιουργία.");
    } finally {
      setCreating(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="grid gap-3 sm:grid-cols-2">
      <div className="flex flex-col gap-1">
        <label className="text-xs text-zinc-400">ID (μοναδικό slug) *</label>
        <input
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="my-agent"
          className="rounded border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-500 focus:border-indigo-500 focus:outline-none"
        />
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-xs text-zinc-400">Εμφανιζόμενο όνομα</label>
        <input
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          placeholder="My Agent"
          className="rounded border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-500 focus:border-indigo-500 focus:outline-none"
        />
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-xs text-zinc-400">Binary *</label>
        <input
          required
          value={binary}
          onChange={(e) => setBinary(e.target.value)}
          placeholder="claude"
          className="rounded border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-500 focus:border-indigo-500 focus:outline-none"
        />
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-xs text-zinc-400">Command template *</label>
        <input
          required
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          placeholder="claude -p {task}"
          className="rounded border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-500 focus:border-indigo-500 focus:outline-none"
        />
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-xs text-zinc-400">Scope</label>
        <select
          value={scope}
          onChange={(e) => setScope(e.target.value)}
          className="rounded border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-100 focus:border-indigo-500 focus:outline-none"
        >
          {SCOPES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-xs text-zinc-400">Est. cost / run (€)</label>
        <input
          type="number"
          min="0"
          step="0.001"
          value={estPerRun}
          onChange={(e) => setEstPerRun(e.target.value)}
          placeholder="0.05"
          className="rounded border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-500 focus:border-indigo-500 focus:outline-none"
        />
      </div>

      <div className="sm:col-span-2 flex flex-col gap-1">
        <label className="text-xs text-zinc-400">Περιγραφή</label>
        <input
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Σύντομη περιγραφή…"
          className="rounded border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-500 focus:border-indigo-500 focus:outline-none"
        />
      </div>

      <div className="sm:col-span-2 flex flex-col gap-1">
        <label className="text-xs text-zinc-400">Capabilities (κόμματα)</label>
        <input
          value={capabilities}
          onChange={(e) => setCapabilities(e.target.value)}
          placeholder="code, git, web"
          className="rounded border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-500 focus:border-indigo-500 focus:outline-none"
        />
      </div>

      <div className="sm:col-span-2 flex items-center gap-2">
        <input
          type="checkbox"
          id="inject-ctx"
          checked={injectContext}
          onChange={(e) => setInjectContext(e.target.checked)}
          className="h-3.5 w-3.5 rounded border-zinc-600 bg-zinc-800 accent-indigo-500"
        />
        <label htmlFor="inject-ctx" className="text-xs text-zinc-400 cursor-pointer">
          Inject context (preamble από profile.yaml + standards)
        </label>
      </div>

      {error && <p className="sm:col-span-2 text-xs text-red-400">{error}</p>}
      {success && <p className="sm:col-span-2 text-xs text-green-400">Ο πράκτορας δημιουργήθηκε!</p>}

      <div className="sm:col-span-2 flex justify-end">
        <button
          type="submit"
          disabled={creating}
          className="rounded bg-indigo-600 px-5 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-40"
        >
          {creating ? "Δημιουργία…" : L2.create}
        </button>
      </div>
    </form>
  );
}
