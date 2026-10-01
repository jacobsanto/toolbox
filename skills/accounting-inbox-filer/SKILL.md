---
name: accounting-inbox-filer
description: Deterministic, rule-based system for filing incoming Greek accounting documents (τιμολόγια, ΑΠΥ, ΤΑΚΚ, πιστωτικά) from a Google Drive inbox into a per-legal-entity, per-month folder tree — with GR/VIES/THIRD country routing, myDATA-MARK-based duplicate detection, and a monthly "what's missing" report for the accountant. Works for one or many ΑΦΜ/legal entities at once; the entity list, Drive/Sheet IDs, and personal-expense-owner are supplied by a per-deployment config, never hardcoded in the skill. Use this whenever the user wants to set up, run, extend, or debug a document-filing pipeline for a company's (or group's) accounting inbox — triggers include "φτιάξε μου σύστημα αρχειοθέτησης παραστατικών", "οργάνωσε τα τιμολόγιά μου στο Drive", "duplicate invoice detection", "monthly missing documents report", "TITAN-style filer", or requests to build the 4 filing agents (PROCESSOR/VERIFIER/DUPE_HUNTER/MONTHLY) for a new client or entity set.
compatibility: "Coordinator: Opus or Sonnet. The 4 agents (PROCESSOR, VERIFIER, DUPE_HUNTER, MONTHLY): Haiku-class. This model split has not been A/B tested. Requires Google Drive MCP with write access to the configured Shared Drive, and Google Sheets MCP for the 5 control sheets. No scripts or libraries."
---

# Accounting Inbox Filer

A deterministic, rule-based pipeline that takes a messy Google Drive inbox of accounting
documents (invoices, receipts, credit notes, climate-resilience fees, etc.) for one or more
Greek legal entities and files each one into the correct entity → year → month → category →
vendor folder, with the correct filename, without duplicates, and with a clear paper trail of
what still needs a human decision.

This skill is the **generalized engine**. It contains no company names, ΑΦΜ, Drive IDs, or
Sheet IDs — those live in a **per-deployment config** that you create once per client/group.
The same engine runs one solo-proprietor ΑΦΜ or a six-entity group; only the config changes.

**The AI reads, the rules decide.** A prompt-based pipeline processing hundreds of financial
documents a month will hallucinate if you let it, so every ambiguous case goes to a review
folder for a human, never to a guess. That's the design, not a limitation. Every rule below
traces back to one of the 7 principles in `references/principles.md` — read them before
changing any rule.

## Requirements

- **Google Drive MCP** — read, create folder, move, rename, metadata, shortcut, on a
  Shared Drive. Test write access before the first real batch (setup step 2); some
  connectors document only read scopes, some don't support Shared Drive writes at all.
- **Google Sheets MCP** — read and append rows on the 5 control sheets.
- No scripts, no pip/npm dependencies.

## Reference map

All files are one level below this one. Read only what the current task needs.

| File | Read when |
|---|---|
| `references/principles.md` | before changing or adding any rule |
| `references/setup-checklist.md` | first-time setup for a new client/entity set |
| `references/config-template.md` | creating or loading a deployment config |
| `references/folder-structure.md` | folder/month/file naming, exception folders, quality gate |
| `references/pipeline.md` | the 13 steps in detail, with a worked example |
| `references/duplicate-rules.md` | duplicate algorithm, what is NOT a duplicate, edge cases |
| `references/agents.md` | agent overview, safety rule, whole-project run order |
| `references/prompts/processor.md` | dispatching A1 · PROCESSOR (verbatim prompt) |
| `references/prompts/verifier.md` | dispatching A2 · VERIFIER (verbatim prompt) |
| `references/prompts/dupe-hunter.md` | dispatching A3 · DUPE_HUNTER (verbatim prompt) |
| `references/prompts/monthly.md` | dispatching A4 · MONTHLY (verbatim prompt) |
| `references/data-model.md` | the 5 control sheets and their columns |
| `references/limitations.md` | known technical limits and what's out of scope |

## Before you do anything: load the config

Never invent entity names, ΑΦΜ, or Drive/Sheet IDs — always read them from the config.

1. Ask the user (or read from their project files) where the config lives — usually a
   `SETTINGS` sheet in `_CONTROL/` or a config file in the project.
2. No config yet → first-time setup: walk through `references/setup-checklist.md` with the
   user before processing any files. Don't improvise folder names, entity lists, or IDs
   while waiting for answers.
