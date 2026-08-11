# Master Email Blueprints — Hair Solutions Co.
**Built 2026-07-28.** Structure and modules only — no copy.

Sources merged: the deep-research report (Klaviyo/Shopify/Mailchimp/HubSpot/Litmus/FTC/Baymard consensus), the 45-min video structural rules, the 85 live HubSpot emails, and module intel harvested from all 123 competing Notion rows before deletion.

---

## How to read

`●` **Non-negotiable** — the email fails its job without it.
`○` **Recommended** — include unless there's a reason not to.
`·` Not in this email.
`⚠` Module does **not exist** in the Atelier Zero library yet → see §Build Queue.

Every email also carries the **universal layer**, which is never listed in the matrices because it is always present: subject line, preheader, `Header - Centered logo`, live-text body (not image-trapped), one dominant CTA, mobile-safe single column, and `Footer - Standard` (or `Footer - Wide` / `Footer - Social` per family) carrying the postal address, unsubscribe, and permission reminder. Plain-text emails use `⚠ M11 Plain-text founder wrapper` instead of the branded header/footer.

**Three rules applied throughout**, taken from the research consensus:
1. The most specific context block sits nearest the top.
2. One dominant CTA per email, pointing at the exact next step.
3. Every later email in a flow must add something *new* — proof, education, help, urgency, or incentive — never a re-send of the first.

---

## The 26 top-level master series

Every embedded mini-series has been promoted. Nothing nests inside anything else.

| # | Master series | Emails | Was buried inside |
|---|---|---|---|
| 1 | Site Abandonment | 2 | — |
| 2 | Browse Abandonment | 4 | — |
| 3 | Cart Abandonment | 3 | — |
| 4 | Checkout Abandonment | 4 | — |
| 5 | Welcome — Lead Nurture | 5 | *(merged from two broken half-series)* |
| 6 | Newsletter Nurture — Subscriber Onboarding | 5 | — |
| 7 | Consultation — Recap | 1 + variants | — |
| 8 | Consultation — Follow-Up | 4 | — |
| 9 | New Customer Onboarding | 4 | — |
| 10 | Shipping Updates | 2 | — |
| 11 | Post-Purchase Care | 3 | — |
| 12 | Review Request | 2 | — |
| 13 | Cross-Sell — Care Kits | 3 | — |
| 14 | Reorder — Supplies Subscription | 3 | — |
| 15 | Reorder — System Replacement Window | 3 | — |
| 16 | Renewal — Continuity Plan | 4 | — |
| 17 | Win-back | 4 | — |
| 18 | Newsletter — Education | template | `Newsletter -- Always-on content` |
| 19 | Newsletter — Customer Story | template | `Newsletter -- Always-on content` |
| 20 | Newsletter — Offer / Promo | template | `Newsletter -- Always-on content` |
| 21 | Newsletter — Brand & Recap | template | `Newsletter -- Always-on content` |
| 22 | Newsletter — Product Launch | template | `Newsletter -- Always-on content` |
| 23 | Cross-Sell — Accessories (broadcast) | template | `Newsletter -- Always-on content` |
| 24 | Launch Day — Brand Relaunch | 2 (A/B) | — |
| 25 | Post-Launch Nurture | 4 | `Launch -- Brand relaunch` |
| 26 | Payment Recovery | 2 | — |
| — | Consent — Resubscribe | 1 | operational, no blueprint needed |

**Why the splits matter.** `Newsletter -- Always-on content` was holding six structurally different email types under one label — an education deep-dive and a 25%-off sale email have almost nothing in common at the module level. Likewise `Reorder` was conflating *consumable supplies running low* (predictable, replenishment logic) with *the system itself wearing out* (lifespan logic, higher ticket, needs base-type guidance). Those are different emails to different mental states and now have separate series.

---

# RECOVERY

## 1 · Site Abandonment
*Visited the site, did not view a product. Highest-funnel, lowest intent — orient, don't sell.*

| Module | E1 Browse Encouragement | E2 Personal Reminder |
|---|---|---|
| Hero - Text-led | ● | · |
| ⚠ M11 Plain-text founder wrapper | · | ● |
| Text - Opening *(acknowledge the visit)* | ● | ● |
| Grid - Collections (4) *(bestsellers / popular)* | ● | · |
| Product - 3-up grid | ○ | ○ |
| Text - Why it matters *(brand mission)* | ○ | ● |
| Testimonial | ○ | · |
| Text - Offer discount | ○ | ○ |
| Button - Primary CTA *(return to site)* | ● | ● |
| ⚠ M10 Support / help strip | ○ | ● |
| Photo - Founder note | · | ● |

