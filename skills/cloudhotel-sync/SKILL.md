---
name: "cloudhotel-sync"
description: "After a booking-reconciliation workbook is verified, check and correct CloudHotel (Welcome PMS / Netera) reservations so villas, dates and totals incl. TAKK match the file's host payout."
---

# CloudHotel sync (after booking-reconciliation)

Run `booking-reconciliation` first. The verified Master (villa, dates, guest, channel, ref, host payout) is the source of truth. Full worked example: project doc `claude/Reconciliation_CloudHotel_Methodology.md` (Living Moments and Versanto, Aug-Sep 2026).

## Scope (owner rule)
- **No fixed or default timeframe.** Each request can give a different period. Use exactly the dates in that request; if none are given, ask. Never reuse an earlier period.
- Only check and correct bookings whose **check-in falls inside the requested period**. Ignore stays that check in before or after it, even if they overlap it.
- **Agent filter:** when asked about one agent (Booking.com, airbnb2, Guesty, EXPEDIA...), filter CloudHotel `agent` and the Master Channel to that agent only and leave the others untouched.
- State the hotel, period and agent filter at the top of every report.

## Hard rules
- CloudHotel has NO file import. Only Guesty sync, manual Reservations -> New, or a bulk load by Netera support (211 500 7007).
- Never delete or wipe a period. Receipts (APY/TAKK) go to myDATA; the Guesty sync re-pushes. Deleting is the owner's action; cancellations need an explicit yes per booking.
- Target rule (owner decision), with Master column letters:
  - **Airbnb: CloudHotel total = GROSS earnings (column H). TAKK is included inside the gross**, so in the edit form enter Revenue = Gross - TAKK. Never use the net payout.
  - Booking.com/Expedia: total = Host payout (column K) = full guest price incl. VAT, city tax and fees, before commission.
  - TravelNest: the TravelNest file amount.
  - Direct/website/Agoda: Guesty host payout (column K).
- Status codes: **1 = cancelled. 5 = IN-HOUSE (checked in)** - NOT checked out and NOT locked. While in-house the Edit button is hidden.
  - To edit an in-house reservation (owner asks, usually on the check-in date): Front Desk (Dashboard) -> Inhouse grid -> click the row's ▶ arrow -> **Undo Checkin** -> YES. It moves back to Checkins and Edit reappears. Then correct the revenue.
  - Check the PMS hotel date in the header first (e.g. "Sat 1/8/26").
- Pick the right hotel in the CloudHotel header selector first (e.g. "Living Moments", "Milestone Villas"). A hotel can contain units from other owners; stay inside the Guesty listings.

## Read CloudHotel (read-only) in the built-in browser
1. Plan page: hook XHR for `api/ReservationRooms/getPlanReservations/{hotelId}/{from}/{to}`, then click -14 and +21 repeatedly to cover the period. Each item has the guest, arrival/departure, per-day euro and room ID.
2. Map room IDs to villas by matching known guests.
3. Reservation list (Reservations -> List, Syncfusion grid): `document.querySelector('.e-grid').ej2_instances[0]`; tick radio `all` (`in` = in-house); loop with `goToPage` and read `currentViewData`.
   - Paging is unstable while the grid refreshes: wait ~2.5s per page, do two passes, dedupe by `aa`, and confirm the count equals `pageSettings.totalRecordsCount`.
   - Dates come in UTC (21:00 previous day): add 3h before filtering by check-in.
   - Useful fields: aa, guest, agent, arrival, departure, roomNumbers, amount (= revenue, without tax), reference, otaProviderResID, actualStatus.
   - `otaProviderResID` = Guesty reservation ID; match on it, because Booking.com codes can differ between Guesty and CloudHotel.
   - If it is null, the booking was typed by hand.
   - If it points to a Guesty inquiry (an Airbnb row with no HM code), it is an unconfirmed inquiry pushed as a reservation; the owner should cancel it.
4. Per reservation (selectRow, then wait until the panel shows `Nr\n{aa}`), read Revenue, `Tax: X`, the "Tax Included" flag and Balance.
   - Total = revenue if Tax Included, else revenue + tax.
   - Run long loops as a background async and poll; each JS call has a 45s limit.
   - Recompute the page count on every search, retry the select, and always read back.

## Compare
- Join the Master to CloudHotel on Guesty ID (otaProviderResID), falling back to villa + check-in + check-out for hand-typed rows.
- Report:
  - missing in CloudHotel (including confirmed bookings that disappeared since the last run)
  - extra in CloudHotel
  - same-villa overlaps (calendar-day granularity)
  - total diffs over EUR 0.005 against the target rule above
- For conflicts, give the owner the evidence (Guesty ID, amounts, manual vs synced) and let the owner decide. The Plan's "N overlaps" counter covers future dates only.

## Create a missing reservation (Reservations -> New)
1. Guest, then In date (Tab, Esc), then Remarks ("<channel> - added from verified reconciliation <date>").
2. Agent: the first click can open the Board list. Pick RO, reopen the agent list and select the option via find.
   - Booking.com -> Booking.com; Airbnb -> airbnb2; Expedia -> EXPEDIA; TravelNest/manual -> Guesty; website/direct -> none.
3. Set Nights LAST (editing Booked resets it to 2), then Booked, then Reference.
4. Click +<room type>, set Ad/Ch, open the room dropdown. If it says "No records found", type the first letters of the room name.
5. Revenue = the target total (Airbnb: gross). Tick "Environmental Tax is included in the price". Save.
6. Verify the panel shows: Revenue, Tax, "Tax Included: net ...".

## Correct an existing total
- Edit, then set Revenue, then click the save icon next to it ("Apply this as total amount"). It saves immediately.
- The edit form has no tax-included box, so enter Revenue = target - TAKK.
- To automate: set the `ejs-numerictextbox` instance value, then dispatch mousedown/mouseup/click on `i.fa-save`.
- Read back the Revenue and Tax after each edit (reload the list to confirm), and re-verify the whole batch at the end.

## Finish
Re-run the full read and compare until there are 0 diffs. Deliver:
- a created/corrected list with CloudHotel numbers
- in-house (status 5) items needing Undo Checkin, with the revenue they should have
- the inquiries to cancel
- the open owner decisions

Append new property-specific facts (room IDs, TAKK per night, agents, hotel name) to the methodology doc.