3. Once loaded, the config is the single source of truth for: the closed list of legal
   entities (ΑΦΜ + display name + type), the Shared Drive and root folder ID, the Sheet IDs,
   the personal-expense owner, the known-external-entity exclusion list, and the tunable
   thresholds (batch size, stale-lock minutes, amount tolerance, etc.).

## Degrees of freedom

Low wherever a step moves files, touches amounts, or writes to the control sheets.

| Step / activity | Freedom | Why |
|---|---|---|
| Load config, entity match (pipeline step 3) | low | closed list, exact ΑΦΜ only — a wrong guess files into another company's books |
| Lock, path, move, verify arrival (steps 0, 9, 11, 12) and the parent-ID check | low | files move; a wrong parent once landed files in a personal My Drive |
| Extract fields (step 2) | low | verbatim, no conversion — every later decision depends on these values |
| Routing, duplicates, arithmetic, currency (steps 5–8) | low | money and VAT routing; a different answer means wrong books or a lost document |
| Name (step 10) | low | fixed pattern; resumability depends on it |
| Log to registries (step 13) | low | append-only ledger |
| Agent prompts | low | sent verbatim, only `{...}` substituted |
| Duplicate deletion | low | DUPE_HUNTER proposes, a human approves, then a move to `99_DELETIONS` |
| Read content (step 1) | medium | fixed ladder: text layer → single OCR pass → manual read of key fields |
| Is it an accounting document? (step 4) | medium | judgment, bounded by the step-4 table |
| MONTHLY report wording | medium | fixed columns, free summary text |
| Handling REVIEW items, diagnosing failures | high | the coordinator's job; the goal is the right rule, not a quick fix |

## The shape of the system

```
{DRIVE_ROOT}/
├── 00_INBOX/                       ← the only entry point, always ends up empty
├── _PROCESSING/                    ← lock: a file here means someone is working on it
├── _SCRATCH/                       ← temp OCR docs, must be empty when you're done
├── _CONTROL/                       ← control sheets (see references/data-model.md)
├── _BANK_PENDING/                  ← bank receipts/transfers, untouched (reconciliation is out of scope)
├── UNIDENTIFIED_REVIEW/            ← docs that don't match any configured ΑΦΜ
├── PERSONAL_EXPENSES_{OWNER}/      ← receipts with no company ΑΦΜ, addressed to a natural person
├── PENDING_ALLOCATION/             ← not even a document — exports, summaries, lists
├── 99_DELETIONS/{YYYY-MM}/{entity or PERSONAL}/   ← confirmed duplicates, month first
├── TO_ACCOUNTANT/{YYYY-MM}/{ΑΦΜ}/  ← monthly delivery folder, shortcuts only
└── {company_root}/                 ← one folder per configured entity
    └── [ΑΦΜ] [Display Name]/
        ├── REVIEW/                 ← tried, failed an explicit rule, needs a human
        ├── INFORMATIONAL/          ← company docs that aren't accounting documents
        └── {YYYY}/{N}. {MonthName}/
            ├── Expense Documents/
            │   ├── {VENDOR}/               ← domestic vendors
            │   ├── VIES/{VENDOR}/          ← EU vendors
            │   └── THIRD_COUNTRY/{VENDOR}/ ← non-EU vendors
            └── Income/
                ├── {CUSTOMER}/
                └── VIES/
```

Full folder-naming rules, locked month-name format, and the quality gate for promoting a
sandbox tree to a live accounting folder: `references/folder-structure.md`.

## The 13-step pipeline

Every file goes through the same 13 steps, in the same order, no exceptions. If a step
fails, the file stops there and goes to a known exception location — never silently
dropped, never left half-processed, never advanced on a guess.

The one-line version: `[00_INBOX] → lock → read → extract fields → 6 filter checks →
route/name → move → log → [final location]`.

Full detail — extraction fields, the closed-list ΑΦΜ match, the "is this even an accounting
document" branch, the Κ1a Greek-VAT-overrides-country-of-issuer exception, currency, and a
worked example — is in `references/pipeline.md`. Read it before running PROCESSOR for the
first time on a new deployment.

## Duplicate detection

Documents get filed idempotently even when the same PDF lands in the inbox three times, and
genuinely different documents (a ΤΠΥ and a same-day ΤΑΚΚ for the same customer, an invoice
and the credit note against it) never get mistaken for duplicates. The myDATA MARK always
wins when present. Algorithm, the "what is NOT a duplicate" rules, and the edge cases
(Booking.com totals vs. turnover, SaaS invoice+receipt pairs, OCR decimal misreads):
`references/duplicate-rules.md`.

