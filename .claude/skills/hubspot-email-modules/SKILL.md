---
name: hubspot-email-modules
description: Create, fix, or deploy Hair Solutions Co. HubSpot Design Manager email modules — module.html/fields.json/meta.json structure, light/dark theming, logos, palette, field editability, and deployment to HubSpot account 50966981 via the hs CLI. Use whenever the user asks to build a new email module, fix a broken/locked/frozen module control, wire up an image or color field, correct module colors, add a module family, or push module changes to HubSpot Design Manager. Also use when the user mentions "Design Manager", "email_modules", "hs cms", or a module not being editable in the drag-and-drop email editor.
---

# HubSpot Email Modules — Hair Solutions Co.

Building blocks for HubSpot marketing emails, deployed as HubSpot Design Manager custom modules in account **50966981**.

## This is a living document

Whenever you hit a bug, discover a wrong assumption, or find a better pattern while doing this work, **update this file** (or the relevant reference file) before ending the session. Vincent has asked for this explicitly — the point is that the next session doesn't re-learn the same lesson the hard way. Add it to "Known pitfalls" below with what broke and what fixed it, not just the fix in isolation — the *why* is what keeps this file trustworthy instead of turning into another stale doc nobody checks.

This file has already been rewritten once because it had drifted badly: it pointed at a local repo (`Email Marketing Studio`) that no longer exists, a palette that was superseded weeks earlier, and an `npm run build` workflow this project doesn't have. None of that was caught until someone actually tried to follow it. **Before trusting anything below about file paths, palettes, or "current state," verify it against the live account with `hs cms list`/`hs cms fetch` — this doc describes the system, it is not the system.**

## Ground truth, not local repo

There is **no local source-of-truth repo** for these modules. The live HubSpot Design Manager *is* the source of truth. Work like this:

1. `hs cms fetch email_modules ./some-scratch-dir --account 50966981` to pull current state
2. Edit the fetched files locally
3. `hs cms upload ./some-scratch-dir email_modules --account 50966981` to push
4. `hs cms fetch` again into a fresh dir and diff/verify — **never trust that upload succeeded just because the CLI said so; confirm by reading it back**

Auth is already configured (`hs accounts list` shows `HairSolutionsCo [standard] (50966981)` as default). Don't pass `--clean` on upload unless you intend to delete anything at the destination not present in your local folder — it's a live, shared system other people (and other agent sessions) also touch.

## Current live structure (verify with `hs cms list email_modules`)

```
email_modules/
  <family>.module/        — light theme
  <family>_dark.module/   — dark theme
  cart-recovery/          — small, older, cart-recovery-specific set (header+hero combo, reassurance, cta+faq)
```

There is no `core/`, `launch/`, or `newsletter/` subfolder structure — if you see a reference to one (in an old doc, a skill, a script), it's describing a state that has since been flattened/reorganized. Check `references/module-inventory.md` for the actual current family list — but re-verify counts with `hs cms list` since this project's module set has grown mid-session more than once.

**Theming convention (superseded 2026-08-10):** the twin-file split (`family.module` light + `family_dark.module` dark) still exists as folders, but both files now carry the identical HTML and a `surface` choice field; only the default differs (light defaults `paper`, dark defaults `ink`). The `_dark` folder is a redundant alias kept so existing email drafts don't break — not a separate design. Do not hand-maintain two divergent copies.

## The module shell (every module uses this)

```html
<style>@media only screen and (max-width:480px){.final-card{width:100%!important}.final-pad{padding:24px!important}.final-card td{box-sizing:border-box}}</style>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;background:transparent;border-radius:16px;overflow:hidden;border-collapse:separate;">
  <tr><td align="center" style="padding:0;border-radius:16px;">
    <table role="presentation" class="final-card" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px;max-width:100%;background:{{ c.bg }};border-radius:16px;overflow:hidden;border-collapse:separate;">
      <tr><td class="final-pad" style="padding:32px;font-family:Arial,Helvetica,sans-serif;color:#15140F;font-size:16px;line-height:1.55;">
        <!-- module content -->
      </td></tr>
    </table>
  </td></tr>
</table>
```

