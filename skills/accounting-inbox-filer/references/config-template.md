# Deployment Config Template

This is the **only** place entity names, ΑΦΜ, and Drive/Sheet IDs should ever live. The
skill itself must never hardcode any of this — every deployment (a solo proprietor, a
six-entity group, a new client next month) gets its own copy of this config, filled in once
during setup, and the agent prompts in `prompts/` read from it via the `{{...}}` placeholders.

Store the filled-in version wherever makes sense for the deployment — a `SETTINGS` sheet
inside `_CONTROL/` (mirroring the sheet-based settings model in `data-model.md`) is the
natural home since the agents already read that folder, but a plain config file works too.

## 1. Drive locations

```
SHARED_DRIVE_NAME:      <e.g. "General Accounting">
SHARED_DRIVE_ID:        <Drive ID>
DRIVE_ROOT_FOLDER_NAME:  <e.g. "AccountingFiler_V1">
DRIVE_ROOT_FOLDER_ID:    <folder ID — everything created/moved must stay inside this tree>
```

## 2. Legal entities (closed list — never auto-extended)

One row per ΑΦΜ. This is the list step 3 of the pipeline (company identification) matches
against, exact-match only. An ΑΦΜ that isn't in this list never gets a new folder
auto-created for it — it goes to `UNIDENTIFIED_REVIEW` instead (see `folder-structure.md`).

| ΑΦΜ | Display name | Entity type | Notes |
|---|---|---|---|
| `<tax id>` | `<name shown in folder>` | `<e.g. ΙΚΕ, ΟΕ, ΕΕ, ατομική>` | `<anything worth flagging — e.g. "easily confused with ΑΦΜ X, different entity"` |

Example (placeholder data, not a real deployment):

| ΑΦΜ | Display name | Entity type | Notes |
|---|---|---|---|
| 090000001 | EXAMPLE HOLDINGS ΙΚΕ | ΙΚΕ | — |
| 090000002 | Ε. ΠΑΡΑΔΕΙΓΜΑΤΟΥ | Ατομική / φυσικό πρόσωπο | — |

## 3. Personal-expense routing

```
PERSONAL_EXPENSE_OWNER_NAME:   <natural person's name>
PERSONAL_EXPENSE_OWNER_EMAIL:  <personal email pattern used to recognize addressed-to-them docs>
PERSONAL_EXPENSE_FOLDER_NAME:  PERSONAL_EXPENSES_{OWNER}   (auto-derived from the name above)
```

A receipt/invoice/credit-note with **no company ΑΦΜ anywhere on it** and addressed to this
person (by name or personal email) routes here instead of `UNIDENTIFIED_REVIEW`. It's
excluded from the duplicate-detection index and vendor registry — it isn't any entity's
expense.

## 4. Known external entities (optional exclusion list)

Some ΑΦΜ will legitimately keep showing up in the inbox (e.g. because you handle bookings
or invoicing for a property/client you don't own) without ever belonging in the books. List
them here so they route straight to `UNIDENTIFIED_REVIEW`'s "known foreign ΑΦΜ" bucket
instead of being re-investigated every time. This list only ever grows by adding a new
entry when a new one shows up — it never means "solved," it means "we know why this one
doesn't resolve, and where it lives."

| ΑΦΜ | Why it appears | 
|---|---|
| `<tax id>` | `<e.g. "managed property, not owned">` |

## 5. Control sheet IDs

```
VENDORS_SHEET_ID:    <sheet ID — vendor→country-route registry>
DOC_INDEX_SHEET_ID:  <sheet ID — filed-document index, duplicate detection>
JOBS_SHEET_ID:       <sheet ID — per-file processing state>
EVENTS_SHEET_ID:     <sheet ID — append-only audit log>
SETTINGS_SHEET_ID:   <sheet ID — this config, if stored as a sheet>
OCR_CACHE_SHEET_ID:  <sheet ID — optional, for the one-OCR-pass-per-file rule>
```

Schema for each in `data-model.md`.

## 6. Tunable settings

```
BATCH_SIZE:               12      # files per PROCESSOR run
STALE_LOCK_MINUTES:       30      # _PROCESSING timeout before VERIFIER reclaims it
SNIPPET_MIN_CHARS:        120     # below this, fall back to OCR
AMOUNT_TOLERANCE_EUR:     0.02    # net + vat vs total arithmetic check
VENDOR_NAME_MAX_CHARS:    20      # in filenames only, full name stays in the folder
MISSING_DOC_LOOKBACK:     4       # months looked back for the "what's missing" report
MISSING_DOC_THRESHOLD:    3       # of the last N months, appeared in ≥ this many
GATE_MIN_FILES:           100     # quality gate, see folder-structure.md
GATE_MAX_REVIEW_PCT:      15      # quality gate, see folder-structure.md
FLOW_B_ENABLED:           false   # payment reconciliation — out of scope unless explicitly built
FX_SOURCE:                https://api.frankfurter.dev/v1/{date}?base={currency}&symbols=EUR
```

## Setting up a new deployment

Don't process a single file until every section above is filled in and confirmed with the
user — especially section 2 (the entity list). Guessing at ΑΦΜ or inventing a plausible
folder structure defeats the entire point of this system: determinism requires a config
that's actually correct, not a best guess. See `setup-checklist.md` for the full first-time
walkthrough.
