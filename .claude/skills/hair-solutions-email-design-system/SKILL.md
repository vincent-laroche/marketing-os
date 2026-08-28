---
name: hair-solutions-email-design-system
description: The visual and typographic system for Hair Solutions Co. emails — surfaces, stacking, the role-locked type scale, section grammar, and component contracts. Use when designing, reviewing, or critiquing the look of any email module or campaign, when copy needs turning into sections, or when something "looks off" and you need the rule it broke. Pairs with mailerlite-html-blocks (how to build it), mailerlite-email-preflight (technical validation) and email-ship-approval (the seven-gate final check that decides whether it ships).
---

# Hair Solutions Co. — email design system

Authority: `brand-design-system/specs/PLATFORM_EMAIL.md`, present byte-identical at
`/Users/vMac/08_brand/…` and `/Users/vMac/07_design/brand/…`. Re-read it at use time.
**Where that spec is silent — radius, shadow, spacing scale — the authority is the Figma Email
Design System** (`figma.com/design/9Il504CQE8jLaUTBVzphqc`) and its export
`/Users/vMac/00_inbox/Downloads/email-marketing-main/DESIGN.md`. The two agree on the type stacks:
Inter Tight/Inter → Arial, Playfair Display → Georgia, JetBrains Mono → Courier New. This skill is
the working distillation plus the rules learned in production — it never overrides the spec.

## 1. The stack

An email is a column of **flush-stacked cards**. Each card is `max-width:576px` inside a wrapper
cell with **`padding:0 12px` — zero vertical**. No gaps. Radius is role-based (see §3) and every
card carries the 1px hairline. Alternating surfaces make the corners read as stacked boxes; that
rhythm *is* the design.

**The wrapper arithmetic is `CARD + 2 × GUTTER = 600`** — the spec's maximum wrapper. Both values
live in `scripts/build_wb1.py` as `GUTTER` / `CARD`; change one and the other follows.

| Card | Gutter | Token | Note |
|---|---|---|---|
| 568 | 16px | `spacing/base` | what we shipped until 2026-08-19 |
| **576** | **12px** | `spacing/md` | **current** — the practical maximum |
| 584 | 8px | `spacing/sm` | crowds the phone bezel |
| 600 | 0 | — | Figma's own value; full-bleed, and the stacked-card read disappears |

The gutter does double duty: on a 320px phone the same padding is the margin keeping cards off the
screen edge, so it cannot shrink far. Keep it at or above 12px, and never below the content radius
(20px) by so much that the inset reads as accidental. Widening the card does **not** disturb the
fitted line measures — 380/430/476 all sit below the content width either way.

```html
<table role="presentation" width="100%" style="background-color:transparent;border-collapse:collapse;margin:0;">
 <tr><td align="center" style="padding:0 16px;">
  <table role="presentation" class="az-module-shell" width="100%"
         style="max-width:568px;background-color:#EFE7D2;border:none;border-radius:16px;border-collapse:separate;">
    …
```