**The outer table's background must be `transparent`, not the theme color.** Only the inner 600px `.final-card` table gets the actual card color. This was a real bug live in every module for a while: both tables had the same background, so if the email/section canvas is ever wider than 600px, the outer wrapper bled a colored rectangle out from behind the card — exactly the "wrapper with a background" look Vincent explicitly does not want. If you're building a new module and it looks fine at 600px but you're not sure why the wrapper background is set to a color, it shouldn't be — copy the transparent pattern above.

Single flush card, 16px radius, no double-background — that's the whole visual language. Don't add an additional outer band or container around this.

## Current palette — Atelier Zero v1

Verify against `/Users/vMac/06_design/brand/brand-design-system/specs/PLATFORM_EMAIL.md` before trusting these — this project has been through at least three palette generations and the brand repo is the only reliable check, not this file, not any other cached copy.

| Role | Tier | Hex | Use |
|---|---|---|---|
| Paper | **main** | `#EFE7D2` | Light section surface, and the email body |
| Ink | **main** | `#15140F` | Dark section surface; primary text on light |
| Coral | **main** | `#ED6F5C` | Accent block / CTA fill — one per email |
| Bone | supporting | `#F7F1DE` | Text on Ink; raised inset on Paper |
| Paper Dark | supporting | `#DDD2B6` | Dividers on Paper; secondary text on Ink |
| Ink Soft | supporting | `#2A2620` | Dividers on Ink; inset panel on Ink |
| Ink Mute | supporting | `#5A5448` | Muted body copy on light |

**Only the three main values may be a section background** (header, footer, any section).
Derived per surface:
- Paper section: bg `#EFE7D2`, strong `#15140F`, muted `#5A5448`, divider `#DDD2B6`, inset `#DDD2B6`
- Ink section: bg `#15140F`, strong `#F7F1DE`, muted `#DDD2B6`, divider `#2A2620`, inset `#2A2620`
- Coral section: bg `#ED6F5C`, text `#15140F`, button flips to Ink `#15140F` with `#F7F1DE` label
- CTA on Paper/Ink: `background:#ED6F5C` with `color:#15140F` — the button is not part of the surface swap

If you find a module with `#F6EFD9`/`#151411`/`#25221D`/`#EDE3CC`/`#EA6452`/`#C7BFAC`/`#c55042`/`#eae0c9`/`#181714`/`#f6efd9` — that's stale, migrate it. There have been at least three distinct old palette generations found live in this account; grep broadly, don't assume you've found them all after one pass.

## Logos

Real, current, working assets are in HubSpot's own File Manager:
- `https://50966981.fs1.hubspotusercontent-na1.net/hubfs/50966981/Logos/logo-v5-dark.png` — the **dark-ink** colored logo, for **light** backgrounds
- `https://50966981.fs1.hubspotusercontent-na1.net/hubfs/50966981/Logos/logo-v5-light.png` — the **cream/light** colored logo, for **dark** backgrounds

Filename describes the logo's own color, not the background it's meant for — easy to get backwards, double check before wiring a default. Don't reach for CSS `filter:invert()` tricks to fake one color from the other; a real invert-filter hack was found live in a module and removed — just reference the correct asset directly.

Any other logo path you find referenced (`brand/hair-solutions-co-logos/email-exports/...`, anything under `/Users/vMac/08_brand`) is very likely stale — verify it actually loads and is the current mark before trusting it, and prefer the `Logos/logo-v5-*` files above when in doubt.

## Field patterns that actually work

**Text / richtext / choice** — straightforward, these just work:
```json
{"id":"heading","name":"heading","label":"Heading","required":false,"locked":false,"allow_new_line":false,"type":"text","display_width":null,"default":"Add a heading"}
```

**Image — must wire width/height into the HTML, not hardcode.** Declaring `"resizable": true` makes Width/Height boxes appear in the editor, but if `module.html` hardcodes `width="320"` instead of `{{ module.field.width }}`, those boxes are cosmetic — they update the field value but the render never reads it, so nothing visibly changes. This was live and broken across ~20 modules. Correct pattern:
```html
<img src="{{ module.logo_image.src }}" alt="{{ module.logo_image.alt }}"
     width="{{ module.logo_image.width }}"
     style="display:block;width:{{ module.logo_image.width }}px;max-width:100%;height:auto;border:0;">
```
For circular/avatar crops where the aspect ratio must stay locked (border-radius trick), wire both width *and* height instead of leaving height:auto.