**Timing:** E1 ~4h. E2 ~24h.
**Note:** E2 is deliberately the human-sounding plain-text follow-up to E1's branded email — the alternation rule from the video.

## 2 · Browse Abandonment
*Viewed a specific product. The exact viewed item must be at the top and the CTA must return them to that product page.*

| Module | E1 Product Reminder | E2 Related Products | E3 Discount Opener | E4 Last Chance |
|---|---|---|---|---|
| Hero - Text-led | ● | ● | ● | · |
| ⚠ M11 Plain-text founder wrapper | · | · | · | ● |
| ⚠ M3 Viewed product (dynamic) | ● | ● | ● | ● |
| Text - Opening | ● | ● | ● | ● |
| ⚠ M14 Dynamic product recommendations | · | ● | ○ | · |
| Product - 3-up grid | · | ● | ○ | · |
| Text - Why it matters *(product value prop)* | ○ | ● | · | · |
| Testimonial | ○ | ● | ○ | · |
| ⚠ M12 Review stars | ○ | ● | · | · |
| Text - Offer discount | · | · | ● | ● |
| ⚠ M9 Promo code block | · | · | ● | ● |
| ⚠ M8 Countdown / expiry | · | · | ○ | ● |
| Button - Primary CTA *(back to that product)* | ● | ● | ● | ● |
| ⚠ M10 Support / help strip | ○ | ○ | ○ | · |
| FAQ | · | ○ | · | · |

**Timing:** E1 ~4h · E2 ~24h · E3 ~48h · E4 ~72h.
**Progression:** reminder → proof + alternatives → incentive → urgency. Nothing repeats.

## 3 · Cart Abandonment
*Items in cart. Make resuming frictionless. The dynamic cart block is the whole email.*

| Module | E1 Gentle Reminder | E2 Value Reinforcement | E3 Urgency Incentive |
|---|---|---|---|
| Hero - Text-led | ● | ● | · |
| ⚠ M11 Plain-text founder wrapper | · | · | ● |
| ⚠ M1 Cart — dynamic line items | ● | ● | ● |
| Text - Opening | ● | ● | ● |
| List - Trust strip | ○ | ● | ○ |
| Text - Reassurance *(returns, guarantee)* | ○ | ● | ○ |
| Testimonial | · | ● | ○ |
| ⚠ M12 Review stars | · | ○ | · |
| List - Questions *(objection handling)* | · | ● | · |
| Text - Offer discount | · | · | ● |
| ⚠ M9 Promo code block | · | · | ● |
| ⚠ M8 Countdown / expiry | · | ○ | ● |
| Button - Primary CTA *("Return to cart")* | ● | ● | ● |
| ⚠ M10 Support / help strip | ● | ● | ○ |
| FAQ | ○ | ○ | · |

**Timing:** E1 1–4h · E2 24h · E3 48–72h.
**⚠ Blocker:** `M1 Cart — dynamic line items` does not exist. All three emails are currently flat rich-text. This is the single highest-value module to build — it gates the entire series.

## 4 · Checkout Abandonment
*Started checkout, gave an email, left. Baymard's abandonment drivers are the module list: extra costs, delivery doubt, trust, forced account creation, form friction.*

| Module | E1 Checkout Reminder | E2 Trust + Social Proof | E3 Discount Incentive | E4 Last Chance (Text) |
|---|---|---|---|---|
| Hero - Text-led | ● | ● | ● | · |
| ⚠ M11 Plain-text founder wrapper | · | · | · | ● |
| ⚠ M2 Resume-checkout summary | ● | ● | ● | ● |
| Text - Opening | ● | ● | ● | ● |
| Text - Reassurance *(cost transparency, no hidden fees)* | ● | ● | ○ | ○ |
| List - Trust strip *(secure payment, guarantee)* | ● | ● | ○ | · |
| Timeline *(delivery expectation)* | ● | ○ | · | · |
| Testimonial | · | ● | ○ | · |
| ⚠ M12 Review stars | · | ● | · | · |
| Stat bars | · | ○ | · | · |
| Text - Offer discount | · | · | ● | ● |
| ⚠ M9 Promo code block *(auto-apply)* | · | · | ● | ● |
| ⚠ M8 Countdown / expiry | · | · | ○ | ● |
| Button - Primary CTA *("Complete checkout")* | ● | ● | ● | ● |
| ⚠ M10 Support / help strip | ● | ● | ● | ● |
| FAQ *(shipping, returns, payment)* | ● | ○ | · | · |

