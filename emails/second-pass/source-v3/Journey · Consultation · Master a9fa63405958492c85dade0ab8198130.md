# Journey · Consultation · Master

## Spec

| Field | Value |
| --- | --- |
| **Object** | Contact — enrolled from the associated Deal |
| **Trigger** | Deal stage = Consultation completed — **build the deal-stage trigger first (order-of-ops item 8); the journey is inert without it** |
| **Branch** | None — single track C-0 → C-4 |
| **Re-enrolment** | On — a new consultation restarts the ladder from C-0 |
| **Hard exit** | Order placed → exit immediately, hand to Post-Purchase Master |
| **Silent exit** | No order after C-4 → newsletter audience. **Never Win-Back** — non-buyers have no last-order date |
| **Priority** | Cart Recovery outranks J5 · frequency cap (2 marketing emails per contact per 7 days) applies |
| **Subscription** | C-0 → One to One (Sales channel) · C-1…C-4 → News & Offers (Marketing) |

---

## Why this journey exists

The legacy Post-Consultation Nurturing sequence pitched the **Continuity Plan** — a post-purchase construct — at people who had never placed an order. Wrong framing for the moment: after a consultation the contact has a spec and a quote, but no experience of the product yet.

J5 replaces it with pre-purchase framing: **recap → objections → spec confidence → soft incentive → founder close.** C-0 salvages the token-driven structure from the legacy Consultation Recap Master (deal tokens resolve currency and spec — one email instead of seven variants). Everything else is written new, pre-purchase.

Blueprint rows live in [emails_master](https://app.notion.com/p/831f4e0d84e0831992d481ae881cfede?pvs=21) under Series **J5 · Consultation · Master**.

---

## Replacement — 5 Emails

### C-0 · Consultation Recap · Day 0 · One to One (Sales)

**Subject:** Your consultation recap and recommended spec

**Preview:** Everything we discussed, in one place — take your time with it.

**Notes:** A working document, not marketing — their situation, the recommended spec with reasoning, the quote, the production timeline, and the guarantee. Deal tokens drive currency and spec. Proof: one optional testimonial only.

---

### C-1 · Objections Answered · Day 2 · News & Offers

**Subject:** The three questions everyone asks before their first order

**Preview:** Will it look real, will it hold, and what happens if it's wrong.

**Notes:** Trust strip + testimonial at the objection moment (proof-by-intent). Same three answers that carry CR-2 — this is the consultation-side twin.

---

### C-2 · Spec Confidence · Day 6 · News & Offers

**Subject:** Your shortlist, side by side

**Preview:** The trade-offs between the options we discussed — in one table.

**Notes:** For a considered purchase, spec doubt is a bigger blocker than price. This email settles the shortlist with an honest comparison and repeats the unchanged quote.

---

### C-3 · Soft Incentive · Day 12 · News & Offers

**Subject:** Something to make the first order easier

**Preview:** A small discount, live for one week — no pressure attached.

**Notes:** [OFFER — confirm before send: FIRSTFIT10 · 10% off the first system · valid 7 days.] Promo code + countdown + testimonial at the offer moment (proof-by-intent).

---

### C-4 · Founder Close · Day 18 · News & Offers

**Subject:** Where I'll leave it

**Preview:** One honest question, then I'll stop nudging.

**Notes:** T1 founder note — 3 modules, reply-driven, no pressure, no proof modules. After C-4 with no order, the contact moves to the newsletter audience and this journey never re-contacts them.