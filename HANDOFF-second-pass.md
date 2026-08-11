# Handoff — Second pass on the 22 journey emails (Figma)

Paste this into a fresh Claude Code session started in `/Users/vMac/04_marketing/Email Marketing`.

---

## Start here

Load the skill first: **`hubspot-email-modules`**. Its three reference files are the standards for this work:
- `references/design-system.md` — palette, typography scale, spacing, radius, alignment rule, and the editorial component vocabulary (ruled eyebrow, serif numerals, coral serif prices, eyebrow pill, meta row, mixed-font headings, glyph tiles, soft-fill sub-cards)
- `references/module-inventory.md` — every live module family + the Figma frame IDs for the assembled campaign references
- `references/deployment-playbook.md` — `hs cms` commands and failure modes

Figma file: `9Il504CQE8jLaUTBVzphqc` ("Email Design System"). Work on the **Journey Emails** page (`291:724`).

HubSpot account `50966981`. HubSpot Design Manager is the source of truth for module *design*; Figma is the review surface. Pull real module design from HubSpot (`hs cms fetch email_modules ./scratch --account 50966981`) so Figma reflects what will actually ship.

---

# PRIORITY 1 — Get the emails back on the brand palette

**This is the headline task. Do it first.** Vincent's direction: the brand has a great palette and the emails are barely using it. Fix that before anything else.

### The problem

Every module hardcodes its surface to exactly one of two colors — Bone (light) or Ink (dark) — as a fixed light/dark twin-file pair. Four other brand surfaces are effectively unused, and the emails alternate light/dark mechanically on every module (a naive toggle from the original build script). The result reads flat and monotonous, and it under-uses a palette that has real range.

| Surface | Hex | Current usage |
|---|---|---|
| Bone | `#F7F1DE` | The default light card — used constantly |
| Paper | `#EFE7D2` | Only ever a nested sub-card fill. **Never used as a card surface.** |
| Paper Dark | `#DDD2B6` | Only dividers/muted text. **Never a surface.** |
| Ink | `#15140F` | The default dark card — used constantly |
| Ink Soft | `#2A2620` | Only dividers/nested fills. **Never a surface.** |
| Coral | `#ED6F5C` | Buttons and accents only. Can carry a whole block. |

Bone → Paper → Paper Dark gives real tonal stepping inside the light register; Ink → Ink Soft does the same in the dark register. Use the full range.

**Pure white is out.** It was considered and explicitly rejected by Vincent: the brand spec (`06_design/brand/brand-design-system/specs/PLATFORM_EMAIL.md`) says card surfaces are Bone/Paper and *"Never pure white,"* and Bone `#F7F1DE` already covers the near-white role. Do not reintroduce it.

### The refactor

Modules need a **surface choice field** (Bone / Paper / Paper Dark / Ink / Ink Soft / Coral) instead of the current fixed light-or-dark twin files. Text/divider colors derive from the chosen surface — light surfaces get Ink text + Paper Dark dividers; dark surfaces get Bone text + Ink Soft dividers; Coral gets Ink text.

This replaces the twin-file convention (`family.module` + `family_dark.module`) with one module per family. That's a big change to ~90 live module folders, so:
- **Scope it with Vincent before starting.**
- **Prove the pattern on 3–5 high-traffic modules first** (header, footer, text block, hero, CTA) and show him before touching the rest.
- Existing emails reference the old module IDs — check what breaks before deleting any `_dark` module. Migration path matters more than speed here.

### Then compose tonally

