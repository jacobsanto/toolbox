# First-Time Setup Checklist

Walk through these in order with the user before processing a single real file. Skipping
ahead to "just start filing" without this is how you get a system that looks like it works
until the 50th file lands in the wrong entity's folder.

Copy this and tick it off — the order matters:

```
- [ ] 1. Entity list gathered (incl. look-alike ΑΦΜ and known external entities)
- [ ] 2. Drive skeleton created as a sandbox; write access tested on the Shared Drive
- [ ] 3. Five control sheets created, vendors sheet seeded
- [ ] 4. Config filled in and read back to the user
- [ ] 5. Dry-run on 5–10 known documents, every decision checked by hand
- [ ] 6. Quality gate passed (only if promoting to a live folder)
```

## 1. Gather the entity list

Ask for every ΑΦΜ that should be recognized, with its display name and entity type. This is
the single most important input — it's the closed list step 3 of the pipeline matches
against, and nothing outside it ever gets an auto-created folder. Explicitly ask: "are there
any ΑΦΜ that look similar to each other but are actually different entities?" — this is a
known failure mode (e.g. a natural person's ΑΦΜ and a similarly-named ΟΕ being confused).
Flag anything like that in the Notes column of the config.

Also ask whether any ΑΦΜ will show up in the inbox but should *never* be treated as one of
the entities (managed properties, pass-through billing, etc.) — that goes in the "known
external entities" list so it doesn't get re-investigated every month.

## 2. Set up the Drive skeleton

Create (or confirm the user has already created) a Shared Drive with the root folder tree
from `folder-structure.md`, under a single root folder. Do this as a **sandbox first** — a
brand-new tree, not a reuse of whatever ad-hoc filing existed before. Never point this
system at a live accounting folder the accountant is actively using until the quality gate
(section below) has been cleared.

Confirm write access: the account or service account the agents will use needs Content
Manager (or equivalent) permission on the Shared Drive, and the ability to
create/move/rename — not just list/read. This is worth testing explicitly before running a
real batch; some connectors document only read/list scopes even when write technically
works, and some don't support write on Shared Drives at all.

## 3. Create the control sheets

Five sheets under `_CONTROL/` (see `data-model.md` for exact columns): vendors, doc index,
jobs, events, settings. Seed the vendors sheet with any vendors already known to be
recurring (SaaS subscriptions, OTA platforms, major suppliers) and their country route —
this saves the first few batches from generating a wave of `AUTO_NEW` vendor rows.

## 4. Fill in the config

Complete every section of `config-template.md` and confirm it with the user, especially:
- the entity list (section 2) — read it back to them explicitly
- the personal-expense owner (section 3), if there's a natural person whose personal
  receipts will show up in the same inbox
- the known-external-entities list (section 4), if applicable

## 5. Dry-run before the first real batch

Before letting the PROCESSOR agent touch real files, run it on a small handful (5–10) of
already-known documents and manually check every decision: right entity, right month, right
route (GR/VIES/THIRD), right filename. This catches config mistakes (wrong ΑΦΜ typed in,
wrong entity type) far more cheaply than finding them after 100 files are filed.

## 6. The quality gate before touching a live folder

If this sandbox is meant to eventually replace or feed into an existing, accountant-facing
folder, don't move anything there until **all five** hold at once:

- ≥ `GATE_MIN_FILES` files have been processed
- 0 files in the wrong entity
- 0 files in the wrong month
- 0 duplicates that slipped through
- REVIEW folder < `GATE_MAX_REVIEW_PCT`% of the total

If any of these fail, go back to testing — don't promote "almost." "Done" means: `00_INBOX`
empty, `_SCRATCH` empty, every file in exactly one location, one tree, REVIEW under single
digits.
