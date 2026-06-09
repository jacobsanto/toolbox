# ADR 0003 — Inbox & Integrations Hub

- **Κατάσταση:** Αποδεκτό
- **Ημερομηνία:** 2026-06-09

## Πλαίσιο

Phase 4: το OS αποκτά **ένα σημείο εισόδου για τα πάντα** (inbox) και
**επεκτάσιμες ενσωματώσεις** (connectors). Χωρίς inbox, το Mission Control
θα ήταν ακόμα ένα «ψάξ' το μόνος σου» εργαλείο.

## Απόφαση

| Θέμα | Επιλογή | Αιτιολόγηση |
|---|---|---|
| Watcher | **Polling scanner** (stdlib, χωρίς watchdog dependency) | Interval 2s αρκεί για ανθρώπινη ροή εργασίας· μηδέν νέες εξαρτήσεις· δουλεύει παντού (macOS/Linux/network drives). Αγνοεί κρυφά και μισοκατεβασμένα αρχεία (.crdownload/.part). |
| Triage | **Δύο στρώματα: κανόνες πρώτα, AI προαιρετικά (--ai)** | Οι κανόνες είναι δωρεάν, deterministic και κωδικοποιούν τους επιχειρησιακούς κανόνες. Το AI triage κάνει ΠΡΑΓΜΑΤΙΚΗ κλήση LLM **μέσω του δικού μας runner** (dogfooding: το inbox είναι πελάτης του agent registry) — κάθε AI triage είναι καταγεγραμμένο run με κόστος/διάρκεια/log. |
| Ελληνικοί κανόνες | Embedded στον κώδικα του triage | `Παρ_/Πλη_/ΤΑΚΚ/ΤΠΥ` → reference με σήμανση «ΠΟΤΕ μετονομασία, μόνο μετακίνηση»· ο φάκελος «ΙΑΚΩΒΟΣ ΠΡΟΣ ΤΡΑΠΕΖΑ» είναι **OFF LIMITS** — απορρίπτεται στο capture, πριν καν μπει στη βάση. |
| Connectors | **YAML schema στο `connectors/`** (name, binary, auth, actions, events) | Ίδιο pattern με τις κάρτες πρακτόρων: νέος connector = νέο YAML, χωρίς κώδικα. Τα actions είναι command templates πραγματικών CLIs (gh, gws, find) με argv-safe templating. Το `auth` δηλώνει ποιος το χειρίζεται (το ίδιο το CLI) — το Mission Control ΔΕΝ αποθηκεύει credentials. |
| Connector events | Δηλώνονται στο YAML αλλά **δεν υλοποιούνται ακόμα** | Είναι το συμβόλαιο για τα user-defined flows του Phase 5+ («όταν PR merged → γράψε στο Obsidian»). |
| Εκτέλεση actions | Άμεσο subprocess με live output, **χωρίς** εγγραφή στο runs | Τα connector actions είναι σύντομα, διαδραστικά queries — δεν είναι agent runs. Αν χρειαστεί ιστορικό, ενοποιούνται με τον runner αργότερα. |

## Συνέπειες

- **Θετικές:** drop ένα αρχείο → ταξινομείται αυτόματα· τα πάντα έχουν ένα σημείο εισόδου· νέο integration σε 10 γραμμές YAML.
- **Αρνητικές / αποδεκτά trade-offs:**
  - Polling αντί για FSEvents/inotify — latency έως 2s, αδιάφορο για τη χρήση.
  - Το AI triage εξαρτάται από εγκατεστημένο LLM CLI· χωρίς αυτό, πέφτει σιωπηλά στους κανόνες.
  - Τα gws command templates μπορεί να θέλουν προσαρμογή στην εγκατεστημένη έκδοση — γι' αυτό ζουν σε YAML.
