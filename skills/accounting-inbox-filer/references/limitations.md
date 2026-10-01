# What This System Does Not Do & Known Limitations

## Explicitly out of scope

Bank reconciliation · myDATA (or equivalent tax-authority e-invoicing) cross-checks ·
bookkeeping · tax calculation · permanent deletion (only a move to `99_DELETIONS`, emptied
by a human) · auto-creating an entity folder · inferring an entity from
email/name/address · guessing, ever, for any reason.

## Payment flow — usually disabled

`FLOW_B_ENABLED = false` by default. Payments, IBANs, bank-matching rules, and
invoice↔payment reconciliation are a separate, larger project — only build it if explicitly
asked to. Reconciliation is the accountant's job; this system exists to hand them clean
income/expense paper to check against. Bank receipts/transfers just accumulate untouched in
`_BANK_PENDING/`.

## Known technical limitations

| What | Why | Consequence |
|---|---|---|
| No real cryptographic checksum | most Drive/file connectors don't expose one | use a pseudo-hash (the weak key); never auto-delete on that basis alone |
| Single OCR provider | whatever's available in the environment | handwritten/blurry documents land in REVIEW more often |
| One model, not several | no second model available | do two passes (extraction + adversarial check) instead of cross-checking with a second model |
| No transactions on Sheets | spreadsheet backends don't support them | one worker at a time, no parallelism on the same files |
| No native attachment-fetch from some mail providers | connector limitation | manual "save to Drive" step for those |

A higher REVIEW rate is not a bug — see `principles.md`. The goal isn't zero mistakes, it's
catching every mistake before it leaves the system.
