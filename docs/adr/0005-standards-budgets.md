# ADR 0005 — Self-Evolving Standards & Budgets

- **Κατάσταση:** Αποδεκτό
- **Ημερομηνία:** 2026-06-09

## Πλαίσιο

Phase 6: το OS μαθαίνει από τη χρήση (standards) και προστατεύει το
πορτοφόλι (budgets). Ιδέα δανεισμένη από το Agent OS του Brian Casel,
αλλά operational — όχι μόνο code standards.

## Απόφαση

### 🧬 Standards

| Θέμα | Επιλογή | Αιτιολόγηση |
|---|---|---|
| Pattern detection | **Deterministic ανιχνευτές σε πραγματικά δεδομένα** (όχι LLM) | Μετρήσιμο confidence, μηδέν κόστος, εξηγήσιμα ευρήματα. Ανιχνευτές: προτίμηση πράκτορα ανά scope, επαναλαμβανόμενα σφάλματα (≥3×), ταξινόμηση inbox ανά extension. Νέοι ανιχνευτές = νέες συναρτήσεις στο `standards.py`. |
| Κατώφλια | MIN_EVIDENCE=5, **MIN_CONFIDENCE=0.8** | Μόνο ≥80% γίνεται auto-rule (όπως ορίζει το spec)· τα υπόλοιπα εμφανίζονται στο `standards detect` για ανθρώπινο review. |
| Αποθήκευση | **Vault `Standards/<slug>.md`** με frontmatter (confidence, evidence, status: auto) | Versioned, reviewable, και — το κλειδί — **η διαγραφή του αρχείου απενεργοποιεί τον κανόνα**. Ο χρήστης έχει πάντα τον τελευταίο λόγο. |
| Auto-inject | `llm_preamble()`: πάγιοι κανόνες (profile.yaml) + learned standards + σχετικές σημειώσεις | Ένα σημείο σύνθεσης context για ΟΛΕΣ τις LLM εργασίες (CLI run, API, μελλοντικά flows). Μετά από λίγους μήνες χρήσης, οι agents «ξέρουν» τον Ιάκωβο χωρίς να τα ξαναλέει. |

### 💰 Budgets

| Θέμα | Επιλογή | Αιτιολόγηση |
|---|---|---|
| Όρια | `budgets.yaml` ανά scope: `monthly_eur`, `runs_per_day` | Editable αρχείο, όχι UI ρύθμιση — ταιριάζει στο local-first ethos. |
| Κόστος | **Εκτίμηση**: `est_per_run` της κάρτας × πλήθος runs | Τα CLIs δεν αναφέρουν tokens ομοιόμορφα· η εκτίμηση αρκεί για να πιάσει το «ξεχασμένο cron job». Ακριβές accounting όταν τα CLIs το εκθέσουν. |
| Enforcement | **Στο `submit_run`** — warning event στο 80%, `BudgetExceeded` στο 100% | Κεντρικό σημείο: πιάνει CLI, API, AI triage, ask synthesis, reflection. Override: `--force` (CLI) — συνειδητή απόφαση, όχι σιωπηλή υπέρβαση. |
| Degradation | Οι εσωτερικοί AI callers (triage, synthesize, recap) πιάνουν το BudgetExceeded → **πέφτουν σε rules/sources** | Εξαντλημένο budget δεν σπάει το σύστημα — απενεργοποιεί μόνο τα AI extras. |

## Συνέπειες

- **Θετικές:** το OS βελτιώνεται μόνο του με ανθρώπινο veto· κανένα surprise bill· τα budget events (warning/exceeded) φαίνονται στο SSE feed.
- **Αρνητικές / αποδεκτά trade-offs:**
  - Το κόστος είναι εκτίμηση, όχι λογιστική ακρίβεια.
  - Οι deterministic ανιχνευτές πιάνουν συχνότητες, όχι σημασιολογικά patterns («ο Ιάκωβος βάζει dates στο τέλος για invoices») — αυτά θα έρθουν με LLM-powered ανίχνευση πάνω στα session notes, όταν τη δικαιολογεί ο όγκος δεδομένων.