Outer body background is **Bone `#F7F1DE`** (`bone/100`, "lightest background — outer email
wrapper"). The `#F4F1EA` we shipped until 2026-08-19 was ours alone and appears in no palette.
In MailerLite the block's own **Background must be toggled OFF** or it paints a rectangle behind
the rounded corners.

### Radius is role-based, and every card has a hairline

There is **no radius rule in `PLATFORM_EMAIL.md`** — it is silent. The authority is the Figma
**Email Design System** (file `9Il504CQE8jLaUTBVzphqc`) and its `DESIGN.md`. One uniform 16px is
wrong; the system assigns radius by section role:

| Section | Token | Radius |
|---|---|---|
| Navigation / header | `radius/md` | **8px** |
| Hero | `radius/lg` | **12px** |
| Footer · Divider · Blog · Service | `radius/xl` | **16px** |
| Title · Content · Call-To-Action | `radius/2xl` | **20px** |
| Pill button | `radius/full` | 999px |

Every Figma section also carries `strokeWeight: 1px` in **`rgba(21,20,15,0.08)`** — a hairline that
separates stacked cards without a gap. We shipped `border:none`, which is why our stack read flatter
than the Figma comps. Outlook desktop ignores `border-radius`, so each module must still read
correctly at radius 0 — never let the rounding carry meaning.

## 2. Surfaces — one light, one dark

| Token | Hex | Role |
|---|---|---|
| Paper | `#EFE7D2` | **the** light card surface |
| Ink | `#15140F` | **the** dark card surface |
| Coral | `#ED6F5C` | accent block, ≤1 per email, never header/footer |
| Bone | `#F7F1DE` | text on Ink · inset panel *inside* a Paper card — **never a card surface** |
| Paper Dark | `#DDD2B6` | dividers on light · secondary text on Ink |
| Ink Soft | `#2A2620` | dividers on Ink |
| Ink Mute | `#5A5448` | muted body on light |

**One light.** Two adjacent light cards in slightly different lights reads as a bug, because it is.
Never put the wordmark on Coral — the coral "co" disappears.

## 3. Type — three families, role-locked

The spec allows three stacks. Use these **exactly**; `Helvetica Neue` and `SF Mono` are not in the
system and drift the design.

```css
font-family: Arial, Helvetica, sans-serif;              /* headings, body, buttons, footer */
font-family: 'Courier New', Courier, monospace;         /* metadata + eyebrow labels only */
font-family: Georgia, 'Times New Roman', Times, serif;  /* short emphasis, pull quote, founder note */
```

**Five sizes, two weights, one tracking.** Anything outside this table needs a reason.

| Role | Family | Size | Weight | Tracking |
|---|---|---|---|---|
| Eyebrow | Courier | 11px | 700 | 2px, uppercase |
| Metadata (attribution, role line) | Courier | 11px | 400 | — |
| Fine print (address) | Arial | 12px | 400 | — |
| Body · button label · link | Arial | 15px | 400 / 700 | — |
| Pull quote | Georgia italic | 22px | 700 | — |
| Title | Arial | 26px | 700 | −0.3px on Paper · +0.2px on Ink (see below) |

Sentence case everywhere. **Tracked uppercase is for eyebrow metadata only, never body copy.**
Georgia italic is a single deliberate accent — a quote is a different voice, so it earns a different
face. Using it anywhere else spends the effect.

A stack of eight sizes and three weights reads as "about ten fonts" even when it is three families.
Count the *styles*, not the families.

### Optical compensation on titles

Identical CSS does not render as equal weight. Light type on a dark ground **irradiates** — it
bleeds outward and reads both heavier and tighter. The same words in Ink on Paper look thinner and
more sparse. Set them side by side in a stacked email and the mismatch is obvious.

Arial has no weight above 700, so stroke weight cannot be matched. Track instead, and let them meet:

- Title on **Paper** → `letter-spacing:-0.3px`
- Title on **Ink** → `letter-spacing:0.2px`

This closes the "sparse" half of the gap, which is the larger part of what the eye catches. A small
residual weight difference remains and is inherent to the medium — do not chase it by bumping size
or breaking the scale.

### Line balance — the measure is fitted, not chosen once

Email has no `text-wrap: balance`. Every client greedy-wraps, so the last line's length is an
accident of where the words happen to run out. At the full 500px card measure that produced, in
WB-1: a 491px line over a 160px line (33%), and worse, `buying.` alone at 10%.

**You cannot fix this by picking one global width.** Measured across WB-1's five body runs, 380px
balances `close` (52%) and wrecks `pref` (25%); 410px does the exact reverse. There is no value
that passes all of them, because the failure depends on the string, not the column.

So the measure is **fitted per paragraph**, inside a band that is readable by construction:

| | |
|---|---|
| Band | **380–440px** — 53–61 characters at Arial 15px, inside the 45–75 rule |
| Metric | **min(line width) / max(line width) ≥ 45%** — min/max, *not* last/longest: a short **first** line scores 100% on last/longest and still looks broken |
| Applies to | runs of **2–3 lines**. In a 4+ line paragraph a short last line is just a paragraph ending |
| Always forbidden | a **single-word last line**, at any length. Bind the final two words with `&nbsp;` |

Fit it with the tool, never by eye:

```bash
python3 scripts/measure_lines.py --text "…" --width 430 --suggest   # fit one string
python3 scripts/measure_lines.py --audit mailerlite-blocks/wb1_*.html   # gate a whole build
```

It uses the real Arial/Courier/Georgia TTFs, models `&nbsp;` as glue and `<br/>` as a break, and
substitutes merge tags with their fallback rather than counting `{$name|default(there)}` literally.

**The model is a first pass; the renderer is the truth.** PIL measures glyph advances and the
browser shapes text, so PIL runs slightly narrow — enough to flip a marginal fit into an extra
line. On WB-1 it mis-fitted two of five runs: `pref` was modelled at 410px/2 lines/85% and actually
rendered 3 lines with `support.` alone (15%), and `hero` was capped at 380px when the sentence break
alone already balanced it at the full width (82%) — the cap forced a third line and made it worse.
Always confirm in a real render before shipping:

```js
const r = document.createRange(); r.selectNodeContents(el);
[...r.getClientRects()].filter(x => x.width > 1).map(x => x.width)   // true line boxes
```

Substitute merge tags in the DOM before measuring, or you are measuring `{$months_since_last_order}`
instead of `a few`.

**Mobile is free.** Card content on a 320px viewport is ~220px — narrower than the whole band — so
a `max-width` in the band never reaches mobile. It is a desktop-only correction with no mobile cost.

**Breaks: sentence boundaries only.** A `<br/>` at a *sentence* end survives re-wrap and wins at
both widths (WB-1 hero: 38%→100% desktop, 9%→72% mobile). A `<br/>` mid-sentence wins on desktop and
destroys mobile — `close` measured 24%→93% desktop but 68%→23% at 220px, because the clause fragment
is too short to fill a phone line. If a paragraph is a single sentence, it does not get a break; fit
the measure and accept what is left. Copy is verbatim — `<br/>` and `&nbsp;` are typography and are
allowed, re-wording is an edit and is not.

Outlook desktop ignores `max-width` on a div and falls back to the full 500px — i.e. exactly the rag
we ship today, so the degradation is never worse than the status quo.

## 4. Section grammar

Every section is the same four beats, any of which may be omitted:

**coral eyebrow with a leading `—`** → **large centred title** → **muted centred body** → **coral pill CTA**

```html
<span style="letter-spacing:0;padding-right:8px;">&mdash;</span>IF YOU STOPPED
```

The pill is `border-radius:999px`, Coral fill, **Ink label** (never Bone — fails contrast),
`padding:15px 30px`.

Titles break across two lines with `<br/>` at a natural phrase boundary; centred type with a ragged
single line looks accidental.

## 5. Rules learned in production

**Every section is a Code block, including text ones and the footer.** Native MailerLite text and
footer blocks cannot take the rounded card, so they break the stack. A custom footer must then carry
`{$unsubscribe}` and the verified postal address itself.

**Don't structure what should be spoken.** Copy written as a person talking stays prose. Lists,
rules and inset panels are for genuinely enumerable things — specs, features, steps. Splitting a
founder's sentence into bullets turns a personal note into a survey form. If the copy would be said
aloud in one breath, it is one paragraph.

**Don't let design contradict copy.** An email that opens "no pitch in this email" should not carry
a testimonial, a discount, or a product grid. Structural consistency is a design decision.

**Tonal identity per journey.** Choose a register for a whole series and hold it — Win-Back can run
mostly Ink, Post-Purchase mostly Paper. Contrast *between* journeys is good; randomness *within* one
is not. Mechanical light/dark alternation on every module is the tell of a generated email.

## 6. Component contracts

**Header** — Paper or Ink, never Coral. Wordmark centred, rendered at 220px wide.
Ink letterforms on Paper (`width="220" height="66"`, `padding:24px 26px`);
Bone letterforms on Ink (`width="259" height="114"`, `padding:0 26px` — the asset's own transparent
margin is the padding). Both produce a 114px card.

**Pull quote** — Coral 4px bar on the left, 20px gutter, Georgia italic 22px, Courier attribution.
Eyebrow and attribution left-aligned; the quote is not centred.

**Divider** — Figma `Email / Divider`. A short card whose only content is a 1px rule:
`padding:24px 40px`, `radius/xl` 16px, ~51px tall. Its job is to separate **two adjacent cards of
the same surface** — a stack of two Paper cards otherwise reads as one long card. It is not needed
where the surface already changes.

| Variant | Card | Border | Rule |
|---|---|---|---|
| **Bone** | Bone `#F7F1DE` | `#E5DFCD` | `#D3CEBD` |
| Light | Paper `#EFE7D2` | `#DED6C2` | `#CCC5B3` |
| Dark | Ink `#15140F` | Ink Soft `#2A2620` | Ink Soft `#2A2620` |

Saved in MailerLite as `Divider - Bone` / `Divider - Light` / `Divider - Dark`.

**Figma draws this card in pure white — do not copy that.** §1.1 forbids a pure-white section
surface outright, so Bone `#F7F1DE` is the brand's near-white and the correct substitute (confirmed
by Vincent 2026-08-19). Bone is nominally excluded as a *surface* by that same rule; the divider is
the one exemption, because it is a spacer carrying no content. Bone against Paper is a 1.09:1
step — deliberately quiet. Everywhere else, Bone remains text-on-Ink or an inset panel, never a card.

**Card borders are pre-composited solid hex, never `rgba()`.** Figma draws the stroke as
`rgba(21,20,15,0.08)`; Outlook's Word engine cannot parse `rgba()` and may fall back to black, so
ship `#DED6C2` on Paper, `#2A2620` on Ink, `#ECECEC` on white. Same for the divider rule
(`rgba(21,20,15,0.16)`).

**Footer** — Ink. Eyebrow, one short paragraph, `{$unsubscribe}`, then sender identity and the
verified postal address in fine print. Hairline dividers in Ink Soft.

**Personalization** — `{$field}` or `{$field|default(value)}`. Every token needs a fallback, and
the fallback must read naturally mid-sentence.

## 7. What the library ships vs what is correct

The Atelier Zero set (102 modules) ships a **near-miss palette** and **vertical wrapper padding**.
`scripts/make_mailerlite_blocks.py` corrects both. Role matters and inverts easily:
`#F6EFD9` is the light **card surface** → Paper; `#EDE3CC` is **text on dark** → Bone.
It also ships 18 dead `href="#"` links — see `mailerlite-email-preflight`.
