# Automation Assembly Guide — MailerLite UI

Automation steps/emails **cannot be created via the API** (only draft shells). Build each
automation in the MailerLite dashboard following the specs below (verbatim from the 4 journey
masters). For every email step: **Email step → Custom HTML editor → paste the full content of
`emails/<file>.html` → set Subject + Preview text from the ledger → save.**

Keep every automation **disabled** until: domain authenticated → seed test → Vincent's approval.

---

## J1 · Post-Purchase · Master — shell ID 196137612884313321

- **Trigger:** E-commerce → *Purchases a product* (Shopify). Re-enrolment: ON (a second order restarts the flow).
- **Suppression:** 48h hold on all other marketing for enrolled contacts.
- **Steps:**
  1. Email **PP-1** — immediately (Day 0)
  2. Wait 1 day → Email **PP-2**
  3. Wait 4 days → Email **PP-3** (Day 5)
  4. **PP-4 is event-driven, not a fixed delay.** MailerLite has no native "fulfilled" trigger → workaround: Shopify fulfilment webhook → small script sets subscriber field `estimated_delivery_date`/`tracking_number`/`carrier`/`tracking_url` and adds them to a "Fulfilled" group → J1 branch rule "in group Fulfilled" → send PP-4. (Until the sync exists, keep the PP-4 step disabled.)
  5. Wait until delivery +7d → Email **PP-5**
  6. Wait until delivery +21d → Email **PP-6**
  7. Wait until delivery +35d → Email **PP-7**
  8. **Branch on PP-7 link click:** positive ("It's going well") → wait 7 days → Email **PP-7b**. Negative ("It's not quite right") → exit journey + no marketing for 14 days.
- **Exit:** Day 45 → hand to J4 · Reorder.

## J2 · Cart Recovery · Master — shell ID 196137613572179554

- **Trigger:** E-commerce → *Abandoned cart* (native Shopify trigger; requires shop enabled — done 2026-08-18).
- **Re-enrolment:** ON, 7-day cooloff. **Hard exit:** order placed → exit immediately (hand to J1).
- **Steps:**
  1. Wait 4 hours → Email **CR-1**
  2. Wait 20 hours → Email **CR-2** (abandon +1d)
  3. Wait 1 day → Email **CR-3** (abandon +2d)
  4. Wait 2 days → Email **CR-4** (abandon +4d)
- **In CR-1, CR-2, CR-4:** after pasting the HTML, replace the dashed placeholder block with the native **E-commerce → Abandoned cart** block (or rebuild those three emails in the drag-&-drop editor using the HTML as the exact spec).
- **Browse-only branch (BR-1)** is out of the current scope — add later.

## J3 · Win-Back → Sunset — shell ID 196137614133167847

- **Trigger:** Segment entry — *last order > 180 days ago AND no email engagement in 90 days*
  (segment on the Shopify-synced last-order field + MailerLite engagement).
- **Re-enrolment: OFF. One win-back attempt per contact, ever.**
- **Steps:**
  1. Email **WB-1** — immediately (Day 0)
  2. Wait 7 days → Email **WB-2**
  3. Wait 7 days → Email **WB-3**
  4. Wait 7 days → Email **WB-4**
  5. **Sunset action (mandatory, not optional):** wait 7 more days → condition *no opens/clicks in this automation* → **remove from all marketing groups** (the sunset). *Without this step the promise in WB-4's first line is a lie.*
- **Exit — engaged:** any open or click → exit, return to normal marketing.

## J4 · Reorder · Master — shell ID 196137614701496127

- **Prerequisite (master's own rule):** the "days since last order" / due-date fields must exist
  first → the Shopify→MailerLite field-sync script. Nothing here works without it.
- **Trigger:** `days_since_last_order` = 45 (or segment on synced delivery date), delays keyed off delivery date.
- **Branches:** consumables buyer → RO-2, RO-5 · system owner → RO-3, RO-4, RO-6 · both → full ladder.
- **Steps:**
  1. Delivery +45d → Email **RO-1** (all)
  2. +60d → Email **RO-2** (consumables)
  3. +90d → Email **RO-3** (system)
  4. +110d → Email **RO-4** (system)
  5. +125d → Email **RO-5** (consumables) — **exclude the plan-customers group (132 contacts)** (master rule: never pitch a plan to someone already on one)
  6. +140d → Email **RO-6** (all)
- **Exit:** any order → exit and re-enter J1. **Silent exit:** no engagement 7 days after RO-6 → hand to J3 · Win-Back → Sunset.

---

## After assembly (gates, in order)

1. Domain authenticated (DKIM/SPF green in Domains tab).
2. Field-sync script live; test subscriber shows real values for all 18 fields.
3. Send each email as a test to Vincent + seed list; verify merge fields, links, images, mobile.
4. Vincent approves each journey explicitly → enable that automation only.
5. Watch first 50 sends per journey before calling it done.