**Timing:** E1 1h · E2 24h · E3 48h · E4 72h.
**Difference from Cart:** checkout is friction-focused, not desire-focused. Lead with reassurance and cost transparency, not with product appeal.

---

# ACQUISITION & NURTURE

## 5 · Welcome — Lead Nurture
*Merged from the two broken half-series. Downloaded the guide / submitted the lead form.*

| Module | E1 Welcome + Resource | E2 Education Hook | E3 Base Types | E4 Social Proof | E5 Soft Close |
|---|---|---|---|---|---|
| Hero - Text-led | ● | ● | ● | ● | · |
| ⚠ M11 Plain-text founder wrapper | · | · | · | · | ● |
| Text - Opening *(true welcome)* | ● | ● | ● | ● | ● |
| ⚠ M9 Promo code block *(promised incentive)* | ● | ○ | · | ○ | ● |
| Text - Offer discount | ● | ○ | · | ○ | ● |
| Text - Why it matters *(1–2 differentiators)* | ● | ● | ○ | · | ○ |
| Text - Next step *(expectation setting)* | ● | · | · | · | · |
| Photo - Founder note | ○ | ● | · | · | ● |
| Text - Founder pillars | · | ● | · | · | · |
| List - Belief | · | ● | · | · | · |
| Timeline *("how it works")* | · | ● | · | · | ○ |
| Comparison *(lace / poly / hybrid)* | · | ○ | ● | · | · |
| Text - Base type guidance | · | · | ● | · | ○ |
| Product - Goal-based recommendation | ○ | · | ● | · | ● |
| Testimonial | ○ | ○ | ○ | ● | ○ |
| Quote - Accent bar | · | · | · | ● | · |
| Stat bars | · | ○ | · | ● | · |
| ⚠ M12 Review stars | · | · | · | ● | · |
| Grid - Collections (4) | ○ | · | ○ | · | ● |
| ⚠ M8 Countdown / expiry *(offer expiry)* | · | · | · | ○ | ● |
| List - Questions | · | · | ○ | · | ● |
| FAQ | ○ | ○ | ● | ○ | ● |
| Button - Primary CTA | ● | ● | ● | ● | ● |
| ⚠ M10 Support / help strip | ○ | ○ | ○ | ○ | ● |
| Footer - Social | ○ | ● | · | ○ | · |

**Timing:** E1 immediate (<5 min) · E2 Day 2 · E3 Day 4 · E4 Day 7 · E5 Day 10.
**⚠ Fix first:** HubSpot currently holds six emails numbered "N of 5" across two campaigns, and the four `Welcome -- Onboarding campaign` emails are attached to **no workflow at all**. Consolidate to this single 5-email series and wire it to `Journey -- Lead Nurture -- Welcome`.

## 6 · Newsletter Nurture — Subscriber Onboarding
*Subscribed to the newsletter, not a lead-magnet download. Lower intent, education-led, subtler CTAs.*

