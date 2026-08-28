# Hair Solutions Co. HubSpot Email Module Inventory

**This is a snapshot, not a live source.** Re-verify with `hs cms list email_modules --account 50966981` before trusting counts or names — this list has already grown mid-session more than once, and the folder structure has been reorganized at least twice in this project's history (an earlier `core/`/`launch/`/`newsletter/` scheme was flattened into the current one). If what you see live doesn't match this file, the live account wins; update this file to match.

HubSpot destination: `email_modules/` in account `50966981`. No local repo mirrors this — see `SKILL.md` for the fetch/edit/upload/verify workflow.

## Notion → live module-name mapping (v3, 2026-08-11)

The Notion `modules_master` CSV (`emails/second-pass/source-v3/modules_master …_all.csv`) is **not**
a reliable map to what's live. Two of its own columns are wrong in different ways:

- **`Slug` is Notion's own guessed name, not the live one.** Example verified directly against the
  CSV: the row for family `Footer - Preference centre` (Dark) carries `Slug`
  `footer_preference_centre_dark`. The live folder for that family is `preference_opt_down_dark` (see
  "Active families" below) — a completely different string. Don't wire a slug straight out of this
  CSV into code; it will point at a module that doesn't exist.
- **`Source Path` references a `core/`/`newsletter/` folder structure that does not exist live.**
  Same row: `Source Path` = `core/footer_preference_centre_dark.module`. The live tree is flat —
  there is no `core/` or `newsletter/` subfolder (see "Naming" below, and `SKILL.md`'s "Current live
  structure"). Its `Notes` column also isn't reliable — some rows are flagged "Local only - not
  uploaded" when `hs cms list` shows them live. Use this CSV for *intent* (what module family exists,
  what it's for) and cross-check everything else — path, slug, upload status — against
  `hs cms list`/`hs cms fetch`.

**`emails/second-pass/module_map.py` is the canonical family → live-slug mapping** — it's what the
v3 composer actually reads, keyed by the Notion `Family` name (e.g. `"Footer - Preference centre":
"preference_opt_down"`), with `None` for families that genuinely have no live module yet (composer
emits a labelled placeholder instead). **Update `module_map.py` whenever a family is renamed on
either side** — in Notion, or by renaming/replacing a live module folder — or the mapping silently
goes stale the same way the CSV's own `Slug` column already has.

**`text_block_generic` intentionally serves five separate Notion families**, not one: `Text -
Opening`, `Text - Reassurance`, `Text - Customer snapshot`, `Text - Section`, `Text - Offer
discount` all map to it. It's one reusable generic text block standing in for five distinct semantic
slots per the copy, not a sign the mapping is under-specified. (A description of this rule circulated
during planning said "four" slots — the live `module_map.py` has five; trust the code over the
recollection.)

## Figma — Journey Emails page (rebuilt 2026-08-11)

The page (`291:724`) now holds **22 email frames** built natively from the composed
emails: real auto-layout, real text nodes, one frame per module named
`<module> / <surface>` so the stack is readable at a glance. Everything that came
before — the v1 assemblies *and* the v2 blueprint-derived ones — sits on
**`357:1203` "Journey Emails — superseded (v1 + v2)"** (57 nodes). Nothing was deleted.

Figma-specific things worth knowing next time:

- **`figma.createImageAsync` is not supported** in `use_figma`, so the wordmark cannot
  be pulled from its HubSpot URL. Clone the vector group **`284:8864`** instead — but note
  its "co" suffix is **`#FF5757`**, not brand Coral. Map `#FF5757` → `#ED6F5C` explicitly
  and recolour only the letterforms (`#000000`/`#1B1B1B`) to the surface text colour.
  A guard list of brand corals misses `#FF5757` and silently flattens the suffix, which
  is exactly how two monochrome not-the-brand logos shipped once. Re-clone from the
  source to repair; a flattened clone has no coral left to rescue.
- **Fonts here are better than the email fallbacks**, so Figma renders the design
  system's stated intent rather than Arial/Georgia: JetBrains Mono Regular (eyebrow),
  Inter Tight Bold (heading), Playfair Display Italic (accent), Inter Regular/Italic
  (body/signature). Arial, Georgia and Courier New are **not** installed.
- **`appendChild` throws on unloaded fonts** — moving or deleting existing text nodes
  requires loading every font already used on the page first. Collect them with
  `getStyledTextSegments(["fontName"])` and `loadFontAsync` each before touching anything.
- **`page.children` under-reports on a page that isn't current** (pages load lazily), so
  a move can look like it lost nodes. Verify with a second call that sets that page current.

## Surface status (collapsed to 3 surfaces, 2026-08-11)

Live count verified: **45 families = 90 folders**, plus `cart-recovery/` (3 families, 6 folders)
and 2 single dividers = 96 `module.html` files.

**All 94 non-divider module folders are on the `surface` field, offering Paper / Ink / Coral
only** (headers and footers offer Paper / Ink — Coral excluded, since the wordmark's coral
"co" vanishes on it). The two dividers keep their own `color` field and are untouched.

An earlier six-surface version (bone / paper / paper_dark / ink / ink_soft / coral) was
built and then rejected — see `design-system.md` §Surfaces. Instances still holding a
retired value fall back through each module's `{% if not c %}` guard, so nothing broke.

Notable module work, all verified live by fetch-back:

| Family | Notes |
|---|---|
| `header_centered_logo` (+`_dark`) | `logo_image` field **removed**, wordmark derived from surface. New `logo_width`. Coral excluded. |
| `footer_standard` (+`_dark`) | Fully redesigned — see below. Coral excluded. |
| `text_block_generic` (+`_dark`) | Ruled eyebrow + mixed-font heading + derived colours. |
| `hero_text_led` (+`_dark`) | Same, 32px heading. |
| `button_standalone_cta` (+`_dark`) | **Now centred** — it is a standalone CTA card, one of the three legitimate centred moments. It was left-aligned and had a bare (unruled) eyebrow before, both design-system violations. |

`footer_standard` was rebuilt because it rendered as small centred plain text with **default
blue browser links** and no wordmark, social row, or permission reminder. It now carries:
wordmark → tagline → hairline → mono social row → hairline → bold company name → postal
address → permission reminder → legal links, all left-aligned with explicit link colours.
The permission reminder is required by the blueprint universal layer and was missing entirely.

**All 94 non-divider folders are migrated.** The `_dark` folders hold identical HTML to
their light twin and differ only in the `surface` default — they are aliases, not designs.

## Naming

Folders are `snake_case`, one folder per theme: `family_name.module` (light) and `family_name_dark.module` (dark). `meta.json` labels use an em-dash format, e.g. `"Header — Centered logo — Light"`. There is no `CORE -`/`Launch -`/`Newsletter -` scope prefix in the current live set — that was an earlier convention that's since been abandoned; don't reintroduce it unless asked.

## Active families (39, = 78 module folders) + `cart-recovery/` (3 families, 6 folders) = 84 total

### Structural / core (used across almost every email)
| Family | Notes |
|---|---|
| `header_centered_logo` | Fields: `logo_image` (image, wired width/height), `logo_url`, `preheader_note`. Uses real logo assets — see SKILL.md Logos section. Content `<td>` needs `text-align:center`. |
| `footer_standard` | Fields: `logo_image`, `company_name`, `company_address`, `privacy_url`, `instagram_url`/`facebook_url`/`youtube_url`. Note: social URL fields exist but were never wired into the HTML in the original build — check before assuming they render. |
| `footer_social` | Logo + social links variant. |
| `footer_wide` | Wider footer layout. |
| `plain_text_founder_wrapper` | Fields: `greeting`, `letter_text` (richtext), `signature`, `show_button`, `button_label`, `button_url`. The personal-letter format — Vincent's real body copy goes in `letter_text` as one flowing block, not split into micro-fields. |
| `preference_opt_down` | Fields: `eyebrow`, `heading`, `body_text`, `button_label`, `button_url`. |
| `support_strip` | Short "need help?" strip. Same field shape as `hero_text_led`/`text_block_generic`/`button_standalone_cta` — historically these four were literal byte-identical templates under different names; check before assuming they've diverged. |

### Hero / opening
| Family | Notes |
|---|---|
| `hero_text_led` | Fields: `eyebrow`, `heading`, **`heading_accent`** (optional, renders as italic coral word after heading — added later, backward compatible, empty by default), `body_text`, `show_button`, `button_label`, `button_url`. |
| `hero_photo_led` | Text + photo hero. |
| `text_masthead` | Newsletter-style masthead, no photo. |
| `text_block_generic` | Generic reusable text block — reused multiple times per email for distinct semantic slots (opening, why-it-matters, next-step, etc.) rather than having a dedicated module per slot. |

### Commerce / transactional
| Family | Notes |
|---|---|
| `commerce_order_summary` | Built this session. Fields: `eyebrow`, `heading`, `label_order`/`value_order`, `label_spec`/`value_spec`, `label_status`/`value_status`, `label_eta`/`value_eta`, `note` (richtext), `button_label`, `button_url`. |
| `commerce_shipping_tracking` | Built this session. Same shape as order_summary but `label_carrier`/`value_carrier`, `label_tracking`/`value_tracking`, `label_eta`/`value_eta`. |
| `commerce_quote_spec_table` | Built this session. Same shape, 5 rows: `label_1..5`/`value_1..5`. |
| `billing_payment_details` | Pre-existing. 4-row label/value table (`detail_1..4_label`/`detail_1..4_value`) + `support_note`. Closest existing analog for the three above — used as the template. |
| `countdown_expiry` | Offer deadline / urgency strip. |
| `promo_code_block` | Fields: `heading`, `promo_code`, `terms_text`, `button_label`, `button_url`. |
| `product_goal_based_recommendation_3up` | Combined product recommendation module — **deliberately not extended further**; Vincent wants native HubSpot/Shopify product modules for real product data, not more custom mimics. |

### Social proof / trust
| Family | Notes |
|---|---|
| `testimonial` | Fields: `quote_text`, `customer_name`, `customer_detail`, `customer_image` (circular, width+height wired), `show_stars`. |
| `review_stars` | Star rating + count. |
| `stat_bars` | Bar-chart style stats. |
| `faq` | 5 Q&A pairs (`faq_1..5_question`/`faq_1..5_answer`). |
| `quote_accent_bar`, `quote_centered` | Pull-quote treatments. |

### Rich content (added mid-session, richer visual alternatives to plain text blocks)
| Family | Purpose |
|---|---|
| `numbered_process_cards` | Replaces flat "— item" checklists. 3 rows, each a coral numbered badge (01/02/03, hardcoded sequential, not fielded) + bold label + detail. |
| `key_benefits_icon_row` | 3-column icon + label + detail row. Built but not yet placed in a real email — no natural 3-parallel-benefit content existed after the numbered-cards swap absorbed that use case. |
| `founder_photo_quote` | Circular founder photo + italic pull-quote + name/role. Richer alternative to the plainer `photo_founder_note`. |
| `stats_grid` | 3-column big-number stat grid with dividers. Built but not yet placed — no genuine quantifiable stats (real customer counts, satisfaction %) exist in the source copy yet; don't fabricate numbers to fill it. |
| `visual_comparison_cards` | 3-card side-by-side comparison (e.g. Lace/Poly/Hybrid), replaces flat comparison tables. |
| `comparison` | The older flat label/value comparison table — still live, `visual_comparison_cards` is the richer alternative for the same job. |
| `column_image_and_text` | Image + eyebrow/heading/body two-column layout. |
| `photo_feature_story`, `photo_founder_note`, `photo_logo_system` | Various photo-led content blocks. |
| `grid_collections_4` | 4-item collection grid. |
| `list_generic` | Generic reusable list (heading + intro + up to 6 items). |
| `button_standalone_cta` | Standalone centered CTA button in its own card, for when a CTA needs its own visual beat rather than being appended inline. |
| `text_base_type_guidance` | Built this session. Fields: `eyebrow`, `heading`, `body_text` (richtext), `show_button`, `button_label`, `button_url`. |

### `cart-recovery/` subfolder (older, smaller, separate set — journey-specific, not core)
| Family | Notes |
|---|---|
| `header_hero` | Combined logo + eyebrow + headline + supporting-copy hero, one module. Has its own `logo` field (not `logo_image`) — same logo-wiring rules apply. |
| `cta_faq` | Combined CTA + FAQ. |
| `reassurance` | Trust/reassurance strip. |

### Dividers
| Family | Notes |
|---|---|
| `divider_rounded_link` | Single module (not a light/dark pair — this is a 3-way color choice, not a theme). Field: `color` (choice: paper/ink/coral, default paper). Small rounded-corner (16px) card with a centered thin horizontal line, sized to sit *between* two stacked content cards as a connective accent — not a full section. |
| `divider_full_band` | Single module. Fields: `color` (choice: ink/paper, default ink), `height` (text, px, default "80"). Square corners, full width, solid color, no line — a deliberate long black or long paper band used to close out a themed run of cards before the next section starts. Different job from `divider_rounded_link`, don't conflate them. |

### Editorial sections (built from the Figma assembled-campaign templates)
Source of truth for these designs is the Figma page **Modules Library + Hubspot Source** (`225:357`), specifically the assembled campaign frames — Welcome (`284:21734`), Abandoned Cart (`284:21746`), Post-Purchase Care Guide (`284:21758`), Promo (`284:21772`), Replenishment (`284:21784`), Win-Back (`284:21796`), plus Newsletter/Transactional/Welcome version variants. When building a new rich section, screenshot the relevant frame and match it rather than inventing a treatment.

| Family | Notes |
|---|---|
| `steps_three_column` | 3 columns with vertical hairline rules, coral mono kicker (`01 · INTAKE`), bold label, small description. Distinct from the vertical `numbered_process_cards` — this is the compact horizontal variant. |
| `trust_badge_row` | 4 across, outlined circle containing a text glyph, two-line bold centered label. Glyphs are text fields (not images) so there's no asset dependency or broken-image state. |
| `split_image_text` | Image left (40%) / text right (60%), vertically centered. Stacks on mobile via `.stack`. |
| `cta_dual_buttons` | Solid ink primary + outlined ghost secondary side by side. Ghost button collapses if its label is empty. |
| `preheader_bar` | Thin announcement/browser-view bar. `style` choice: neutral (theme color) or coral. |

## v3 module-count target, per email (2026-08-11 journey rebuild)

Vincent's explicit standard: a v3 journey email averages **~7 modules**, not the ~3.6 the previous
build shipped (header + one text block + footer, repeatedly) — he rejected that build on sight as
"not my vision of email marketing." If a stack you're looking at is that thin, you are almost
certainly reading a stale source (see `SKILL.md`'s v3 source-of-truth-hierarchy pitfall) or missing
a mapped family, not looking at a genuinely simple email. Two emails are *correctly* 3 modules
(`WB-1`, `WB-4`, `RO-1` below) — thin is not always wrong, but it should be rare and deliberate, not
the default outcome.

Per-email target (module count), from the plan's Scope section, verified against
`emails/second-pass/source-v3` CSV `Module Stack` columns:

| Email | now (pre-rebuild) | v3 target | | Email | now (pre-rebuild) | v3 target |
|---|---|---|---|---|---|---|
| PP-1 | 4 | **9** | | CR-4 | 4 | **7** |
| PP-2 | 3 | **8** | | BR-1 | 4 | **7** |
| PP-3 | 3 | **4** | | WB-1 | 3 | 3 ✓ |
| PP-4 | 4 | **7** | | WB-2 | 3 | **9** |
| PP-5 | 3 | **8** | | WB-3 | 5 | **9** |
| PP-6 | 4 | **8** | | WB-4 | 3 | 3 ✓ |
| PP-7 | 4 | **3** ⚠ | | RO-1 | 3 | 3 ✓ |
| PP-7b | — (never built) | **12** | | RO-2 | 4 | **7** |
| CR-1 | 3 | **5** | | RO-3 | 4 | **8** |
| CR-2 | 3 | **8** | | RO-4 | 4 | **5** |
| CR-3 | 3 | **8** | | RO-5 | 3 | **7** |
| C-0 | — (never built) | **13** | | RO-6 | 5 | **9** |
| C-1 | — (never built) | **9** | | C-3 | — (never built) | **9** |
| C-2 | — (never built) | **8** | | C-4 | — (never built) | **3** |

⚠ PP-7 is the one email that was **over**-built pre-rebuild: it carried a `cta_dual_buttons` block
the v3 stack doesn't call for.

28 emails total (5 journeys: J1 Post-Purchase 8, J2 Cart Recovery 5, J3 Win-Back→Sunset 4, J4 Reorder
6, J5 Consultation 5). The 5 `W · Newsletter Welcome` emails in the same export are explicitly out of
scope — parsed and skipped by `v3_source.py`, never built.

## Future idea (Vincent, not yet scoped)

A **visual wireframe catalog** — a single page/board showing every available section as a thumbnail, so blocks can be picked visually when assembling an email instead of by scrolling module names in the HubSpot sidebar. Raised as thinking-out-loud, explicitly not a current task. Worth revisiting once the module set stabilizes.

## Known gaps / deliberately not built

- No custom cart or product-detail modules beyond `product_goal_based_recommendation_3up` — Vincent wants native HubSpot/Shopify commerce modules for real cart and product data. Don't build more custom mimics of that data.
- `key_benefits_icon_row` and `stats_grid` exist live but aren't wired into any real email yet — they're waiting on content that actually fits (genuine parallel 2-3-point benefits; genuine quantifiable stats). Don't force real copy to fit these shapes if it doesn't naturally have that structure.
