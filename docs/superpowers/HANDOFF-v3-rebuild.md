# Handoff — Journey Emails v3 Rebuild (Tasks 6–9)

**Written:** 2026-08-11 · **Branch:** `journey-emails-v3-rebuild` · **HEAD at handoff:** `0806814`

Tasks 1–5 of `docs/superpowers/plans/2026-08-11-journey-emails-v3-rebuild.md` are **complete,
reviewed and committed**. Tasks 6–9 remain. This document is the authority for resuming; it
outranks the plan wherever they disagree, because it records defects found in the plan itself.

---

## 1. How to resume

Invoke `superpowers:subagent-driven-development` with the plan file
`docs/superpowers/plans/2026-08-11-journey-emails-v3-rebuild.md`.

**Skip the Setup and pre-flight phase entirely** — it is done, and its findings are below.
Resume by dispatching **Task 6** with BASE = `0806814`.

Ledger (richer, chronological, includes every adjudication):
`.superpowers/sdd/2026-08-11-journey-emails-v3-rebuild/progress.md`

> ⚠️ `.superpowers/` is **gitignored**. `git clean -fdx` destroys the ledger and all task
> briefs/reports. The commits survive; the reasoning does not. This handoff is the committed backup.

---

## 2. Environment — already done, do not redo

| Fact | Detail |
|---|---|
| Git | Repo initialised (project was untracked). Branch `journey-emails-v3-rebuild` off `main`. `user.name`/`user.email` set locally — subagents can just `git commit`. |
| pytest | **Was not installed.** Installed 9.1.1 for `/usr/local/bin/python3`. `python3 -m pytest` works. |
| Live modules | Fetched to `/tmp/live` (91 modules). **`/tmp` is ephemeral** — if absent, re-fetch:<br>`hs cms fetch email_modules /tmp/live --account 50966981` |
| Tests | 35 passing. Run from `emails/second-pass/`: `python3 -m pytest tests/ -v` |

One test **hard-fails** (deliberately, not skips) if `/tmp/live` is missing:
`test_fields_for_every_key_is_real_across_all_28_emails`. That is by design — see §6.

---

## 3. What is built (Tasks 1–5)

| Commit | What |
|---|---|
| `ab1f8ed` | baseline |
| `d30a067`→`d3d9787` | **Task 1** `v3_source.py` — parses the v3 CSV into 28 email records |
| `72c2a37`→`fc6c54b` | **Task 2** `module_map.py` — 31 Notion families → live HubSpot slugs |
| `410da2b` | **Task 3** `placeholder_fields` — labelled placeholders for unavailable modules |
| `c3700a5`→`1754e4d` | **Task 4** `fields_for` — v3 copy → real module fields |
| `0806814` | **Task 5** `tonal_plan.py` — per-journey surface assignment |

### Verified properties (checked against the real export, not assumed)

- 28 emails parse; newsletters (`W ·`) excluded. All 31 stack families mapped, **zero unmapped**.
- `missing_families` = **4**: Cart line items, Viewed product, Dynamic recommendations, **Review stars**.
- Across all 130 copy-bearing blocks: **zero** returned field names are absent from their target
  module, and **zero** blocks produce entirely-empty field values.
- Surfaces: only paper/ink/coral. **Exactly 5 coral blocks** — PP-4 `Commerce - Shipping tracking`;
  CR-4/WB-3/RO-6/C-3 `Signal - Promo code`. None on chrome.
- Every stack opens on a Header family and closes on a Footer family.

---

## 4. Vincent's rulings (binding — do not re-litigate)

1. **CR-4 and RO-4 keep their FULL v3 stacks** (7 and 5 blocks), not the 3-module founder-letter
   shape the plan's prose suggests. The founder wrapper carries the whole unsegmented letter;
   stack slots with no matching copy render as visible bracketed placeholders, never blank.
   This is why coral stays at 5 (CR-4 keeps its promo block).
2. **Figma rebuild is approved**, including archiving the existing 22 frames from page `291:724`
   to page `357:1203`.
3. **`Review stars` is treated as unavailable** → `MODULE_MAP` `None` → labelled placeholder.
   Reason: the live module hardcodes `★★★★★` as literal text (`rating` only fills the "N/5"
   caption), so it always shows five filled stars; the Proof Bank is empty. Shipping it would
   have fabricated a rating in 5 emails.

---

## 5. Defects found **in the plan itself** — corrections already applied

The plan is not trustworthy as written. These were found and fixed during Tasks 1–5:

| Plan said | Reality |
|---|---|
| `parse_body` tags are alone on their line | 12 real tag lines carry `(recommended)`/`(optional)`; copy leaked into the previous block across 11 emails |
| — | `[PULL from Proof Bank: …]` was parsed as a module family; those 10 briefs would have vanished |
| Task 4 field table for `review_stars`: `rating_text`, `count_text` | Neither exists. Real: `eyebrow, rating, heading, body_text, button_label, button_url` |
| Task 4 field table for `timeline`: "label + matching detail" | Actually **three** fields per step: `step_N_label`, `step_N_heading`, `step_N_text` |
| Task 4 field table for `support_strip` includes `show_button` | It does not have `show_button` |
| Task 4 code routes 20 blocks to a generic branch | Those modules have no `body_text`; the copy was being **dropped** and demo defaults rendered |
| Task 5 test `assert … == "paper" or True` | Tautology — can never fail. Corrected to `== "ink"` (authorised deviation) |

### The hazard that outranks all others

`render_emails.block_html` does `ctx = defaults(folder)` then `ctx.update(values)`. **Any field not
supplied keeps that module's demo default**, and several demo defaults assert business facts:

