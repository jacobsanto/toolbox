# The Pipeline, Step by Step

## Contents
- The 13 steps (each heading carries its degree of freedom: low = exact rule, medium = guided judgment)
  - Step 0 — Lock
  - Step 1 — Read content
  - Step 2 — Extract fields
  - Step 3 — Whose is this? (entity identification)
  - Step 4 — Is this even an accounting document?
  - Step 5 — Country routing (GR/VIES/THIRD)
  - Step 6 — Duplicate check
  - Step 7 — Arithmetic check
  - Step 8 — Foreign currency
  - Step 9 — Build the path
  - Step 10 — Name
  - Step 11 — Move
  - Step 12 — Verify arrival
  - Step 13 — Log to the registries
- Batch size
- Worked example

## The 13 steps

One line: `[00_INBOX] → lock → read → extract fields → 6 filter checks → route/name → move →
log → [final location]`.

Every file goes through all 13 steps, in this exact order. A failure at any step stops the
file there and sends it to a known exception location — never deleted, never left hanging,
never advanced on a guess.

### Step 0 — Lock · low

Move the file from `00_INBOX/{source}` into `_PROCESSING/`. Prevents two
processors from grabbing the same file. If a file sits there longer than
`STALE_LOCK_MINUTES` without completing, the VERIFIER agent returns it to `00_INBOX` and
logs a `STALE_LOCK_RELEASED` event.

### Step 1 — Read content · medium

Start with the PDF's native text layer — no conversion, no OCR
call. This is sufficient for essentially all digital-native PDFs. If the text is empty or
under `SNIPPET_MIN_CHARS` (scanned image) → OCR fallback: convert to a temp Google Doc in
`_SCRATCH/` → read its content → delete the temp doc **in the same pass**, not "I'll clean
it up later" (delayed deletion is exactly how a prior deployment ended up with hundreds of
orphaned temp docs wrecking a folder). Never use a bulk-convert-folder tool for this — same
root cause as the orphan problem. Edge case: badly OCR'd Greek text (letters become `?????`)
often still leaves numbers/ΑΦΜ/dates readable — no need for a second OCR pass, a manual read
of just those fields is fine.

### Step 2 — Extract fields · low

Verbatim, no conversions or rounding: `docType`, `issuerName`,
`issuerVat`, `recipientVat`, `docNumber`, `docDate`, `netAmount`, `vatAmount`, `totalAmount`,
`currency`, `myDataMark` (if a QR/MARK is present). No judgment calls here — pure
extraction, decisions come later.

### Step 3 — Whose is this? (entity identification) · low

Compare `issuerVat`/`recipientVat`
against the config's closed entity list, ignoring an `EL` prefix and leading zeros.
`recipientVat` = one of ours → **expense**. `issuerVat` = one of ours → **income**. Both or
neither → `UNIDENTIFIED_REVIEW`, reason "ambiguous entity". Absolute rule: **never** infer
the entity from a name, email, or address — exact ΑΦΜ match only.

### Step 4 — Is this even an accounting document? · medium



| The document is… | Goes to… |
|---|---|
| An application, certificate, debt statement, reminder, insurance policy — anything with no document number AND no charge amount | `INFORMATIONAL/` for that entity |
| A bank receipt/transfer/payment | `_BANK_PENDING/` (payment flow usually disabled — see `limitations.md`) |
| A receipt/invoice/credit note with no company ΑΦΜ, addressed to a natural person | `PERSONAL_EXPENSES_{OWNER}/` |
| Not even a document/receipt — a list, export, multi-property summary | `PENDING_ALLOCATION/` |
| A normal company accounting document | continue to step 5 |

Check the personal-expense and pending-allocation branches **before** falling through to
`UNIDENTIFIED_REVIEW` in step 3's ambiguous case — that folder is for genuinely uncertain
documents, not a general dumping ground. If everything that isn't obviously identified lands
there, it stops being useful.

### Step 5 — Country routing (GR/VIES/THIRD) · low

Exact match of `issuerVat` (or its normalized
name) against the vendors sheet; its `route` column gives `GR | VIES | THIRD`. Never decide
country from OCR guesswork or a name's ending. Not found → add a new vendors row with
`status=AUTO_NEW`, route derived from the VAT prefix (`EL`→GR, other EU→VIES, non-EU/no
VAT→THIRD), log a `VENDOR_AUTO_ADDED` event. Two or more plausible matches → `REVIEW`,
reason "ambiguous vendor".

⚠️ **Exception, overrides everything above:** if the document shows domestic VAT actually
charged at >0% (not 0%, not reverse-charge), the route is **always** the domestic route,
regardless of the issuer's VAT country. Worked example: a vendor with an Irish VAT ID that
charges 24% Greek VAT still routes GR, not VIES — because the tax actually charged, not the
issuer's registration country, determines the routing. VIES/THIRD only apply when domestic
VAT genuinely isn't being charged.

### Step 6 — Duplicate check · low

Full algorithm in `duplicate-rules.md`.

### Step 7 — Arithmetic check · low