**URL — exact schema matters, a plausible-looking variant will fail the upload.** This is the one that will bite you if you guess:
```json
{"id":"button_url","name":"button_url","label":"Button URL","required":false,"locked":false,
 "supported_types":["EXTERNAL","CONTENT","FILE","EMAIL_ADDRESS","BLOG"],
 "type":"url","display_width":null,
 "default":{"type":"EXTERNAL","href":"https://hairsolutions.co/"}}
```
`default` is `{type, href}` directly — **not** nested under a `url` key, and don't add `open_in_new_tab`/`no_follow` into `default`. A nested-`url` version looks reasonable and will pass local JSON validation, but HubSpot's API rejects it on upload with "URL field ... has an invalid default value" — only surfaces at upload time, not before.

**Centering isn't automatic.** A module named "Centered X" needs explicit `text-align:center` on the content `<td>` (or the equivalent on the specific element) — the shell's outer `align="center"` only centers the 600px card within the wider canvas, it says nothing about how content is aligned *inside* that card.

## Editability rules (so it works in the drag-and-drop editor)

- `meta.json`: `"global": false`
- every field: `"locked": false`
- expose text/url/image/richtext/choice fields for anything editable — never require an operator to hand-edit HTML
- don't make reusable structural pieces (headers, footers) journey-specific — those are core, shared across every email
- no fake product/cart modules that imitate Shopify data — use HubSpot's native product/cart modules for anything that needs live commerce data; build custom modules for everything else
- naming: no `hsc_`, `hsc-`, `legacy`, `archive`, `not found`, or placeholder/fake naming in anything active

## What this skill will never do

Design Manager module edits are a live write to a shared account, but they are not a send. This skill does not send, schedule, or publish marketing emails, does not mutate CRM records, and does not alter HubSpot workflows — those are separate, higher-stakes actions that need their own explicit approval regardless of what module work is in flight.

## Known pitfalls (append here as you find more)