- `commerce_shipping_tracking` → `'UPS Ground'`, tracking `'1Z999AA10123456784'`, `'Aug 9'`
- `trust_badge_row` → `'Free Shipping'`, `'30-day Money-back'`, `'Secure Payment'`
- `visual_comparison_cards` → `'Option A/B/C'`; `countdown_expiry` → `'Ends on [date]'`

**Rule: every module a branch targets must have every content-bearing field explicitly set or
blanked.** Task 4 now does this. Any new branch in Tasks 6–9 must too.

---

## 6. Landmines waiting in Tasks 6–9 — all verified present

### Task 6 — compose and render

1. **`render_emails.py:11`** is `LIVE = "final-verify"`. Must become `/tmp/live`.
2. **`render_emails.py:9`** is `from emails import EMAILS`. Must become `from compose_v3 import EMAILS`.
3. **`render_emails.py:51`** wraps each block in `padding:0 0 12px` — a **12px gap between
   modules**. The Global Constraints say *"The wrapper uses zero gap between modules; each
   module's own 32px padding sets the rhythm."* **These contradict.** The 12px gap is what makes
   sections read as separately tinted cards — the exact effect that was rejected on sight.
   Recommend setting it to `padding:0`. Confirm with Vincent, or at minimum render both and compare.
4. `_compose` in the plan swaps to `PLACEHOLDER_HOST` only when `resolve(fam) is None`. That is
   now correct because `Review stars` is `None`. Do not "fix" it to also swap for Testimonial —
   Testimonial has a real `quote_text` and its branch is correct.
5. The plan's `compose_v3.build()` calls `load_emails(CSV)` **inside a loop** to compute `total`
   — O(n²) file reads. Hoist it.

### Task 7 — audit

6. **`surface.py` has `SURFACES` but NOT `SUPPORTING`.** The plan's `audit.py` does
   `from surface import SURFACES, SUPPORTING` → **ImportError**. Define it from the Global
   Constraints: Bone `#F7F1DE`, Paper Dark `#DDD2B6`, Ink Soft `#2A2620`.
7. Task 7's screenshot step is the **first visual check of the whole rebuild**. Do not skip it.
   Look for: a wall of near-identical text blocks (means `fields_for` is over-using its generic
   branch), and whether sections read as one continuous field or as tinted cards (see landmine 3).

### Task 8 — Figma

8. **`spec_figma.py:12` is `from emails import EMAILS`.** Task 6's `sed` only repoints
   `render_emails.py`. If not also repointed, Task 8 regenerates Figma from the **stale 22-email
   composition**. Both `spec_figma.py` and `render_emails.py` import it.
9. Four Figma constraints already learned the hard way — in
   `~/.claude/skills/hubspot-email-modules/references/module-inventory.md`. Read before any
   `use_figma` call: `createImageAsync` unsupported (clone vector group `284:8864`, map its
   `#FF5757` suffix to `#ED6F5C` explicitly); `appendChild` throws on unloaded fonts (collect via
   `getStyledTextSegments(["fontName"])` and `loadFontAsync` first); `page.children` under-reports
   on a non-current page (verify with a second call that sets it current); only Inter, Inter Tight,
   JetBrains Mono and Playfair Display are installed.

### Task 9 — documentation

10. Record: the CSV-vs-markdown source hierarchy; that `module_map.py` is now the canonical
    family→slug mapping; that `text_block_generic` intentionally serves several semantic text
    slots; the per-email module-count table; and **the demo-defaults hazard in §5**, which is the
    single most valuable thing learned in this rebuild.

---

## 7. Open questions for Vincent (do not guess)

1. **Button destinations.** No CTA in the export carries a URL — only labels. Current code uses
   `https://hairsolutions.co/`. Real URLs are required before anything ships.
2. **J5 Consultation channel.** C-0 uses `{{ deal.hsc_quote_base_type }}`,
   `{{ deal.hsc_quote_down_payment }}` etc. Those are **deal** properties, not contact properties.
   Whether J5 sends from Sales (1:1, deal-scoped) or Marketing changes the subscription type and
   whether those tokens resolve at all.
3. **`OFFER — confirm before send`** appears twice in the copy. Those offers need confirming.
4. **C-0's Timeline has 5 steps; the module has 4.** Currently the 5th is folded into
   `step_4_text`. Confirm that is acceptable or ask for a 5-step module.
5. **`Comparison` → `visual_comparison_cards`** caps at 2 attributes per card while C-2's copy
   lists 5 candidate attributes. Copy gets trimmed at fill time.
6. **`review_stars` module bug** (separate from ruling 3): the whole card is wrapped in
   `{% if module.button_label %}` and the `{% endif %}` sits *inside* the table, so an empty
   `button_label` emits only stray `</td></tr></table></td></tr></table>`. Worth repairing in
   Design Manager whenever that module is next touched.

---

## 8. Process notes that paid off

- **Verify every plan claim against the live account before dispatching.** The plan's field table
  was wrong three times; `/tmp/live` settled it each time in seconds.
- **Nothing in Tasks 1–5 was caught by the plan's own tests.** Every real defect — leaked copy,
  vanished Proof Bank briefs, fabricated star ratings, dropped copy, demo-default business claims
  — was found by reading real data or real module templates. Keep doing that in 6–9.
- Implementers were told **never to guess a field name or slug** and to escalate instead. Task 4's
  implementer did exactly that and surfaced the `review_stars` template bug. Preserve that framing.
- Model tiers used: `haiku` where the plan contained complete code (transcription + testing),
  `sonnet` where judgment was needed (Task 4, all reviews). Task 8's Figma work needs `sonnet`+.
