---
name: email-shade-composition
description: Composes Hair Solutions Co. emails by sequencing module shades — Bone, Paper, Ink and a single Coral accent block — so consecutive campaigns feel visually different while staying unmistakably one brand. Use when choosing shades for a new email, when a draft reads flat, monotonous or "same as the last one", when deciding where an Ink or Coral block belongs, when varying a recurring series such as the newsletter, or when reviewing whether a shade sequence is coherent. Covers shade roles, run-and-switch rhythm, the seam as a framing device, the approved moods, what changes with the surface, and the accent vocabulary that creates variety inside one shade. Do not use this skill for hex values, the type scale, radius or spacing — use hair-solutions-email-design-system. Do not use it to build, paste or save blocks — use mailerlite-html-blocks. Do not use it for pre-send validation or ship approval — use mailerlite-email-preflight and email-ship-approval. Do not use it to write copy, choose imagery, or plan a campaign calendar.
---

# Email shade composition

Every module ships in three shades. That is the whole variation instrument: a campaign's mood
comes from *which shades its blocks sit on, in what order* — not from new modules, new colours or
new type. Composition is a sequencing problem.

**Authority:** the approved library at git tag `approved-module-library-2026-08-19`, and the
rendered references in `on-brand email templates inspirations/`. Read the real files at use time;
where this skill and an approved render disagree, the render wins.

## 1. The surfaces

Shade is a function, not a decoration. Assign by the job the block is doing.

| Surface | Role | Use for |
|---|---|---|
| **Bone** | Air. Lightest; recedes, creates breathing space. | Openers, seams, sign-offs, breaking a Paper run. |
| **Paper** | Body. The workhorse; warmer, holds attention. | Most content — heroes, statements, grids, offers, editorial. |
| **Ink** | Punctuation. Maximum weight; stops the eye. | A hero, a decisive CTA, header/footer framing. |
| **Coral** | Interruption. Maximum saturation. | **At most one block per email.** Never a header or footer. Ink text, ink CTA. |

Two errors dominate. Treating Ink as a *paragraph* rather than punctuation — it earns its effect
by scarcity. And spending Coral more than once — the second block cancels the first.

## 2. Runs and switches

Notate a draft top to bottom, one letter per block: `B B P P P B P`.

- **Run** — consecutive blocks on one shade. Runs create calm.
- **Switch** — a boundary between different shades. Switches create movement.
- **Switch density** — switches ÷ content blocks, seams excluded. Seams exist to manufacture
  switches, so counting them makes every seam-using email look frantic.

Density **describes** energy; it does not gate quality. The approved set spans 0.14 to 0.75, and
the per-mood ranges overlap heavily — so a sequence is never wrong for its density alone. Read it
as a reading, not a verdict.

Bone and Paper may sit directly adjacent. The visible gutter over a transparent page separates
them into distinct panels; two sands only read as an accidental gradient when sections are flush,
which this architecture never is. Every approved template relies on this.

Measure before arguing: `python3 scripts/shade_sequence.py "B B P P B I B"`.

## 3. The seam — the quietest instrument

A divider here is not separating topics. It is a **near-empty thin card carrying one mark**, and
its job is emphasis, not division.

**Its primary use is bracketing.** A seam above *and* below a block lifts that block out of the
surrounding flow — it frames it. In the approved set this is how a trust strip, a testimonial, or
a product row gets set apart, without changing its shade and without adding weight. A single seam
before a block instead marks one moment you want noticed.

Two properties make it read as a seam rather than an empty section:

- **Much thinner than a content card.** Minimal padding, one mark, nothing else.
- **On the opposite shade to what it separates.** Bone between Paper blocks, Paper between Bone.
  Matching the neighbours defeats it entirely.

It is the workhorse because it articulates a run without inventing content and without spending a
shade change on a whole block.

### One mark, three scales

A single email routinely uses all three.

| Scale | Where | Job |
|---|---|---|
| **Seam** | Its own thin card between content blocks | Frames and articulates; creates rhythm |
| **Edge** | Inside a card — under a logo, above a headline, above a cell | Caps and anchors one element |
| **Row rule** | Inside a card, repeated | Separates FAQ rows, list items, order lines |

### Choosing the mark

Structurally identical, emotionally different.

| Mark | Reads as | Use |
|---|---|---|
| Plain hairline | Neutral, utility | Order detail, transactional, content-first |
| Dashed or dotted rule | Softer, editorial | Between narrative sections, guides |
| Hairline with one centred coral dot | A deliberate flourish | **Once per email**, before the block to notice |
| Short coral rule | An opening accent | As an edge at a card's top, above the headline |

Constraints: one coral dot per email; a seam never opens or closes an email; two seams in a row is
a gap with decoration in it.

## 4. What travels with the shade

Changing a block's shade changes more than its background. Move all of it, or the block looks
broken rather than varied.

| | Bone / Paper | Ink | Coral |
|---|---|---|---|
| Heading | `#15140F` | `#F7F1DE` | `#15140F` |
| Muted text | `#5A5448` | `#DDD2B6` | `#15140F` |
| Card border | `#DDD2B6` | `#2A2620` | none |
| Primary CTA | Ink pill, Bone label | **Coral pill, Ink label** | Ink pill, Bone label |
| Social icons | Filled grey circles | Outlined circles | n/a |
| Nested inset | Paper Dark `#DDD2B6` | Ink Soft `#2A2620` | n/a |
| Logo | Dark lockup | Bone lockup, coral `co.` | Dark lockup |

