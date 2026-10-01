---
name: "cloudhotel-property-runbook"
description: "Run or resume CloudHotel invoicing for any Arivia property (new or existing): build Master, sync CloudHotel, daily invoice loop, audit, handover. Use for 'start/resume a property' or 'next chat prompt'."
---

# CloudHotel property runbook (Arivia)

One fixed procedure for every property. Property-specific facts live ONLY in the **property card** (`claude/<Prop>_Card.md` in project MATCH RESERVATIONS) and `daily_check/properties.json`. Never re-derive what the card already says. Deep background (read only if a step fails): `claude/Reconciliation_CloudHotel_Methodology.md`, `claude/CloudHotel_Daily_Invoicing_Workflow.md`, skills `booking-reconciliation`, `cloudhotel-sync`.

Working folder (user's computer): `MATCH RESERVATIONS/` — run scripts there with device_bash.

## 0. Start of every chat (2 minutes, in this order)
1. Read the property card → section **Resume point**. Read nothing else unless needed.
2. Chrome: `tabs_context_mcp`. Owner logs in; never type passwords. Normal Chrome only.
3. CloudHotel header: select the card's **hotel name** in the selector; confirm header hotel + hotel date = card. If different → stop and tell the owner.
4. Guesty = Open API only (`guesty_refresh.sh 23`, token reused ≤23h, max 5/day). Never the old GUESTY connector.
5. If card status = NEW → Phase 1. If Master approved but not synced → Phase 2. Else → Phase 3 at the resume date.

## Owner rules (all properties, fixed)
- Invoice total (ΑΠΥ + ΤΑΚΚ) = OTA amount incl. ΤΑΚΚ; ΤΑΚΚ split out, never added. ΤΑΚΚ €2/night unless card says otherwise.
- Targets: **Booking.com = card `booking_target`** (`payout` → extranet Total price = Master K; `gross` → extranet Price = Master H). Airbnb = CSV Gross earnings = Master H. Expedia / Agoda / TravelNest / Direct / Website = Master K.
- Always ΑΠΥ to the guest. Bank Transfer for everything. Delete every Guesty-synced deposit line. Owner saves PDFs.
- Jev ALWAYS ON: start of each hotel day, before every Issue, before every check-in.
- Never Night-Audit today's real date without the owner saying the day is over.
- Airbnb rows without an HM code = inquiries: never check in / invoice; list for owner deletion.
- Stop only for: name, unit, dates, missing/extra booking, total that can't be fixed, anything irreversible not pre-approved. Everything else: fix and continue.
- Never create fake dates/notes on tax documents (refuse; offer the passant with real dates).

## Phase 1 — Master (read-only on CloudHotel)
1. Find listings: Guesty listings_all → filter by the card's `guesty_tag`. Record listing IDs in the card.
2. Pull reservations (copy `guesty_recon/dayone/pull.py` → `guesty_recon/<prop>/pull.py`, change tag). Window = card period ± 1 month.
3. Ask the owner for the OTA files the card lists (BC extranet .xls — check Unit type first; Airbnb earnings CSV; Expedia Partner Central; TravelNest). Save in `ota_files/<Prop>_*`.
4. Build `<Prop>_Reconciliation_<period>.xlsx` by copying `guesty_recon/dayone/build_master.py` (Summary, Master, one sheet per unit, Excluded; formulas; LibreOffice recalc). Every BC row: Total price = K and Price = H checked to the cent; Airbnb Gross = H.
5. Report to owner: counts per channel, cancelled, inquiries, overlaps (calendar-day granularity), missing, unit conflicts, amount conflicts → owner approves. Write the approval into the card.

## Phase 2 — CloudHotel = Master (fix only what the owner approves)
1. Add property to `daily_check/properties.json` (backup `.bak_<date>_<prop>` first): label, guesty_tag, master_file, cloudhotel_hotel, takk_per_night, booking_target, villa_aliases, room IDs, agent IDs. Create `daily_check/<p>_c.py` (copy `dy_c.py`, set hotel id + name) and `<p>_day.sh` (copy `dy_day.sh`).
2. Read Plan (capture hook below) over the whole period → diff vs Master: missing / extra / wrong unit / wrong dates / wrong total / inquiries / deposits.
3. Present the fix list → owner approves per line → apply → read back → log every change in `guesty_recon/<prop>/cloudhotel_fixes_<prop>.log`.
   - Not checked in: Reservations → List → Edit → Revenue = target − ΤΑΚΚ → save icon.
   - In-house: In House → Per Day rates (closed nights keep old rate; put difference on open nights) → Update; or fix in Billing at checkout.
   - Missing: Reservations → New (fill order in methodology doc; tick "Environmental Tax included").
   - Agent changes on in-house bookings: owner does it (In House → Agent → Update) — classifier blocks Claude.

## Phase 3 — Daily loop (per hotel day, exact order)
A. **Night Audit** (only for past dates): Night Audit menu → wait ~10 s → `find` "blue Night Audit button element (type button) in main content" → confirm the list date → click → header date +1.
B. **Capture Plan**: inject hook (below), click Plan, wait 8 s, read rows for the hotel date. If the hook is denied by the permission filter → do NOT work around; verify on Billing vs Master and ask the owner before any Issue.
C. **Jev**: `cd daily_check && python3 <p>_c.py <<'EOF' | ./<p>_day.sh YYYY-MM-DD` (paste capture) / re-run on saved snapshot: `./<p>_day.sh <date> < /dev/null`. Exit 1 = no movements → go to A. `[FIX]` on amount → fix Billing; on agent only → note, continue; anything else → stop.
D. **Each departure**: Billing → click guest (click again if bill empty) → delete deposit lines → Charges = target (fix: tick only Arrangement lines → Edit → Νέα τιμή = (target−ΤΑΚΚ)/nights; rounding on one night) → Bank Transfer radio → Paid by → Balance 0 → Jev re-run → Invoice → ⊗ (removes BC/Airbnb agent; form becomes Απόδειξη Παροχής Υπηρεσιών) → Invoice Name = First Last → country (BC → Booker country; else Guesty phone prefix; combobox: clear with End + Backspace×20, type short name e.g. "USA", "Greece", click the list item; verify via `.e-combobox` ej2 instance `.text`) → tick Ταυτόχρονη ΤΑΚΚ → myDATA ✅, email ☐ → verify form → Issue once → wait ~10 s → invoice view shows two docs with MARKs (never re-click Issue; if unsure, check Invoices list first) → log line → Front Desk ✈ → Yes.
E. **Each arrival**: Jev OK → Check-in page → click the guest row until the form shows the right **Reservation no.** (never WALK IN 666) → Check In / Check In (Dirty) → Front Desk Final = target.
F. Next day → A. On today's real date: finish movements, do NOT Night-Audit.

Log line format (`invoice_audit/invoices_log_<prop>.txt`):
`d/m|#res|First Last (CC, basis)|UNIT in–out|ΑΠΥ no|ΑΠΥ €|MARK|ΤΑΚΚ no|ΤΑΚΚ €|MARK|total|channel rule ✅ (notes)`

## Phase 4 — Audit when caught up
1. Script check on the log: ΑΠΥ/ΤΑΚΚ numbering continuous, MARKs unique 15-digit, ΑΠΥ+ΤΑΚΚ = total, total = Master (Airbnb H, else K / booking_target), ΤΑΚΚ = €2 × nights.
2. CloudHotel Invoices → Year → read pages (screenshot/zoom; page text can be stale) → every logged doc present, ✓ myDATA, balance 0; note the 2026 balance and explain it.
3. Completeness: every Master stay with checkout ≤ today invoiced; in-house list = Master.

## Phase 5 — Handover (every session end, in this order)
1. Validate (Phase 4 quick version). 2. Clear: remove cloud scratch only; never delete in the user's folder. 3. Save: update the property card (Resume point, open owner items, lessons) + `claude/<Prop>_Invoicing_Log.md`, commit copies to MATCH RESERVATIONS. 4. Résumé to the owner: done / state / next / owner items.

## Capture hook (inject after every full page load)
```js
if(!window.__chResp){window.__chResp=[];const oo=XMLHttpRequest.prototype.open,os=XMLHttpRequest.prototype.send;XMLHttpRequest.prototype.open=function(m,u){this.__u=u;return oo.apply(this,arguments)};XMLHttpRequest.prototype.send=function(){this.addEventListener('load',()=>{try{if(/getPlanReservations/.test(this.__u))window.__chResp.push({u:this.__u,s:this.status,t:typeof this.response==='string'?this.response:JSON.stringify(this.response)})}catch(e){}});return os.apply(this,arguments)};}
window.__chResp.length=0;document.querySelector('a[href="/reservations/nameplan"]').click();'ok'
```
Then (separate call, after ~8 s), with `hd` = hotel date:
```js
const hd='YYYY-MM-DD';const x=window.__chResp.filter(x=>x.s===200).pop();JSON.parse(x.t).filter(r=>r.arrival.slice(0,10)===hd||r.departure.slice(0,10)===hd).map(r=>[r.reservation.staticData.fullName.trim(),r.reservation.staticData.agentID||'',r.arrival.slice(0,10),r.departure.slice(0,10),r.nights,r.arrivalTimeStamp?1:0,r.departureTimeStamp?1:0,Math.round(r.reservationRoomsPerDay.filter(p=>p.dayIndex<r.nights).reduce((s,p)=>s+p.euro,0)*100)/100,(r.reservationRoomsPerDay[0]||{}).roomID,r.reservation.reservationID].join('|')).join('\n')
```
Never `await` inside the click call (renderer times out); split inject/click and read.

## Known gotchas
- Plan euro sums exclude ΤΑΚΚ; tax-included reservations show a spurious +ΤΑΚΚ FIX in Jev — Billing Charges are final.
- Guesty sync can revert a corrected revenue — re-check Charges before every Issue.
- Dropdown lists stay open after selection; a following click can land on a list item. Press Escape and verify the field before saving.
- Over €500 cash is refused — always Bank Transfer.
- Classifier may block: XHR hook, typing into agent dropdowns, JS numeric edits. Don't work around; hand to owner.
- Coordinates change with frame size (1456×817 vs 1512×799): always screenshot before clicking.
- Start a fresh chat every 2–3 hotel days (token cost); the card's Resume point makes this cheap.

## Property card template (`claude/<Prop>_Card.md`)
```
# <Property> — card
Status: NEW | MASTER APPROVED | SYNCED | INVOICING | CAUGHT UP
CloudHotel hotel: <exact selector name> · hotel id <uuid> · company/ΑΦΜ <..> · Drive PDF folder <..>
Guesty tag: <tag> · listings: <name id> …
Rooms (CloudHotel → Guesty): <code roomID → listing> …
Agents: <id → Booking.com / airbnb2 / Expedia / Guesty / none>
booking_target: payout|gross · ΤΑΚΚ €/night: 2 · Series: ΑΠΥ <..> ΤΑΚΚ <..>
Master: <file> (approved <date>) · OTA files: <..>
Property rules/decisions: <owner decisions with dates>
Open owner items: <..>
Resume point: hotel date <..> · last ΑΠΥ/ΤΑΚΚ <..> · in house <..> · next movements <..>
```