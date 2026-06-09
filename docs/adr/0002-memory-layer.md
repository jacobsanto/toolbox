# ADR 0002 — Memory Layer (Obsidian bridge)

- **Κατάσταση:** Αποδεκτό
- **Ημερομηνία:** 2026-06-09

## Πλαίσιο

Το Phase 3 δίνει στο Mission Control μνήμη: κάθε run αφήνει ίχνος, και νέα
tasks ξεκινούν με σχετικό context. Η μνήμη ζει στο **Obsidian vault** του
χρήστη — όχι σε κρυφή βάση — ώστε να είναι αναγνώσιμη, επεξεργάσιμη και
ορατή στο graph view / backlinks του Obsidian.

## Απόφαση

| Θέμα | Επιλογή | Αιτιολόγηση |
|---|---|---|
| Γέφυρα vault | **File-based** (απλά `*.md` αρχεία) | Δεν απαιτεί το Obsidian app ή plugin· δουλεύει με οποιοδήποτε vault. Το `MC_VAULT_DIR` δείχνει στο πραγματικό vault (default: `data/vault` για out-of-the-box demo). |
| Session notes | Αυτόματα στο `MissionControl/Sessions/<date>-<run_id>.md` | Frontmatter (run_id, agent, status, scope, tags), εργασία, αποτέλεσμα, απόσπασμα log, wikilink στο MOC. Αποτυχία εγγραφής σημείωσης **δεν** ρίχνει το run. |
| Αναζήτηση | **RAG-lite: keyword search, ΧΩΡΙΣ embeddings** (αρχικά) | Μηδέν νέες εξαρτήσεις, άμεσα αποτελέσματα, εύκολο debugging. Κανονικοποίηση **accent-insensitive** (NFD, αφαίρεση τόνων) ώστε «εκτελεση» = «εκτέλεση». Τίτλος/tags ζυγίζουν περισσότερο από το σώμα. Τα embeddings (ChromaDB/LanceDB) είναι μελλοντική drop-in αναβάθμιση πίσω από το ίδιο API. |
| Context injection | **Opt-in ανά κάρτα** (`inject_context: true`) | Μόνο LLM agents (claude-code, codex, opencode) — σε shell εντολές το επιπλέον κείμενο προκαλεί syntax errors (επιβεβαιώθηκε πειραματικά). Το context μπαίνει πριν από το task, με όριο χαρακτήρων, και παραλείπεται τελείως αν δεν βρεθεί τίποτα σχετικό. |
| MOC | Αυτόματη παραγωγή `MissionControl/MOC.md` | Index ανά φάκελο και ανά tag με wikilinks — το Obsidian χτίζει backlinks/graph από αυτό. Επιγράφεται κάθε φορά (declared «μην το επεξεργάζεσαι χειροκίνητα»). |
| Greek-aware | Ελληνικά filenames/tags/IDs διατηρούνται ως έχουν | Το regex των hashtags καλύπτει ελληνικούς χαρακτήρες· κανένα transliteration. |

## Συνέπειες

- **Θετικές:** η μνήμη είναι ανθρώπινα αναγνώσιμη και versionable· το vault του χρήστη γίνεται το «long-term memory» όλων των agents χωρίς lock-in.
- **Αρνητικές / αποδεκτά trade-offs:**
  - Keyword search δεν πιάνει συνώνυμα/παραφράσεις (π.χ. «αριβια» ≠ «Arivia» — άλλο αλφάβητο). Λύνεται με embeddings αργότερα.
  - Πλήρες rescan του vault σε κάθε αναζήτηση — αποδεκτό για vaults χιλιάδων σημειώσεων· αν αργήσει, μπαίνει cache/index.