## The 4 permanent agents

Four narrow, repeatable prompts do the work on the cheapest model capable of following
rules; the coordinating model only diagnoses failures and handles whatever lands in REVIEW.

| Agent | Runs | Does | Writes? |
|---|---|---|---|
| PROCESSOR | every batch (config `BATCH_SIZE`, default 12) | full cycle: read → classify → name → place → log | yes |
| VERIFIER | every 5 batches | integrity check, orphan cleanup, stale-lock release | limited |
| DUPE_HUNTER | once the inbox is empty | duplicate detection (proposes, never executes) | proposes only |
| MONTHLY | on a fixed day each month | "what's missing" + delivery folder for the accountant | yes |

Each prompt is in its own file under `references/prompts/`. Send it verbatim, substituting
only the placeholders — paraphrasing defeats the determinism this system depends on.

## Per-batch checklist

The order matters. Copy this for each batch:

```
- [ ] 1. Config loaded; entity list matches the config (closed list)
- [ ] 2. Session start or every 5th batch → VERIFIER run, its ⚠️ rows handled
- [ ] 3. PROCESSOR run on the next BATCH_SIZE files
- [ ] 4. Check the batch:
        - every file is in a final folder or a known exception folder
        - _PROCESSING/ and _SCRATCH/ are empty
        - every parent-ID check passed
        - arrivals confirmed by a fresh listFolder (step 12)
        - jobs/doc-index rows appended for every file that needs them
- [ ] 5. Any check failed → diagnose, fix, re-run step 4 for this batch; repeat until clean
- [ ] 6. Report the batch (PROCESSOR's RETURN table + REVIEW reasons)
```

When the inbox is empty: DUPE_HUNTER per entity → present findings → execute only what the
user approved.

**End of run — rule proposal.** If a REVIEW item, a failed check, or a correction exposed a
pattern no rule covers (a mis-registered vendor, a new edge case), propose the new rule —
where it goes (vendors sheet, `duplicate-rules.md` edge cases, pipeline step) and which
principle it follows from. It goes in only after the user approves.

## The one non-negotiable safety rule

Everything created or moved during processing stays **exclusively** inside the deployment's
configured Shared Drive and root folder — never a personal My Drive, regardless of where the
source file came from. After *every* `createFolder`, `moveItem`, `copyFile`, or
`createSheet` call: immediately fetch the new item's metadata and confirm its parent is
exactly what was requested. Mismatch (or an unrecognized/My-Drive parent) → **stop**, move
nothing further into it, report immediately.

This isn't theoretical — it's here because a real deployment once had `createFolder` calls
made directly by the coordinator (bypassing the subagent) silently land files in the user's
personal My Drive despite a correct `parentId` argument. The bug was in that specific
tool-calling path, not the argument. The lesson that survives into any real (non-prompt-based)
implementation: always verify the parent after a write, never trust that a correct-looking
argument produced a correct result.

## Data model

Five control sheets (never more — extra "business sheets" violate the single-source-of-truth
principle) hold everything needed for determinism without a database: vendor routing, the
already-filed index (duplicate detection's backbone), per-file job state, an append-only
event log, and the tunable settings. Schema: `references/data-model.md`.

## What this system explicitly does not do

Bank reconciliation, myDATA cross-checks, bookkeeping, or tax calculation. The line: **paper
is this system's job, numbers are the accountant's.** It also never invents a 7th entity —
an ΑΦΜ that matches none of the configured entities goes to `UNIDENTIFIED_REVIEW`, never to
an auto-created folder. Known technical limitations (no real checksum, single OCR provider,
no transactions on Sheets): `references/limitations.md`.

## Quick reference for common requests

- **"Set this up for a new client"** → `references/setup-checklist.md`, then
  `references/config-template.md`.
- **"Why did file X get flagged as a duplicate of Y?"** → walk the algorithm in
  `references/duplicate-rules.md` against the two files' extracted fields.
- **"The monthly missing-docs report"** → `references/prompts/monthly.md`.
- **"A file landed in the wrong entity folder"** → re-check step 3 (company identification)
  in `references/pipeline.md`; exact-ΑΦΜ-match only, never inference from name/email.
- **"Can we promote the sandbox to the live folder?"** → the quality gate in
  `references/folder-structure.md`.
