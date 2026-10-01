---
name: file-renamer
description: >
  Elite File Intelligence and Renaming Agent. Reads ANY file type deeply (PDF text/scanned via OCR,
  DOCX/XLSX/PPTX, images via vision, ZIP/RAR by listing contents, CSV/JSON/XML/code by parsing),
  extracts key metadata, and proposes precise filenames following the Arivia/Dakoutros naming
  convention. Operates in two modes: PROPOSE (shows suggestions for approval) and AUTO (renames
  autonomously after rules are learned). Use this skill ANY time the user wants to rename files,
  analyse what a file contains, organise a folder, detect duplicates, or batch-process documents.
  Triggers include: "μετονόμασε", "διάβασε αυτό το αρχείο", "τι είναι αυτό", "rename",
  "organise files", "what's in this file", "check for duplicates", "batch rename", "clean up Drive",
  "αρχειοθέτηση", or any upload where the filename looks wrong or generic (e.g. "scan001.pdf",
  "document(3).docx", "IMG_4892.jpg"). When in doubt — use this skill.
---

# File Renamer — Elite File Intelligence Agent

Reads any file, understands what it is, and proposes or applies a precise filename following
established naming rules. Operates in PROPOSE or AUTO mode.

---

## 0. Quick Decision Tree

```
File received or path given?
├── Is it a Google Drive file?  → use google_drive_fetch or google_drive_search
├── Is it uploaded to Claude?   → find at /mnt/user-data/uploads/
├── Is it on local filesystem?  → read via bash (cat / python / pdfplumber / etc.)
└── Unknown location?           → ask user for path or Drive link
```

Then: identify type → extract intelligence → apply naming rules → output report card.

---

## 1. Naming Convention (Arivia/Dakoutros Standard)

This is the source of truth. Every filename proposal MUST follow this exactly.

### Pattern

```
[ΤύποςΕγγράφου]_[ΌνομαΑπόΠεριεχόμενο][.Αύξων]_[YYYY-MM-DD].[ext]
```

**Κρίσιμος κανόνας:** Η **οντότητα (entity) ΔΕΝ μπαίνει στο όνομα αρχείου**. Βρίσκεται στον **φάκελο**. Το αρχείο περιγράφει μόνο τι είναι και από/για ποιον — όπως αυτό προκύπτει από το περιεχόμενο.

### Components

| Field | Rules | Examples |
|-------|-------|---------|
| ΤύποςΕγγράφου | Τι είναι — Greek or English, no spaces | `Τιμολόγιο`, `Βεβαίωση`, `Συμβόλαιο`, `Λογαριασμός`, `ΑΠΥ` |
| ΌνομαΑπόΠεριεχόμενο | Το κύριο αναγνωριστικό από το document (αντισυμβαλλόμενος, αριθμός, θέμα) — no spaces, dashes OK | `WIND-Σταθερή`, `ALPHA-SERVICES-AE`, `ΕΦΚΑ-Ασφαλιστική`, `Σύμβαση-Εργασίας` |
| Αύξων | Optional `.N` μόνο αν υπάρχουν πολλά ίδια αρχεία στον ίδιο φάκελο την ίδια ημερομηνία | `Τιμολόγιο_WIND.1`, `Τιμολόγιο_WIND.2` |
| Date | ISO 8601: YYYY-MM-DD. Ημερομηνία εγγράφου, ΟΧΙ σημερινή | `2024-03-15` |
| Extension | Lowercase, preserve original | `.pdf`, `.docx`, `.xlsx` |

### Correct examples (folder context shown)

```
/ΔΑΚΟΥΤΡΟΣ-ΙΚΕ/
  Τιμολόγιο_ALPHA-SERVICES-AE_2024-11-07.pdf
  Βεβαίωση_ΕΦΚΑ-Ασφαλιστική_2025-01-01.pdf
  Λογαριασμός_WIND-Σταθερή_2024-12-01.pdf
  Συμβόλαιο_Μίσθωση-Γραφείου_2023-06-01.pdf
  ΑΠΔ_ΕΦΚΑ_2025-03.pdf

/ΑΛΕΞΙΟΥ-ΔΑΚΟΥΤΡΟΣ-ΟΕ/
  Τιμολόγιο_BOOKING-COM_2024-10-15.pdf
  Κίνηση_EUROBANK-Οκτώβριος_2024-10-31.pdf

/ΔΑΚΟΥΤΡΟΣ (personal)/
  Ασφαλιστικό_Interamerican_1990-07-15.pdf
  Βεβαίωση_Γέννησης_1983-04-10.pdf
  Διαβατήριο_2022-05-01.pdf
```

