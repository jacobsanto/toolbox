# 🏛️ Mission Control — Agentic OS

Τοπικό κέντρο ελέγχου (control plane) για AI πράκτορες: καταχώρηση, εκτέλεση, παρακολούθηση — όλα σε ένα ενιαίο interface.

> **Local-first** · **Greek-first** · **Real tools only** (όχι mocks — πραγματικά CLIs μέσω subprocess)

## Τι κάνει (Phase 0 + 1 + dashboard)

- 🎛️ **Agent Registry** — κάρτες πρακτόρων σε YAML (`agents/*.yaml`): Claude Code, Codex, OpenCode, Shell. Κάθε κάρτα δηλώνει το πραγματικό CLI, τις δυνατότητες, το budget scope (Arivia / Titan / Personal) και το εκτιμώμενο κόστος.
- ▶️ **Runner** — εκτέλεση task με ζωντανό streaming output, καταγραφή log ανά run, statuses: `queued / running / done / error / cancelled`.
- 🌐 **API** (FastAPI, θύρα 8777) — agents, runs, υποβολή νέου run, **SSE live feed** που βλέπει και τα runs του CLI (cross-process event bus πάνω από SQLite).
- 🖥️ **Dashboard** (Next.js, θύρα 7777) — κάρτες πρακτόρων, ιστορικό εκτελέσεων, ζωντανή ροή, φόρμα «Νέα εκτέλεση». Dark mode by default.
- 🧠 **Memory Layer (Obsidian)** — κάθε run γράφει αυτόματα session note στο vault, αναζήτηση accent-insensitive στα Ελληνικά, context injection σε LLM agents πριν από κάθε task, αυτόματο MOC index. Δείξε το `MC_VAULT_DIR` στο πραγματικό σου vault.

## Γρήγορη εκκίνηση

```bash
# Backend + CLI
uv sync
uv run mission-control --version          # mission-control 0.1.0
uv run mission-control agents list        # ποιοι πράκτορες υπάρχουν & αν είναι εγκατεστημένοι
uv run mission-control run shell "echo Γεια σου && date"
uv run mission-control runs list
uv run mission-control runs show <run_id>

# Μνήμη (Obsidian)
export MC_VAULT_DIR=~/Obsidian/MyVault      # προαιρετικό — default: data/vault
uv run mission-control memory status
uv run mission-control memory search "τιμολόγια Arivia"
uv run mission-control memory moc           # (ανα)παράγει το Map of Content

# API server
uv run mission-control serve              # http://127.0.0.1:8777 (δες /docs για OpenAPI)

# Dashboard (σε δεύτερο terminal)
cd web && bun install && bun run dev      # http://localhost:7777
```

## Αρχιτεκτονική

```
┌────────────┐   submit/exec    ┌──────────────────────┐
│    CLI     │ ───────────────▶ │  runner (subprocess)  │──▶ data/logs/<id>.log
│  (typer)   │                  │  πραγματικά CLIs      │
└────────────┘                  └──────────┬───────────┘
      │                                    │ events + runs
      ▼                                    ▼
┌─────────────────────────── SQLite (WAL) ───────────────────────────┐
│  agents · runs · artifacts · events  ← κοινό μεταξύ διεργασιών     │
└──────────────────────────────┬─────────────────────────────────────┘
                               │ polling cursor (~0.7s)
                     ┌─────────▼─────────┐        ┌──────────────────┐
                     │  FastAPI :8777    │  SSE   │  Next.js :7777   │
                     │  REST + /events   │ ─────▶ │  dashboard (el)  │
                     └───────────────────┘        └──────────────────┘
```

Γιατί έτσι; Δες το [ADR 0001](docs/adr/0001-stack.md).

## Προσθήκη νέου πράκτορα

Ένα YAML αρχείο στο `agents/` — χωρίς κώδικα:

```yaml
name: hermes
display_name: "Hermes"
description: "Ο προσωπικός μου agent"
binary: hermes                  # ανίχνευση με `which`
command: "hermes run {task}"    # το {task} γίνεται ένα argv token (ασφαλές)
capabilities: [research, files]
budget_scope: personal          # arivia | titan | personal
cost: { currency: EUR, est_per_run: 0.10 }
timeout_s: 1800
```

> ⚠️ Τα flags των AI CLIs (`claude -p`, `codex exec`, …) αλλάζουν μεταξύ εκδόσεων — γι' αυτό τα command templates ζουν σε YAML και τα διορθώνεις χωρίς να αγγίξεις κώδικα.

## Budget scopes

Κάθε πράκτορας ανήκει σε ένα από τα 3 scopes: **Arivia**, **Titan**, **Personal** — η βάση για το cost tracking και τα budgets των επόμενων phases.

## Roadmap (επόμενα phases)

- 📥 Inbox — universal capture + AI triage
- 🔌 Integrations Hub — connectors (Google Workspace, GitHub, Hue)
- 📊 Reflection — ημερήσιο/εβδομαδιαίο recap στο Obsidian
- 🎙️ «Ask the OS» — ελληνικό voice & query layer (Whisper STT, Edge TTS)
- 🧬 Self-evolving standards + budget alerts
