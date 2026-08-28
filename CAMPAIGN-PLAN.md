# Campaign Implementation Plan — the 53-email programme

> **Execution status, 2026-08-24:** Shopify Messaging + Shopify Flow is the sole marketing
> campaign/lifecycle platform. This document is the approved 2026-08-19 baseline plan, not the
> current status ledger. Since it was written: Phase 0 sender authentication was completed;
> Phases 1–3 produced all 53 artifacts (51 structurally green, 2 source-blocked); Phase 4 is
> partially complete; Phase 5 has segments and consent tags but
> not the journey automations; Phase 6 has not started. Use `PROJECT.md` and
> `shopify-messaging/PHASE5-PLAN.md` for current state. Any later statement below that Shopify
> authentication is blocked or that work is "not done" is historical to 2026-08-19.

> Source of truth: `Email Reference File/` (AGENTS.md §1). Everything below was verified against
> that folder and against live DNS/R2/API on 2026-08-19. Nothing live was touched.

## 1. Verified state

### Scope — 53 emails, 6 journeys + a 20-edition newsletter

| Series | Emails | Workflow assigned |
|---|---|---|
| J1 · Post-Purchase | 8 | yes |
| J2 · Cart Recovery (incl. BR-1 browse) | 5 | yes |
| J3 · Win-Back → Sunset | 4 | yes |
| J4 · Reorder | 6 | yes |
| J5 · Consultation | 5 | no |
| W · Newsletter Welcome | 5 | no |
| N · Newsletter Programme | 20 | n/a (campaigns) |

23 of 53 carry a Workflow ID. J5, W and N have none — they need creating.

### Copy is complete

All 53 have Body, Subject, Preview Text and CTA. 72,254 body chars, avg 1,363.
Single gap: PP-7b has no Preview Text and no CTA.

### The module gap is ONE module, not sixteen

The Missing Modules column lists 16 distinct modules — but "missing" meant missing from
HubSpot, which no longer matters. Mapped against the 102 resolved HTML previews:

- **12 map exactly** — text_masthead, column_image_and_text, faq, product_3up_grid,
  comparison, quote_centered, grid_collections_4, hero_photo_led, list_trust_strip,
  timeline, photo_founder_note, quote_accent_bar, stat_bars
- **2 are naming aliases** — Review stars → signal_review_stars (renders
  "★★★★★ 4.8 out of 5"), Signal - Countdown → signal_offer_deadline (renders a static
  date deadline — which is correct; live countdown timers do not render in most clients)
- **1 genuinely does not exist**: Text - Section — required by 9 emails
  (W-1, NL-04, NL-05, NL-09, NL-10, NL-14, NL-15, NL-19, NL-20)

And Text - Section is a consolidation, not a from-scratch build. modules_master says
verbatim: "Generic heading + richtext module. Absorbs legacy variants: Why it matters /
Next step / Five changes / Founder pillars — maintain 1 module instead of 4." All four
variants exist as complete trios.

### The 102 trios are HubSpot modules; the previews are the deployable artifacts

module.html is HubL (`{% if %}` ×89, `{% set %}` ×74, `{{ module.* }}`), marked
"Atelier Zero v7". HubSpot access is lost (AGENTS.md §3). So:

- `fields.json` = the content contract for each module (what it accepts)
- `Atelier Zero — Resolved HTML Module Previews (102)/` = the build material

### Images — migrated and live, but 4 are too heavy to send

All 9 R2 objects re-verified live: HTTP 200, key contract
`approved/<category>/<slug>/<sha256>.<ext>` via assets.hairsolutions.co → Worker
hsc-media-delivery.

| Asset | Size | Verdict |
|---|---|---|
| 5 × product feature shots (webp) | 59–110 KB | fine |
| launch-day hero png | 658 KB | too heavy |
| 3 × launch-day pngs | 2.07 / 2.18 / 2.18 MB | far too heavy |

One 2 MB PNG timed out mid-transfer at 12s. Email images want ≤200 KB. Use raw
`/v1/public/<key>` URLs, never `?variant=` — the variant transform emits AVIF, which
many email clients cannot render.