### ΌνομαΑπόΠεριεχόμενο — extraction rules

1. **Αντισυμβαλλόμενος / counterparty**: αν το έγγραφο έχει εκδότη ή αποδέκτη που δεν είναι η οντότητα του φακέλου → αυτός μπαίνει εδώ
2. **Θέμα εγγράφου**: αν δεν υπάρχει counterparty (π.χ. εσωτερική έκθεση) → το θέμα σε 2-3 λέξεις
3. **Αριθμός αναφοράς**: για σειριακά έγγραφα (ΑΠΔ, μισθοδοσία) → μήνας ή αριθμός αντί για πλήρη ημερομηνία
4. **Ποτέ δεν επαναλαμβάνεται** ο τύπος εγγράφου μέσα στο ΌνομαΑπόΠεριεχόμενο

### Date extraction priority
1. Ημερομηνία εκτυπωμένη στο έγγραφο (ημ. έκδοσης, υπογραφής, ισχύος)
2. Ημερομηνία στο υπάρχον όνομα αρχείου
3. File creation/modification metadata (με ⚠️ σημείωση)
4. Παράλειψη date field — **ποτέ δεν μαντεύεται**

### Duplicate prevention rules
- Before proposing a name, mentally check: would this name clash with a known file?
- If sequence is needed, find the highest existing `.N` and increment
- If content is identical to an existing file (same MD5), flag as DUPLICATE — do NOT rename, suggest deletion

---

## 2. File Reading Strategies by Type

Read `references/reading-strategies.md` for detailed per-type instructions.

**Quick reference:**

| Type | Primary method | Fallback |
|------|---------------|---------|
| PDF (text) | `pdfplumber` — extract first 2 pages | `pdfminer` |
| PDF (scanned) | `pdf2image` + `pytesseract` OCR (Greek+English) | Vision model |
| DOCX | `python-docx` — title, first 500 chars, author, created | Google Drive fetch |
| XLSX | `openpyxl` — sheet names, A1 region, named ranges | |
| PPTX | `python-pptx` — slide 1 title + text | |
| JPG/PNG | Claude vision — describe, read any visible text | `pytesseract` |
| ZIP/RAR | List contents only (no extraction unless asked) | |
| CSV/JSON/XML | `pandas` head(5) + column names | raw `head -50` |
| Code files | `head -100` + detect language + first docstring | |
| Google Doc | `google_drive_fetch` | |

**Always extract:**
- Document type (invoice, contract, certificate, report, etc.)
- Issuing entity / counterparty
- Document date
- Document number / reference (ΑΦΜ, invoice no., contract no.)
- Language (GR / EN / other)
- Page count
- MD5 hash (for duplicate detection)

---

## 3. Operating Modes

### MODE A — PROPOSE (default for new sessions)

Use when: first time working with a folder, or user hasn't confirmed AUTO mode yet.

**Output format per file:**

```
📄 FILE REPORT CARD
───────────────────────────────────
Original name : scan_2024_003.pdf
Folder        : /ΔΑΚΟΥΤΡΟΣ-ΙΚΕ/  ← entity lives here
Type          : Τιμολόγιο
Name from doc : ALPHA SERVICES AE
Date          : 2024-11-07
Doc reference : ΤΙΜ-2024-1183
Language      : Greek
Pages         : 2
MD5           : a3f2c1...8b
───────────────────────────────────
⚡ PROPOSED NAME: Τιμολόγιο_ALPHA-SERVICES-AE_2024-11-07.pdf
───────────────────────────────────
Confidence    : ✅ HIGH
Reasoning     : Counterparty clearly printed top-right. Date from invoice stamp.
⚠️  Flags      : None
```

After 3–5 proposals, ask:
> "Εγκρίνεις αυτά τα ονόματα; Θέλεις να τα εφαρμόσω ή να περάσουμε σε AUTO mode;"