| Module | E1 Welcome | E2 How Systems Work | E3 Style Inspiration | E4 Maintenance Tips | E5 Soft Consult Invite |
|---|---|---|---|---|---|
| Text - Masthead | ● | ● | ● | ● | ● |
| Text - Opening | ● | ● | ● | ● | ● |
| Text - Next step *(what you'll get / never get)* | ● | · | · | · | · |
| Text - Why it matters | ○ | ● | ○ | ● | ○ |
| Comparison | · | ● | · | · | · |
| Text - Base type guidance | · | ● | · | · | · |
| Column - Image and text | ○ | ● | ● | ● | ○ |
| Photo - Feature story | ○ | ○ | ● | ○ | · |
| Timeline *(routine / process)* | · | ○ | · | ● | ● |
| Product - Goal-based recommendation | · | ○ | ● | ○ | ● |
| Product - 3-up grid | · | · | ● | ○ | · |
| Quote - Centered | ○ | ○ | ○ | ○ | ○ |
| Testimonial | ○ | ○ | ● | · | ● |
| List - Questions | · | · | · | ○ | ● |
| Photo - Founder note | · | · | · | · | ● |
| FAQ | ○ | ● | · | ● | ● |
| Button - Primary CTA *(low pressure)* | ● | ● | ● | ● | ● |
| Footer - Social | ● | ○ | ● | ○ | ○ |

**Timing:** E1 immediate · E2 Day 3 · E3 Day 7 · E4 Day 14 · E5 Day 21.
**Rule:** 90/10 educational-to-promotional. Only E5 carries a sales CTA.

---

# CONSULTATION & SALES

## 7 · Consultation — Recap
*Sent immediately after a consultation call. One master template; currency and context variants are token-driven, not separate emails.*

| Slot | Module | Priority |
|---|---|---|
| 1 | Hero - Text-led | ● |
| 2 | Text - Opening *(thank you + framing)* | ● |
| 3 | Text - Customer snapshot *(their situation as discussed)* | ● |
| 4 | Text - Base type guidance *(the recommended spec)* | ● |
| 5 | **⚠ M6 Quote & spec table** *(base, hair, path, unit price, shipping, total)* | ● |
| 6 | Timeline *(what happens next, production window)* | ● |
| 7 | Text - Reassurance *(guarantee, adjustment policy)* | ● |
| 8 | Testimonial | ○ |
| 9 | List - Questions *(anticipated objections)* | ○ |
| 10 | FAQ | ● |
| 11 | Button - Primary CTA *(approve / proceed)* | ● |
| 12 | Photo - Founder note | ● |
| 13 | **⚠ M10 Support / help strip** | ● |

**Variants collapsed into tokens:** USD / CAD / EUR / GBP (currency token), No-Local-Partner, Current-System-User, Front-Partial (conditional content blocks). Seven Notion rows become one email with conditional logic.

## 8 · Consultation — Follow-Up
*No response after the recap. Escalating gently, then releasing.*

| Module | E1 Day 5 | E2 Day 10 | E3 Day 90 Re-engage | E4 Final Close Loop |
|---|---|---|---|---|
| ⚠ M11 Plain-text founder wrapper | ● | ● | ● | ● |
| Text - Opening *(no-pressure check-in)* | ● | ● | ● | ● |
| Text - Customer snapshot *(spec still on file)* | ○ | ● | ● | ○ |
| List - Questions *(what's holding you back)* | ● | ● | ○ | · |
| Text - Reassurance | ● | ● | ● | ● |
| Text - Why it matters | · | ○ | ● | · |
| ⚠ M14 Dynamic product recommendations *(what's new since)* | · | · | ● | · |
| Testimonial | · | ○ | ○ | · |
| Text - Offer discount | · | · | ○ | · |
| Button - Primary CTA *(reply / book)* | ● | ● | ● | ● |
| Text - Next step *(door stays open)* | ○ | ● | ○ | ● |
| ⚠ M13 Preference / opt-down | · | · | · | ● |

**All four are plain-text founder emails.** This is a 1:1 sales conversation, not a campaign — branded templates actively hurt here.

---

# POST-PURCHASE

## 9 · New Customer Onboarding
*Order placed. Reassure, prepare, educate, then ask.*

| Module | E1 Order Confirmation | E2 Prep Guide | E3 Care + Cross-Sell | E4 Check-In + Review |
|---|---|---|---|---|
| Hero - Text-led | ● | ● | ● | · |
| ⚠ M11 Plain-text founder wrapper | · | · | · | ● |
| **⚠ M4 Order summary / production status** | ● | ○ | · | · |
| Text - Opening | ● | ● | ● | ● |
| Timeline *(what happens now, 4–6 weeks)* | ● | ● | ○ | · |
| Text - Reassurance | ● | ● | ○ | ○ |
| Text - Base type guidance | · | ● | ○ | · |
| Text - Why it matters *(how to prepare)* | · | ● | ● | · |
| List - Questions *(find a stylist etc.)* | · | ● | · | · |
| Product - Goal-based recommendation *(care kit)* | · | ○ | ● | · |
| Product - 3-up grid | · | · | ● | · |
| Text - Customer snapshot | · | · | · | ● |
| Testimonial | ○ | · | ○ | ○ |
| Text - Next step *(lifespan / reorder horizon)* | · | · | ● | ● |
| FAQ | ● | ● | ● | ○ |
| Button - Primary CTA | ● | ● | ● | ● |
| Photo - Founder note | ● | · | · | ● |
| **⚠ M10 Support / help strip** | ● | ● | ● | ● |

**Timing:** E1 immediate · E2 Day 3 · E3 Day 10 · E4 Day 21.
**Cross-sell placement:** E3 only, after education, never before. Research is unanimous — education precedes or accompanies the cross-sell.

## 10 · Shipping Updates

| Module | E1 What Happens Next | E2 Mid-Wait Check-In |
|---|---|---|
| Hero - Text-led | ● | ● |
| **⚠ M5 Shipping tracking block** | ● | ● |
| Text - Opening | ● | ● |
| Timeline *(order journey stages)* | ● | ● |
| Photo - Feature story *(how it's made)* | · | ● |
| Text - Why it matters *(craft / process)* | ○ | ● |
| Text - Reassurance | ● | ● |
| Text - Next step *(what to do on arrival)* | ● | ○ |
| FAQ | ● | ○ |
| Button - Primary CTA *(track)* | ● | ● |
| **⚠ M10 Support / help strip** | ● | ● |

## 11 · Post-Purchase Care
*Delivered. Now maximise the outcome so they reorder.*

| Module | E1 Delivery QuickStart | E2 Maintenance Schedule | E3 Longevity Tips |
|---|---|---|---|
| Hero - Text-led | ● | ● | ● |
| Text - Opening | ● | ● | ● |
| Timeline *(30/60/90 calendar)* | ○ | ● | ○ |
| Text - Why it matters *(technique)* | ● | ● | ● |
| Column - Image and text *(step visuals)* | ● | ● | ● |
| Text - Base type guidance | ○ | ○ | ● |
| Product - Goal-based recommendation *(care products)* | ○ | ● | ● |
| Text - Reassurance | ● | ○ | ○ |
| Text - Next step *(lifespan → reorder)* | · | ○ | ● |
| List - Questions | ○ | ○ | ○ |
| FAQ | ● | ● | ● |
| Button - Primary CTA | ● | ● | ● |
| **⚠ M10 Support / help strip** | ● | ● | ● |

## 12 · Review Request

| Module | E1 Review Request | E2 UGC Photo Request |
|---|---|---|
| ⚠ M11 Plain-text founder wrapper | ● | · |
| Hero - Text-led | · | ● |
| Text - Opening *(personalised ask)* | ● | ● |
| Text - Customer snapshot *(the exact product bought)* | ● | ● |
| List - Questions *(guiding prompts)* | ● | ○ |
| Photo - Feature story *(example UGC)* | · | ● |
| Testimonial *(what a good one looks like)* | · | ● |
| Text - Offer discount *(incentive)* | ○ | ● |
| Button - Primary CTA *(one-click to review form)* | ● | ● |
| Text - Reassurance *(30 seconds, no account needed)* | ● | ○ |
| **⚠ M10 Support / help strip** | ○ | ○ |

**Timing:** E1 1–2 weeks after delivery confirmation · E2 +7 days.

---

# RETENTION & EXPANSION

## 13 · Cross-Sell — Care Kits
*Triggered after delivery, when enthusiasm is highest.*

| Module | E1 Care Kit Intro | E2 Problem / Solution | E3 Bundle Offer |
|---|---|---|---|
| Hero - Text-led | ● | ● | ● |
| Text - Opening *(why these fit)* | ● | ● | ● |
| Text - Customer snapshot *(their system)* | ● | ○ | ○ |
| Text - Why it matters *(the #1 mistake)* | ○ | ● | ○ |
| Product - Goal-based recommendation | ● | ● | ● |
| Product - 3-up grid | ● | ○ | ● |
| ⚠ M14 Dynamic product recommendations | ○ | ○ | ○ |
| Testimonial | ○ | ● | ○ |
| ⚠ M12 Review stars | ○ | ○ | ○ |
| Text - Offer discount | · | · | ● |
| ⚠ M9 Promo code block | · | · | ● |
| ⚠ M8 Countdown / expiry | · | · | ○ |
| Text - Reassurance | ○ | ○ | ● |
| FAQ | ○ | ● | ○ |
| Button - Primary CTA | ● | ● | ● |

## 14 · Reorder — Supplies Subscription
*Consumables running low. Replenishment logic — timing is the whole design.*

| Module | E1 Friendly Reminder | E2 Subscription Pitch | E3 Last Reminder + New |
|---|---|---|---|
| Hero - Text-led | ● | ● | ● |
| Text - Opening | ● | ● | ● |
| Text - Customer snapshot *(what they bought, when)* | ● | ● | ● |
| ⚠ M14 Dynamic product recommendations *(previous items)* | ● | ● | ● |
| Timeline *(refill cycle)* | ○ | ● | · |
| Text - Why it matters *(never run out)* | ○ | ● | ○ |
| Stat bars *(savings maths)* | · | ● | · |
| Product - 3-up grid *(what's new)* | · | · | ● |
| Text - Reassurance *(cancel anytime)* | ○ | ● | ○ |
| Text - Offer discount | · | ○ | ● |
| ⚠ M8 Countdown / expiry | · | · | ○ |
| FAQ | ○ | ● | ○ |
| Button - Primary CTA *(reorder / subscribe)* | ● | ● | ● |

**Timing:** send *before* they run out — E1 at ~80% of expected consumption, E2 +7d, E3 +14d with the incentive only once the normal cycle has passed.

## 15 · Reorder — System Replacement Window
*The system itself is wearing out. Higher ticket, needs lifespan and base-type logic. Deliberately separate from supplies.*

| Module | E1 Mid-Cycle Care Check | E2 Replacement Nudge | E3 Loyalty Hook |
|---|---|---|---|
| Hero - Text-led | ● | ● | ● |
| Text - Opening | ● | ● | ● |
| Text - Customer snapshot *(their spec, order date)* | ● | ● | ● |
| Text - Why it matters *(mid-cycle care)* | ● | ○ | · |
| Text - Base type guidance *(lifespan by base)* | ● | ● | ○ |
| Text - Next step *(where they are in the cycle)* | ● | ● | ● |
| Timeline *(wear curve / production lead time)* | ○ | ● | ○ |
| Product - Goal-based recommendation *(same spec, reorder)* | ○ | ● | ● |
| Comparison *(upgrade options)* | · | ○ | ○ |
| Testimonial | ○ | ○ | ○ |
| Text - Offer discount *(loyalty / free care kit)* | · | · | ● |
| ⚠ M9 Promo code block | · | · | ● |
| ⚠ M8 Countdown / expiry | · | ○ | ● |
| Text - Reassurance | ○ | ● | ● |
| FAQ | ● | ● | ○ |
| Button - Primary CTA | ● | ● | ● |
| ⚠ M10 Support / help strip | ● | ● | ○ |

**Timing:** E1 at 50% of expected lifespan · E2 15 days before projected wear-out · E3 at wear-out date.

## 16 · Renewal — Continuity Plan
*Subscription billing. Legally and commercially distinct — billing facts are non-negotiable in every email.*

| Module | E1 30-Day Snapshot | E2 14-Day Heads-Up | E3 7-Day Urgency | E4 Final Confirmation |
|---|---|---|---|---|
| Hero - Text-led | ● | ● | ● | · |
| ⚠ M11 Plain-text founder wrapper | · | · | · | ● |
| Text - Opening | ● | ● | ● | ● |
| Text - Customer snapshot *("your year on the plan")* | ● | ○ | · | · |
| Stat bars *(systems delivered, adjustments made)* | ● | · | · | · |
| **⚠ M7 Billing / payment details** *(date, amount, card on file, spec)* | ● | ● | ● | ● |
| Text - Why it matters *(price lock, queue priority, spec preservation)* | ○ | ● | ● | ○ |
| List - Belief *(what continues)* | ○ | ○ | ● | · |
| Timeline *(renewal + production schedule)* | ○ | ● | ○ | · |
| Text - Reassurance *(manage / update / cancel)* | ● | ● | ● | ● |
| ⚠ M8 Countdown / expiry | · | ○ | ● | ● |
| Testimonial | ○ | · | · | · |
| FAQ | ● | ● | ○ | · |
| Button - Primary CTA *(manage subscription)* | ● | ● | ● | ● |
| ⚠ M10 Support / help strip | ● | ● | ● | ● |

**⚠ E1 does not exist in HubSpot** — the live series starts at E2. Build it.
**Compliance:** these are mixed-purpose. Marketing content inside a billing notice still requires a working unsubscribe.

## 17 · Win-back
*90+ days dormant. Acknowledge the lapse, add something new, then release cleanly.*

| Module | E1 Just Checking In | E2 What's New | E3 Specific Offer | E4 Last Email |
|---|---|---|---|---|
| ⚠ M11 Plain-text founder wrapper | ● | · | · | ● |
| Hero - Text-led | · | ● | ● | · |
| Text - Opening *(acknowledge the gap)* | ● | ● | ● | ● |
| Text - Customer snapshot *(spec on file)* | ● | ○ | ● | ● |
| Text - Why it matters *(what's changed)* | ○ | ● | ○ | · |
| Text - Five changes | · | ● | · | · |
| ⚠ M14 Dynamic product recommendations *(by past purchase)* | · | ● | ● | · |
| Product - 3-up grid | · | ● | ○ | · |
| Testimonial | · | ○ | ○ | · |
| Text - Offer discount | · | · | ● | ○ |
| ⚠ M9 Promo code block | · | · | ● | ○ |
| ⚠ M8 Countdown / expiry | · | · | ● | ○ |
| Text - Reassurance | ○ | ○ | ● | ● |
| Text - Next step | ○ | ○ | ○ | ● |
| **⚠ M13 Preference / opt-down** | · | · | ○ | ● |
| Button - Primary CTA | ● | ● | ● | ● |

**Timing:** E1 Day 90 · E2 +7d · E3 +14d · E4 +21d.
**E4 is a deliverability asset**, not a sales email — it segments the genuinely dead off the list. Opt-down (fewer emails) must be offered alongside opt-out.

---

# BROADCAST TEMPLATES
*Recurring sends, one reusable structure each. These replace the single flat `Newsletter -- Always-on content` bucket.*

## 18 · Newsletter — Education
`Text - Masthead ●` → `Text - Opening ●` → `Text - Why it matters ●` → `Column - Image and text ●` → `Comparison ○` → `Text - Base type guidance ○` → `Timeline ○` → `Quote - Centered ○` → `Product - Goal-based recommendation ○` → `FAQ ○` → `Button - Primary CTA ●` → `Footer - Social ●`
*One teaching angle per send. Product links only where genuinely helpful.*

## 19 · Newsletter — Customer Story
`Text - Masthead ●` → `Photo - Feature story ●` → `Text - Opening ●` → `Quote - Centered ●` → `Testimonial ●` → `⚠ M12 Review stars ○` → `Stat bars ○` → `Text - Why it matters ○` → `Product - Goal-based recommendation ●` → `Button - Primary CTA ●` → `Footer - Social ●`
*One authentic voice, the product they used, one CTA to shop it or read the full story.*

## 20 · Newsletter — Offer / Promo
`Text - Masthead ●` → `Text - Offer discount ●` *(hero position)* → `⚠ M9 Promo code block ●` → `⚠ M8 Countdown / expiry ●` → `Grid - Collections (4) ●` → `Product - 3-up grid ○` → `Testimonial ○` → `List - Trust strip ○` → `Text - Reassurance ○` → `Button - Primary CTA ●` → `Footer - Standard ●`
*Offer in the hero. Terms and expiry unmistakable. Minimum competing links. CTA lands on the exact collection the offer applies to.*

## 21 · Newsletter — Brand & Recap
`Text - Masthead ●` → `Text - Opening ●` → `Stat bars ●` → `Text - Five changes ○` → `Photo - Feature story ○` → `Timeline ○` → `Quote - Centered ○` → `Photo - Founder note ●` → `Grid - Collections (6) ○` → `Button - Primary CTA ●` → `Footer - Social ●`

## 22 · Newsletter — Product Launch
`Text - Masthead ●` → `Hero - Photo-led ●` → `Text - Opening ●` → `Text - Why it matters ● *(benefits tied to pain points)*` → `Column - Image and text ●` → `Product - 3-up grid ●` → `Comparison ○` → `Testimonial ○` → `List - Trust strip ○` → `⚠ M8 Countdown / expiry ○ *(early access)*` → `Button - Primary CTA ●` → `Footer - Social ●`

## 23 · Cross-Sell — Accessories (broadcast)
`Text - Masthead ●` → `Text - Opening ●` → `Text - Why it matters ●` → `Product - 3-up grid ●` → `⚠ M14 Dynamic product recommendations ○` → `Testimonial ○` → `Text - Offer discount ○` → `Button - Primary CTA ●` → `Footer - Social ●`

---

# CAMPAIGN

## 24 · Launch Day — Brand Relaunch
*The only emails in the account with real send data. Two audiences, A/B on offer placement.*

| Module | A — Existing Customer | B — New Prospect |
|---|---|---|
| Photo - Logo system | ● | ● |
| Hero - Photo-led | ● | ● |
| Text - Opening | ● | ● |
| Text - Offer discount *(A/B: top vs bottom)* | ● | ● |
| ⚠ M9 Promo code block | ● | ● |
| Text - Five changes | ● | ● |
| Product - 3-up grid | ● | ● |
| Grid - Collections (4) | ○ | ● |
| List - Belief | ○ | ● |
| Testimonial | ○ | ● |
| List - Trust strip | ○ | ● |
| Photo - Founder note | ● | ● |
| Text - Customer snapshot *(their history with us)* | ● | · |
| Button - Final CTA | ● | ● |
| Footer - Wide | ● | ● |

**Fix:** HubSpot labels both A/B parents "Audience A". Rename the New Prospect one to Audience B.

## 25 · Post-Launch Nurture
*Promoted out of `Launch -- Brand relaunch`. Weekly cadence after launch day.*

| Module | W2 Trust | W3 Education | W4 Customer Proof | W5 First Order Offer |
|---|---|---|---|---|
| ⚠ M11 Plain-text founder wrapper | ● | · | · | · |
| Hero - Text-led | · | ● | ● | ● |
| Text - Opening | ● | ● | ● | ● |
| Photo - Founder note | ● | · | · | ○ |
| Text - Founder pillars | ● | · | · | · |
| List - Belief | ● | · | · | · |
| Comparison *(lace vs poly)* | · | ● | · | · |
| Text - Base type guidance | · | ● | · | · |
| Column - Image and text | · | ● | ○ | · |
| Testimonial | ○ | · | ● | ○ |
| Quote - Accent bar | · | · | ● | · |
| Stat bars | · | · | ● | · |
| ⚠ M12 Review stars | · | · | ● | · |
| Product - Goal-based recommendation | · | ● | ○ | ● |
| Product - 3-up grid | · | ○ | ○ | ● |
| Text - Offer discount | · | · | · | ● |
| ⚠ M9 Promo code block | · | · | · | ● |
| ⚠ M8 Countdown / expiry | · | · | · | ● |
| FAQ | ○ | ● | ○ | ○ |
| Button - Final CTA | ● | ● | ● | ● |

---

# OPERATIONAL

## 26 · Payment Recovery

| Module | E1 Payment Failed | E2 Grace Period |
|---|---|---|
| Hero - Text-led | ● | ● |
| Text - Opening *(what happened, plainly)* | ● | ● |
| **⚠ M7 Billing / payment details** | ● | ● |
| Text - Next step *(exactly how to fix it)* | ● | ● |
| ⚠ M8 Countdown / expiry *(48h remaining)* | ○ | ● |
| Text - Reassurance *(nothing lost yet)* | ● | ● |
| FAQ | ○ | ○ |
| Button - Primary CTA *(update payment)* | ● | ● |
| **⚠ M10 Support / help strip** | ● | ● |

*No promotional content. No cross-sell. Single job.*

---

# Build Queue — 14 modules that do not exist

Ordered by how many blueprints they block.

| ID | Module | Blocks | Priority |
|---|---|---|---|
| **M10** | Support / help contact strip | 40+ emails, every series | **P0** |
| **M9** | Promo code block *(code, copy action, terms, expiry)* | 20+ emails | **P0** |
| **M8** | Countdown / expiry cue | 20+ emails | **P0** |
| **M11** | Plain-text founder wrapper *(light shell, compliant footer)* | 18 emails | **P0** |
| **M1** | Cart — dynamic line items | Cart Abandonment ×3 *(series is non-functional without it)* | **P0** |
| **M2** | Resume-checkout summary | Checkout Abandonment ×4 | **P1** |
| **M3** | Viewed product (dynamic) | Browse Abandonment ×4 | **P1** |
| **M14** | Dynamic product recommendations *(behavioural)* | 12 emails | **P1** |
| **M12** | Review stars / rating snippet | 12 emails | **P1** |
| **M7** | Billing / payment details | Renewal ×4, Payment Recovery ×2 | **P1** |
| **M4** | Order summary / production status | New Customer ×2 | **P2** |
| **M5** | Shipping tracking block | Shipping ×2 | **P2** |
| **M6** | Quote & spec table | Consultation Recap | **P2** |
| **M13** | Preference centre / opt-down | Win-back E4, Consultation E4 | **P2** |

**The five P0 modules unblock roughly 70% of the blueprint set.** M10, M9, M8 and M11 are small, generic, and reusable everywhere — build those four first and almost every series becomes buildable.

Existing library coverage: **37 live Atelier Zero families** cover every other slot in every blueprint. No blueprint calls for a module that exists only in the archived or deleted sets.
