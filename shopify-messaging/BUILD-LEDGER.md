# BUILD-LEDGER — the 53-email Shopify Messaging programme

> What has actually been built for the CAMPAIGN-PLAN.md programme (J1–J5, W, N — 53 emails).
> Nothing here is pushed, scheduled, or sent — local artifacts only (AGENTS.md §2).
> Platform: Shopify Messaging + Shopify Flow. Palette: module palette from the resolved
> previews (AGENTS.md §1). Page background is transparent on every email.

## Standing rules

- **Image URLs: raw `/v1/public/<key>` only — never `?variant=`.** The variant transform
  emits AVIF, which many email clients cannot render. Recorded 2026-08-19, re-verified
  Phase 2.
- Key contract: `approved/<category>/<slug>/<sha256>.<ext>` — sha256 is of the uploaded
  file, so a re-encode means a new key. Old keys are left in place (immutable, content-
  addressed); references move, objects are not deleted.
- Upload path: `wrangler r2 object put hsc-media-origin/<key> --file <f> --remote`
  with `CLOUDFLARE_API_TOKEN=$CLOUDFLARE_MASTER_ACCOUNT_API_TOKEN`.
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
