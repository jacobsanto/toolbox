# Data Model (Control Sheets)

Five control sheets, no more (extra "business sheets" would violate the one-source-of-truth
principle), all under `_CONTROL/`. IDs for each live in the deployment config
(`config-template.md` §5).

**VENDORS** — the single source of truth for country routing. Columns: `normalizedName`,
`displayName`, `shortName`, `vatId`, `country`, `route` (home/EU/third-country),
`aliases`, `status` (`SEED_UNVERIFIED`, `SEED_VAT_HIGH`, `AUTO_NEW`,
`CONFIRMED_DOMESTIC_VAT_EXCEPTION`, …), `createdAt`. Seed this with known recurring
vendors during setup — every unseeded vendor becomes an `AUTO_NEW` row on first sight.

**DOC_INDEX** — what's already been filed; the backbone of duplicate detection. Columns:
`keyStrong`, `keyWeak`, `entityId`, `docType`, `vendorNorm`, `docNumber`, `docDate`,
`totalCents`, `currency`, `fileId`, `finalName`, `finalUrl`, `state`, `timestamp`.
Partition by year (`DOC_INDEX_2026`, `DOC_INDEX_2027`, …) as the deployment grows. Contains
no rows for `PERSONAL_EXPENSE`/`PENDING_ALLOCATION` states.

**JOBS** — per-file processing state, admin actions, audit trail. Columns: `jobId` (e.g.
`J-00NN`), `fileId`, `originalName`, `finalName`, `entityId`, `state` (`COMPLETED`,
`REVIEW`, `PENDING_FILE`, `DUPLICATE`, …), `reason`, `destination`, `timestamp`,
`parentJobId`, `retryCount`, `ADMIN_ACTION`.

**EVENTS** — append-only audit log. Columns: `timestamp`, `event`, `jobId`, `fileId`,
`detail`. Records things like `VENDOR_AUTO_ADDED`, `STALE_LOCK_RELEASED`,
`SESSION_CLOSED`, and serious incidents worth a permanent record (e.g. a
misplacement bug found and fixed — see the safety rule in `SKILL.md`).

**SETTINGS** — every threshold and every Drive/Sheet ID in one place. Columns: `key`,
`value`, `editable`, `notes`. This is the natural home for the filled-in
`config-template.md` if you'd rather store it as a sheet than a standalone file. Core keys
mirror `config-template.md` §6: `BATCH_SIZE`, `STALE_LOCK_MINUTES`, `SNIPPET_MIN_CHARS`,
`AMOUNT_TOLERANCE_EUR`, `VENDOR_NAME_MAX_CHARS`, valid VAT rates, `MISSING_DOC_LOOKBACK`,
`MISSING_DOC_THRESHOLD`, `GATE_MIN_FILES`, `GATE_MAX_REVIEW_PCT`, `FLOW_B_ENABLED`,
`FX_SOURCE`.

*(Optional, not always active: an `OCR_CACHE` sheet, for the "OCR runs exactly once per
file" rule — see R2 in `duplicate-rules.md`.)*
