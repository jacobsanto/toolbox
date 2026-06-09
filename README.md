# 🏛️ Mission Control — Agentic OS

Τοπικό κέντρο ελέγχου (control plane) για AI πράκτορες: καταχώρηση, εκτέλεση, παρακολούθηση — όλα σε ένα ενιαίο interface.

> **Local-first** · **Greek-first** · **Real tools only** (όχι mocks — πραγματικά CLIs μέσω subprocess)

## Τι κάνει (Phase 0 + 1 + dashboard)

- 🎛️ **Agent Registry** — κάρτες πρακτόρων σε YAML (`agents/*.yaml`): Claude Code, Codex, OpenCode, Shell. Κάθε κάρτα δηλώνει το πραγματικό CLI, τις δυνατότητες, το budget scope (Arivia / Titan / Personal) και το εκτιμώμενο κόστος.
- ▶️ **Runner** — εκτέλεση task με ζωντανό streaming output, καταγραφή log ανά run, statuses: `queued / running / done / error / cancelled`.
- 🌐 **API** (FastAPI, θύρα 8777) — agents, runs, υποβολή νέου run, **SSE live feed** που βλέπει και τα runs του CLI (cross-process event bus πάνω από SQLite).
- 🖥️ **Dashboard** (Next.js, θύρα 7777) — κάρτες πρακτόρων, ιστορικό εκτελέσεων, ζωντανή ροή, φόρμα «Νέα εκτέλεση». Dark mode by default.
- 🧠 **Memory Layer (Obsidian)** — κάθε run γράφει αυτόματα session note στο vault, αναζήτηση accent-insensitive στα Ελληνικά, context injection σε LLM agents πριν από κάθε task, αυτόματο MOC index. Δείξε το `MC_VAULT_DIR` στο πραγματικό σου vault.
- 📥 **Inbox** — universal capture: αρχεία (watcher στους `MC_WATCH_DIRS`, default Desktop/Downloads), σκέψεις, links. Triage σε Εργασία/Project/Αναφορά/Αρχείο/Έλεγχο — με κανόνες (δωρεάν) ή με AI (`--ai`, πραγματική κλήση LLM μέσω του runner). Ελληνικοί επιχειρησιακοί κανόνες embedded: τα Παρ_/Πλη_/ΤΑΚΚ/ΤΠΥ δεν μετονομάζονται ποτέ, ο φάκελος «ΙΑΚΩΒΟΣ ΠΡΟΣ ΤΡΑΠΕΖΑ» είναι off-limits.
- 🔌 **Integrations Hub** — connectors σε YAML (`connectors/*.yaml`): GitHub (gh), Google Drive (gws), filesystem. Νέο integration = νέο YAML, χωρίς κώδικα.
- 📊 **Reflection** — αυτόματο ημερήσιο recap (`Journal/<date>.md`) και εβδομαδιαίο review στο vault, με στατιστικά, blockers και wikilinks στα session notes. Προαιρετικό AI αφήγημα (`--ai`).
- 🎙️ **«Ask the OS»** — μία ερώτηση στα Ελληνικά ψάχνει ΠΑΝΤΟΥ (notes, runs, inbox) και συνθέτει απάντηση με citations μέσω πραγματικού LLM. Voice: `say` (edge-tts, ελληνικές φωνές), `transcribe` (whisper, τοπικά), `brief --speak` για πρωινή ενημέρωση τύπου Jarvis.
- 💰 **Budgets** — όρια ανά scope στο `budgets.yaml` (€/μήνα, runs/ημέρα). Warning στο 80%, hard stop στο 100% με `--force` override. Όταν εξαντληθεί το budget, τα AI extras (triage, σύνθεση) πέφτουν αυτόματα σε κανόνες/πηγές.
- 🧬 **Self-Evolving Standards** — το OS ανιχνεύει patterns από τη χρήση (προτιμήσεις πρακτόρων, επαναλαμβανόμενα σφάλματα, ταξινομήσεις inbox). Μόνο τα ≥80% confidence γίνονται auto-rules στο `Standards/` του vault — η διαγραφή του αρχείου απενεργοποιεί τον κανόνα. Πάγιοι κανόνες + learned standards + σχετικές σημειώσεις εγχέονται σε κάθε LLM εργασία.

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

# Inbox
uv run mission-control inbox add "πρέπει να στείλω την προσφορά"
uv run mission-control inbox watch          # watcher daemon (Ctrl-C για στοπ)
uv run mission-control inbox triage --ai    # AI ταξινόμηση των νέων items
uv run mission-control inbox list

# Connectors
uv run mission-control connectors list
uv run mission-control connectors run github prs
uv run mission-control connectors run filesystem recent ~/Projects

# Reflection & Ask the OS
uv run mission-control reflect daily --ai   # Journal/<σήμερα>.md στο vault
uv run mission-control reflect weekly
uv run mission-control ask "Τι έγινε με τα τιμολόγια Arivia;"
uv run mission-control brief --speak        # πρωινή ενημέρωση + ελληνικό TTS
uv run mission-control say "Γεια σου Ιάκωβε"
uv run mission-control transcribe ~/voice-memo.m4a

# Budgets & Standards
uv run mission-control budgets              # χρήση ανά scope (Arivia/Titan/Personal)
uv run mission-control standards detect     # ανίχνευση patterns → auto-rules στο vault
uv run mission-control standards list       # πάγιοι + learned κανόνες

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

Κάθε πράκτορας ανήκει σε ένα από τα 3 scopes: **Arivia**, **Titan**, **Personal**. Τα όρια ορίζονται στο `budgets.yaml` και το προφίλ/οι πάγιοι κανόνες στο `profile.yaml`.

## Roadmap (μελλοντικά)

- Embeddings (ChromaDB/LanceDB) πίσω από το ίδιο memory API
- User-defined flows («όταν PR merged → γράψε στο Obsidian → notification») πάνω στα connector events
- LLM-powered pattern detection στα session notes
- Inbox & budgets σελίδες στο dashboard
