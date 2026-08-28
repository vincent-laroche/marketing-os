# Social Media Atelier Zero — Figma Design System & Campaign Build Plan

**Prepared:** 2026-08-05
**Model:** Same three-layer approach used for `Hair Solutions Co — Atelier Zero Email Modules`, applied to social.
**Target file (new):** `Hair Solutions Co — Atelier Zero Social Modules` (separate Figma file, same team/project as the Storefront and Email files)

---

## 0. What I checked before writing this

- Read `PROJECT.md`, `README.md`, `AGENTS.md`, `docs/SOCIAL_MEDIA_FOLDER_AUDIT_2026-07-27.md`, `reference/README.md`, `reference/TEMPLATE_CATALOG.md`, `templates/manifest.json`, and `campaigns/2026-rebrand-launch/campaign.snapshot.json` in the connected `Social Media Marketing` folder.
- Inspected the two Storefront Figma nodes directly: `95:2` (`03 — Library / Foundations`, root frame `96:2`) and `95:3` (`04 — Library / Components`, root frame `105:2`, components C01–C37).
- Pulled every local Figma variable collection from that file — this is the real, current token system, richer than what Email Marketing used.

Everything below is grounded in that material, not assumed.

---

## 1. What already exists (source of truth)

### Brand authority chain (per `AGENTS.md`)
1. `/Users/vMac/08_brand/brand-design-system/brand-design-system.html` — brand master
2. `/Users/vMac/08_brand/atelier-zero-design-system-from-theme.md` — measured visual authority
3. `/Users/vMac/08_brand/brand-design-system/specs/PLATFORM_SOCIAL.md` — social platform constraints
4. `/Users/vMac/08_brand/logos` — approved logo source
5. `campaigns/2026-rebrand-launch/` — active retained campaign package
6. `templates/` — reusable source-controlled HTML template system

The Storefront Figma file (`tIxpf4Pjf3uYJMHwH2WVz4`) is the same Atelier Zero lineage as this authority chain — its Foundations/Components pages are the Figma-native expression of items 1–2. This plan treats it as the canonical **design-token source**, same role it played for Email.

### Real token system (Storefront file, confirmed via API)

| Collection | Modes | What it holds |
|---|---|---|
| `HSC / Primitives` | Default | 28 raw values — paper/bone/ink scale, coral/mustard/olive accents, ink/bone alpha ramps |
| `HSC / Color` | **Paper, Warm, Deep, Ink** (4 modes) | 17 semantic roles: surface/canvas, surface/section, surface/raised, surface/media, text/primary–tertiary, text/inverse, text/on-accent, accent/primary, accent/secondary, border/default–strong, icon/default, icon/accent, focus/ring |
| `HSC / Product Hair` | Default | 13 hair-color swatches |
| `HSC / Space` | Default | 31-step spacing scale (000–140) |
| `HSC / Radius` | Default | 7 roles (none, option, nested, card, plate, pill, field-multiline) |
| `HSC / Geometry` | Default | stroke weights, icon sizes, control sizes, opacity roles |
| `HSC / Layout` | Desktop/1440, Mobile/480 | canvas width, gutters, header/footer/button/field dimensions |
| `HSC / Typography` | Desktop, Mobile | 4 families (display/body/serif/mono), 6 weights, 11 size roles, matching line-heights and tracking |
| `HSC / Motion` | Default | 4 durations, 2 easings |

**This is a 4-mode color system, not 2.** Email Marketing simplified to Paper/Ink because email clients can't reliably do more. Social has no such constraint — and critically, **the campaign content already references these exact mode names** (`campaign.snapshot.json` day 1: `"archetype": "wordmark (ink)"`). The plan below keeps all 4 modes live, the same way the source file does.

