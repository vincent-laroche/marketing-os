# Hair Solutions Co. — Email Marketing Design System

Formal token system for email modules: color, typography, spacing, radius, and the one rule that matters most — **alignment consistency**. Before this document existed, module typography/spacing/alignment was decided ad hoc per module, which is exactly why things drifted (e.g. `grid_collections_4`'s captions not matching the rest of the system). Check new and existing modules against this doc; don't improvise a new size/weight/alignment because it "looks fine" in isolation.

**Source of truth order:** `06_design/brand/brand-design-system/specs/PLATFORM_EMAIL.md` (verified live, check it directly, don't trust a cached copy) → this doc → nothing else. A Figma-AI-generated `DESIGN.md` was used as a starting draft for this file and had drifted — it included a stale hex (`#151411`, exactly the pre-migration residue documented in `SKILL.md`'s Known Pitfalls) and was missing `Ink Soft`/`Mustard` from the real palette. Reconciled below. If you find this doc has drifted too, fix it — see `SKILL.md`'s "This is a living document" note.

## Alignment — the rule that actually matters

**Left-align by default.** Headings, eyebrows, body copy, captions, card content — left-aligned. That's the default you reach for without thinking.

**Centered is for whole-block promotional moments, not a per-element style choice:**
1. A coupon/promo code block, in its entirety — eyebrow, code, body, button all centered together as one self-contained moment
2. A standalone CTA button/badge sitting alone in its own card
3. Dividers (the rounded-link divider's centered line)

The distinction that matters: centering is a decision made **once, for a whole module that is itself a singular focused moment** (redeem this code, click this one button) — not something applied to individual captions or headings inside an otherwise left-aligned card. Mixing left and center *within the same content block* (e.g. a heading centered but its caption left-aligned, or product captions centered while everything else in the email is left) is the thing to avoid. Mixing left-aligned informational modules with occasional fully-centered promotional modules, when each choice is deliberate, is fine — that's what "be logical about where things are placed" means in practice. If a module centers one element while leaving siblings left-aligned for no structural reason (e.g. `grid_collections_4`'s "Collection 1/2/3/4" captions previously being off from the rest of that same card), that's a bug to fix.

## Color

### Primitives (verified against the live brand repo)

| Token | Tier | Hex | Use |
|---|---|---|---|
| Paper | **main** | `#EFE7D2` | Light section surface, and the email body behind it |
| Ink | **main** | `#15140F` | Dark section surface; primary text on light |
| Coral | **main** | `#ED6F5C` | Accent block, CTA fill, small accent — one per email |
| Bone | supporting | `#F7F1DE` | Text on Ink; raised inset panel on Paper. **Never a section surface** |
| Paper Dark | supporting | `#DDD2B6` | Dividers on Paper; secondary text on Ink; recessed inset. **Never a section surface** |
| Ink Soft | supporting | `#2A2620` | Dividers on Ink; inset panel on Ink. **Never a section surface** |
| Ink Mute | supporting | `#5A5448` | Muted body copy and captions on light |
| Coral Soft | `#F08E7C` | Limited secondary emphasis on Ink panels |
| Olive | `#6E7448` | Success / eco-messaging state only — not decorative |
| Mustard | `#E9B94A` | Focus/caution utility only — not decorative |

Do not use `#151411` (one character off from `#15140F` — this is stale pre-migration residue, not a real token, no matter where you see it referenced). Do not invent additional grays/creams beyond this table without checking the brand repo first — a prior draft added `bone/300 #ECE4CF` and `warm-gray/500 #8B8676`, neither of which exist in the verified source.

### Surfaces — the `surface` field (revised 2026-08-11)

**Three main surfaces only.** A main surface is the background of a header, a footer, or
any main section. `surface` offers exactly these:

| surface | card bg | strong text | muted text | divider | inset fill | button | label | accent | wordmark |
|---|---|---|---|---|---|---|---|---|---|
| `paper` | `#EFE7D2` | `#15140F` | `#5A5448` | `#DDD2B6` | `#DDD2B6` | `#ED6F5C` | `#15140F` | `#ED6F5C` | logo-v5-dark |
| `ink` | `#15140F` | `#F7F1DE` | `#DDD2B6` | `#2A2620` | `#2A2620` | `#ED6F5C` | `#15140F` | `#ED6F5C` | logo-v5-light |
| `coral` | `#ED6F5C` | `#15140F` | `#15140F` | `#15140F` | `#15140F` | `#15140F` | `#F7F1DE` | `#15140F` | — |

**Bone `#F7F1DE`, Paper Dark `#DDD2B6` and Ink Soft `#2A2620` are supporting colours.**
They are never selectable as a surface and never a section background. They appear only
as derived values: dividers and rules, inset fills for elements that must separate from
the base (input fields, media placeholders, state/callout panels, pinned bars), and text
on dark. This is enforced by the `surface` field only offering three choices.

**A six-surface version of this system was built and rejected.** Bone, Paper Dark and
Ink Soft were promoted to selectable card surfaces on the theory that they gave "tonal
stepping". In practice a single email stacked three sand tones or two near-blacks, which
reads as neither intentional nor systematic. Do not reintroduce it, whatever a brief says.

**The structural consequence.** With one light and one dark main surface, adjacent
sections stop reading as separately tinted cards — a light email is one continuous Paper
field, a dark one one continuous Ink field. Hierarchy comes from spacing, hairlines and
type. Two knock-on rules follow: the email wrapper uses **no gap between modules** (each
module's own 32px padding sets the rhythm; a gap plus two paddings stacks into an ~83px
void), and you must not add per-section tinting to manufacture separation.

**Three derived rules that are not obvious:**

1. **On Coral the button flips to Ink** (`#15140F` fill, `#F7F1DE` label) and the accent
   rule goes Ink. The standard coral button and coral rule are invisible on a coral card.
2. **On Coral, muted text == strong text.** Hierarchy there comes from weight and size.
3. **Header and footer exclude Coral entirely.** The wordmark's "co" is Coral, so it
   disappears on a Coral card, and chrome is not where the loudest surface belongs.

**Migration convention:** the field was applied additively — the light file defaults to
`paper`, the dark file to `ink`, and any instance still holding a retired value ("bone",
"paper_dark", "ink_soft") misses the lookup and falls back via the module's own
`{% if not c %}` guard. No module ID was ever deleted.

### Applied per theme (dead — twin-file convention, superseded by `surface` above)

| | Light card | Dark card |
|---|---|---|
| Background | `#F7F1DE` | `#15140F` |
| Strong text | `#15140F` | `#F7F1DE` |
| Muted text | `#5A5448` | `#DDD2B6` |
| Divider | `#DDD2B6` | `#2A2620` |
| CTA button | `background:#ED6F5C; color:#15140F` — identical in both themes, the button is not part of the theme swap |

## Typography

Fallback stack (email-safe, apply everywhere — web fonts don't render reliably in email clients):
```
Inter Tight     → Arial, Helvetica, sans-serif
Inter           → Arial, Helvetica, sans-serif
Playfair Display → Georgia, "Times New Roman", serif
JetBrains Mono   → "Courier New", Courier, monospace
```

### Scale

| Style | Weight | Size | Line height | Use |
|---|---|---|---|---|
| H1 | ExtraBold | 48px | 115% | Campaign hero headlines — used sparingly |
| H2 | ExtraBold | 32px | 120% | Section headings |
| H3 | Bold | 24px | 125% | Card titles, feature callouts |
| H4 | SemiBold | 18px | 130% | Subsection labels |
| Body/Large | Regular | 16px | 150% | Primary body copy |
| Body/Base | Regular | 14px | 155% | Standard body text, list items |
| Body/Small | Regular | 12px | 150% | Captions, fine print |
| Label/Small | SemiBold, 0.5px tracking | 11px | 140% | Eyebrow text, category labels — **open question, see below** |
| Editorial/Heading | Playfair Display Italic | 24–30px | 125–135% | A single accent word/phrase within a heading — this is the "heading + heading_accent" pattern already live in `hero_text_led` |

**Open decision, not yet resolved — flag before building more eyebrow-heavy modules:** every module built so far uses JetBrains Mono (uppercase, tracked) for eyebrow/label text, which Vincent has approved repeatedly and never flagged as wrong. A separate draft spec calls for Inter Tight SemiBold instead. Don't silently switch existing modules to match the draft — the live monospace-eyebrow convention has real, repeated approval behind it and that outweighs an unreviewed draft. Confirm explicitly with Vincent before changing this system-wide; until then, keep building new modules with monospace eyebrows to match everything already live.

## Spacing

| Token | Value | Use |
|---|---|---|
| xs | 4px | Tight inline spacing |
| sm | 8px | Inner button padding, tag padding |
| md | 12px | List item spacing, small card padding |
| base | 16px | Standard section padding, paragraph spacing |
| lg | 20px | Card internal padding |
| xl | 24px | Between content blocks within a module |
| 2xl | 32px | Standard module content padding — this is the `.final-pad` default already used everywhere |
| 3xl | 40px | Major section breaks, hero vertical padding |

## Border radius

| Token | Value | Use |
|---|---|---|
| none | 0 | The square full-band divider only |
| md | 8px | Nested chips (e.g. promo code box), sub-cards within a module |
| lg | 12px | Image containers where a smaller radius reads better than the card radius |
| xl | 16px | **The standard card radius — every module's outer card uses this.** Also the rounded-link divider. |
| full | 999px | Pill CTA buttons, circular avatars |

If you're setting a radius and it's not one of these five values, stop and ask which one applies rather than picking an arbitrary number.

## Editorial component vocabulary

These are the recurring visual devices from the brand's own reference designs. They're what separates a module that looks designed from one that looks like a functional minimum. Reuse these rather than inventing a new treatment per module — that consistency *is* the design system working.

**Ruled eyebrow** — a short (~22px) coral rule, 10px gap, then tracked uppercase mono label in ink (not coral). This is the signature section opener; it appears above nearly every heading in the reference material. Preferred over a bare coral uppercase line, which reads flatter.

**Editorial serif numerals** — `01` `02` `03` in Georgia/Playfair *italic*, coral, ~26px, in a narrow left column beside a bold label + muted description. Use for any ordered/numbered list or process. This replaced an earlier filled-coral-circle badge treatment, which looked generic by comparison.

**Coral serif price** — Georgia italic, coral, 16–18px. Prices are never plain body text; the serif italic is a deliberate signature.

**Eyebrow pill** — bordered capsule (1px rule, 999px radius, muted mono text) for editorial/article cards, as opposed to the ruled eyebrow used on standard content sections. Signals "this is a piece of content" vs "this is a section."

**Meta row** — a hairline, then mono uppercase meta on the left (`HAIR SOLUTIONS CO. · 5 MIN READ`) and a bold inline link with a trailing arrow on the right. Closes editorial cards.

**Mixed-font heading** — bold sans heading with one trailing phrase in italic serif ("Confidence starts *at the hairline.*", "Start with the base. Choose for *your routine.*"). Implemented as an optional `heading_accent` field so it's opt-in per instance and never forced.

**Glyph icon tile** — soft-fill rounded square (10px) containing a text glyph (`≡` `+` `★`), bold label, small muted description. Text glyphs over images: no asset dependency, no broken-image state, renders everywhere.

**Soft-fill sub-card** — nested block one step off the parent card color (`#EFE7D2` on light, `#2A2620` on dark), 10–12px radius. Used for product tiles and benefit tiles so items read as distinct objects without needing borders.

## Effects

Skip shadows entirely unless there's a specific reason to reconsider. `box-shadow` doesn't render in Outlook desktop or many mobile clients, and this system's whole visual language (flush cards, flat color, generous radius) doesn't need them — introducing shadows now would be a bigger visual-language decision than a token choice.

## Email client reality check

| Feature | Apple Mail | Gmail | Outlook.com | Outlook Desktop |
|---|---|---|---|---|
| Web fonts | Yes | No | No | No |
| border-radius | Yes | Yes | Yes | No (renders square — designs must hold up at radius 0) |
| box-shadow | Yes | Partial | Yes | No |
| Dark mode meta | Yes | No | Yes | No |

Outlook Desktop drops border-radius entirely — every module needs to look acceptable as a plain rectangle, not just as the intended rounded card.