### Sender authentication — historical Phase 0 snapshot; now complete

```
SPF    v=spf1 include:_spf.google.com a mx include:_spf.mlsend.com
       include:_spf.mailersend.net ~all
DMARC  v=DMARC1; p=quarantine; rua=mailto:admin@hairsolutions.co
DKIM   shopifyemail1/2._domainkey → none    shopify1/2._domainkey → none
```

This was the verified 2026-08-19 starting state. Shopify admin subsequently showed the sender
domain as **Authenticated** on 2026-08-21, so these missing-selector observations are historical
and must not be treated as a current blocker.

`shops.shopify.com` publishes `v=spf1 ~all` — it authorizes nothing, so an SPF include
is not the fix. Shopify's real records are store-specific CNAMEs shown in the admin.

### Shopify Admin API — full access confirmed

`SHOPIFY_APP_ADMIN_TOKEN` works (`SHOPIFY_ADMIN_API_TOKEN` returns 401 — wrong key,
ignore it). Store: Hair Solutions Co, one-head-hair.myshopify.com, plan Basic. 159 scopes
granted, including everything this programme needs: read/write_customers,
read/write_marketing_events, read/write_discounts, read/write_privacy_settings,
read/write_content, read/write_metaobjects.

Verified by introspection:

- `segmentCreate` / `segmentUpdate` / `segmentDelete` all exist → the entire segment
  layer is scriptable. 17 segments exist today, 8 of which are junk Shopify defaults
  (Customers not added to companies (2)(3)(4)) that should be pruned.
- Shopify Messaging and Shopify Flow are both installed. Also installed: Judge.me
  Reviews, Trustpilot Reviews, HubSpot, and MailerLite Email Automation — that last one
  is the app behind the 631-subscriber consent incident and is still connected.
- `emailSenderConfiguration` does not exist on QueryRoot, on Shop, or as a mutation.
  Shop exposes only email, contactEmail, myshopifyDomain, primaryDomain. The sender
  CNAMEs are genuinely unreachable by API — that is now proven, not assumed.
- **Plan consequence** — Basic plan. Shopify Flow's Send HTTP Request action requires
  Grow, Advanced or Plus. On Basic it is unavailable, which removes the external-trigger
  option for J5 Consultation. J5 must run on a tag-driven segment plus Flow's Customer
  joined segment.

### Cloudflare DNS — write access confirmed

`CLOUDFLARE_API_KEY` is an API Token, not a Global Key — it authenticates as
`Authorization: Bearer`, not `X-Auth-Key` (that returns error 6103).
Zone hairsolutions.co = `44c9e2d6eb71ce0de6bb40e563bbf351`, active, 50 records.
Write access proven by creating and deleting a throwaway TXT record.

Existing DKIM at the record level: MailerLite (litesrv), MailerSend (ms1, ms2),
Fastmail (fm1–fm3). No Shopify selector. www and shop both CNAME to shops.myshopify.com.

### List health — the finding that changes sequencing

From `exports/hubspot-2026-08-18/contacts.csv` (3,967 contacts, aggregates only —
no PII read out):

| Signal | Count | Consequence |
|---|---|---|
| Marketable | 1,732 | the real addressable list, not 3,967 |
| Not marketable | 2,235 | excluded by definition |
| Documented legal basis for consent | 3 of 3,967 | provenance is undocumented for 99.9% |
| Global email optout | 29 | suppress |
| Any email open or click ever recorded | 186 | this is the engaged core |
| Non-zero total revenue | 276 | actual purchasers |
| Lifecycle: customer / MQL / lead | 435 / 697 / 2,807 | |

Two fields are unusable and should not be planned around: `hs_current_customer` reads yes
for all 3,967 (miscoded), and the eight `profile_hair_*` fields are populated on exactly
one contact — there is no hair-profile personalisation data.

This makes warm-up a real phase item, not a footnote. A brand-new sending identity plus
1,732 addresses with no documented consent basis and only 186 showing any engagement is
the textbook way to burn a domain. Start at the engaged core and widen gradually.