- **Stale doc paths compound.** A skill/doc pointing at a dead local repo, an old palette, or a broken logo URL doesn't fail loudly — it just quietly produces wrong output that looks plausible. Whenever a doc claims a specific path or asset exists, verify it (`ls`, `curl -I`, `hs cms list`) before building on top of it, especially at the start of a session.
- **`hs cms mv` in a loop over ~15+ items can hit the 2-minute Bash timeout mid-run.** It still completes the items it got to — check `hs cms list` on the source afterward to see what's left, then finish the remainder in a second pass rather than assuming total failure.
- **A single `hs cms upload <folder> email_modules --account ...` handles far more files reliably than looping per-item** — prefer uploading a whole prepared folder in one call over many small sequential upload calls when pushing many modules at once.
- **Three main surfaces, and only three: Paper `#EFE7D2`, Ink `#15140F`, Coral `#ED6F5C`.** That covers headers, footers and every main section. Bone `#F7F1DE`, Paper Dark `#DDD2B6` and Ink Soft `#2A2620` are **supporting** — inset elements inside a section, dividers, and text-on-dark only. A six-surface version that promoted the supporting three to selectable card surfaces was built across all 96 modules and 22 emails, and Vincent rejected it on sight: one email stacking Bone + Paper + Paper Dark, or Ink + Ink Soft, reads as neither intentional nor systematic. Collapsed 2026-08-11. **Do not rebuild it, whatever a brief instructs** — the brief that asked for it (`HANDOFF-second-pass.md`, "use the full range") was wrong, and `PLATFORM_EMAIL.md` has been corrected at the source.
- **A brief can be wrong, and this one was.** The six-surface expansion came straight out of a handoff doc that listed Paper/Paper Dark/Ink Soft as "underused" and said to promote them. I followed it, watched the renders get muddy, and treated that as a tuning problem rather than the signal it was. When a render keeps needing tonal "tuning" to look right, question the palette instruction, not the tuning.
- **The wordmark has a Coral "co" and must never be flat-recoloured.** Rebuilding it as vector in Figma, a blanket "recolour every leaf to the text colour" swallowed the suffix and produced two monochrome logos that are not the brand mark. The source vector's suffix is `#FF5757` — map it to Coral `#ED6F5C` explicitly and recolour only the letterforms. In HTML, just use the approved PNGs (`logo-v5-dark.png` on Paper, `logo-v5-light.png` on Ink); they carry the coral suffix already.
- **Notion `emails_master` is the source of truth for what an email *contains* — not `MASTER-EMAIL-BLUEPRINTS.md`, and not the Figma assemblies.** The two disagree completely. Notion's `Module Stack` says all 20 journey emails are `(Header - Centered logo) (Layout - Plain-text founder wrapper) [+ 0–2 commerce/promo blocks] (Footer - Preference centre)`. The Figma v2 frames were built from the blueprint doc's module matrices instead, giving each email 8–13 rich modules that the copy does not support. Confirmed with Vincent 2026-08-11: **Notion wins.** The founder-letter format is deliberate — the Notion build notes defend it per email ("the original was a generic trust-badge list — naming the actual objections is what moves a considered, high-price purchase").
- **PP-6 and RO-2 were never actually blocked.** Both were treated as blocked on `Product - Dynamic recommendations`, but Notion has that module in **square brackets** — recommended, not non-negotiable. Square vs round brackets in the `Module Stack` field is load-bearing: `( )` = required, `[ ]` = optional. Both now ship with a clearly-marked placeholder block in that slot, to be swapped for the native HubSpot/Shopify product module. All 22 journey emails are built.
- **The copy is written as one flowing letter, not per-module fields.** Do not try to split it into eyebrow/heading/body slots — that requires inventing brand copy. `plain_text_founder_wrapper` takes the whole thing in `letter_text`. Where a letter contains an inline label/value block or a promo code, move *that* into its dedicated module (the labels are the copy's own words); leave everything else as prose.
- **`preference_opt_down` was named "Footer - Preference centre" but was not a footer.** It carried only eyebrow/heading/body/button — no postal address, no unsubscribe, no permission reminder — while being the terminal module on 19 of the 20 journey emails. That is a compliance gap, not a styling one. Upgraded 2026-08-11 to append the full compliance block; its opt-down "ask" fields are now optional, so blanking them yields a pure compliance footer (only WB-4 fills them).
- **Empty optional fields left visual artifacts until 2026-08-11.** An empty `button_label` still rendered the coral pill (a floating blob), and an empty `label_N`/`value_N` still rendered its ruled table row. Both are now guarded by `{% if %}` across 38 module folders. If you add a new optional field, guard its markup the same way — modules must collapse gracefully or they can only be used fully populated.
- **The "stale palette migrated" claim in this doc was false for 15 modules until 2026-08-10.** `footer_social`, `footer_wide`, `quote_accent_bar`, `quote_centered`, `photo_logo_system` (all ×2 themes), `divider_rounded_link` and all four `cart-recovery/*` were still on the pre-migration hexes. Two of them are footers, which is part of why footers "looked like nothing." Lesson: this file asserting a migration is done is not evidence — `grep` the fetched tree for the stale list before believing it.
- **A stale asset that still returns HTTP 200 fails silently.** All three footer families pointed at `brand/hair-solutions-co-logos/email-exports/wordmark-ink-black-email.png`. It loads fine — it is simply the wrong, older mark. `curl -I` proves nothing here; compare the URL against the canonical `Logos/logo-v5-*` paths instead.
- **The wordmark is now derived from `surface`, not a field.** The `logo_image` image field was removed from header/footer and the `src` comes from the surface token table. Reason: module defaults only affect *new* instances, so leaving it as a field meant every existing email kept the stale wordmark forever. Deriving it fixed all existing instances at once. `logo_width` stays a field so sizing is still editable.
- **All 44 light/dark twin pairs were structurally identical** — the only difference was hex values. Verified by normalising every `#RRGGBB` to a placeholder and diffing. This is what made the surface refactor a safe scripted transform instead of 90 hand-rewrites. Re-run that check before assuming a twin pair has diverged.
- **Don't design a footer against the Figma campaign frames.** All six assembled campaign frames (`284:21734`, `284:21746`, `284:21758`, `284:21772`, `284:21784`, `284:21796`) carry the same minimal footer — pure white card, tiny grey copyright, two underlined links, no wordmark, no social. They are not a reference for footer design, and they contain the pure white Vincent explicitly rejected. Build the footer from the editorial vocabulary in `design-system.md` instead.
- **A bare `h2 { }` rule in a local proof-sheet harness cascades into module HTML.** Module headings set `font-size`/`color` inline but not `text-transform`, so a page-level `text-transform:uppercase` silently uppercased every rendered heading and looked like a module bug. Scope harness CSS to a class.
- **Figma text nodes with mixed fonts across a range return `figma.mixed`** from `.fontName` — calling `loadFontAsync` on that throws "Cannot unwrap symbol." Load the specific fonts you're about to apply explicitly instead of trying to read-then-reload an existing mixed-font node's current font.
- **When cloning a Figma frame and changing its `layoutMode`** (e.g. VERTICAL → HORIZONTAL) after creation, `primaryAxisSizingMode`/`counterAxisSizingMode` keep their old meaning relative to the *new* axis — a frame that was "FIXED width" under VERTICAL layout can silently become "FIXED height, HUG width" under HORIZONTAL, collapsing to content size. Set sizing modes explicitly after changing layoutMode, don't assume they carry over correctly.
- **The v3 Notion export contradicts itself, and the wrong half looks equally plausible.** Each email exists as a CSV row (`emails_master …_all.csv`) and a mirrored `.md` page. The CSV's `Module Stack` and `Body` (`[Module]`-tagged) columns are the corrected v3 spec. The same `.md` file *also* carries a `### Build notes` → `Module stack: …` line with the **old, thinner stack**, and a `### Body` section with **old flowing prose that predates the `[Module]` tags**. Concretely, on disk right now: BR-1's CSV `Module Stack` has 7 modules including `Hero - Text-led` and `Button - Primary CTA`; its own `### Build notes` stack has only 5, missing both. PP-1's CSV stack has 9 modules; its `### Build notes` stack has 4. **The CSV wins, always — parse it, never the markdown prose.** This exact ambiguity already produced one full rebuild built against the `### Build notes` stack, averaging 3.6 modules/email against a v3 target of ~7; Vincent rejected it on sight as "not my vision of email marketing." `emails/second-pass/v3_source.py` now reads the CSV exclusively and is the only module that touches the export — don't add a second reader that might parse the `.md` files instead. A stack that's just header + one block + footer is the tell that something upstream read the stale source.
- **This codebase fails silently, not loudly — four unrelated defects this session shared exactly one shape: a missing value produced plausible output instead of an error.** Treat that as the standing risk, not a closed list:
  - `render_emails.block_html` does `ctx = defaults(folder); ctx.update(values)` — any content-bearing field you don't explicitly supply keeps the **module's own demo default**, and several assert real business facts: `commerce_shipping_tracking` defaults `value_carrier` to `'UPS Ground'`, `value_tracking` to `'1Z999AA10123456784'`, `value_eta` to `'Aug 9'`; `trust_badge_row` defaults its four labels to `'First Purchase Assurance'`, `'30-day Money-back'`, `'Free Shipping'`, `'Secure Payment'`; `countdown_expiry` defaults `expiry_text` to `'Ends on [date]'`. Ship any of those unset and you've stated an invented fact to a customer. Rule: every content-bearing field must be explicitly set or explicitly blanked (`""`), never omitted — and grep rendered output for the literal default strings before calling anything done.
  - **Nine live module families gated their entire card on the button, not just the button.** `plain_text_founder_wrapper`, `support_strip`, `text_base_type_guidance`, `promo_code_block`, `countdown_expiry`, `column_image_and_text`, `photo_founder_note`, `review_stars`, `button_standalone_cta` all opened `{% if module.button_label %}` immediately after the shell preamble and closed the matching `{% endif %}` at the very end of the file — so an empty `button_label` (a legitimate, common state) rendered **zero visible content**, not "card minus button." Byte-offset proof from the live templates: `support_strip` opened the `if` at byte 1029 and closed it at 2277 of a 2325-byte file; `plain_text_founder_wrapper` 1029→2162 of 2210; `text_base_type_guidance` 1029→2324 of 2371 — i.e. the gate wrapped essentially the whole card in each case. Live impact: 27 of 199 rendered blocks across 23 of 28 emails were completely blank (13.6%), including whole founder-signed letter bodies. Repaired 2026-08-11 in HubSpot (account 50966981) by moving the `{% if module.button_label %}`/`{% endif %}` pair to wrap only the button sub-table, nested inside `{% if module.show_button == 'yes' %}` where that field exists so an empty label still can't render a bare coral pill — verified by `hs cms fetch` into a clean directory and confirming byte-identical output to what was uploaded. **Rule: when a module gates optional markup with `{% if %}`, check where the matching `{% endif %}` actually lands — a condition named after one element (the button) can silently scope the whole card.**
  - `spec_figma.py` read `heading_accent` on `button_standalone_cta`, a field that folder's `fields.json` does not define. Undefined-field lookups don't error here — `val()` returns `""` — so it would have shipped as a permanently blank accent nobody noticed until someone happened to expect it. Rule: read field names from the live `fields.json` (`hs cms fetch`'d, e.g. `<folder>.module/fields.json`), never guess from a sibling module's shape, and don't trust a report's claim that field names were verified — re-check yourself.
  - A fourth instance is recorded above under "The wordmark has a Coral 'co'…": a recolour allow-list that didn't include the source hex `#FF5757` silently flattened the wordmark to monochrome instead of erroring. Same shape as the other three — a missing entry produced quiet, wrong output rather than a failure.
- **Every one of the above was caught by reading live data, reading real templates, or looking at a rendered screenshot — not by the test suite.** All 44/47/57 tests (task-by-task) stayed green the entire time 13.6% of blocks were rendering blank. The visual read mandated at Task 7 Step 3 is not garnish on top of the automated checks; on this project it has been the single highest-yield step for finding real defects. Don't skip it because the tests passed.
- **`audit.py` reporting `problems: 0` / exit 0 is not proof of anything if the check that would catch your bug was never wired in.** The blank-render defect above existed the entire time `audit.py`'s `class="final-card"` regex was computing a match (or `None`) and then discarding the `None` case instead of reporting it — the signal was already there, unused. Fixed by reporting `bg is None` as a `BLANK RENDER` problem instead of silently skipping it; audit went from "28 emails / 5 coral / 0 problems" (false) to "27 problems, exit 1" (true) with the exact same render pass, no new code path. **Technique worth repeating: don't just add a check and move on — deliberately revert the underlying fix and confirm the audit/test actually goes non-zero, then restore it.** This was done twice this session (the blank-render check, and later an empty-FAQ-answer check) and is the only way to know a check actually bites rather than passing by accident.
- **A family→module mapping can be structurally correct and still wrong for the copy.** `List - Questions` maps to the live `faq` module, which assumes real Q&A pairs. In practice only 2 of 8 `List - Questions` blocks in the v3 copy were genuinely Q&A-shaped (CR-2, C-1); the other 6 were flat lists — checklists, timelines, step sequences — with no answer text at all. Feeding them through `faq` produced 20 empty-answer rows out of 26 (76%): bold question rows with a "+" expand affordance that does nothing in email, and no answer underneath. Fixed with a data-driven fallback (no email codes hardcoded) that routes an all-unanswered `faq` block through `text_block_generic` as a flat list instead. Rule: when a Notion family maps to a structured module (Q&A, label/value table, etc.), check that the actual copy has that structure before trusting the mapping — a plausible family name is not evidence of matching shape.
- **Plan and brief text is not authoritative over the live account or the real export — verify every concrete claim before building on it.** This session alone: the plan's Task 4 field tables for `review_stars` named fields (`rating_text`, `count_text`) that don't exist on the live module; its Task 8 "families still missing a Figma branch" list named 8 (and wrongly included the already-retired `review_stars`) when the real answer, measured from data, was 11; it said "the 5 unsegmented founder-letter emails" when the real data has 7 (PP-7, CR-4, WB-1, WB-4, RO-1, RO-4, C-4); it estimated "~190 module frames" for the Figma rebuild when the real, measured count is 199. None of these were malicious — they were unverified assumptions written into planning prose. Treat any specific number, field name, or list in a plan/brief as a hypothesis to check against `hs cms fetch`/live data/the real CSV, not a fact to build on.

## Design system

`references/design-system.md` has the formal color/typography/spacing/radius tokens and — most importantly — the alignment rule (**left-align by default, centered only for standalone CTAs and dividers**). Typography and spacing were ad hoc per-module before this existed; that's exactly why inconsistencies crept in. Check new modules against it, don't improvise a size/weight/alignment because it looks fine in isolation.

## Reference files

- `references/design-system.md` — color/typography/spacing/radius tokens and the alignment rule. Check before building or fixing any module's visual details.
- `references/module-inventory.md` — the actual current family list as of last verification, with field IDs. Re-verify with `hs cms list email_modules` before trusting counts if it's been a while.
- `references/deployment-playbook.md` — exact `hs cms` commands for fetch/upload/list/delete/mv, with the failure modes actually seen in this account and how they were resolved.