### MODE B — AUTO (after explicit user approval)

Use when: user has approved the naming pattern and said "κάν' τα μόνος σου" or equivalent.

- Process files silently
- Only interrupt for: DUPLICATE detected, confidence < 70%, file unreadable
- Output a summary table at the end (not per-file cards)
- Log all actions to `_RENAME_LOG.md` in the same folder

**AUTO mode summary format:**

```
✅ Renamed 14 files
⚠️  2 flagged for review (see below)
🔁 1 duplicate detected — not renamed

FLAGGED:
- document(7).pdf → LOW CONFIDENCE (no date found, entity ambiguous)
- IMG_0042.jpg → UNREADABLE (blurry scan, OCR failed)
```

---

## 4. Confidence Scoring

| Score | Meaning | Action |
|-------|---------|--------|
| HIGH (90–100%) | All 3 key fields extracted cleanly | Rename / propose |
| MEDIUM (70–89%) | 1 field uncertain | Propose with ⚠️ note |
| LOW (<70%) | 2+ fields missing/guessed | Always ask user |

Confidence drops for: no visible text, ambiguous entity, missing date, unreadable scan.

---

## 5. Duplicate Detection

On every file processed:

1. Compute MD5: `import hashlib; hashlib.md5(open(f,'rb').read()).hexdigest()`
2. Compare against MD5s of other files in same session
3. If match found → flag as `🔁 DUPLICATE OF [other filename]`
4. Never rename a duplicate — propose deletion or archiving instead

Store MD5s in session memory as `{md5: original_filename}` dict.

---

## 6. Learning New Rules Mid-Session

If user corrects a proposal:
- "Όχι, αυτό πρέπει να λέγεται SUPPLIER_Τιμολόγιο_..." → extract the delta, update internal rules
- Verbally confirm: "Κατάλαβα — supplier στο entity field αντί για issuer. Εφαρμόζω από εδώ και πέρα."
- Apply corrected rule to all subsequent files

---

## 7. Batch Processing from Google Drive

When user says "κάνε όλα τα αρχεία στον φάκελο Χ":

1. `google_drive_search` with folder ID to list all files
2. Process each file using the reading strategy table (§2)
3. In PROPOSE mode: show all report cards, then ask for bulk approval
4. In AUTO mode: process, log, summarise

For large batches (>20 files): process in groups of 10, report progress.

---

## 8. Special Document Types (Greek business context)

Read `references/greek-doc-types.md` for full taxonomy.

Quick reference:

| Document | Entity source | Date source | DocType field |
|----------|--------------|-------------|---------------|
| Τιμολόγιο | Εκδότης (top) | Ημ. έκδοσης | `Τιμολόγιο` |
| ΑΠΥ | Παρέχων | Ημ. έκδοσης | `ΑΠΥ` |
| Βεβαίωση ΕΦΚΑ | ΕΦΚΑ | Ημ. έκδοσης | `Βεβαίωση-ΕΦΚΑ` |
| Δήλωση ΦΠΑ | ΑΑΔΕ/ΔΟΥ | Φορολ. περίοδος | `ΔήλωσηΦΠΑ` |
| Μισθοδοτική κατάσταση | Εταιρεία | Μήνας/Έτος | `Μισθοδοσία` |
| Συμβόλαιο | Αντισυμβαλλόμενοι | Ημ. υπογραφής | `Συμβόλαιο` |
| Τραπεζικό αντίγραφο | Τράπεζα | Ημ. αντιγράφου | `Κίνηση` |
| Passport/ID scan | Κάτοχος | Ημ. έκδοσης | `Ταυτότητα` |

---

## 9. Session Kickoff Script

When skill first activates, run this mentally:

```
1. Ask (if not clear): PROPOSE or AUTO mode?
2. Ask (if not clear): Single file, folder, or batch?
3. If Google Drive: ask for folder link or search term
4. If upload: check /mnt/user-data/uploads/
5. Initialise MD5 registry: {}
6. Initialise rule log: []
7. Begin processing
```

---

## Reference files

- `references/reading-strategies.md` — Detailed per-filetype extraction code/instructions
- `references/greek-doc-types.md` — Full Greek business document taxonomy + naming examples
