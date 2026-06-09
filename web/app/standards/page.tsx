"use client";

import { useEffect, useState } from "react";
import { detectStandards, getStandards } from "@/lib/api";
import type { StandardsInfo } from "@/lib/types";
import { L2 } from "@/lib/labels";

interface Pattern {
  slug: string;
  statement: string;
  confidence: number;
  evidence: number;
}

export default function StandardsPage() {
  const [info, setInfo] = useState<StandardsInfo | null>(null);
  const [detecting, setDetecting] = useState(false);
  const [patterns, setPatterns] = useState<Pattern[] | null>(null);
  const [minConf, setMinConf] = useState<number>(0.8);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getStandards()
      .then(setInfo)
      .catch(() => setError("Αδυναμία φόρτωσης κανόνων."));
  }, []);

  async function handleDetect() {
    setDetecting(true);
    setError(null);
    try {
      const data = await detectStandards();
      setPatterns(data.patterns);
      setMinConf(data.min_confidence);
      // Refresh rules after detection
      const updated = await getStandards();
      setInfo(updated);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Σφάλμα κατά την ανίχνευση.");
    } finally {
      setDetecting(false);
    }
  }

  return (
    <div className="flex flex-col gap-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-zinc-100">🧬 {L2.standards}</h1>
        <button
          onClick={handleDetect}
          disabled={detecting}
          className="rounded border border-indigo-700 px-3 py-1.5 text-xs text-indigo-300 hover:bg-indigo-900/40 disabled:opacity-40"
        >
          {detecting ? L2.working : L2.detectPatterns}
        </button>
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {/* Fixed rules from profile.yaml */}
      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5 flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-zinc-200">{L2.fixedRules}</h2>
        {!info || info.fixed.length === 0 ? (
          <p className="text-xs text-zinc-500">{L2.noRules}</p>
        ) : (
          <ul className="flex flex-col gap-2">
            {info.fixed.map((rule, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-zinc-300">
                <span className="mt-0.5 shrink-0 text-indigo-400">▸</span>
                <span className="leading-relaxed">{rule}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Learned rules */}
      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5 flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-zinc-200">{L2.learnedRules}</h2>
        {!info || info.learned.length === 0 ? (
          <p className="text-xs text-zinc-500">{L2.noRules}</p>
        ) : (
          <ul className="flex flex-col gap-2">
            {info.learned.map((rule, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-zinc-300">
                <span className="mt-0.5 shrink-0 text-green-400">◆</span>
                <span className="leading-relaxed">{rule}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Detected patterns (after running detect) */}
      {patterns !== null && (
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-zinc-200">Ανιχνεύθηκαν patterns</h2>
            <span className="text-xs text-zinc-500">
              min confidence: {(minConf * 100).toFixed(0)}%
            </span>
          </div>
          {patterns.length === 0 ? (
            <p className="text-xs text-zinc-500">Δεν βρέθηκαν patterns με αρκετή εμπιστοσύνη.</p>
          ) : (
            <ul className="flex flex-col gap-3">
              {patterns.map((p) => (
                <li key={p.slug} className="flex flex-col gap-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-zinc-500">{p.slug}</span>
                    <span className="ml-auto text-xs text-zinc-400">
                      conf {(p.confidence * 100).toFixed(0)}% · {p.evidence} αποδείξεις
                    </span>
                  </div>
                  <p className="text-sm text-zinc-300">{p.statement}</p>
                  <div className="h-1.5 w-full rounded-full bg-zinc-700 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-indigo-500"
                      style={{ width: `${p.confidence * 100}%` }}
                    />
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
