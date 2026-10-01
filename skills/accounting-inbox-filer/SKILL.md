---
name: accounting-inbox-filer
description: Deterministic, rule-based system for filing incoming Greek accounting documents (τιμολόγια, ΑΠΥ, ΤΑΚΚ, πιστωτικά) from a Google Drive inbox into a per-legal-entity, per-month folder tree — with GR/VIES/THIRD country routing, myDATA-MARK-based duplicate detection, and a monthly "what's missing" report for the accountant. Works for one or many ΑΦΜ/legal entities at once; the entity list, Drive/Sheet IDs, and personal-expense-owner are supplied by a per-deployment config, never hardcoded in the skill. Use this whenever the user wants to set up, run, extend, or debug a document-filing pipeline for a company's (or group's) accounting inbox — triggers include "φτιάξε μου σύστημα αρχειοθέτησης παραστατικών", "οργάνωσε τα τιμολόγιά μου στο Drive", "duplicate invoice detection", "monthly missing documents report", "TITAN-style filer", or requests to build the 4 filing agents (PROCESSOR/VERIFIER/DUPE_HUNTER/MONTHLY) for a new client or entity set.
---

# Accounting Inbox Filer

A deterministic, rule-based pipeline that takes a messy Google Drive inbox of accounting
documents (invoices, receipts, credit notes, climate-resilience fees, etc.) for one or more
Greek legal entities and files each one into the correct entity → year → month → category →
vendor folder, with the correct filename, without duplicates, and with a clear paper trail of
what still needs a human decision.

This skill is the **generalized engine**. It contains no company names, ΑΦΜ, Drive IDs, or
Sheet IDs — those live in a **per-deployment config** (see `references/config-template.md`)
that you create once per client/group and point the skill at. The same engine can run one
solo-proprietor ΑΦΜ or a six-entity group; nothing in the logic changes, only the config.

## Why this exists

A prompt-based LLM pipeline processing hundreds of financial documents a month will
hallucinate if you let it. This skill encodes the fix: **the AI reads, the rules decide.**
Every ambiguous case goes to a review folder for a human, never to a guess. This isn't a
limitation — it's the design. Read `references/principles.md` for the 7 principles this
whole system is built on before changing any rule; they explain *why* the pipeline is this
strict, and every rule below traces back to one of them.

## Before you do anything: load the config

This skill needs a config before it can file a single document. Never invent entity names,
ΑΦΜ, or Drive/Sheet IDs — always read them from the deployment's config.

1. Ask the user (or read from their project files) where the config lives — usually a
   `SETTINGS` sheet in `_CONTROL/` or a config file in the project. See
   `references/config-template.md` for the exact schema and a filled-in example with
   placeholder data.
2. If no config exists yet, this is a **first-time setup** — walk through
   `references/setup-checklist.md` with the user before processing any files. Do not
   improvise folder names, entity lists, or IDs while waiting for answers.
3. Once loaded, treat the config as the single source of truth for: the closed list of
   legal entities (ΑΦΜ + display name + type), the Shared Drive and root folder ID, the
   Sheet IDs, the personal-expense owner, the known-external-entity exclusion list, and the
   tunable thresholds (batch size, stale-lock minutes, amount tolerance, etc.).

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

Full folder-naming rules, locked month-name format, and the "quality gate" for promoting a
sandbox tree to a live accounting folder are in `references/folder-structure.md`.

## The 13-step pipeline

Every file goes through the same 13 steps, in the same order, no exceptions. If a step
fails, the file stops there and goes to a known exception location — never silently
dropped, never left half-processed, never advanced on a guess.

Full step-by-step detail (with the exact extraction fields, the closed-list ΑΦΜ match, the
"is this even an accounting document" branch, the Κ1a Greek-VAT-overrides-country-of-issuer
exception, and a fully worked example) is in `references/pipeline.md`. Read it before
running the PROCESSOR agent for the first time on a new deployment.

The one-line version: `[00_INBOX] → lock → read → extract fields → 6 filter checks →
route/name → move → log → [final location]`.

## Duplicate detection

Documents get filed idempotently even when the same PDF lands in the inbox three times, and
— just as important — genuinely different documents (a ΤΠΥ and a same-day ΤΑΚΚ for the same
customer, an invoice and the credit note against it) never get mistaken for duplicates. The
myDATA MARK (the AADE QR code's unique ID) is the strongest signal available and always
wins when present. Full algorithm, the "what is NOT a duplicate" absolute rules, and a set
of hard-won edge cases (Booking.com totals vs. turnover, SaaS invoice+receipt pairs, OCR
decimal misreads) are in `references/duplicate-rules.md`.

## The 4 permanent agents

Four narrow, repeatable prompts do the actual work, always run on the cheapest model
capable of following rules — the coordinating model only diagnoses failures and handles
whatever lands in REVIEW.

| Agent | Runs | Does | Writes? |
|---|---|---|---|
| PROCESSOR | every batch (config `BATCH_SIZE`, default 12) | full cycle: read → classify → name → place → log | yes |
| VERIFIER | every 5 batches | integrity check, orphan cleanup, stale-lock release | limited |
| DUPE_HUNTER | once the inbox is empty | duplicate detection (proposes, never executes) | proposes only |
| MONTHLY | on a fixed day each month | "what's missing" + delivery folder for the accountant | yes |

Full agent prompts (parameterized — `{{FOLDER_ID}}`, `{{N}}`, `{{YYYY-MM}}`, and the entity
list are filled in from the config, never hardcoded) are in `references/agents.md`. Call
them verbatim, substituting only the placeholders — paraphrasing them defeats the
determinism this whole system depends on.

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
event log, and the tunable settings. Schema and column list in `references/data-model.md`.

## What this system explicitly does not do

Bank reconciliation, myDATA cross-checks, bookkeeping, or tax calculation. The line: **paper
is this system's job, numbers are the accountant's.** It also never invents a 7th entity —
an ΑΦΜ that matches none of the configured entities goes to `UNIDENTIFIED_REVIEW`, never to
an auto-created folder. Full list of known technical limitations (no real checksum, single
OCR provider, no transactions on Sheets) is in `references/limitations.md`.

## Quick reference for common requests

- **"Set this up for a new client"** → `references/setup-checklist.md`, then
  `references/config-template.md`.
- **"Why did file X get flagged as a duplicate of Y?"** → walk the algorithm in
  `references/duplicate-rules.md` against the two files' extracted fields.
- **"The monthly missing-docs report"** → the MONTHLY agent in `references/agents.md`.
- **"A file landed in the wrong entity folder"** → re-check step 3 (company identification)
  in `references/pipeline.md`; remember exact-ΑΦΜ-match only, never inference from name/email.
- **"Can we promote the sandbox to the live folder?"** → the quality gate in
  `references/folder-structure.md`.