### Components already built (Storefront file, C01–C37)
37 production components exist: Logo, Nav Link, Icon/Glyph, Icon Button, Action/Button, Text Link, Eyebrow, Badge, Filter Chip, Option Tile, Hair Swatch, Field/Input (Light+Dark), Divider, Rating/Stars, Accordion, Media/Image Frame, Surface/Card, Card/Product, Card/Article, Card/Directory, Stat, Testimonial, Notice, Progress/Dashes, Quantity Stepper, Key-Value Row, Cart Line Item, Cart Order Summary, Nav/Header, Mobile Drawer, Footer, Newsletter Form, Search Form, Product Gallery, Purchase Panel, Custom Order Step, Contact Form Frame. Several of these (Logo, Icon/Glyph, Rating/Stars, Media/Image Frame, Divider, Eyebrow, Badge, Testimonial) are directly reusable inside social templates instead of rebuilding from scratch.

### What exists in the Social Media Marketing project today
- **16 HTML templates**, source-controlled (`templates/src/templates.mjs` + `template.css`, generated into `templates/html/`):
  - **Feed (7):** hero-brand-post, single-product-post, collection-post, quote-testimonial-post, blog-article-post, sale-promo-post, announcement-post
  - **Stories (3):** story-product, story-quote, story-sale
  - **Carousels (4):** how-it-works (5 frames), before-after (3), drop-reveal (4), testimonial-set (3)
  - **Reels (2):** reel-cover (1080×1350), reel-storyboard (5-beat, 1080×1920)
- **Canvas sizes + safe zones** (from `manifest.json`, this is load-bearing and must carry into Figma exactly):
  - `feed-square`: 1080×1080, 160px inset
  - `feed-portrait`: 1080×1350, 160px top/bottom, 80px sides
  - `story-reel`: 1080×1920, 250px top/bottom, 160px sides
- **Active campaign**: `campaigns/2026-rebrand-launch/campaign.snapshot.json` — a 90-day calendar (104 scheduled rows) and a detailed 30-day creative draft (44 feed items + 98 Story frames across 4 phases: Opening Week, Foundation, Resonance, Conversion), plus a weekly Stories rhythm (Mon–Sun recurring content types).
- **Hard content-safety rules** (`AGENTS.md`, apply to everything built in Figma too):
  - No AI-generated imagery or stock photography for brand production
  - No invented facts, offers, testimonials, customer quotes, or consent
  - Customer proof/media requires exact-use written consent on file
  - Nothing gets published/scheduled from this work — it's design production only

### Gap: archetypes vs. templates (flagging, not resolving yet)
The calendar's 30+ distinct `archetype` labels (product, quote, how-it-works, typo, before-after, typo editorial, BTS reel, founder reel, typo (ink), testimonial reel, wordmark (ink), manifesto carousel, etc.) don't map 1:1 to the 16 templates — most are **content variants of a shared structural template**, exactly like Email's many `Text - X` placeholders all resolving to one `Text Block — generic` component. But at least one likely gap stands out on inspection: the Day-1 `"quote"` archetype ("Same company. New standard.") is a **brand statement**, not a customer testimonial — yet the only quote template in the library (`quote-testimonial-post`) is explicitly gated for *consented customer proof*. Using it for a brand-voice line would be a category error. Phase 2 below runs the full archetype-to-template reconciliation properly (the way I did the M1–M14 gap analysis for email) instead of guessing here.

---

## 2. Part 1 — Figma project architecture

One new file: **`Hair Solutions Co — Atelier Zero Social Modules`**. Page structure, mirroring the email project's proven shape:

