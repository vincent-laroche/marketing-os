# Journey · Post-Purchase · Master

## Spec

| Field | Value |
| --- | --- |
| **Object** | Contact |
| **Trigger** | Deal moves to Closed Won *or* Shopify order created |
| **Re-enrolment** | On — a second order restarts the flow |
| **Suppression** | Suppression — Master, plus a 48h hold on all other marketing |
| **Key change** | Days 4–7 driven by the **fulfilment event**, not a fixed delay |
| **Exit** | Day 45 → hand to Journey · Reorder · Master |

---

## Before — The Collision (6 workflows → 24 slots → 13 archived)

**Day 0: six simultaneous emails.** Order confirmation ×3 (one live, two archived) + delivery quickstart + shipping update + review request — all before the item left the workshop.

**Day 1–2:** Two copies of the same "system is on the way" email queued a day apart.

**Logical inversion:** "Did your system arrive safely?" fired day 4–5, but "Your system is on the way" fired day 1–2. Fulfilment takes longer than either.

A customer who ordered received **24 emails in 29 days**, including a review request on the day they bought.

| Day | Old workflow | Email | State | Decision |
| --- | --- | --- | --- | --- |
| +0d | New Customer — Compact | New Customer 1of4 — Order Confirmation | Live | Keep → PP-1 |
| +0d | Onboarding Post-Purchase | New Customer 1of8 — Order Is Confirmed | Archived | Delete |
| +0d | Onboarding — Full Series | New Customer 1of8 — Order Is Confirmed | Archived | Delete |
| +0d | Post-Purchase — Care | Post-Purchase 1of3 — Delivery QuickStart | Live | Keep → PP-4 |
| +0d | Shipping Updates | Shipping 1of2 — What Happens Next | Live | Keep → PP-2 |
| +0d | Review Request | Review Request 1of2 — Review Request | Live | Keep → PP-7 |
| +1d | New Customer — Compact | New Customer 2of4 — Prep Guide | Live | Fold into PP-2 |
| +1d | Onboarding Post-Purchase | New Customer 3of8 — System Is On The Way | Archived | Delete |
| +1d | Onboarding — Full Series | New Customer 2of8 — Preparation Guide | Archived | Delete |
| +2d | Onboarding — Full Series | New Customer 3of8 — System Is On The Way | Archived | Delete |
| +3d | Post-Purchase — Care | Post-Purchase 2of3 — Maintenance Schedule | Live | Keep → PP-5 |
| +3d | Shipping Updates | Shipping 2of2 — Mid Wait CheckIn | Live | Keep → PP-3 |
| +3d | Review Request | Review Request 2of2 — UGC Photo Request | Live | Keep → PP-7b |
| +4d | New Customer — Compact | New Customer 3of4 — Care Instructions CrossSell | Live | Keep → PP-6 |
| +4d | Onboarding Post-Purchase | New Customer 4of8 — Did System Arrive Safely | Archived | Delete |
| +5d | Onboarding — Full Series | New Customer 4of8 — Did System Arrive Safely | Archived | Delete |
| +7d | Onboarding Post-Purchase | New Customer 5of8 — Week 1 Care Tips | Archived | Delete |
| +8d | Onboarding — Full Series | New Customer 5of8 — Week 1 Care Tips | Archived | Delete |
| +10d | Post-Purchase — Care | Post-Purchase 3of3 — Longevity Tips | Draft | Fold into PP-5 |
| +11d | New Customer — Compact | New Customer 4of4 — CheckIn Review Request | Live | Duplicate of PP-7 |
| +14d | Onboarding Post-Purchase | New Customer 6of8 — Week 2 Maintenance Routine | Archived | Delete |
| +15d | Onboarding — Full Series | New Customer 6of8 — Week 2 Maintenance Routine | Archived | Delete |
| +22d | Onboarding — Full Series | New Customer 7of8 — Styling And Removal | Archived | Delete |
| +29d | Onboarding — Full Series | New Customer 8of8 — Review & Next Steps | Archived | Delete |

---

## Replacement — 7 Emails

### PP-1 · Day 0 · Order & Shipping Updates

**Subject:** Your order is confirmed, {{ firstname }}

**Preview:** Here's exactly what happens between now and the day it arrives.

**Replaces:** New Customer 1of4 (rewrite content, keep record) + two archived duplicates.

**Why it changes:** the original promised nothing specific. Setting the production expectation here prevents the "where is my order" ticket on day six.

---

### PP-2 · Day 1 · Order & Shipping Updates

**Subject:** Getting ready for your system — a short prep guide

**Preview:** Three things worth doing before it arrives. Ten minutes, total.

**Replaces:** New Customer 2of4 (Prep Guide) + Shipping 1of2 (214989746992) — merged because both were "here's what to expect" sent a day apart.

---

### PP-3 · Day 5 · Order & Shipping Updates

**Subject:** Your system is on the bench

**Preview:** A look at what's actually happening to it right now.

**Replaces:** Shipping 2of2 — Mid Wait CheckIn (214989746995).

**Why it earns its place:** the only email in the sequence doing brand work. It justifies the wait and the price.

---

### PP-4 · On fulfilment event (not a fixed delay) · Order & Shipping Updates

**Subject:** It's shipped — tracking inside

**Preview:** Plus the quick-start steps for the day it lands.

**Replaces:** Post-Purchase 1of3 — Delivery QuickStart (214989746974).

**Critical change:** originally fired at +0d, before the item shipped. Must be re-triggered off the fulfilment webhook.

---

### PP-5 · Delivery + 7 days · Hair Care Guidance

**Subject:** Your 30 / 60 / 90 day maintenance calendar

**Preview:** What to do, and when, so it lasts as long as it should.

**Replaces:** Post-Purchase 2of3 — Maintenance Schedule (214989746977), with Post-Purchase 3of3 (Longevity Tips, draft) folded in.

---

### PP-6 · Delivery + 21 days · Hair Care Guidance

**Subject:** The four products that actually matter

**Preview:** Not a bundle pitch — the short list, and what to skip.

**Replaces:** New Customer 3of4 — Care Instructions CrossSell (214987971504).

**Positioning:** filed under Hair Care Guidance, not News & Offers — survives a promotional unsubscribe.

---

### PP-7 · Delivery + 35 days · Customer Service Communication

**Subject:** Honestly — how's it going?

**Preview:** One question. Good or bad, I want the real answer.

**Branch:** Positive click → PP-7b (UGC request, 214987971586) after 7 days. Negative click → service ticket + exit journey, no marketing for 14 days.

**Replaces:** Review Request 1of2 (214989746989) and New Customer 4of4 CheckIn (duplicate of PP-7).