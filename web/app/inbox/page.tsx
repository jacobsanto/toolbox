"use client";

import { useEffect, useRef, useState } from "react";
import {
  addInboxItem,
  getInbox,
  triageInbox,
} from "@/lib/api";
import type { InboxItem } from "@/lib/types";
import { KIND_LABELS, L2 } from "@/lib/labels";

const STATUS_COLOR: Record<string, string> = {
  new: "bg-blue-900 text-blue-300",
  triaged: "bg-zinc-700 text-zinc-300",
  done: "bg-green-900 text-green-300",
};

export default function InboxPage() {
  const [items, setItems] = useState<InboxItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [triaging, setTriaging] = useState(false);
  const [content, setContent] = useState("");
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  async function load() {
    try {
      const data = await getInbox();
      setItems(data);
    } catch {
      setError("Αδυναμία φόρτωσης inbox.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    const text = content.trim();
    if (!text) return;
    setAdding(true);
    setError(null);
    try {
      await addInboxItem(text);
      setContent("");
      await load();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Σφάλμα κατά την προσθήκη.");
    } finally {
      setAdding(false);
    }
  }

  async function handleTriage(ai: boolean) {
    setTriaging(true);
    setError(null);
    try {
      await triageInbox(ai);
      await load();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Σφάλμα κατά την ταξινόμηση.");
    } finally {
      setTriaging(false);
    }
  }

  const newCount = items.filter((i) => i.status === "new").length;

  return (
    <div className="flex flex-col gap-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-zinc-100">
          📥 {L2.inbox}
          {newCount > 0 && (
            <span className="ml-2 rounded-full bg-blue-800 px-2 py-0.5 text-xs text-blue-200">
              {newCount} νέα
            </span>
          )}
        </h1>
        <div className="flex gap-2">
          <button
            disabled={triaging || newCount === 0}
            onClick={() => handleTriage(false)}
            className="rounded border border-zinc-700 px-3 py-1.5 text-xs text-zinc-300 hover:bg-zinc-800 disabled:opacity-40"
          >
            {L2.triageAll}
          </button>
          <button
            disabled={triaging || newCount === 0}
            onClick={() => handleTriage(true)}
            className="rounded border border-indigo-700 px-3 py-1.5 text-xs text-indigo-300 hover:bg-indigo-900/40 disabled:opacity-40"
          >
            {triaging ? L2.working : `${L2.triageAll} ${L2.triageAI}`}
          </button>
        </div>
      </div>

      {/* Add item form */}
      <form onSubmit={handleAdd} className="flex flex-col gap-2 rounded-lg border border-zinc-800 bg-zinc-900 p-4">
        <label className="text-xs font-medium text-zinc-400">{L2.addToInbox}</label>
        <textarea
          ref={inputRef}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={3}
          className="w-full rounded border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:border-indigo-500 focus:outline-none resize-none"
          placeholder="Κάτι που θέλεις να επεξεργαστείς, link, σημείωση…"
        />
        {error && <p className="text-xs text-red-400">{error}</p>}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={adding || !content.trim()}
            className="rounded bg-indigo-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-40"
          >
            {adding ? "Προσθήκη…" : L2.add}
          </button>
        </div>
      </form>

      {/* Items list */}
      {loading ? (
        <p className="text-sm text-zinc-500">Φόρτωση…</p>
      ) : items.length === 0 ? (
        <p className="text-sm text-zinc-500">{L2.inboxEmpty}</p>
      ) : (
        <div className="flex flex-col gap-2">
          {items.map((item) => (
            <div
              key={item.id}
              className="rounded-lg border border-zinc-800 bg-zinc-900 p-4 flex flex-col gap-1.5"
            >
              <div className="flex items-start justify-between gap-2">
                <p className="text-sm text-zinc-100 flex-1 leading-relaxed">{item.content}</p>
                <span
                  className={`shrink-0 rounded px-2 py-0.5 text-xs font-medium ${STATUS_COLOR[item.status] ?? "bg-zinc-700 text-zinc-300"}`}
                >
                  {item.status}
                </span>
              </div>
              <div className="flex items-center gap-3 text-xs text-zinc-500">
                {item.kind && (
                  <span className="rounded bg-zinc-800 px-1.5 py-0.5">
                    {KIND_LABELS[item.kind] ?? item.kind}
                  </span>
                )}
                {item.reason && <span className="italic">{item.reason}</span>}
                <span className="ml-auto">
                  {new Date(item.created_at).toLocaleDateString("el-GR", {
                    day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit",
                  })}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