| # | Page | Purpose |
|---|---|---|
| 1 | `01 — Social Design System — HSC Brand` | Color (4 modes), Typography (social-scaled), Spacing/Radius, Logo lockups, Icon set, Safe-zone guides — all pulled live from the Storefront Foundations/Components |
| 2 | `02 — Social Template Library — Paper／Warm／Deep／Ink` | The 16 templates rebuilt as real, variable-bound Figma components, each with mode variants matching how the campaign actually uses them (not all 16×4 — see §3) |
| 3 | `03 — Social Custom Modules — Gaps` | Whatever the Phase 2 reconciliation turns up (e.g., a Brand Statement/Wordmark static distinct from customer-quote) |
| 4 | `04 — Campaign · Phase 1 Opening Week` | Real, populated post/Story/carousel/Reel frames for Days 1–7 |
| 5 | `05 — Campaign · Phase 2 Foundation` | Days 8–~15 |
| 6 | `06 — Campaign · Phase 3 Resonance` | Days ~16–~23 |
| 7 | `07 — Campaign · Phase 4 Conversion` | Days ~24–30 |
| 8 | `08 — Campaign · Weekly Stories Rhythm (reference)` | The 7 recurring Monday–Sunday Story concepts as a standing reference set, since these repeat past day 30 |

Pages 4–7 boundaries follow the calendar's own 4 named phases exactly (`1 - Opening Week`, `2 - Foundation`, `3 - Resonance`, `4 - Conversion`) rather than an arbitrary day-count split — one page per phase keeps each page to roughly 25–35 individual asset frames, which is what page 34 in the email file handled comfortably.

Within each campaign page, frames are organized **by day**, each day showing: Hero feed post → Filler feed post(s) → that day's Story frame sequence → any carousel/Reel scheduled that day. This mirrors the calendar's own `day` grouping in `campaign.snapshot.json`.

---

## 3. Part 2 — "Social Media Atelier Zero" Design System page contents

Built the same way page 31 was for email: pull real tokens, adapt only what the medium requires.

1. **Color** — all 17 semantic roles × all 4 modes (Paper/Warm/Deep/Ink) as swatch grids, directly bound to `HSC / Color` variables (no re-invention, no hex duplication — same binding technique used throughout the email build: `setBoundVariableForPaint`).
2. **Typography** — the real `HSC / Typography` scale, but with a **social legibility pass**: feed/Story text is read at thumbnail size and on a phone screen, not in an email client, so the design system page must show each type role at its *actual rendered pixel size on a 1080px canvas* next to its *shrunk mobile-feed-thumbnail equivalent* (~110px wide), so we can see what still reads. This is the one real adaptation step, parallel to Email's font-fallback pass.
3. **Safe-zone guides** — a first-class section, not an afterthought, since two platforms (Instagram/TikTok UI chrome) actively cover the outer frame. Three guide overlays built directly from `manifest.json`: feed-square (160px inset), feed-portrait (160/80px), story-reel (250px top/bottom, 160px sides). These get embedded as a toggleable guide layer in every template built afterward.
4. **Logo lockups** — reuse Storefront C01 (Brand/Logo component set) directly rather than re-deriving; add social-specific crops (square profile-picture lockup, Story-safe centered lockup).
5. **Buttons / Links / Badges / Chips** — reuse Storefront C05 (Action/Button), C06 (Text link), C08 (Badge) directly as instances, not rebuilt — these are already token-bound and correct.
6. **Icon set** — reuse Storefront C03 (Icon/Glyph) directly.
7. **Motion reference** — the `HSC / Motion` durations/easings, documented as a reference panel only (informs Reel pacing notes, not an animatable Figma property).