**The CTA inverts with the shade.** On Bone and Paper the primary button is an ink pill
`#15140F` with a Bone label; on Ink it flips to a coral pill `#ED6F5C` with an ink label. Both
directions clear contrast comfortably — 16.3:1 and 6.2:1 — and the inversion is what keeps the
button reading as the heaviest object on whatever surface it sits on.

A Coral block follows the light rule: ink pill, Bone label. Coral on coral would vanish.

Decided 2026-08-19 by Vincent, adopting the treatment used in the rendered inspiration comps. The
earlier shipped library used a coral pill on every surface; all 54 light-shade pills were inverted
at that decision, so the library and this skill now agree. If you meet an older artifact with a
coral pill on Bone or Paper, it predates the change.

Paper Dark and Ink Soft are **inset fills only** — a recessed sub-card inside a block. Neither is
ever a block's own surface.

### Buttons

- **Ink pill, Bone label** — the primary CTA on Bone, Paper, and inside a Coral block.
- **Coral pill, ink label** — the primary CTA on Ink.
- **Outlined pill, ink label and arrow** — secondary. Pair it beside a filled pill.

## 5. The moods

Shapes, not templates. Pick by job, then fill with whatever modules the content needs.
`references/observed-compositions.md` holds the measured sequence behind each.

### Quiet — `B B P P B P`
Long light runs, no Ink. Observed 0.14–0.33. Calm and factual. Transactional, service, sensitive
news. Strip the chrome too: no announcement bar, no nav, footer reduced to legal links.

### Editorial — `P P P B P B P P B`
Paper-dominant, Bone used purely as breathing gaps. Observed 0.25–0.50. Considered and long-form.
Education, story, guides, narrative offers.

### Framed — `I I P B I B I`
Ink at both ends, light content between, one Ink block at the decision point. Observed 0.25–0.75 —
the widest band in the set, because framing tolerates both calm and high contrast.
Premium and deliberate. Welcome, launch, high-consideration moments.

### Punctuated — `B B P P B P P B`
Light throughout with one weighted block — Ink or Coral — placed exactly where the decision
happens. Observed 0.14–0.38. Bright, with a single moment of gravity. Promotions, CTA-led campaigns.

An **Ink-dominant** mood is not in the approved set. If a brief seems to want one, build it but
flag it as untested rather than shipping it as established.

## 6. Variety inside one shade

Two emails can share a sequence and still feel different, because the accent vocabulary rotates.
Pick two or three per email; using many reads as a sampler. Full list with usage notes in
`references/accent-vocabulary.md`.

The signature move is the **mixed-font headline** — a bold grotesque line followed by an italic
serif line ("Talk to someone who *builds these.*"). Then: coral serif prices, coral serif numerals
in numbered lists, the dashed coral code chip, glyph circle tiles for trust strips, a large coral
quote mark opening a testimonial, an avatar with a handwritten signature in the sign-off.

Alignment is also a variable. Centre a statement, left-align an editorial block. Shifting
alignment between adjacent blocks does more for perceived variety than changing a colour.

## 7. The spine that never varies

- Outer wrapper `background-color:transparent` — no page background, ever
- `az-module-shell`, `max-width:576px`, card-and-gutter stacking
- Role-based radius (header 8, hero 12, footer 16, content 20)
- Coral em-dash eyebrow: Courier, 11px, 700, uppercase, 2px tracking
- Grotesque headline, grey body, mono meta, serif for accents only
- Coral never carries body copy
- `Warmly, / Hair Solutions Co.` sign-off and a working unsubscribe

## 8. Procedure

1. State the job in one sentence.
2. Choose a mood from §5 by job, not taste.
3. List the blocks the content requires, in order.
4. Assign a shade per block using §1. Spend Ink sparingly; spend Coral once or not at all.
5. Bracket with seams (§3) any block that should sit apart — trust strip, testimonial, product row.
6. Write the shade string and run `python3 scripts/shade_sequence.py "<string>"`.
7. Fix what it flags, or record why the deviation is deliberate.
8. Apply §4 to every block whose shade you set — CTA colour first.
9. Pick two or three accents from §6; confirm the previous campaign in the series used a different
   mood or a different accent set.
10. Verify the §7 spine survived, then hand to `mailerlite-html-blocks` and
    `mailerlite-email-preflight`.

## 9. Reviewing a sequence

Diagnose in this order. Density is not on this list — it is a reading, not a defect.

1. **Ink as wallpaper** — three or more consecutive Ink blocks, or Ink over half the email.
2. **Coral spent twice** — two coral blocks, or a coral header or footer.
3. **Broken CTA** — ink pill on Ink, coral pill on Coral, or coral on light with no offer.
4. **Decorated gap** — two seams in a row, or a seam opening or closing the email.
5. **Spent flourish** — more than one coral-dot seam.
6. **Series fatigue** — the same mood twice running in one series. Change mood, not just copy.
7. **Sampler** — four or more accent devices in one email. Cut to two or three.

## Error Handling

- If an approved render and this skill disagree, follow the render and report the discrepancy.
  The library at `approved-module-library-2026-08-19` is the authority; this skill is its summary.
- If the required shade of a module does not exist in the library, stop and ask. Do not recolour a
  module inline — a missing shade is a build task, not a composition decision.
- If the brief needs a fifth surface, or a second Coral block, stop and request approval rather
  than inventing a variant.
- If `scripts/shade_sequence.py` reports an issue you intend to override, record the reason in the
  campaign brief. Density readings are never an issue and never require an override.
- If the sequence cannot satisfy the brief without breaking §7, escalate: the spine does not bend
  for a campaign.
- If a module renders correctly on one shade and breaks on another, treat it as a library defect,
  report it, and use a different shade until it is fixed.