### Shopify Messaging — live state, read from the admin

Channels: Email, SMS and WhatsApp are all present. Nothing has ever been sent —
0 messages, 0 orders attributed.

**Sender.** info@hairsolutions.co shows Verified. That badge is address verification,
not domain authentication — DNS still publishes no Shopify DKIM selector, so the
Phase 0 CNAMEs remain outstanding. Do not read "Verified" as "authenticated".

UTM tracking is already configured: shopify_email · email · Email name + activity ID.
The convention exists; Phase 6 no longer needs to invent one.

**Delivery settings** — three switches are wrong for this list:

| Setting | State | Should be |
|---|---|---|
| Smart delivery | On | On |
| Bot filtering | Off | On |
| List health | Off | On — it blocks invalid addresses and hard bounces |
| Double opt-in | Inactive | Active — see the consent finding below |

**Automations:** two exist, both Email, both Inactive — Recover abandoned checkout and
Abandoned checkout. They are duplicates. Resolve to one before activating anything.

**Templates:** 5 email templates, all from Nov 2025, all scratch (Meet the Favorites and
Meet the favorites differ only in case; two are raw-code type). None is the Atelier Zero
system.

### The consent finding — the most serious item in this plan

| Source | Signal | Count |
|---|---|---|
| Shopify | customers | 3,958 |
| Shopify | email SUBSCRIBED | 3,780 |
| Shopify | email NOT_SUBSCRIBED | 8 |
| Shopify | SMS SUBSCRIBED | 2 |
| Shopify | has ordered ≥ 1 | 209 |
| HubSpot export | marketable | 1,732 |
| HubSpot export | documented legal basis | 3 |
| HubSpot export | any open or click, ever | 186 |

Shopify marks 3,780 contacts as subscribed, while the system those contacts came from
can document a lawful basis for three of them and has ever seen engagement from 186.
The import set a subscription state it had no provenance for. This is the 631-subscriber
incident at scale.

The company is Estonia-registered, so GDPR applies to EU contacts. Sending marketing to
3,780 addresses on that basis, from a brand-new sending identity, risks a spam-complaint
spike that burns the domain and a consent exposure. Do not send broadly until this is
resolved. Options, in order of preference: re-permission the list; or send only to the
engaged core and let the rest lapse; or document a defensible basis per contact before
any broad send.

### WhatsApp — connected, not yet operational

| Item | State |
|---|---|
| Meta Business account | Connected, +1 555 368 6894 |
| Templates | 1 — "Back in stock", Draft, not submitted to Meta |
| Quiet hours | Off — messages can send at any local hour |
| Keyword replies | none |
| Default auto-reply | not configured |
| WhatsApp-consented audience | effectively 0 |
| Regions | Shopify states 100+ supported |

Two things to verify before planning volume. The number is in the +1 555 range, which is
commonly a Meta test number — a test number can only message pre-approved recipients, so
confirm it is a production number. And turn quiet hours on before any send; marketing
arriving at 3am is a complaint generator and, in several jurisdictions, a compliance
problem.

WhatsApp is a Phase 3 channel, not a launch channel. Consent is per-channel and non-
transferable: an email subscriber is not a WhatsApp subscriber. The audience has to be
built from zero through Forms and checkout opt-in before any journey can use it.

## 2. Two decisions — settled 2026-08-19

**Platform: Shopify Messaging.** The 53 emails build and send from Shopify Messaging and
Shopify Flow. AGENTS.md §3 updated to record this, superseding the MailerLite-as-sender
note for this programme. The consent lesson behind "MailerLite's Shopify sync is
quarantine/catalog-only, never an audience source" is not retracted, it relocates:
consent state must be verified *inside Shopify*,
per channel, before any journey activates (Phase 0.5). Phases 1–4 were written platform-
neutral and are unaffected.

**Page background: transparent.** The module palette applies to cards and insets only.
`<body>` and the outer wrapper are `background-color:transparent` on all 53 — `#F6EFD9`
is not painted as a page background, and neither is any other value. The gutter goes dark
in dark-mode clients; that is intended. AGENTS.md §1 updated with the exception. This
means the resolved previews are correct for card content but must have their page/wrapper
background stripped during assembly — add that to the Phase 3 per-email checklist.