Net effect: unlike Email (which had to invent font fallbacks and reduced-radius buttons because email clients can't render the real system), the Social design system page is **mostly direct reuse** of Storefront components plus one real adaptation (legibility-at-size) and one new addition the Storefront file doesn't need (safe-zone guides).

---

## 4. Part 3 — Building post/Story frames already branded from the start

Same clone-based assembly technique proven on the 88 emails, adapted for fixed-canvas social formats instead of flowing email frames:

1. **Build each of the 16 (or 17, pending Phase 2) templates once per canvas size as a true component**, fully variable-bound to `HSC / Color`, `HSC / Typography`, `HSC / Space`, `HSC / Radius` — built once in whichever mode is its sensible default, then mode-paired via the same `clone()` + `setExplicitVariableModeForCollection()` technique used for every email module. Because the source system has 4 modes, not 2, each template gets built once and can resolve to any of the 4 without rebuilding — mode becomes a per-instance choice, not a per-template rebuild.
2. **Populate with real planned copy, not generic placeholder text.** This is a meaningful advantage over Email: `campaign.snapshot.json` already contains actual approved `hookHeadline` copy for every calendar row and every Story frame line (e.g., Day 1: *"A new chapter starts today."*, *"Same company. New standard."*). Frames get built with that real copy directly, not a reusable dummy sentence — because unlike the email module library, these aren't reference components, they're production-intent assets for a specific dated campaign.
3. **Image slots stay honest placeholders.** Per the explicit "no AI imagery, no stock photography" rule, every photo/product/BTS slot is built as a neutral flat-fill placeholder (the same warm-gray swatch treatment used for email product/photo modules) labeled with what real asset needs to go there (e.g. "Studio QC photo — Rio, consent on file required"), never a generated image.
4. **Anything gated by `TEMPLATE_CATALOG.md`'s "hard gate" column gets a visible flag on the frame** — sale/promo frames, testimonial/quote frames, and announcement frames are marked with a small red "VERIFY BEFORE USE" tag bound to nothing (plain static label) so nobody mistakes a design-stage frame for a publish-ready one. This directly encodes the AGENTS.md safety rules into the artifact itself rather than relying on someone remembering the rule.
5. **Carousels and Reel storyboards build as a connected frame sequence** (5/3/4/5 frames per the manifest), each frame individually safe-zone-checked, with the first carousel frame flagged "must stand alone" per the catalog's own rule.

---

## 5. Execution phases (what I'd actually run, in order)

| Phase | Work | Est. scope |
|---|---|---|
| **1** | Create the Social Atelier Zero file + Design System page (color, type, safe zones, logo/button/icon reuse) | 1 page, ~7 sections |
| **2** | Reconcile all 30+ campaign archetypes against the 16 templates; identify true structural gaps (e.g. Brand Statement/Wordmark static) the way M1–M14 were identified for email | Analysis pass, likely 1–4 new template types |
| **3** | Build the Template Library page — 16(+gap) templates × their real-usage modes, each as Paper/Warm/Deep/Ink-capable components | ~20 components |
| **4** | Build Phase-1 "Opening Week" campaign page (Days 1–7) fully populated and branded, as a pilot — verify visually before scaling | ~7 days × (2–3 feed + 3–5 Story frames + occasional carousel/Reel) |
| **5** | Fan out to Phases 2–4 (Foundation, Resonance, Conversion) once the pilot is approved | Remaining ~23 days |
| **6** | Build the Weekly Stories Rhythm reference page (the 7 recurring Mon–Sun concepts, since they recur past Day 30) | 7 frame sequences |
| **7** | Final verification pass — safe-zone compliance check, mode-contrast check, hard-gate flags present on every gated frame | Screenshot sampling across all pages |

This is proposed as a plan only, per your request — nothing above has been built yet. Confirming before I start Phase 1 (or flag which phase you'd like first) makes sense given the scope, especially the Phase 2 gap analysis, which may change how many template types we're actually building.

---

## 6. Open questions worth a quick answer before I start building

1. **New Figma file or a new page inside the Storefront/Email file?** I've assumed a dedicated new file (cleanest separation, matches how Email got its own file rather than living inside Storefront).
2. **Default mode per template category** — e.g. should `hero-brand-post`/wordmark statics default to Ink (as Day 1 already specifies), while product/education posts default to Paper? I can infer sensible defaults per archetype from the calendar data itself rather than asking per-template.
3. **How far to build campaign content** — just the 30-day creative draft (44 feed + 98 Story frames, fully detailed), or also the remaining 60 days of the 90-day calendar (which has slot/format/archetype but not full frame-by-frame Story scripts yet)?
