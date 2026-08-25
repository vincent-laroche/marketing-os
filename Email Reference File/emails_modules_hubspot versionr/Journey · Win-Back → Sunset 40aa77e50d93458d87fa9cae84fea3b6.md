# Journey · Win-Back → Sunset

## Spec

| Field | Value |
| --- | --- |
| **Object** | Contact |
| **Trigger** | Last order > 180 days ago **AND** no email engagement in 90 days |
| **Re-enrolment** | **Off.** One win-back attempt per contact, ever. |
| **Exit — engaged** | Any open or click → exit, reset engagement, return to normal marketing |
| **Exit — silent** | After WB-4 + 7 days with no engagement → **set marketable status false** |
| **Why it matters** | This is the only mechanism that stops list decay compounding |

---

## Before — The Collision (3 workflows + Sunset → 11 slots → 5 archived)

**Win-Back — Final Push sends the exact same two email records as Win-Back — Re-engagement.** Not similar emails: identical content IDs — 211345979664 on day 0 and 211345977476 on day 21.

If both are ever on, a lapsed customer receives "Just checking in — Vincent here" **twice on the same day**, and "Last email from us — we respect your inbox" **twice on the same day**, three weeks later. It is a promise not to email, delivered twice.

**And the ladder ends nowhere.** Sunset — Unengaged has zero actions, so after "last email from us", the contact stays fully marketable and receives the next newsletter.

| Day | Old workflow | Email | State | Decision |
| --- | --- | --- | --- | --- |
| +0d | Win-Back — Re-engagement | Win-back 1of4 — Just Checking In | Live | Keep → WB-1 |
| +0d | Win-Back — Final Push | Win-back 1of4 — Just Checking In | Live | Same email ID |
| +0d | Win-Back — Promotional Offer | Win-back 1of4 — Soft CheckIn | Archived | Delete |
| +7d | Win-Back — Re-engagement | Win-back 2of4 — What's New | Live | Keep → WB-2 |
| +7d | Win-Back — Promotional Offer | Win-back 2of4 — Whats New | Archived | Delete |
| +14d | Win-Back — Re-engagement | Win-back 3of4 — Specific Offer | Live | Keep → WB-3 |
| +14d | Win-Back — Promotional Offer | Win-back 3of4 — Reengagement Offer | Archived | Delete |
| +21d | Win-Back — Re-engagement | Win-back 4of4 — Last Email From Us | Live | Keep → WB-4 |
| +21d | Win-Back — Final Push | Win-back 4of4 — Last Email From Us | Live | Same email ID |
| +21d | Win-Back — Promotional Offer | Win-back 4of4 — Final Goodbye | Archived | Delete |
| +28d | Win-Back — Promotional Offer | Win-back Week 12 — Reengagement Push | Archived | Delete |
| — | Sunset — Unengaged | — zero actions — | Empty | Build it |

---

## Replacement — 4 Emails

### WB-1 · Day 0 · News & Offers

**Subject:** Checking in — Vincent here

**Preview:** No offer attached. Just wondering how you got on.

**Keep record:** Win-back 1of4 (211345979664).

**Deliberate:** no button and no offer — reply-only by design. The first win-back email that asks for money confirms the reason they left. A reply re-establishes engagement, which is the actual goal.

---

### WB-2 · Day 7 · News & Offers

**Subject:** What's changed since you last ordered

**Preview:** Three things, briefly. Some of them fix the reasons people leave.

**Keep record:** Win-back 2of4 (214988061042).

**Structure:** each of the three items maps to a common churn reason — durability, delivery anxiety, maintenance fatigue.

---

### WB-3 · Day 14 · News & Offers

**Subject:** 20% off, if you want to try again

**Preview:** Your previous specification is saved — reordering takes a minute.

**Keep record:** Win-back 3of4 (214990267465).

**Requires:** last_order_specification populated. If empty, drop the personalisation line rather than shipping an empty token.

---

### WB-4 · Day 21 · then Sunset action at +7d · News & Offers

**Subject:** Last email from us

**Preview:** We'll stop here unless you tell us otherwise.

**Keep record:** Win-back 4of4 (211345977476).

**This is the only email in the portal that must be followed by an action, not a delay.** Build the Sunset step: wait 7 days → if still no engagement → set hs_marketable_status = false. *Without it the promise in the first line is a lie.*