# ADR 0001 — Επιλογές τεχνολογικής στοίβας

- **Κατάσταση:** Αποδεκτό
- **Ημερομηνία:** 2026-06-09

## Πλαίσιο

Το Mission Control είναι ένα **local-first Agentic OS**: ένα κέντρο ελέγχου που καταχωρεί, εκτελεί και παρακολουθεί AI πράκτορες (Claude Code, Codex, OpenCode, Hermes, custom). Απαιτήσεις-κλειδιά:

1. Όλα τρέχουν τοπικά, τα δεδομένα μένουν στον χρήστη.
2. Πραγματικά CLIs μέσω subprocess — όχι mocks.
3. Ελληνικά σε UI/μηνύματα, αγγλικά identifiers στον κώδικα.
4. Το CLI και ο server είναι **ξεχωριστές διεργασίες** που πρέπει να μοιράζονται κατάσταση και γεγονότα.
5. Ελάχιστες εξαρτήσεις, zero-config εκκίνηση.

## Απόφαση

| Επίπεδο | Επιλογή | Αιτιολόγηση |
|---|---|---|
| Γλώσσα backend | **Python 3.11 + uv** | Agentic/ML οικοσύστημα· το `uv` δίνει γρήγορο, αναπαραγώγιμο setup με ένα `uv sync`. |
| CLI | **Typer** (+ rich, έρχεται transitively) | Δηλωτικό API, αυτόματο help, πίνακες/χρώματα χωρίς επιπλέον δηλωμένη εξάρτηση. |
| API | **FastAPI + uvicorn** | Pydantic validation δωρεάν, async για SSE, αυτόματο OpenAPI. |
| Αποθήκευση | **stdlib `sqlite3`, χωρίς ORM** | Ένα αρχείο, μηδέν εξαρτήσεις, μηδενική ρύθμιση. **WAL mode + busy_timeout=5000** επιτρέπουν ταυτόχρονη πρόσβαση CLI/server. Ένα ORM δεν προσφέρει τίποτα σε 4 πίνακες. |
| Event bus | **Πίνακας `events` στη SQLite + polling cursor** | Ένα in-memory bus θα έκανε αόρατα στο SSE τα runs που ξεκινούν από το CLI (άλλη διεργασία). Με τον πίνακα `events`, κάθε διεργασία γράφει, ο server διαβάζει με `WHERE id > :cursor` ανά ~0.7s. Κόστος: latency ≤1s — αποδεκτό για τοπικό, single-user εργαλείο. |
| Logs | **Αρχεία `data/logs/<run_id>.log`** | Πλήρης πιστότητα στο αρχείο· στη DB πάνε μόνο throttled `run.log` chunks (≤1/sec) για το live feed, ώστε να μη φουσκώνει η βάση. |
| Εκτέλεση πρακτόρων | **`subprocess.Popen`, argv-based templating** | Το `{task}` της κάρτας γίνεται ΕΝΑ argv token μέσω `shlex.split` — όχι shell, όχι injection. Εξαίρεση ο πράκτορας `shell` (σκόπιμα `bash -lc`). |
| Κάρτες πρακτόρων | **YAML στο `agents/*.yaml`** | Η αυθεντική πηγή είναι editable/versionable· η DB είναι queryable καθρέφτης. Τα CLI flags αλλάζουν με τις εκδόσεις — γι' αυτό ζουν σε YAML, όχι σε κώδικα. |
| Dashboard | **Next.js + Tailwind, bun, θύρα 7777** | Πυκνό, dark-mode UI τύπου Linear/Raycast. Χειροποίητα UI primitives αντί για shadcn CLI — λιγότερες εξαρτήσεις. |
| Διάταξη repo | **Monorepo: Python στη ρίζα, web στο `web/`** | Ένα clone, ένα PR, κοινό ιστορικό. |

## Συνέπειες

- **Θετικές:** μηδενική υποδομή, άμεση εκκίνηση (`uv sync` και τέλος), cross-process ορατότητα γεγονότων, εύκολη προσθήκη πράκτορα (ένα YAML αρχείο).
- **Αρνητικές / αποδεκτά trade-offs:**
  - SSE latency ~0.7–1s λόγω polling (αντί για push).
  - stderr ενώνεται με stdout στον runner (μία ροή, χρονολογική σειρά, χωρίς δεύτερο reader thread).
  - Σε restart του server, runs που έτρεχαν σε threads μένουν ορφανά → ο server τα σημαδεύει ως σφάλμα στην εκκίνηση (`recover_stale_runs`).
- **Μελλοντικά:** αν χρειαστεί πολυχρηστικότητα ή push-based events, η μετάβαση σε Postgres + LISTEN/NOTIFY είναι ευθεία, γιατί όλη η πρόσβαση περνά από το `db.py`.
