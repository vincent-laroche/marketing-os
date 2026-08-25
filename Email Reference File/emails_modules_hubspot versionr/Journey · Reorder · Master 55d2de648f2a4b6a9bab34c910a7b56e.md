# Journey · Reorder · Master

## Spec

| Field | Value |
| --- | --- |
| **Prerequisite** | Turn on **Days Since Last Order** and **Due Date Calculator** first. Nothing here works without them. |
| **Object** | Contact |
| **Trigger** | days_since_last_order = 45, then delays keyed off delivery date |
| **Branch** | Consumables buyer → RO-2, RO-5 · System owner → RO-3, RO-4, RO-6 · Both → full ladder |
| **Exit** | Any order → exit and re-enter Post-Purchase Master |
| **Silent exit** | No engagement by day 140 → hand to Win-Back → Sunset |

---

## Before — The Collision (4 workflows → 13 slots → 6 emails)

**Four flows on an identical clock — day 0, day 7, day 14.** The result: four emails on day 0, four on day 7, four on day 14 and one on day 21 — **13 emails in three weeks**, all saying "buy again".

**They contradict each other.** Day 0 simultaneously tells the customer their supplies are running low, their system is at its midpoint, their renewal is 14 days away, and they should buy a care kit. *Four different implied positions in the lifecycle, on the same morning.*

**All four are keyed to a placeholder trigger** — and the two workflows that would compute the real date (Data — Reorder — Due Date Calculator and Data — Reorder — Days Since Last Order) are both **switched off**. There is no date to key a date-driven flow to.

| Day | Reorder — Maintenance | Reorder — Replacement | Reorder — Renewal | Cross-Sell — Care |
| --- | --- | --- | --- | --- |
| +0d | Friendly Reminder | Mid Cycle Care Check | Renewal 14 Day Heads Up | Care Kit Intro |
| +7d | Subscription Pitch | Replacement Nudge | Renewal 7 Day Urgency | Problem Solution |
| +14d | Last Reminder / New Products | Loyalty Hook | Renewal Final Confirmation | Bundle Offer |
| +21d | — | — | — | Cross Sell Accessories |

---

## Replacement — 6 Emails

### RO-1 · Delivery + 45 days · Hair Care Guidance

**Subject:** Six weeks in — how's it holding up?

**Preview:** Two things to check, and what they tell you.

**Keep record:** Reorder 1of3 — Mid Cycle Care Check (214990267468).

**Role:** the only non-selling email in this journey. It establishes that the reorder emails which follow are calendar-based advice, not random pitching.

---

### RO-2 · Delivery + 60 days · consumables branch · Hair Care Guidance

**Subject:** You're about due for supplies

**Preview:** Based on when you last ordered, not a guess.

**Keep record:** Reorder Subscription 1of3 — Friendly Reminder (214989746983).

**Requires:** days_since_supply_order from the Data workflows. *Do not send with an unresolved token.*

---

### RO-3 · Delivery + 90 days · system branch · Hair Care Guidance

**Subject:** Your replacement window is opening

**Preview:** Not urgent yet — but worth knowing the lead time.

**Keep record:** Reorder 2of3 — Replacement Nudge (214988061045), retimed from an arbitrary +7d to a real 90-day milestone.

**The rotation argument is the highest-value idea in this journey** — it doubles order frequency and is genuinely better for the customer.

---

### RO-4 · Delivery + 110 days · system branch · News & Offers

**Subject:** Same spec, or change something?

**Preview:** Now's the moment to adjust density or base type.

**New email — replaces Renewal 3of4 — 7 Day Urgency (214988061048).**

The original applied a subscription-renewal deadline to a product with no renewal date. *Manufactured urgency on a considered purchase reads as a scam*; a spec conversation converts better and generates fit intelligence.

---

### RO-5 · Delivery + 125 days · consumables branch · News & Offers

**Subject:** Stop thinking about supplies entirely

**Preview:** Auto-reorder on your schedule. Cancel any time.

**Keep record:** Reorder Subscription 2of3 — Subscription Pitch (214989746986).

**Suppression:** must exclude Marketing Email Exclusion — Plan Customers (132 contacts). *Pitching a plan to someone already on one is the clearest possible signal that nobody is watching.*

---

### RO-6 · Delivery + 140 days · final · News & Offers

**Subject:** A returning-customer price, while it's useful

**Preview:** Last reorder note before I leave you alone.

**Keep record:** Reorder 3of3 — Loyalty Hook (214989747033).

**Exit:** no engagement 7 days after this → hand to Win-Back → Sunset. This is the join between the two journeys, and the reason neither loops forever.