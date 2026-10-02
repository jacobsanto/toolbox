# Failure Patterns by Domain
# DiagnoseGPT Reference — common causes to seed Step 4 hypotheses

Use as a prompt for breadth, not as a verdict. A pattern listed here still has to pass
the three confirmation tests in SKILL.md Step 6.

## Contents

- Financial and reconciliation
- Accounting and tax documents
- Procurement and tenders
- Contracts and legal
- Policies and compliance
- Data, metrics and reports
- Customer and guest experience
- Sales, outreach and partnerships
- Product and UX
- Design systems
- Prompts and AI workflows
- Software and integrations

---

## Financial and reconciliation

- Gross vs net mixed: commissions, fees or taxes (e.g. ΤΑΚΚ, VAT) included on one side only.
- Timing: booking date vs stay date vs payout date vs bank value date.
- Currency: conversion rate source or date differs; rounding per line vs per total.
- Duplicates: same transaction from two sources (channel + channel manager, invoice + receipt).
- Partial payments, refunds, chargebacks, cancellations recorded on one side only.
- Manual adjustments with no audit trail.

## Accounting and tax documents

- Document type misread (τιμολόγιο vs ΑΠΥ vs πιστωτικό).
- Wrong legal entity / ΑΦΜ on the document.
- myDATA MARK missing, duplicated or belonging to a cancelled document.
- Country routing wrong (GR / VIES / third country) → wrong VAT treatment.
- Period mismatch: issue date vs service date vs receipt date.
- Rate or deadline changed by new legislation — verify by search.

## Procurement and tenders

- Route chosen does not match value or CPV (direct award where open procedure is required).
- Threshold or article outdated — revised thresholds not checked.
- Offer written around the bidder's strengths instead of the stated award criteria.
- Qualification document expired or missing (φορολογική / ασφαλιστική ενημερότητα).
- No relationship before the specification was written; specification favours another supplier.
- Decision-maker assumed to have authority they do not have.

## Contracts and legal

- Clause ambiguous; two readings both plausible.
- Clause conflicts with mandatory law and is void or overridden.
- Definitions section inconsistent with the operative clauses.
- Obligation without a remedy, or a remedy without a trigger.
- Governing law or jurisdiction different from what the parties assumed.
- Later amendment or side letter not reflected in the working copy.

## Policies and compliance

- Policy written but never communicated, trained or acknowledged.
- Policy conflicts with another policy or with local law in one jurisdiction.
- No owner and no review date; the policy is outdated.
- Control exists on paper but no evidence that it runs.

## Data, metrics and reports

- Definition drift: the metric was redefined or computed differently over time.
- Filter or join drops or duplicates rows.
- Missing data treated as zero, or zero treated as missing.
- Time zone, date format or period boundary error.
- Sample too small; change is noise.
- Mix shift: the average moved because the composition changed, not the parts (Simpson's paradox).
- The source system changed its export format.

## Customer and guest experience

- Expectation set before arrival differs from what is delivered (listing copy, photos, messages).
- Hand-off failure between teams (reservations → housekeeping → maintenance).
- A single recurring defect drives most of the negative reviews.
- Message timing wrong — sent too early, too late, or in the wrong language.
- Review score change driven by a channel or segment mix shift.

## Sales, outreach and partnerships

- Wrong ideal customer profile; message is fine, audience is wrong.
- Deliverability: emails land in spam, domain not warmed, links blocked.
- Offer unclear or with no next step.
- Follow-up sequence too short or missing.
- Decision-maker not reached; message stops at a gatekeeper.

## Product and UX

- Users do not reach the feature (discovery problem), not that they reject it.
- Onboarding step with a large drop-off.
- Metric instrumented wrongly or event fired twice.
- Seasonality or an external event mistaken for a product effect.
- Performance regression on one device or browser.

## Design systems

- Tokens defined but bypassed by hard-coded values.
- Components duplicated with small variations; no single source.
- Dark/light theme or responsive breakpoints not covered by the tokens.
- Documentation lags the component library.

## Prompts and AI workflows

- Instruction ambiguous or contradicted elsewhere in the prompt.
- Missing example of the edge case that fails.
- Context too long; the key instruction is buried or truncated.
- Model too small for the reasoning required — or a larger model over-interprets.
- Output format not specified or not validated.
- A tool or connector returns a different shape than the prompt assumes.
- Upstream data changed; the prompt is fine.

## Software and integrations

- API version, auth token or permission changed or expired.
- Pagination or rate limit silently truncates results.
- Retry creates duplicates (non-idempotent write).
- Schema change in one system not propagated to the other.
- Environment difference: works locally, fails in production (secrets, network, versions).
- Race condition: order of events not guaranteed.
