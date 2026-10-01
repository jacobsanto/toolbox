# Folder Structure & Naming Rules

## Contents
- Two entry doors
- The full tree
- Locked naming conventions (entity folder, months, files)
- The three folders every entity gets
- Root-level exception folders
- The quality gate (promoting sandbox → live folder)

## Two entry doors

| Door | Accepts | Who has access |
|---|---|---|
| `{ROOT}/00_INBOX/` | accounting documents only | the user, accountant, staff |
| a separate personal "everything else" inbox (if one exists) | everything else | the user only |

The agents scan **only** the first one. Never point PROCESSOR at anything else.

## The full tree

```
{ROOT}/
├── 00_INBOX/                      ← the ONLY entry door, always ends up empty
│   └── (subfolders per source, if the inbox aggregates from multiple upstream places)
├── _PROCESSING/                   ← lock: a file here = someone is working on it
├── _SCRATCH/                      ← temp OCR docs, MUST be empty when a session ends
├── _CONTROL/                      ← all the sheet-based registries
├── _BANK_PENDING/                 ← bank receipts/transfers, untouched (reconciliation out of scope)
├── UNIDENTIFIED_REVIEW/           ← docs matching none of the configured ΑΦΜ
├── PERSONAL_EXPENSES_{OWNER}/     ← receipts w/ no company ΑΦΜ, addressed to a natural person
├── PENDING_ALLOCATION/            ← not even a document/receipt — exports, summaries, lists
├── 99_DELETIONS/{YYYY-MM}/{ΑΦΜ or PERSONAL}/   ← confirmed duplicates, month first
├── TO_ACCOUNTANT/{YYYY-MM}/{ΑΦΜ}/ ← monthly delivery folder, shortcuts + summary only
└── (one folder per entity in the config)/
    └── [ΑΦΜ] [Display Name]/
        ├── REVIEW/                ← tried, failed an explicit rule, waiting for a human
        ├── INFORMATIONAL/         ← company docs that are NOT accounting documents
        └── {YYYY}/
            └── {N}. {MonthName}/
                ├── Expense Documents/
                │   ├── {VENDOR}/              ← domestic vendors, direct
                │   ├── VIES/{VENDOR}/         ← EU vendors
                │   └── THIRD_COUNTRY/{VENDOR}/ ← non-EU vendors
                └── Income/
                    ├── {CUSTOMER}/
                    └── VIES/
```

If this tree is a sandbox feeding into an existing live accounting folder, keep the live
folder **frozen and read-only** until the quality gate passes (see below). Never write into
it directly during testing.

## Locked naming conventions

**Entity folder:** `[ΑΦΜ] [Display Name]` — ΑΦΜ always first (it's immutable), the name is
for human readability only. Never auto-create a folder for an entity not in the config; an
ΑΦΜ that matches none of them goes to `UNIDENTIFIED_REVIEW`, not a new folder.

**Months**, exactly this format, no other variant accepted: `1. January` · `2. February` …
`12. December` (or the local-language equivalent the deployment uses — Greek deployments use
`1. Ιανουάριος` etc.). The month always comes from the document's **issue date** — never
scan date, upload date, due date, or today's date.

**Files** — prefix by document type:

| Prefix | Document type | Full pattern |
|---|---|---|
| (your invoice prefix, e.g. `INV_`) | Invoice / receipt / company accounting document | `{prefix}_{number}_{vendor≤20chars}_{DD.MM.YYYY}_({amount}{currency symbol}).pdf` |
| (climate-resilience-fee prefix) | Local equivalent of a lodging tax replacement | same pattern; a **separate document**, not a duplicate of a same-day invoice |
| (payment prefix) | Payment/transfer (only if payment-flow is enabled — see limitations) | `{prefix}_{DD.MM.YYYY}_{payee}_({amount}{symbol}).pdf` |
| (personal-expense prefixes) | Personal expense (receipt / owed-invoice / credit note) | same pattern, filed under `PERSONAL_EXPENSES_{OWNER}/` |
| `[CHECK]` | Nothing matched / needs manual confirmation | `[CHECK] {8-char fileId} {original name}.pdf` — "don't auto-touch me again" |

A credit note gets a **negative** final amount in parentheses: `(-19.69€)`. A payment line
*inside* an otherwise normal invoice does **not** make the amount negative — only an actual
credit note does. The vendor portion of the filename is capped at 20 characters (uppercase,
hyphens instead of spaces, cut at a word boundary, never mid-word); the folder still gets
the full vendor name.

## The three folders every entity gets

| Folder | Accepts | In the books? |
|---|---|---|
| `{YYYY}/{N}. {Month}/…` | Real, fully-processed documents | yes |
| `REVIEW/` | Tried, failed an explicit rule (amount mismatch, ambiguous vendor, etc.) — waiting on a human | no |
| `INFORMATIONAL/` | Applications, certificates, tax-authority statements, reminders — company docs that aren't accounting documents | no |

Both `REVIEW/` and `INFORMATIONAL/` are always excluded from any delivery to an accountant
or auditor.

## Root-level exception folders

**`UNIDENTIFIED_REVIEW/`** — for documents that match none of the configured entities.
It is explicitly forbidden to infer the entity from an email address, a recipient's name,
or a mailing address — only an exact ΑΦΜ match counts (the reasoning: you need to see who
actually paid, because a document can sometimes be paid from an unexpected source). This
folder also holds "known external entities" from the config — things that will keep
showing up (because you handle bookings/invoicing for them) but never belong in your own
books. Growing this list doesn't mean "solved," it means "we know why this doesn't resolve,
and where it lives."

**`PERSONAL_EXPENSES_{OWNER}/`** — receipts/invoices/credit notes that (a) carry no company
ΑΦΜ anywhere on the document AND (b) are addressed to a natural person by name or personal
email. Never enters the doc index or vendor registry — it isn't any entity's expense.

**`PENDING_ALLOCATION/`** — anything that isn't even a document or receipt: lists, exports,
multi-property summaries, review dashboards. Sits here until further instruction — it's not
unsolved, it's simply not the kind of thing this system resolves.

**`_BANK_PENDING/`** — bank receipts/transfers, collected untouched. Payment reconciliation
is a separate, usually-disabled workflow (see `limitations.md`).

⚠️ **Duplicate checking applies to `UNIDENTIFIED_REVIEW/` and `PERSONAL_EXPENSES_{OWNER}/`
too** — these two folders are outside the doc-index's normal tracking, but a real deployment
found duplicate pairs slipping through exactly because of that gap. Before moving a new file
into either: list the destination and compare `{vendor}+{date}+{amount}` against what's
already there (ignore the doc-type prefix — a receipt and an invoice can be the same
transaction). Keep the stronger proof of payment if there's such a pair, otherwise keep the
older one. Duplicates go to `99_DELETIONS/{YYYY-MM}/PERSONAL/`.

## The quality gate (promoting sandbox → live folder)

Move to a live, accountant-facing folder only when **all five** hold simultaneously:
≥ `GATE_MIN_FILES` files processed · 0 in the wrong entity · 0 in the wrong month · 0
duplicates that slipped through · REVIEW < `GATE_MAX_REVIEW_PCT`% of total. If any fails, go
back to a testing phase — never promote "almost." "Done" means: `00_INBOX` empty, `_SCRATCH`
empty, every file in exactly one place, one tree, REVIEW in the single digits.
