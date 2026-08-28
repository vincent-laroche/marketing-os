# Phase 5 — Automations, segments, consent

Status as of 2026-08-21. See `CAMPAIGN-PLAN.md` §Phase 5 for the original spec — this
file is the live build record against it.

## Re-verified before starting

- **Phase 0 sender-domain auth: confirmed still live.** Shopify admin → Settings →
  Notifications → Email domain authentication shows **Authenticated**. This was the
  hard blocker Phase 5 needed; it is genuinely clear.
- **Consent finding: confirmed still current, not stale.** The "Email subscribers"
  segment (Shopify's own count) is 95% of ~3,960 customers — same order of magnitude
  as the plan's 3,780/3,958 figure from 2026-08-19. Nothing has changed this since
  (0 messages ever sent per Shopify Messaging's own live state). **Do not activate
  any automation against the broad subscribed list.** This is still the single
  biggest risk in this programme.
- `customersCount(query: ...)` **silently ignores its query argument** and always
  returns the unfiltered total — new API gotcha, do not use it for consent-state
  counts. Use a segment's live member count in the admin UI instead, or
  `customerSegmentMembers` with a `query` argument (untested this session).

## Segment layer — done

Naming convention per the plan: `MKT | Email | <state> | <qualifier>`.

Pruned 8 junk Shopify-default segments (`Customers not added to companies` /
`Customers added to companies`, 4 duplicate pairs, all system-generated, all flagged
in the plan as junk). 17 segments → 9, then rebuilt:

**Renamed** (reused existing correct queries, just brought under the convention so an
automation's segment picker is legible):
- `MKT | Email | Eligible | Broad subscribed (consent unverified - do not activate)` —
  was "Email subscribers". Name carries the warning deliberately — anyone about to
  point an automation at this segment sees the blocker in the picker itself.
- `MKT | Email | Eligible | Lapsed 60d (J3 Win-Back candidate)` — was "Winback customers".
- `MKT | Email | Eligible | Purchasers (J1/J4 candidate)` — was "Customers who have
  purchased at least once".
- `MKT | Email | Eligible | Never purchased (W Welcome candidate)` — was "Customers
  who haven't purchased".
- `MKT | Email | Eligible | Abandoned checkout 30d (J2 candidate)` — was "Abandoned
  checkouts in the last 30 days".

**Created new:**
- `MKT | Email | Suppressed | Not subscribed or unsubscribed` —
  `email_subscription_status = 'NOT_SUBSCRIBED' OR email_subscription_status = 'UNSUBSCRIBED'`.
- `MKT | Email | Eligible | J5 Consultation (tag: consultation-interest)` —
  `customer_tags CONTAINS 'consultation-interest'`. Zero members today by design —
  populates once the tag is actually applied (Forms/checkout opt-in, not built yet).
- `MKT | Email | Eligible | Engaged core (safe start)` —
  `customer_tags CONTAINS 'hs-engaged-core'`. 205 members (see engagement-tagging
  section below).
- `MKT | Email | Eligible | Consented cohort 2026 (owner-attested)` —
  `customer_tags CONTAINS 'hs-consented-2026'`. 986 members.

13 segments total now.

Left alone: `From Spain`, `Amazon`, `eBay`, `Customers who have purchased more than
once` — unrelated to this program or already fine as-is.

## "Engaged core" safe-start audience — resolved

Found the real source: `~/02_dev/mkt-resend/data/current/free-prospect-ranking/
selected.json` — **not** the raw HubSpot export CAMPAIGN-PLAN.md's 186 figure came
from. This is a different, better artifact: 1,000 contacts with a genuine owner
attestation (Vincent Laroche, 2026-07-17T05:41:03Z: "all current active HubSpot
contacts in this scope have consciously opted into receiving Hair Solutions Co.
marketing emails") plus real per-contact engagement (opens/clicks/pageviews/
sessions). Already approved and imported into MailerLite in July
(`mailerlite/import_prospects.py`) — reusing an existing decision, not a new one.

Built `shopify-messaging/build_engagement_tags.py`: matched the 1,000-contact cohort
against Shopify customers by email (986 of 1,000 matched, 3,937 Shopify customers
fetched), applied additive tags via `tagsAdd` (never overwrites existing tags):
- `hs-consented-2026` → all 986 matched (owner-attested consent basis)
- `hs-engaged-core` → 205 of those with real `engagement.opened` or `.clicked` > 0

Result: 986 tagged, 0 failed. Built the two segments the tags unlock:
`MKT | Email | Eligible | Engaged core (safe start)` (`customer_tags CONTAINS
'hs-engaged-core'`) and `MKT | Email | Eligible | Consented cohort 2026
(owner-attested)` (`customer_tags CONTAINS 'hs-consented-2026'`). Both are real,
live, and safe to point a starting automation at — this gap is closed.

## Journey → surface mapping (unchanged from the plan)

| Series | Surface | Depends on |
|---|---|---|
| J2 Cart Recovery + BR-1 | Messaging native | `MKT | Email | Eligible | Abandoned checkout 30d` — segment ready |
| W Welcome | Messaging native | `MKT | Email | Eligible | Never purchased` — segment ready |
| J1 Post-Purchase | native + Flow (PP-4 fulfilment-triggered) | `Purchasers` segment ready; Flow trigger not yet built |
| J4 Reorder | Flow, custom timing off delivery date | `Purchasers` segment ready; Flow trigger not yet built |
| J3 Win-Back | Flow, ends in a real sunset | `Lapsed 60d` segment ready; Flow trigger not yet built |
| J5 Consultation | Flow + tag-driven segment (Basic plan has no Send HTTP Request) | Segment scaffolded, zero members — tag application not built |
| N Newsletter | Campaigns, not an automation | **Blocked** — see exclusion-tag gap below |

## Newsletter audience formula — blocked on a tagging convention that doesn't exist yet

The plan's formula: `marketable + News & Offers − suppression − active Cart Recovery /
Win-Back / J5 enrollees`. The subtraction terms need to know who is *currently
enrolled* in another journey — Shopify segment query language has no "customer is
mid-automation" fact. This has to be built as a tag applied on journey entry and
removed on exit (purchase, sunset, or completion), e.g. `journey-j2-active`,
`journey-j3-active`, `journey-j5-active`. **This tagging convention does not exist
yet and needs to be designed and wired into every journey automation as it's built**
— it is not optional, the plan calls the frequency cap it enables "the single most
important operating rule in the programme." Proposing it here rather than building
the newsletter segment on a formula that can't actually exclude anyone yet.

## Collision matrix — precedence rules approved 2026-08-21 by Vincent

- J1 (Post-Purchase) and J4 (Reorder) both key off delivery date: PP-7 +35d, PP-7b
  +42d, RO-1 +45d. A single order could theoretically hit more than one of these in
  the same window. **Approved rule: J1 Post-Purchase runs to completion first; J4
  Reorder cannot enroll a customer who has an active J1 enrollment.** Enforce with
  the `journey-j1-active` tag (see enrollment-tagging convention below) as a
  suppression condition on J4's entry trigger.
- J3 Win-Back and J4 Reorder both target lapsed purchasers — same customer could
  qualify for both. **Approved rule: J4 Reorder wins while active; a customer falls
  through to J3 Win-Back only after J4 exhausts (completes or exits) or the customer
  re-lapses past J4's window without reordering.** Enforce the same way: J3's entry
  trigger checks for absence of `journey-j4-active` before enrolling.

These are now build requirements, not proposals — the Flow workflows for J1, J3 and
J4 must implement both checks from first construction, not have them added after.

## Exit conditions (from the plan)

A purchase exits every recovery and reorder journey (J2, J4). WB-4 ("Last Email From
Us") must actually suppress future contact — needs the same enrollment-tag mechanism
above to be enforceable, since "exit" only means something if something is tracking
enrollment state.

## Native Shopify Messaging — attempted, genuinely blocked by the UI itself

Two automations exist today in Shopify Messaging, both **Inactive**: "Recover
abandoned checkout" and "Abandoned checkout" — duplicates, per the plan.

Attempted to resolve this directly (per Vincent's instruction to do it rather than
hand it back). Every avenue tried hit the same wall:
- `/apps/shopify-messaging/automations` — scroll does not move the page past the
  onboarding-checklist card; `find` and page-text extraction see only the outer
  Shopify chrome (breadcrumbs, "Create automation" button), nothing of the app's own
  content — it's rendered inside an iframe with no accessibility tree exposed.
- `/apps/shopify-messaging/automations/templates` — the template catalog itself
  rendered (visible in screenshots), but every card is genuinely inert: direct
  clicks on the title, the body text, and the card center all did nothing, and a
  `hover` produced no visible hover state either. This isn't a coordinate-targeting
  problem — the cards do not appear to be interactive DOM elements the browser tool
  can trigger at all, consistent with the same iframe/custom-render issue.
- Global admin search for "abandoned checkout" surfaces the Abandoned Checkouts
  orders page and the renamed `MKT | Email | Eligible | Abandoned checkout 30d`
  segment, but no result for either Messaging automation — they aren't indexed by
  admin search.

**Conclusion: this is not resolvable via browser automation in its current form.**
Needs Vincent doing it directly in the Shopify Messaging UI (Automations → find the
two "abandoned checkout" entries → deactivate/delete the duplicate, keep one) — a
two-minute manual task once a human is looking at the actual rendered app, but not
one this session could complete safely or at all through the tooling available.

## What's actually left before any activation

1. ~~Build the engaged-core tag sync~~ — **done**, see above.
2. Design + apply the journey-enrollment tagging convention (`journey-j1-active`,
   `journey-j2-active`, etc., applied on entry, removed on exit) — unblocks the
   newsletter exclusion formula and enforces the now-approved J1/J4/J3 precedence
   rules. Not built yet — needs to land as part of building the automations
   themselves, not before or after.
3. Resolve the two duplicate abandoned-checkout automations — **needs Vincent
   directly in the Shopify Messaging UI.** Attempted this session; the app's UI is
   not reliably automatable (see above) — not a scope decision, a tooling limitation.
4. Build the native automations (J2, W) and the Flow workflows (J1/PP-4, J4, J3, J5)
   — none exist yet beyond the two duplicate abandoned-checkout ones. Same UI
   limitation applies to native Messaging automations (J2, W); Flow workflows (J1,
   J4, J3, J5) haven't been attempted yet this session and may or may not have the
   same problem — Flow is a separate app, untested.
5. ~~Confirm J1/J4 and J3/J4 precedence~~ — **approved 2026-08-21**, see above.
6. The plan's own Phase 5 gate: full QA suite (eligible/ineligible/missing-personalization/
   already-purchased/overlapping-journey/expired-discount/unavailable-product/mobile/
   link-UTM/turn-off-during-wait), then **explicit approval before any activation** —
   unchanged, still applies, nothing above skips it.

Segment layer (13 segments now, all real) and the engagement/consent tagging are
genuinely done and safe to leave as-is regardless of pace on the rest. Nothing built
this session sends or activates anything.