`|netAmount + vatAmount − totalAmount| ≤ AMOUNT_TOLERANCE_EUR`
→ passes. Otherwise → `REVIEW`, reason "amount mismatch". Critical detail: `totalAmount` is
always the **document's** total, never turnover — an OTA invoice's "Reservations" line is
booking turnover, the real payable amount is the "Total amount due" (commission + fees).
Accepted VAT rates: whatever the jurisdiction's valid list is (for Greece: 0, 4, 6, 9, 13,
17, 24, plus reverse charge) — the check never blocks on an "unusual" rate, only on
arithmetic that doesn't add up.

### Step 8 — Foreign currency · low

Only when the document's currency ≠ the home currency.

The foreign amount stays in the filename. The exchange rate is priced as of the **issue
date**, so it's calculated and recorded in the monthly summary. Priority order:

1. **Rate stated on the document itself** — wins, it's what the issuer actually used.
2. **Central-bank rate for the issue date** — e.g.
   `https://api.frankfurter.dev/v1/{YYYY-MM-DD}?base={currency}&symbols=EUR` for EUR-based
   deployments. On a weekend/holiday this correctly returns the previous business day's
   rate (central banks don't publish on non-business days).

Record both the rate **and** its date — they can differ from the document's date. Worked
examples: a $31.00 invoice dated 2026-03-27 converted at the same-day rate; a $520.00
invoice dated 2024-01-01 (a holiday) correctly used the prior business day's rate
(2023-12-29).

### Step 9 — Build the path · low

`{entity}/{YYYY}/{N}. {Month}/{Category}[/{VIES|THIRD_COUNTRY}]
/{Vendor}`. Category: expense→"Expense Documents", income→"Income". The intermediate
VIES/THIRD_COUNTRY segment only appears when `route ≠ home country`. Only call `createFolder`
for what's actually missing. ⚠️ After **every** `createFolder`: mandatory parent-ID
verification (see the safety rule in `SKILL.md`) — a mismatch means stop immediately. The
month always comes from the document's **issue date**, never scan/due/upload/today's date.

### Step 10 — Name · low

Name before moving — this ordering matters for resumability: if processing
gets interrupted between naming and moving, the already-renamed file signals it's already
been analyzed, preventing double-processing. Pattern:
`{docType}_{docNumber}_{Vendor≤20chars}_{DD.MM.YYYY}_({amount}{symbol}).pdf`. Credit note →
negative amount: `(-19.69€)`. A payment line inside an otherwise-normal invoice does **not**
make the amount negative.

### Step 11 — Move · low

`moveItem` (never `copyFile`) from `_PROCESSING/` to the final path.
Absolute move-only rule: no copying, no permanent deletion anywhere in the system (only a
move into `99_DELETIONS`, which a human empties manually).

### Step 12 — Verify arrival · low

Fresh `listFolder`/search of the destination, confirm presence
under the correct final name. Mismatch → flagged as a problem to investigate, never silently
reported as success.

### Step 13 — Log to the registries · low

Append rows, never overwrite — skipped entirely for
`PERSONAL_EXPENSE`/`PENDING_ALLOCATION` states. Rows: doc-index row (key fields + state +
timestamp) and jobs row (job ID, file ID, names, entity, state, reason, destination,
timestamp). Exact columns in `data-model.md`.

### Batch size

`BATCH_SIZE` files per run (smaller batches trade throughput for more
frequent cost/quality checkpoints). Report + confirm-to-continue after every batch.

## Worked example

A vendor invoice, original filename `Inv_(9UC7DAIO-0001)_ExampleVendor.pdf`, three identical
copies landed in the inbox.

| Step | What happened | Result |
|---|---|---|
| 0 | Locked, moved to `_PROCESSING/` | — |
| 1 | Native text layer read — digital PDF, no OCR needed | text available |
| 2 | Fields extracted | docType=invoice, issuerVat=(foreign EU VAT), docNumber=9UC7DAIO-0001, docDate=2026-03-27, net=25.00, vat=6.00, total=31.00, currency=USD |
| 3 | Entity match | No ΑΦΜ explicitly listed as recipient → initially `UNIDENTIFIED_REVIEW`. User manually confirmed: entity = (one of the configured ΑΦΜ) |
| 4 | Is it a document? | Yes, continue |
| 5 | Country routing | Foreign VAT would normally give VIES/THIRD — but 24% domestic VAT is charged → exception applies, route=domestic |
| 6 | Duplicate? | 3 copies, same docNumber/docDate/total → the same document ×3. Kept 1, moved the other 2 to `99_DELETIONS/2026-08/{entity}/` |
| 7 | Arithmetic | 25.00 + 6.00 = 31.00 ✅ |
| 8 | Currency | USD≠home currency, no rate on the document → looked up the issue-date rate → converted |
| 9 | Path | `{entity}/2026/3. March/Expense Documents/EXAMPLEVENDOR/` |
| 10 | Name | `INV_9UC7DAIO-0001_EXAMPLEVENDOR_27.03.2026_(26.92€).pdf` |
| 11 | Moved | done |
| 12 | Verified | `listFolder` confirmed |
| 13 | Logged | doc index + jobs sheet, state=COMPLETED |

Side effect worth building into the habit: this run revealed the vendors sheet had this
vendor mis-registered (wrong route, no VAT, wrong country) — fixed so every future invoice
from them routes correctly without re-applying the domestic-VAT exception by hand each time.
