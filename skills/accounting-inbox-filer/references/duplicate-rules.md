# Duplicates & Exceptions

## The 4 rules that solve "same file in two folders"

**R1 — Country is never read from OCR.** VAT is matched exact against the vendors sheet;
its `route` column gives `GR | VIES | THIRD` (or your jurisdiction's equivalent). Not found
→ a new `AUTO_NEW` row, route from the VAT prefix. Two possible matches → `REVIEW`. There is
no path from "misread text" to "wrong folder."

**R1a — Exception, overrides R1.** Domestic VAT actually charged overrides the issuer's
registration country. If a document charges domestic VAT >0% (not reverse-charge, not 0%),
the route is always domestic. See `pipeline.md` step 5 for the worked example.

**R2 — OCR runs exactly once per file.** The result is frozen (an OCR-cache sheet is the
natural place for this). Don't try to make the model itself deterministic — run it once and
lock the answer in.

**R3 — Document type is the first field of every key.** A credit note never mechanically
matches the original invoice it credits. Same for an invoice vs. a same-day
climate-resilience-fee-style document for the same customer — different document, not a
duplicate.

**R4 — The official unique receipt ID outranks any content-based key.** Greek documents
carry a myDATA QR with a unique AADE MARK (e.g. `400009785666188`) — an official identifier
better than anything derived from content. Where a MARK exists: `keyStrong = MARK|{mark}`
and the duplicate question is settled definitively.

## The practical duplicate-check algorithm

Check against the doc-index, in this order:

1. `keyStrong = MARK|{myDataMark}` — if a MARK exists, this is final.
2. `keyWeak = {docType}|{entityId}|{issuerVat}|{docNumber}|{docDate}|{totalCents}|{currency}`
   — match on all 7 fields.

A match against a `COMPLETED` row → move to `99_DELETIONS/{current YYYY-MM}/{entityId}/`. A
match against any other state → `REVIEW` (avoids confusing two simultaneously-active
records).

## What is NOT a duplicate — absolute rules

Different document type · different document number · a credit note vs. the invoice it
references · a recurring monthly charge of the same amount · identical filename on its own.

⚠️ **Don't trust an inherited "DUP" or similar marker from a prior system.** A verified
real-world case: two documents for the same customer on the same day — one a ~500€ invoice
with 13% VAT, one an ~8€ climate-resilience-style fee with no VAT — had been marked as
duplicates by an older system purely because they shared a customer and date. They were two
genuinely different documents with different official receipt IDs. Deleting either would
have left a real document missing from the books. Ignore any inherited prefix or flag;
judge the content.

## Duplicate checking also applies outside the doc index

`UNIDENTIFIED_REVIEW/` and `PERSONAL_EXPENSES_{OWNER}/` aren't tracked by the normal
doc-index, but duplicates slip in there too if you don't check. Before moving a new file
into either: `listFolder` the destination, compare `{vendor}+{date}+{amount}` against what's
already there (ignore the docType prefix — a "receipt" and an "invoice" version can be the
same transaction). Keep the stronger proof of payment (a receipt beats an unpaid invoice) if
such a pair exists, otherwise keep the older `createdTime`. Duplicate → `99_DELETIONS/
{YYYY-MM}/PERSONAL/`.

## Known edge cases (codified from real mistakes)

| Edge case | The old mistake | The correct rule now |
|---|---|---|
| OTA (Booking.com-style) invoice | Amount = room turnover ("Reservations") | Amount = "Total amount due" (commission + fees) |
| Export/download PDFs | Month = download/print date | Month = the document's actual issue date |
| OCR decimal misreads | Misread decimal (e.g. "1.09€" instead of "1095.66€") | Always derive `net + VAT = total` from the document; use the official receipt ID as final verification |
| SaaS subscriptions (issued as "due" then "paid") | Invoice(due) + Receipt(paid) for the same transaction treated as 2 separate documents | Same document — keep the "receipt/paid" version (stronger proof) |
| Vendor customer-code | — | A vendor-assigned customer code that matches an already-confirmed document is an acceptable identity anchor (not a guess — it's based on a prior confirmation) |
| Badly OCR'd non-Latin text | — | Text→garbled but numbers/VAT-ID/dates often still readable — manual rescue, no new OCR pass needed |
