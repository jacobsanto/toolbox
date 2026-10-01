# The 4 Permanent Agents

All four run on the smallest/cheapest capable model — the coordinator (bigger model) only
coordinates, diagnoses failures, and handles whatever lands in `REVIEW`. Call these
verbatim, substituting only the `{{...}}` placeholders from the deployment's config —
paraphrasing them defeats the determinism the whole system depends on.

Before filling in `{{...}}`, load the config (`config-template.md`) — never write a literal
entity name, ΑΦΜ, or ID directly into these prompts. If you're setting these up for a new
deployment, generate the filled-in versions once and save them alongside the config so they
don't need to be re-assembled every session.

| Agent | Runs | Does | Writes? | Prompt |
|---|---|---|---|---|
| A1 · PROCESSOR | every batch of `{{BATCH_SIZE}}` files | full cycle: read → classify → name → place → log | yes | `prompts/processor.md` |
| A2 · VERIFIER | every 5 batches | integrity check, orphan cleanup, stale-lock release | limited | `prompts/verifier.md` |
| A3 · DUPE_HUNTER | once the inbox is empty | duplicate detection (proposes, never executes) | proposes only | `prompts/dupe-hunter.md` |
| A4 · MONTHLY | a fixed day each month | "what's missing" + accountant delivery folder | yes | `prompts/monthly.md` |

Each agent loads only its own prompt file — the four prompts are kept separate so a
Haiku-class agent never has to read the other three.

## Safety rule — applies to all four, no exceptions

Identical to the rule in `SKILL.md`: every create/move stays exclusively inside
`{{DRIVE_ROOT_FOLDER_ID}}` on `{{SHARED_DRIVE_ID}}`. Mandatory `get_file_metadata` after
every `createFolder`, confirm the `parentId`, mismatch → **stop**, report immediately.
Applies to the coordinator *and* every agent, on every write action, regardless of the
file's source.

## Whole-project flow — no questions asked

```
SESSION START
  → read the state/resume file
  → call A2 VERIFIER (cleans orphans, releases stale locks)
  → find the next unfinished source in 00_INBOX

WHILE FILES REMAIN
  → A1 PROCESSOR in batches of {{BATCH_SIZE}}
  → every 5 batches: A2 VERIFIER
  → update the state file with progress

WHEN THE INBOX IS EMPTY
  → A3 DUPE_HUNTER per entity
  → present findings for approval
  → execute only what was approved

EVERY MONTH (on the configured day)
  → A4 MONTHLY
```

The coordinator only handles: report review, whatever ended up in REVIEW, diagnosis when
something breaks, and updating the state file. Precondition for delegating anything to an
agent: there must be a deterministic safety net that catches the model's own mistakes (net +
VAT = total ± tolerance · VAT-ID checksum · exact match against a registry). Without a net,
don't delegate — the mistake will pass silently into the books.