## 3. The phases

### Phase 0 — Unblock the send path

Access is no longer a blocker: the Admin API token works with 159 scopes, and Cloudflare
DNS write is proven. One item remains, and only you can start it.

1. **Authenticate the sender domain.** Shopify admin → Settings → Notifications →
   Sender email → authenticate your domain. Shopify generates four store-specific CNAMEs
   (DKIM + SPF together; no separate SPF TXT is needed) and shows them only in that
   modal — they exist nowhere in the API. Take the Cloudflare automatic option. Shopify
   configures Cloudflare-hosted domains directly, so nothing has to be copied by hand.
   If it fails, paste me the four records and I will write them via the API in seconds.
2. **DMARC needs no action.** Shopify's default guidance is `p=none` and asks for exactly
   one DMARC record. hairsolutions.co already has exactly one, at `p=quarantine` —
   stricter than Shopify asks for, and correct. Leave it. Note that automatic Cloudflare
   configuration does not touch DMARC, which is fine here.
3. **Verify, don't assume.** Confirm the selector resolves, then seed-send to Gmail and
   Outlook and read `Authentication-Results` for `dkim=pass`, `spf=pass` and `dmarc=pass`.
   Under `p=quarantine` a partial pass still quarantines. Propagation can take up to
   48 hours.
4. **Decide the warm-up ramp** before any volume: start at the 186 engaged contacts,
   widen only as reputation holds. See the list-health table above.
5. **Resolve consent provenance.** 1,732 marketable contacts carry no documented legal
   basis. Decide whether the Shopify import records a basis per contact, or whether the
   list is re-permissioned. This is the same failure mode as the 631-subscriber incident.
6. **Disconnect or quarantine the MailerLite app** on Shopify before Messaging goes live,
   so two systems cannot both claim the lifecycle.

**Gate:** a seed send authenticates on SPF, DKIM and DMARC, and the warm-up ramp is
agreed.

### Phase 1 — Close the one module gap

1. Build `text_section_light.module` + `text_section_dark.module` from
   `text_why_it_matters` — keep eyebrow, heading, body_text (richtext); drop
   pillar_1..4, person_name, role. Full trio each, plus resolved previews → 104.
2. Record the two aliases in modules_master so they are not rediscovered:
   Review stars = signal_review_stars; Signal - Countdown = signal_offer_deadline
   (static deadline is intended, not a degraded countdown).
3. Normalise PP-7b's stack: (Header) → (Header - Centered logo),
   [M10 Support strip] → [List - Support strip].
4. Fill PP-7b's missing Preview Text and CTA.

**Gate:** re-run the module mapping — every module named in all 53 stacks resolves to a
rendered artifact, zero unresolved aliases.

### Phase 2 — Re-encode the four heavy images

1. Re-encode the 4 launch-day PNGs to WebP at 1200px (600px @2x), target ≤200 KB.
   Keep PNG only where transparency is load-bearing.
2. Re-upload under the same key contract (new sha256). Verify 200 + content-type + size.
3. Record the standing rule: raw URLs only, never `?variant=`.

**Gate:** all 9 assets ≤200 KB, all 200, all referenced by raw URL.

### Phase 3 — Build the 53 emails

Build order — by revenue-at-risk and dependency, not series number:

```
J2 Cart Recovery (5) → J1 Post-Purchase (8) → W Welcome (5) →
J4 Reorder (6) → J3 Win-Back (4) → J5 Consultation (5) →
N Newsletter (20)
```

Cart recovery is the highest revenue per email on the smallest surface. Post-purchase
and Welcome fire for every new customer and subscriber. The newsletter is last because
11 of its 20 editions need real offers and real customers that cannot be invented.

**Per email:**

- Assemble from the resolved previews in the exact order of Module Stack. `()` families
  are non-negotiable; `[]` are recommended. A missing `()` is a blocked build, not a
  judgement call.