Once modules can take any surface, give each email — or each whole journey — a deliberate tonal identity instead of even alternation:
- Some emails run **majority dark** with a few light sections as relief
- Others run the **inverse** — mostly light with one or two dark sections for weight
- A whole series can commit to one register (e.g. Win-Back dark throughout — the somber, we're-letting-you-go journey; Post-Purchase light and warm — the welcome-in journey). That's an example of the *kind* of decision, not a prescription.
- **Coral as a rare full-block moment** — a whole coral panel for a single offer or milestone, not just a button fill. Loudest thing in the system: at most once per email, and not in every email.

Vincent's framing: *"maybe we could say, okay, well, that series, we do it all black, the whole series."* Make a deliberate choice per journey, hold it consistently within that journey, and report the reasoning. Contrast between journeys is good; randomness within one is not.

---

# PRIORITY 2 — Fix these known bugs

1. **Weak footer design** — `Footer - Standard` renders as small plain text with no logo, no social row, no visual weight. It doesn't read as a footer at all; this was Vincent's specific complaint ("you don't have any footers in any of your emails"). They *are* present — they just look like nothing. Upgrade the HubSpot module against the footers in the Figma campaign frames below, then reflect it in Figma. Do this before rebuilding emails around it.
2. **Duplicate footers** — `WB-3` (`327:27302`) and `WB-4` (`327:27437`) each have two footers (Preference centre *and* Standard). Keep one. Preference centre is correct for Win-Back (it's the opt-down journey); Standard elsewhere.
3. **Dismantled v1 emails** — `PP-1` (`291:725`) and `PP-2` (`291:769`) have their pieces loose on the canvas as orphan siblings (`291:727`, `291:728`, `291:774`, `291:782`). Also loose: `327:27544` (Text-Reassurance), `327:29417` ("."). Clean these up.
4. **Two competing sets on one page** — the v1 (simple, IDs `291:*`–`294:*`) and v2 (richer, IDs `327:*`) assemblies both live on the Journey Emails page, 55 children total. Consolidate to one reviewable set. Confirm with Vincent whether to delete v1 or archive it before deleting anything.

---

# PRIORITY 3 — The second pass itself

Rebuild the 22 journey emails so they actually look designed. The module library was substantially upgraded *after* these were assembled, so the emails still use older, plainer module versions — flat text stacks and unstyled headings where the live modules now have real editorial treatments.

### Verify while you go

- **Logo** — headers should use the real wordmark:
  - light backgrounds → `https://50966981.fs1.hubspotusercontent-na1.net/hubfs/50966981/Logos/logo-v5-dark.png`
  - dark backgrounds → `https://50966981.fs1.hubspotusercontent-na1.net/hubfs/50966981/Logos/logo-v5-light.png`
  - (filename = the logo's own color, not the background — easy to invert by mistake)
- **Every email has exactly one header and one footer.**
- **Alignment** per the design system: left-align by default; centered only for whole-block promotional moments (promo/coupon blocks, standalone CTA cards) and dividers.

### Reference designs

The visual target lives in Figma on page **Modules Library + Hubspot Source** (`225:357`), in the assembled campaign frames. Screenshot these and match them — don't approximate:
- Welcome — New Customer Education: `284:21734`
- Abandoned Cart — Recovery: `284:21746`
- Post-Purchase — Care Guide: `284:21758`
- Promo — Seasonal Sale: `284:21772`
- Replenishment — Reorder: `284:21784`
- Win-Back — Re-engagement: `284:21796`

### The 22 emails

Real copy (subject, body, CTA, module stack) lives in the Notion `emails_master` database — data source `collection://6349f1df-1126-8256-a8c4-073286a7d05b`. Use real copy, never invent it.

- **Post-Purchase (6):** PP-1 Order Confirmation, PP-2 Prep Guide, PP-3 On The Bench, PP-4 Shipped + Tracking, PP-5 Maintenance Calendar, PP-7 How's It Going
- **Cart Recovery + Browse (5):** CR-1, CR-2, CR-3, CR-4, BR-1
- **Win-Back (4):** WB-1, WB-2, WB-3, WB-4
- **Reorder (5):** RO-1, RO-3, RO-4, RO-5, RO-6

`CR-3` and `RO-4` intentionally stay lean plain-text founder letters — their copy is pure "reply and I'll help you personally," with no natural hero/product moment. Confirmed with Vincent; don't add rich modules to those two.

**Still blocked:** PP-6 and RO-2 need a Product - Dynamic recommendations module that was deliberately deferred — Vincent wants native HubSpot/Shopify product modules for real catalog data, not another custom mimic. Leave those two aside unless he says otherwise.

---

## Hard rules

- **Never fabricate customer content.** Testimonials, review counts, star ratings, and stats have no real source data — they must stay as clearly-bracketed placeholders (`[Pull an approved customer quote…]`). Do not invent quotes, names, or numbers.
- **Don't send, schedule, or publish anything.** Module/Design Manager edits only. No CRM or workflow changes.
- **Verify live after any HubSpot upload** by fetching back — upload success alone isn't proof.
- **Document as you go.** Vincent has explicitly asked that new rules, gotchas, and design decisions get written into the skill's reference files the moment they're learned, not after repeated correction.

## Working style

Vincent wants deliberate, high-craft work over speed — his words: *"even if it takes some time, it's okay… take a decision… I am sure that you will make great decisions, and you can report back to me on that after."* Exercise real design judgment, then report what you decided and why. Show screenshots of finished emails for review.
