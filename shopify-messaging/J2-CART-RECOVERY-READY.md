# J2 Cart Recovery — ready to build

Status: **content and structure reviewed; palette reconciliation still required before
activation.** Automation not yet built — Shopify Messaging's automation UI is not scriptable
from here (confirmed, see PHASE5-PLAN.md), so this is the exact spec to build by hand. Nothing
has been pushed, scheduled, sent, or activated.

Scope: CR-1 through CR-4 only. BR-1 (Base Types Explainer) is browse abandonment, a different
Shopify Messaging automation type — not part of this flow.

## The automation

| Setting | Value |
|---|---|
| Template | Recover abandoned checkout |
| Channel | Email |
| Audience | `MKT | Email | Eligible | Abandoned checkout 30d` (already built, Phase 5) |
| Exit condition | Customer completes the order |
| Sequence | 4 emails, timed off the abandonment event |

Timing (already decided in the approved copy — each subject line carries its own delay):

| Step | File | Delay |
|---|---|---|
| 1 | `emails/01-cr-1.html` | +4 hours |
| 2 | `emails/02-cr-2.html` | +1 day |
| 3 | `emails/03-cr-3.html` | +2 days |
| 4 | `emails/04-cr-4.html` | +4 days |

Shopify's own editor is what determines whether the stock "Recover abandoned checkout" template
starts with 1, 2, or 3 default steps — you'll be adding/editing steps to reach these 4. Each
step's email is a **fully custom-coded HTML email** (Shopify Messaging supports this natively,
under its 500KB limit — each of these 4 is 12–19KB), not the drag-and-drop template editor.

## Per-email build

### Step 1 — CR-1 · Your Cart's Still Here (+4h)
- Subject: **Your cart's still here**
- Preview text: **No pressure — just making sure nothing broke on our end.**
- Paste `emails/01-cr-1.html` as custom code.

### Step 2 — CR-2 · Three Questions Answered (+1d)
- Subject: **The three things people ask before ordering**
- Preview text: **Will it look real, will it hold, and what if it's wrong.**
- Paste `emails/02-cr-2.html` as custom code.

### Step 3 — CR-3 · Not Sure You Picked Right (+2d)
- Subject: **Not sure you picked the right one?**
- Preview text: **Tell me your situation and I'll tell you what I'd choose.**
- Paste `emails/03-cr-3.html` as custom code.
- This one's CTA is "Book 15 minutes" → `hairsolutions.co/pages/contact-us` (a consultation
  offer, not a return-to-cart link) — that's intentional, matches the approved copy.

### Step 4 — CR-4 · Last Note + Free Shipping (+4d)
- Subject: **Last note about your cart**
- Preview text: **Free shipping if it helps. Either way, this is the last one.**
- Paste `emails/04-cr-4.html` as custom code.
- Uses discount code `FREESHIP` — confirmed live via the Admin API: active, no expiry, no
  minimum, unlimited use. See "Open decision" below before shipping this as-is.

## What I fixed this pass (full detail in BUILD-LEDGER.md → Phase 3.5)

All 4 emails had real defects, not cosmetic ones — an unresolved placeholder token
(`{{ cart_contents }}` / `{{ last_viewed_product }}`) sitting next to a completely empty cart
table in every email, CR-2's two CTAs both hardcoded to one static product page instead of the
customer's actual checkout, CR-2's testimonial slot fully empty, a trust-strip module rendering
3 of its 4 columns blank in both CR-2 and CR-3, three dead empty rows in CR-3, and a "Valid for
72 hours" claim in CR-4 that was false (the code has no expiry) and contradicted the email's own
body copy. All functional defects were fixed. The four files were also retokened to
`PLATFORM_EMAIL.md` v1, but that change conflicts with the durable project rule in `AGENTS.md`
§1, which says the Email Reference File module palette is authoritative and explicitly rules
`PLATFORM_EMAIL.md` out of scope. Treat the current palette as unresolved, not approved.

**Do not sweep the other 49 emails to match these four.** First decide whether the current hard
rule remains in force. Unless Vincent explicitly changes that rule, CR-1 through CR-4 should be
returned to the Email Reference File module palette before activation.

## Decisions I made that you should confirm, not just inherit

1. **CR-2's testimonial** — filled with a real published review (Scott S., 5-star, from
   `proof-bank/proof-bank.json`): *"No one can tell it's a system. The hairline blends
   perfectly and I can style it however I want. Quality exceeded my expectations for the
   price."* It's genuinely the best match in the Proof Bank for the "will it look real"
   objection this email answers, but you know these customers — swap it if you have a better
   one in mind.
2. **CR-4's discount framing** — reworded "Valid for 72 hours" to "Apply it at checkout — no
   expiry" because the claim was false as configured. If you'd rather the code genuinely expire
   72 hours after send, that needs a different mechanism (a per-customer discount created at
   send time, which isn't a stock Shopify Messaging capability) — flag it and we can design
   that properly rather than fake it in copy.
3. **Scope** — built CR-1 through CR-4 only. BR-1 (browse abandonment) is a separate automation
   type; say the word if you want it finished next.

## Remaining activation decisions

1. **Sender domain authentication is complete.** Shopify admin showed **Authenticated** on
   2026-08-21. This is no longer a blocker.
2. **Two duplicate automations already exist**, both Inactive: "Recover abandoned checkout" and
   "Abandoned checkout." Confirmed this session that the Messaging automation UI can't be driven
   by browser automation — you'll need to open Apps → Messaging → Automations yourself, keep
   one, delete the other, before turning this on.
3. **The cart discount question was never actually decided** (it's an open item in
   CAMPAIGN-PLAN.md) — CR-4's copy just assumed FREESHIP from the start. Confirm that's really
   the offer you want here before activating.
4. **Palette authority must be reconciled.** The current CR-1 through CR-4 files conflict with
   `AGENTS.md` §1. This is a release blocker even though their structural checks pass.

Once the duplicate automation, palette conflict, and open content decisions above are resolved,
this flow becomes a paste-the-four-files-in-and-set-the-timing job.
