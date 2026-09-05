# BUILD-LEDGER — the 53-email Shopify Messaging programme

> What has actually been built for the CAMPAIGN-PLAN.md programme (J1–J5, W, N — 53 emails).
> Nothing here is pushed, scheduled, or sent — local artifacts only (AGENTS.md §2).
> Platform: Shopify Messaging + Shopify Flow. Palette: module palette from the resolved
> previews (AGENTS.md §1). Page background is transparent on every email.

## Standing rules

- **Image host is `assets.hairsolutions.co` (R2 `hsc-media-origin`).** Decided 2026-09-05 by
  Vincent (#134). All 54 image references in the built emails resolve there; Cloudinary and the
  HubSpot portal CDN are both zero. The wordmark lives at
  `approved/brand/wordmark-dark-on-transparent/cfcbef6a…233.png` — uploaded and verified
  2026-09-05 as HTTP 200, `image/png`, 16,400 bytes, sha256 matching source.
- **Image URLs: raw `/v1/public/<key>` only — never `?variant=`.** The variant transform
  emits AVIF, which many email clients cannot render. Recorded 2026-08-19, re-verified
  Phase 2.
- Key contract: `approved/<category>/<slug>/<sha256>.<ext>` — sha256 is of the uploaded
  file, so a re-encode means a new key. Old keys are left in place (immutable, content-
  addressed); references move, objects are not deleted.
- Upload path: `wrangler r2 object put hsc-media-origin/<key> --file <f> --remote`
  with `CLOUDFLARE_API_TOKEN=$CLOUDFLARE_MASTER_TOKEN`.
  **Corrected 2026-09-05 (#134):** this line previously named
  `CLOUDFLARE_MASTER_ACCOUNT_API_TOKEN`, which `GET /user/tokens/verify` reports as
  *Invalid API Token*. `CLOUDFLARE_MASTER_TOKEN` is active, resolves the HSC Account, and
  reads all five R2 buckets.
  **Trap:** without `--remote`, wrangler 4.72 prints "Upload complete" against a local
  simulation and the object never exists — always verify with a public HEAD after upload.
  (The `CLOUDFLARE_ACCESS_KEY_ID`/`CLOUDFLARE_SECRET_ACCESS_KEY` pair in ~/.env is not
  valid for this bucket — direct S3 API returns 401.)

## Phase 2 — image re-encodes (2026-08-19)

All 9 programme assets live at `https://assets.hairsolutions.co/v1/public/<key>`,
HTTP 200, correct content-type, ≤ 200 KB each. GATE GREEN.

### Product feature shots (already fine, unchanged)

| Slug | Size | Key |
|---|---|---|
| lace-elite | 110 KB webp | approved/products/lace-elite/e207b4ac67ca4f36be3e8366734ab33fee2327e1cee3fd80d5cd6d4288900170.webp |
| lace-pro-ld | 91 KB webp | approved/products/lace-pro-ld/86e7e7e765820cecc2df9d06f27a007449c8c6e8869a3e9f3d1e161649c7e0f3.webp |
| micro-skin-md | 59 KB webp | approved/products/micro-skin-md/d29da587cc353ab7df05bc61c48ed9f36e806daeaa2d328716ab27d559b47536.webp |
| mono-fusion-lf | 67 KB webp | approved/products/mono-fusion-lf/5eeaf8380075484e5fba4c0983b56fb98a75a18c23a08a4b27f63a3163ed0adb.webp |
| mono-pro | 85 KB webp | approved/products/mono-pro/13b047050cb089fb5e44f34b2cc0c69385708004423768f6b363966ba64b6725.webp |

### Launch-day PNGs → WebP (re-encoded 2026-08-19)

No alpha channel in any source (verified `magick identify` — transparency not
load-bearing), so all four became lossy WebP, q82, method 6.

| Source PNG | Before | After (WebP) | New key |
|---|---|---|---|
| hero 640×800 | 658 KB | **43 KB** — 640×800 native | approved/marketing/launch-day/15d29fa43166728d13a4eb021c515a230b27624bcc7658f797cae4e8be957b9f.webp |
| square A 1254×1254 | 2.07 MB | **104 KB** — 1200×1200 | approved/marketing/launch-day/eb688762ff7ff7c6c34fc5df1a2dcf0d8cf25145239bd08d7c48c508a018e94c.webp |
| square B 1254×1254 | 2.18 MB | **124 KB** — 1200×1200 | approved/marketing/launch-day/9eea83eb4d06541c98500bf1dea924b7edabf2ddcbe4a308f7d05dc443205f50.webp |
| square C 1254×1254 | 2.18 MB | **142 KB** — 1200×1200 | approved/marketing/launch-day/ec31b7fbf02b92f64715594e2086147a22064cd8460c7e79794cf44b6499b5e9.webp |

**Deviation from plan:** the hero source is only 640×800 px — smaller than the 1200px
target. It was re-encoded at native size (upscaling adds bytes, not detail). At 43 KB it
comfortably meets the ≤200 KB gate; flag for Vincent if a sharper hero is wanted, the
1200px slot is ready.

Machine-readable mapping for the Phase 3 build: `tools/build53/asset_map.json`.

## Phase 3 — email builds

(filled as series complete)

### Phase 3 — the 53 email builds (2026-08-19)

`python3 tools/build53/build_emails.py` assembles all 53 from the resolved previews and the
`emails_master` Body column. **51 GREEN · 2 BLOCKED · 0 ISSUES.** Local artifacts only —
nothing pushed, scheduled or sent.

| Series | Emails | GREEN | BLOCKED | Avg size |
|---|---|---|---|---|
| J2 Cart Recovery | 5 | 5 | 0 | 15.3 KB |
| J1 Post-Purchase | 8 | 8 | 0 | 13.9 KB |
| W Newsletter Welcome | 5 | 5 | 0 | 15.3 KB |
| J4 Reorder | 6 | 5 | 1 | 13.7 KB |
| J3 Win-Back | 4 | 4 | 0 | 13.1 KB |
| J5 Consultation | 5 | 5 | 0 | 16.9 KB |
| N Newsletter | 20 | 19 | 1 | 18.4 KB |

Mean 16.5 KB, max 26.9 KB — every email is under the 102 KB Gmail clipping threshold.

**Structural gate — 53/53 pass:** `{{ unsubscribe_url }}` present · physical address present ·
hidden preheader present · mobile `@media` block present · `<body>` and outer wrapper
`background-color:transparent` · `alt` on every `<img>` · no unfilled `{{slot:}}` · no leftover
HubL · no dead image host · no double-escaped entities.

**Two BLOCKED — both are source-data gaps, not build failures.** Per CAMPAIGN-PLAN.md Phase 3,
a missing `()` module is a blocked build, not a judgement call. Both need Vincent's decision:

- **RO-4 · Same Spec Or Change — Delivery +110d** — stack requires `Text - Customer snapshot`, the Body has no matching block.
- **NL-16 · Education — Maintenance myths** — stack requires `Comparison`, the Body has no matching block.

**Gated (14 emails)** carry the `⚠️ GATED` preamble as an HTML build note — the W series and the
newsletter depend on the capture form shipping. Built, not schedulable.

**128 loud placeholders** across the set (`border:2px dashed #EA6452`). Every `[PULL from Proof
Bank ...]`, `{{ dynamic: ... }}` and `[OFFER ...]` renders visibly rather than being silently
invented. None of these emails is sendable until they are replaced — that is Phase 4.

**Four CTA destinations are deliberate `#TODO-` placeholders** — they are per-order or per-shipment
automation values that only exist at Phase 5 (`PP-1` order URL, `PP-4` tracking URL), or have no
destination yet (`PP-7` has no public review-submission page; `PP-7b` — `/pages/share-your-look`
is 404).

**Deviations recorded (38 emails):**

- overflow carried into (Testimonial) — 29
- overflow carried into (Product - Dynamic recommendations) — 8
- overflow carried into (Signal - Promo code) — 6
- overflow carried into (FAQ) — 6
- overflow carried into (Photo - Feature story) — 4
- overflow carried into (Commerce - Viewed product) — 2
- overflow carried into (List - Support strip) — 2
- dual CTA rendered in-wrapper — 2
- (Comparison) copy is an option list, not a two-sided comparison — 2
- overflow carried into (Column - Image and text) — 2
- overflow carried into (List - Trust strip) — 2
- overflow carried into (Comparison) — 1
- overflow carried into (Button - Primary CTA) — 1

Overflow carry is the rule that keeps copy verbatim: when a module has fewer slots than the copy
has lines, the surplus is appended to that module rather than dropped. The 20 real-prose carries
are all Story-edition narrative arcs (NL-02, NL-07, NL-12, NL-17) that a 3-quote testimonial
module cannot hold; the other 28 are `[PULL ...]` placeholders.

**Images.** The only image in all 53 is the wordmark. The five product shots and four launch-day
WebPs re-encoded in Phase 2 are not referenced by any email — no module stack in the reference
file calls for them. Flag for Vincent: either the photo modules need image assignments, or Phase 2
served a different purpose than these 53.

#### Build-tool defects found and fixed this session

The builder existed but had never completed a full run — it crashed at email 6. Fixed, in
`tools/build53/`:

| # | Defect | Effect |
|---|---|---|
| 1 | `r_text_opening` / `r_masthead` took 2 positional args, dispatched with 3 | crash at PP-1 |
| 2 | `r_image_text` never returned its fragment | crash at PP-3 |
| 3 | `drop_empty_slots` capped at 6 slots per template | 41 emails shipped literal `{{slot:...}}`; 9 had a `<span>` inside `src="` |
| 4 | `footer_social` logo defaulted to the HubSpot portal CDN | 24 emails pointed at a host the account no longer controls |
| 5 | `r_qa` wrote only the half before the em dash when the target had one slot | every `Q — A` line in `List - Questions` lost its answer |
| 6 | `r_strip` split any line on its first em dash | prose sentences cut into label/value and rendered without a separator |
| 7 | **empty-default fields never got a slot** in `gen_templates.py` | `comparison` items, `timeline` labels/text, `stat_bars` labels, `text_offer_discount` percentage/code — 21 slots the renderers wrote into but that did not exist. Now placed by aligning the HubL source's tag stream with the preview's |
| 8 | `4.8 out of 5` hardcoded in `signal_review_stars` | an unverified aggregate rating in 10 emails. The Proof Bank is 44×5-star + 43×4-star (≈4.5) and carries no verified-buyer badge — the claim was not supportable. Now a slot; with no source it renders as a loud placeholder |
| 9 | `Book a consultation` hardcoded in `text_base_type_guidance` | CR-3 and BR-1 each rendered two different button labels |
| 10 | Three previews still carried `{# ... #}` HubL comment blocks | visible template commentary inside PP-7b, RO-3, C-0 |
| 11 | `loud_inline_tokens` re-escaped already-escaped text | `&amp;amp;` rendering literally |
| 12 | copy queue keyed by family name, not resolved slug | PP-7b's body says `[M10 Support strip]`, its stack says `[List - Support strip]`; the block was orphaned and the module dropped |
| 13 | `r_comparison` split any list across two columns | the module frames column A as "The old routine" and B as "With Atelier Zero" — W-2 and NL-01 are plain option lists, so it asserted a contrast the copy never makes. Now labels blank + deviation |
| 14 | coverage check compared text literally | false "copy not found" wherever a token span split a sentence |
| 15 | `--check-links` was a dangling flag with no implementation | the Phase 3 "every link resolves 200" gate could not run. Implemented as `tools/build53/check_links.py` |

Defects 3–13 each silently changed what a subscriber would have received.

#### Link gate — GREEN (2026-08-19)

`python3 tools/build53/check_links.py` — report at `shopify-messaging/link-report.json`.

| Class | Count | |
|---|---|---|
| OK (HTTP 200) | 47 | every live URL, redirects followed |
| TOKEN | 2 | `{{ unsubscribe_url }}` (53 emails), `{{ checkout.url }}` (2) — resolved at send |
| TODO | 4 | deliberate loud placeholders: PP-1 order URL, PP-4 tracking URL, PP-7 review page, PP-7b UGC page |
| MAILTO | 1 | `mailto:info@hairsolutions.co` |

**Trap:** the storefront returns HTTP 429 under parallel probing — a first pass with 8 threads
reported 30 false failures. The checker probes serially with backoff for this reason. A 429 from
hairsolutions.co is rate limiting, never a broken link.