- Drop the verbatim copy from Body (AGENTS.md §1 — never rewrite it).
- Wire the CTA to its destination with the fixed UTM convention.
- Merge tags: reference copy uses `{{ firstname }}`. Map to the platform token
  (`{{ customer.first_name }}` on Shopify) with a fallback that reads correctly empty.
- Unsubscribe link + physical address on every email.
- Respect the **GATED** marker — W-1's body opens `⚠️ GATED: this audience exists only
  after the newsletter capture form ships.` The whole W series and the newsletter are
  gated on that form. Build them; do not schedule them.

**Gate per email:** renders at 320/375/430 + desktop; readable with images blocked;
alt text present; every link resolves 200; unsubscribe present; copy diffs clean
against Body.

### Phase 4 — The 11 reality-dependent newsletter editions

The Proof Bank already exists — it was in Judge.me the whole time. The
`judgeme.widget` product metafield carries the full rendered review text, reachable with
the Admin token already in hand. `proof-bank/extract_proof_bank.py` pulls it:

| Metric | Value |
|---|---|
| Unique published reviews extracted | 87 across 20 products |
| Quotable (body ≥ 120 chars) | 26 |
| Rating mix | 44 × 5-star, 43 × 4-star |
| Date range | 2025-07-26 → 2025-11-12 |
| Permission | inherent — these are published on the storefront |

**Three honest caveats:**

1. The widget metafield paginates at 5 reviews per product, so 87 of the 102 the badges
   report are reachable this way. The remaining 15 need a Judge.me CSV export or an API
   key (none is in `~/.env`).
2. No review carries a verified-buyer badge (`data-verified-buyer='false'` on all 87).
   Don't describe them as verified purchases.
3. Newest review is 2025-11-12 — nine months stale. NL-14 ("Milestones + the reviews
   that came in") implies recency, so it needs fresher material than this set alone.

The 43 four-star reviews are an asset, not a problem: an honest mixed set reads as
credible where a wall of five stars does not.

**What this unblocks now:** every Testimonial, Review stars, Proof and Stat-bars slot
across all 53 emails, plus NL-14 as a review roundup.

**What it does not:** the four Story editions — NL-02 ("My barber couldn't tell"),
NL-07 (The first 90 days), NL-12 (Gym, pool, travel), NL-17 (Consultation to
confidence). A two-line product review cannot carry a whole Story edition; those need a
real customer account. The programme already contains the machine that produces them:
PP-7 (How's It Going — Delivery +35d) and PP-7b (UGC Photo Request). Shipping J1 early
generates the Story material for later — which is exactly why J1 sits second in the
build order.

**Remaining inputs:**

- Ship the newsletter capture form — approved 2026-08-19. It gates the W series and all
  20 newsletter editions.
- Publish the four paired Education blog posts (NL-01, 06, 11, 16); those CTAs land on
  the post.
- Fill each Template edition at its slot. NL-13 must align figures with the RO-6 code;
  NL-02 needs consent verified before send.

**Gate:** zero unreplaced placeholders; every proof row traceable to a published review
or a consented customer account.

### Phase 5 — Automations, segments, consent

Needs Phase 0.4 or it is all manual UI work.

**Journey → surface mapping (Shopify):**

| Series | Surface | Note |
|---|---|---|
| J2 Cart Recovery + BR-1 | Messaging native | abandoned-cart / checkout / browse |
| W Welcome | Messaging native | Welcome new subscribers |
| J1 Post-Purchase | native + Flow | PP-4 is fulfilment-event triggered → Flow |
| J4 Reorder | Flow | custom timing off delivery date |
| J3 Win-Back | Flow | ends in a real sunset |
| J5 Consultation | Flow + external | no native Shopify trigger exists |
| N Newsletter | Campaigns | not an automation |

**Segments.** Build segments before automations. Naming:
`MKT | Email | <state> | <qualifier>`.

**Newsletter audience** is a formula, recomputed every send — never a static list:
marketable + News & Offers − suppression − active Cart Recovery / Win-Back / J5
enrollees.

**Frequency cap:** 2 marketing emails per contact per 7 days. Journeys always win the
slot; the newsletter skips. No platform enforces this natively — it has to be built as
an exclusion inside the newsletter audience. This is the single most important operating
rule in the programme.

**Collision matrix** across all 6 journeys + newsletter before anything activates.
Known collisions: J1 and J4 both key off delivery date (PP-7 +35d, PP-7b +42d,
RO-1 +45d); J3 Win-Back and J4 Reorder both target lapsed purchasers.

**Exit conditions:** a purchase exits every recovery and reorder journey. WB-4
("Last Email From Us") must actually suppress.

**Abandoned-checkout email** currently does not count toward Messaging email billing,
and its recipient setting can be switched to "All customers" — do not, without a
jurisdiction and consent review.

**J5 has no native trigger.** Decide: tag-driven segment + Flow "Customer joined
segment", or an external trigger.

**Gate:** the full QA suite — eligible subscriber, ineligible/unsubscribed, missing
personalization, already-purchased-before-a-delayed-message, overlapping-journey
customer, expired discount, unavailable product, mobile render, link/UTM, and
turn-off-during-wait behaviour. Then explicit approval before any activation.

### Phase 6 — Measure

The programme doc's KPI-per-format is unusually good; use it as written.

| Format | KPI | Reads |
|---|---|---|
| Education | clicks to paired blog post | does the content answer real questions |
| Story | replies | do readers see themselves in it |
| Offer | revenue | was it worth interrupting for |
| Brand | unsubscribe rate | a no-offer email should cost ~zero |
| Launch | product-page sessions | did the positioning make people look |

Journeys get a primary KPI and a list-health guardrail each. Do not optimise PP-7
(a check-in) or WB-4 (a sunset) on revenue. Fix the UTM convention before the first
send. Use more than one attribution model for material decisions.

## 4. Risks

| Risk | Mitigation |
|---|---|
| Sender auth slips → everything slips | Phases 1–4 are fully parallel with Phase 0; only Phase 5 activation depends on it |
| No Admin API token → Phase 5 becomes hand-clicking | Provision in Phase 0.4 |
| Frequency cap unenforced → fatigue, unsubscribes | Build it as an audience exclusion; the newsletter is the thing that yields |
| Template editions filled with invented content under pressure | Proof Bank Permission = Yes gate; [OFFER — confirm before send] placeholders that fail loudly |

## 5. Open decisions (pre-existing, unchanged)

- LAUNCH30 end date — conditional on whether the launch is over
- Pruning the 769 cold-intent subscribers — destructive
- Cart discount: discount vs none
- Whether the 113 previously-translated Shopify-Liquid emails retire now that the 53
  are the source of truth

## 6. Not done deliberately

- Nothing live was touched
- The module was not built — Phase 1, pending plan approval
- Neither contradiction in §2 was resolved by inference

## 7. B2B and wholesale — not started, deliberately

Confirmed with Vincent 2026-08-19: the B2B strategy has not been planned or designed
yet. No audience, no catalog, no copy, no lifecycle. This is a stated position, not an
omission — do not invent a B2B programme, and do not fold trade messaging into the 53
D2C emails.

**Verified constraints for when it does start:**

- Native Shopify B2B (company profiles, B2B catalogs, per-buyer price lists, payment
  terms) is Plus-only. This store is Basic. `companies` returns 0, and all ten catalogs
  are MarketCatalog or AppCatalog — there is no B2B catalog, and per Vincent the catalog
  layer has never been properly built at all.
- On Basic the routes are: quote-led selling via draft orders (`write_draft_orders` is
  granted), a tagged wholesale segment with its own price rules, a third-party B2B app,
  or a plan upgrade. That is a commercial decision.
- Demand signal already exists: "Do you offer bulk or wholesale orders?" sits in the
  Shopify Knowledge Base as a top unanswered question. Answering it is worth doing
  independently of any programme work, because it is being asked now and returns nothing.
- A trade lifecycle is its own shape: enquiry → qualification → sample → quote →
  first order → reorder at volume → account review. Its proof is margin, MOQ, lead time,
  batch consistency and terms — and those claims carry contractual weight that consumer
  reassurance does not.
