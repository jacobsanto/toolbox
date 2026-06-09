"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { eventsUrl } from "@/lib/api";
import { L } from "@/lib/labels";
import { StatusBadge } from "./status-badge";
import { Card } from "./ui/card";

interface FeedItem {
  id: number;
  type: string;
  runId: string | null;
  text: string;
  time: string;
}

const EVENT_TYPES = [
  "run.queued",
  "run.started",
  "run.log",
  "run.finished",
  "run.error",
  "run.cancelled",
];

const TYPE_TO_STATUS: Record<string, string> = {
  "run.queued": "queued",
  "run.started": "running",
  "run.finished": "done",
  "run.error": "error",
  "run.cancelled": "cancelled",
};

function describe(type: string, payload: Record<string, unknown>): string {
  if (type === "run.log") {
    const lines = String(payload.lines ?? "").trim().split("\n");
    return lines[lines.length - 1] ?? "";
  }
  if (type === "run.finished") {
    return `${payload.agent_id ?? ""} · exit ${payload.exit_code} · ${payload.duration_ms} ms`;
  }
  if (type === "run.error") return String(payload.error ?? "");
  return `${payload.agent_id ?? ""} · ${String(payload.task ?? "").slice(0, 60)}`;
}

export function LiveFeed() {
  const [items, setItems] = useState<FeedItem[]>([]);
  const router = useRouter();

  useEffect(() => {
    const es = new EventSource(eventsUrl());
    const handler = (type: string) => (ev: MessageEvent) => {
      const data = JSON.parse(ev.data);
      setItems((prev) =>
        [
          {
            id: data.id,
            type,
            runId: data.run_id,
            text: describe(type, data.payload ?? {}),
            time: new Date(data.created_at).toLocaleTimeString("el-GR", { hour12: false }),
          },
          ...prev,
        ].slice(0, 100),
      );
      // Σε τερματικά γεγονότα, φρεσκάρισε τους πίνακες της σελίδας
      if (type === "run.finished" || type === "run.error" || type === "run.cancelled") {
        router.refresh();
      }
    };
    const listeners = EVENT_TYPES.map((t) => {
      const fn = handler(t);
      es.addEventListener(t, fn);
      return [t, fn] as const;
    });
    return () => {
      listeners.forEach(([t, fn]) => es.removeEventListener(t, fn));
      es.close();
    };
  }, [router]);

  return (
    <Card>
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-zinc-400">
        {L.liveFeed}
      </h2>
      {items.length === 0 ? (
        <p className="text-sm text-zinc-600">{L.noEvents}</p>
      ) : (
        <ul className="flex flex-col gap-2 text-sm">
          {items.map((item) => (
            <li key={`${item.id}-${item.type}`} className="flex items-start gap-2">
              <span className="font-mono text-xs text-zinc-600">{item.time}</span>
              {TYPE_TO_STATUS[item.type] ? (
                <StatusBadge status={TYPE_TO_STATUS[item.type]} />
              ) : (
                <span className="font-mono text-xs text-zinc-500">log</span>
              )}
              <span className="min-w-0 flex-1 truncate text-zinc-400" title={item.text}>
                {item.runId ? <span className="font-mono text-zinc-500">{item.runId} </span> : null}
                {item.text}
              </span>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
