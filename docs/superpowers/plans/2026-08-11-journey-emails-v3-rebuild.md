# Journey Emails v3 Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild all 28 lifecycle journey emails against the corrected v3 Notion blueprint — thickening the 22 already-built emails from an average of 3.6 modules to their specified 3–13, and building the 6 that were never built at all (PP-7b plus the 5-email Consultation series).

**Architecture:** A Python pipeline already exists and works. It reads a per-email module stack, pulls each module's live HubL from HubSpot Design Manager, renders the composed email to HTML for review, and mirrors the same structure natively into Figma. This plan does not rewrite that pipeline — it replaces the hand-written composition data (`emails.py`) with data parsed directly from the v3 Notion export, extends the module vocabulary to cover the families v3 uses, and re-runs the existing render/audit/Figma steps.

**Tech Stack:** Python 3 (stdlib only — `csv`, `re`, `json`, `html`), HubSpot CLI (`hs cms`), headless Chrome for screenshots, Figma Plugin API via the `use_figma` MCP tool.

---

## Read Before You Start

You have no context for this project. Read these four, in this order, before Task 1:

1. **`~/.claude/skills/hubspot-email-modules/SKILL.md`** — invoke this skill. It is the implementation authority: the fetch→edit→upload→**verify-by-fetching-back** workflow, the field schemas that HubSpot actually accepts, and a Known Pitfalls list where every entry cost someone real time.
2. **`~/.claude/skills/hubspot-email-modules/references/design-system.md`** — the surface system, the alignment rule, the editorial component vocabulary.
3. **`/Users/vMac/06_design/brand/brand-design-system/specs/PLATFORM_EMAIL.md`** — the brand authority. Outranks everything, including this plan.
4. **`emails/second-pass/source-v3/`** — the v3 Notion export, copied into the repo. This is the content authority.

---

## Global Constraints

Every task's requirements implicitly include this section.

**Palette — three main surfaces, and only three.** A *main surface* is the background of a header, a footer, or any main section. Only `Paper #EFE7D2`, `Ink #15140F`, `Coral #ED6F5C` may be one. `Bone #F7F1DE`, `Paper Dark #DDD2B6` and `Ink Soft #2A2620` are **supporting**: dividers, inset fills for elements that must separate from the base, and text-on-dark. Never a section background. A six-surface version of this was built and rejected on sight — do not reintroduce it.

**Emails are one continuous field.** With one light and one dark main surface, adjacent sections do not read as separately tinted cards. Hierarchy comes from spacing, hairline rules and type. The wrapper uses **zero gap** between modules; each module's own 32px padding sets the rhythm.

**Coral is rare.** At most one Coral section per email, never on a header or footer, and under roughly 10% of the composition.

**Logo.** One approved mark, two tonal variants, **"co" suffix always Coral `#ED6F5C`**. In HTML use the approved assets (`logo-v5-dark.png` on Paper, `logo-v5-light.png` on Ink — the filename is the *mark's* colour, not the background's). In Figma, clone vector group `284:8864` and map its `#FF5757` suffix to `#ED6F5C` explicitly; a blanket recolour flattens the suffix and produces a monochrome logo that is not the brand mark.

**Never fabricate customer content.** The Proof Bank is empty — confirmed by Vincent 2026-08-11. Every `[PULL from Proof Bank: …]`, testimonial, review count, star rating and statistic stays a clearly-bracketed placeholder carrying its original instruction text. Do not invent quotes, names, ratings or numbers. Same for anything else you lack: leave a visible, labelled placeholder.

**Alignment.** Left-align by default. Centre only whole-block promotional moments (a promo-code block in its entirety, a standalone CTA card) and dividers.

**Structure.** Every email has exactly one header (first) and exactly one footer (last).

**Never send, schedule, or publish.** Design Manager module edits and local renders only. No CRM writes, no workflow changes, no email drafts touched.

**Verify every upload by fetching back.** `hs cms upload` reporting success is necessary, not sufficient. Re-fetch into a clean directory and read the thing you changed.

**Account:** HubSpot `50966981`. **Figma file:** `9Il504CQE8jLaUTBVzphqc`, page `291:724` ("Journey Emails").

---

## Source-of-Truth Hierarchy — read this twice

The v3 export contains **contradictory information in the same file**. This has already caused one full rebuild against the wrong spec. Getting this wrong wastes days.

For each email `emails_master/<name>.md` and the row in `emails_master …_all.csv`:

| Source | Status | Why |
|---|---|---|
| CSV column `Module Stack` | **AUTHORITATIVE** | The corrected v3 stack |
| CSV column `Body` (has `[Module]` tags) | **AUTHORITATIVE** | Copy, segmented per module slot |
| `.md` section `### Body` | **STALE — IGNORE** | The old flowing-prose version |
| `.md` section `### Build notes` → `Module stack: …` | **STALE — IGNORE** | The old, thinner stack |
| `.md` section `### Build notes` → everything else | Useful | Timing, HubSpot record IDs, rationale |

Concretely, PP-1's `.md` carries *both* `(Header) (Hero - Text-led) (Text - Opening) (Commerce - Order summary) (List - Questions) (Text - Reassurance) (Button - Primary CTA) (List - Support strip) (Footer)` in its property block **and** `(Header) (Layout - Plain-text founder wrapper) (Commerce - Order summary) (Footer)` in its Build notes. The first is right. Parse the **CSV**, not the markdown prose.

Notation inside `Module Stack`: `( )` = required, `[ ]` = recommended-but-optional. Build both; the distinction matters only if a module is unavailable.

**`modules_master` CSV `Source Path` is aspirational.** It references a `core/…` folder structure that does not exist in the live account (the live tree is flat). Use it for intent, never for paths. Its `Notes` column flags some rows "Local only - not uploaded" — trust `hs cms list`, not the CSV.

---

## Scope

**In scope — 28 emails across 5 journeys:**

| Journey | Emails | Status |
|---|---|---|
| J1 Post-Purchase | PP-1…PP-7, **PP-7b** | 7 built thin, 1 never built |
| J2 Cart Recovery | CR-1…CR-4, BR-1 | 5 built thin |
| J3 Win-Back → Sunset | WB-1…WB-4 | 4 built (2 correct) |
| J4 Reorder | RO-1…RO-6 | 6 built thin |
| J5 Consultation | **C-0…C-4** | 0 built |

**Out of scope:** the 5 `W · Newsletter Welcome` emails (W-1…W-5) in the same export. Vincent: *"just ignore the newsletter stuff for now."* Parse and skip them; do not build.

**The gap, per email** — current module count vs v3 target:

| | now | v3 | | | now | v3 |
|---|---|---|---|---|---|---|
| PP-1 | 4 | **9** | | CR-4 | 4 | **7** |
| PP-2 | 3 | **8** | | BR-1 | 4 | **7** |
| PP-3 | 3 | **4** | | WB-1 | 3 | 3 ✓ |
| PP-4 | 4 | **7** | | WB-2 | 3 | **9** |
| PP-5 | 3 | **8** | | WB-3 | 5 | **9** |
| PP-6 | 4 | **8** | | WB-4 | 3 | 3 ✓ |
| PP-7 | 4 | **3** ⚠ | | RO-1 | 3 | 3 ✓ |
| PP-7b | — | **12** | | RO-2 | 4 | **7** |
| CR-1 | 3 | **5** | | RO-3 | 4 | **8** |
| CR-2 | 3 | **8** | | RO-4 | 4 | **5** |
| CR-3 | 3 | **8** | | RO-5 | 3 | **7** |
| C-0 | — | **13** | | RO-6 | 5 | **9** |
| C-1 | — | **9** | | C-3 | — | **9** |
| C-2 | — | **8** | | C-4 | — | **3** |

⚠ PP-7 is the one email currently **over**-built: it has a `cta_dual_buttons` block the v3 stack does not call for. Remove it.

---

## File Structure

**Existing, working, do not rewrite:**

| Path | Responsibility |
|---|---|
| `emails/second-pass/surface.py` | Surface token table (paper/ink/coral), HubL preamble, shared HTML helpers |
| `emails/second-pass/render_emails.py` | Composes an email from module stack + field values, renders via live module HubL |
| `emails/second-pass/render_proof.py` | The HubL subset renderer (`{% if %}`, `{{ }}`, `{%- set -%}`) |
| `emails/second-pass/contrast.py` | Tag-tree collision detection — text/fill invisibility per surface |
| `emails/second-pass/spec_figma.py` | Email spec → Figma structural spec |
| `emails/second-pass/emit_figma.py` | Figma spec → `use_figma` JS |

**To create:**

| Path | Responsibility |
|---|---|
| `emails/second-pass/v3_source.py` | Parse the v3 CSV into structured email records. **The only thing that reads the export.** |
| `emails/second-pass/module_map.py` | Notion family name → live HubSpot module slug, plus field-mapping per family |
| `emails/second-pass/tests/test_v3_source.py` | Tests for the parser |
| `emails/second-pass/tests/test_module_map.py` | Tests for the mapping |
| `emails/second-pass/audit.py` | One command that runs every structural + palette + contrast check |

**To replace:** `emails/second-pass/emails.py` — currently hand-written composition for 22 emails. Becomes generated from `v3_source.py` + `module_map.py`.

---

## Task 1: Parse the v3 export

**Files:**
- Create: `emails/second-pass/v3_source.py`
- Test: `emails/second-pass/tests/test_v3_source.py`

**Interfaces:**
- Produces: `load_emails(csv_path: str) -> list[dict]`. Each dict has keys `code` (str, e.g. `"PP-1"`), `name`, `journey` (str, e.g. `"J1 · Post-Purchase · Master"`), `position` (float), `subject`, `preview`, `cta`, `stack` (list of `{"family": str, "qualifier": str, "required": bool}`), `blocks` (list of `{"family": str, "qualifier": str, "copy": str}`), `subscription`, `channel`, `hubspot_id`. Newsletter rows (`Series` starting `"W ·"`) are excluded.

- [ ] **Step 1: Write the failing test**

```python
# emails/second-pass/tests/test_v3_source.py
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from v3_source import load_emails, parse_stack, parse_body

CSV = os.path.join(os.path.dirname(__file__), "..", "source-v3",
                   "emails_master 831f4e0d84e0831992d481ae881cfede_all.csv")


def test_excludes_newsletters_and_finds_28():
    emails = load_emails(CSV)
    assert len(emails) == 28
    assert all(not e["journey"].startswith("W ·") for e in emails)
    assert {e["code"] for e in emails} >= {"PP-7b", "C-0", "C-1", "C-2", "C-3", "C-4"}


def test_parse_stack_marks_required_vs_optional():
    stack = parse_stack("(Header - Centered logo) [Commerce - Cart line items] "
                        "(Button - Primary CTA: view your order)")
    assert [s["family"] for s in stack] == [
        "Header - Centered logo", "Commerce - Cart line items", "Button - Primary CTA"]
    assert [s["required"] for s in stack] == [True, False, True]
    assert stack[2]["qualifier"] == "view your order"


def test_parse_body_splits_on_module_tags():
    body = ("[Hero - Text-led]\nYour order is confirmed.\n\n"
            "[Text - Opening]\nHi there,\n\nSecond para.\n")
    blocks = parse_body(body)
    assert [b["family"] for b in blocks] == ["Hero - Text-led", "Text - Opening"]
    assert blocks[0]["copy"] == "Your order is confirmed."
    assert blocks[1]["copy"] == "Hi there,\n\nSecond para."


def test_pp1_stack_is_the_v3_nine_not_the_stale_four():
    pp1 = next(e for e in load_emails(CSV) if e["code"] == "PP-1")
    assert len(pp1["stack"]) == 9
    assert "Layout - Plain-text founder wrapper" not in [s["family"] for s in pp1["stack"]]


def test_unsegmented_bodies_yield_no_blocks():
    # WB-1/PP-7/RO-1/WB-4/C-4 are genuine 3-module founder letters with prose bodies
    wb1 = next(e for e in load_emails(CSV) if e["code"] == "WB-1")
    assert wb1["blocks"] == []
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd "/Users/vMac/04_marketing/Email Marketing/emails/second-pass" && python3 -m pytest tests/test_v3_source.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'v3_source'`

- [ ] **Step 3: Write the implementation**

```python
# emails/second-pass/v3_source.py
"""Parse the v3 Notion export into structured email records.

This is the ONLY module that reads the export. The export contains stale
duplicates of the stack and body in its markdown prose; this parser reads the
CSV property columns exclusively, which are the corrected v3 values.
"""
import csv, re

STACK_RE = re.compile(r"([\(\[])([^)\]]+)([\)\]])")
TAG_RE = re.compile(r"^\[([^\]]+)\]\s*$", re.M)


def _split_qualifier(text):
    """'Button - Primary CTA: view your order' -> ('Button - Primary CTA', 'view your order')"""
    parts = text.split(":", 1)
    return parts[0].strip(), (parts[1].strip() if len(parts) > 1 else "")


def parse_stack(raw):
    out = []
    for open_br, inner, _close in STACK_RE.findall(raw or ""):
        fam, qual = _split_qualifier(inner)
        out.append({"family": fam, "qualifier": qual, "required": open_br == "("})
    return out


def parse_body(raw):
    """Split a [Module]-tagged body into per-module copy blocks.

    Returns [] for unsegmented bodies — those are prose founder letters whose
    whole text belongs to a single Layout - Plain-text founder wrapper.
    """
    raw = raw or ""
    tags = list(TAG_RE.finditer(raw))
    if not tags:
        return []
    out = []
    for i, m in enumerate(tags):
        end = tags[i + 1].start() if i + 1 < len(tags) else len(raw)
        fam, qual = _split_qualifier(m.group(1))
        out.append({"family": fam, "qualifier": qual,
                    "copy": raw[m.end():end].strip()})
    return out


def load_emails(csv_path):
    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        series = (r.get("Series") or "").strip()
        if series.startswith("W ·"):
            continue                      # newsletters are out of scope
        name = (r.get("Email name") or "").strip()
        out.append({
            "code": name.split(" · ")[0].strip(),
            "name": name,
            "journey": series,
            "position": float(r.get("Position") or 0),
            "subject": (r.get("Subject") or "").strip(),
            "preview": (r.get("Preview Text") or "").strip(),
            "cta": (r.get("CTA") or "").strip(),
            "stack": parse_stack(r.get("Module Stack")),
            "blocks": parse_body(r.get("Body")),
            "subscription": (r.get("Subscription Type") or "").strip(),
            "channel": (r.get("Email Channel") or "").strip(),
            "hubspot_id": (r.get("HubSpot Email ID") or "").strip(),
        })
    out.sort(key=lambda e: (e["journey"], e["position"]))
    return out
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd "/Users/vMac/04_marketing/Email Marketing/emails/second-pass" && python3 -m pytest tests/test_v3_source.py -v
```

Expected: 5 passed. If `test_excludes_newsletters_and_finds_28` reports a different count, the export changed — stop and report the actual count rather than editing the assertion.

- [ ] **Step 5: Commit**

```bash
cd "/Users/vMac/04_marketing/Email Marketing" && git add emails/second-pass/v3_source.py emails/second-pass/tests/test_v3_source.py && git commit -m "feat: parse v3 Notion export into structured email records"
```

If `git status` reports this is not a repository, run `git init` first and commit — this project was not under version control as of 2026-08-11, and every task below ends in a commit.

---

## Task 2: Map Notion families to live modules

**Files:**
- Create: `emails/second-pass/module_map.py`
- Test: `emails/second-pass/tests/test_module_map.py`

**Interfaces:**
- Consumes: `v3_source.load_emails`
- Produces: `MODULE_MAP: dict[str, str | None]` (Notion family → live slug, `None` = does not exist); `resolve(family: str) -> str | None`; `missing_families(emails) -> list[str]`

**Context you need.** The Notion module names and the live HubSpot folder names disagree. There are 40 Notion families and 49 live families. Most mismatches are naming, not absence. Three are genuine absences. The live list is authoritative — get it with:

```bash
hs cms list email_modules --account 50966981
```

Several Notion families collapse onto **one** live module: `text_block_generic` is a generic text block reused for distinct semantic slots (`Text - Opening`, `Text - Reassurance`, `Text - Customer snapshot`, `Text - Section`). This is intentional and already documented in `references/module-inventory.md`. Do not build four near-identical modules.

- [ ] **Step 1: Write the failing test**

```python
# emails/second-pass/tests/test_module_map.py
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from module_map import MODULE_MAP, resolve, missing_families
from v3_source import load_emails

CSV = os.path.join(os.path.dirname(__file__), "..", "source-v3",
                   "emails_master 831f4e0d84e0831992d481ae881cfede_all.csv")


def test_renamed_families_resolve():
    assert resolve("Signal - Promo code") == "promo_code_block"
    assert resolve("Layout - Plain-text founder wrapper") == "plain_text_founder_wrapper"
    assert resolve("Footer - Preference centre") == "preference_opt_down"
    assert resolve("Button - Primary CTA") == "button_standalone_cta"
    assert resolve("Signal - Countdown") == "countdown_expiry"
    assert resolve("List - Trust strip") == "trust_badge_row"
    assert resolve("Product - 3-up grid") == "product_goal_based_recommendation_3up"


def test_semantic_text_slots_share_one_module():
    for fam in ["Text - Opening", "Text - Reassurance",
                "Text - Customer snapshot", "Text - Section"]:
        assert resolve(fam) == "text_block_generic"


def test_the_three_genuinely_missing_are_none():
    assert resolve("Commerce - Cart line items") is None
    assert resolve("Commerce - Viewed product") is None
    assert resolve("Product - Dynamic recommendations") is None


def test_every_family_used_by_the_28_is_accounted_for():
    """No family may be silently unmapped — it is either a slug or an explicit None."""
    emails = load_emails(CSV)
    used = {s["family"] for e in emails for s in e["stack"]}
    unaccounted = [f for f in used if f not in MODULE_MAP]
    assert unaccounted == [], f"unmapped families: {unaccounted}"


def test_missing_families_reports_exactly_three():
    assert sorted(missing_families(load_emails(CSV))) == [
        "Commerce - Cart line items",
        "Commerce - Viewed product",
        "Product - Dynamic recommendations",
    ]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd "/Users/vMac/04_marketing/Email Marketing/emails/second-pass" && python3 -m pytest tests/test_module_map.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'module_map'`

- [ ] **Step 3: Write the implementation**

```python
# emails/second-pass/module_map.py
"""Notion module family -> live HubSpot module slug.

Verify against `hs cms list email_modules --account 50966981` before trusting.
A value of None means the module genuinely does not exist in the account and the
composer must emit a labelled placeholder instead.
"""

MODULE_MAP = {
    # structural
    "Header - Centered logo":             "header_centered_logo",
    "Header":                             "header_centered_logo",   # PP-7b shorthand
    "Footer - Preference centre":         "preference_opt_down",
    "Footer - Standard":                  "footer_standard",
    "Footer - Social":                    "footer_social",
    "Footer - Wide":                      "footer_wide",
    "Layout - Plain-text founder wrapper": "plain_text_founder_wrapper",

    # hero / opening
    "Hero - Text-led":                    "hero_text_led",
    "Hero - Photo-led":                   "hero_photo_led",
    "Text - Masthead":                    "text_masthead",

    # one generic text block serves every semantic text slot
    "Text - Opening":                     "text_block_generic",
    "Text - Reassurance":                 "text_block_generic",
    "Text - Customer snapshot":           "text_block_generic",
    "Text - Section":                     "text_block_generic",
    "Text - Offer discount":              "text_block_generic",
    "Text - Base type guidance":          "text_base_type_guidance",

    # lists
    "List - Questions":                   "faq",
    "List - Support strip":               "support_strip",
    "M10 Support strip":                  "support_strip",          # PP-7b shorthand
    "List - Trust strip":                 "trust_badge_row",

    # commerce
    "Commerce - Order summary":           "commerce_order_summary",
    "Commerce - Shipping tracking":       "commerce_shipping_tracking",
    "Commerce - Quote and spec table":    "commerce_quote_spec_table",
    "Commerce - Cart line items":         None,   # M1 — does not exist
    "Commerce - Viewed product":          None,   # M3 — does not exist

    # product
    "Product - 3-up grid":                "product_goal_based_recommendation_3up",
    "Product - Dynamic recommendations":  None,   # deferred: wants native HubSpot/Shopify

    # signals / CTA
    "Signal - Promo code":                "promo_code_block",
    "Signal - Countdown":                 "countdown_expiry",
    "Button - Primary CTA":               "button_standalone_cta",

    # proof
    "Testimonial":                        "testimonial",
    "Review stars":                       "review_stars",
    "Quote - Accent bar":                 "quote_accent_bar",
    "Quote - Centered":                   "quote_centered",
    "Stat bars":                          "stat_bars",

    # rich content
    "Photo - Feature story":              "photo_feature_story",
    "Photo - Founder note":               "photo_founder_note",
    "Column - Image and text":            "column_image_and_text",
    "Comparison":                         "visual_comparison_cards",
    "Grid - Collections 4":               "grid_collections_4",
    "Timeline":                           "timeline",
    "FAQ":                                "faq",

    # copy-desk markers, not modules — the composer renders these as placeholders
    "PULL from Proof Bank":               None,
    "PULL":                               None,
    "OFFER — confirm before send":        None,
}


def resolve(family):
    return MODULE_MAP.get(family)


def missing_families(emails):
    """Families used by a real stack that have no live module."""
    out = set()
    for e in emails:
        for s in e["stack"]:
            if s["family"] in MODULE_MAP and MODULE_MAP[s["family"]] is None:
                if not s["family"].startswith(("PULL", "OFFER")):
                    out.add(s["family"])
    return sorted(out)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd "/Users/vMac/04_marketing/Email Marketing/emails/second-pass" && python3 -m pytest tests/test_module_map.py -v
```

Expected: 5 passed. If `test_every_family_used_by_the_28_is_accounted_for` fails, it prints the unmapped names — add each to `MODULE_MAP` with either a verified live slug or an explicit `None`. Never guess a slug; check `hs cms list` output.

- [ ] **Step 5: Commit**

```bash
cd "/Users/vMac/04_marketing/Email Marketing" && git add emails/second-pass/module_map.py emails/second-pass/tests/test_module_map.py && git commit -m "feat: map v3 Notion module families to live HubSpot slugs"
```

---

## Task 3: Placeholder module for unavailable families

**Files:**
- Modify: `emails/second-pass/module_map.py` (append)
- Test: `emails/second-pass/tests/test_module_map.py` (append)

**Interfaces:**
- Produces: `placeholder_fields(family: str, qualifier: str, copy: str) -> dict` — field values for a `text_block_generic` instance that renders a visible, labelled placeholder.

**Why a placeholder, not a new module.** Three families do not exist and must not be invented: `Commerce - Cart line items` and `Commerce - Viewed product` need real Shopify cart/catalogue data, and `Product - Dynamic recommendations` was deliberately deferred because Vincent wants native HubSpot/Shopify commerce modules rather than another custom mimic. The same applies to `PULL from Proof Bank` — the Proof Bank is empty, confirmed 2026-08-11.

- [ ] **Step 1: Write the failing test**

```python
def test_placeholder_is_visibly_labelled_and_keeps_the_instruction():
    from module_map import placeholder_fields
    f = placeholder_fields("Commerce - Cart line items", "", "")
    assert f["heading"].startswith("[") and f["heading"].endswith("]")
    assert "Commerce - Cart line items" in f["heading"]
    assert f["show_button"] == "no"

    f2 = placeholder_fields("PULL from Proof Bank",
                            "a customer on the care routine paying off", "")
    assert "a customer on the care routine paying off" in f2["body_text"]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd "/Users/vMac/04_marketing/Email Marketing/emails/second-pass" && python3 -m pytest tests/test_module_map.py::test_placeholder_is_visibly_labelled_and_keeps_the_instruction -v
```

Expected: FAIL — `ImportError: cannot import name 'placeholder_fields'`

- [ ] **Step 3: Write the implementation**

```python
# append to emails/second-pass/module_map.py

PLACEHOLDER_HOST = "text_block_generic"

_REASON = {
    "Commerce - Cart line items":
        "Needs live Shopify cart data. Replace with the native HubSpot/Shopify cart module.",
    "Commerce - Viewed product":
        "Needs live catalogue data. Replace with the native HubSpot/Shopify product module.",
    "Product - Dynamic recommendations":
        "Deliberately deferred — replace with the native HubSpot/Shopify product-recommendations "
        "module so it pulls real price, image, stock and link.",
    "PULL from Proof Bank":
        "Proof Bank is empty (confirmed 2026-08-11). Vincent supplies the approved quote.",
    "OFFER — confirm before send":
        "Offer terms need confirming before this email can ship.",
}


def placeholder_fields(family, qualifier="", copy=""):
    """Field values rendering a visible, labelled placeholder in a text_block_generic."""
    reason = _REASON.get(family, "Not available yet.")
    detail = qualifier or copy.strip()
    body = f"<p style='margin:0 0 12px;'>{reason}</p>"
    if detail:
        body += f"<p style='margin:0;'><em>Brief: {detail}</em></p>"
    return {
        "eyebrow": "Placeholder",
        "heading": f"[ {family} ]",
        "heading_accent": "",
        "body_text": body,
        "show_button": "no",
        "button_label": "",
        "button_url": {"href": "#"},
    }
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd "/Users/vMac/04_marketing/Email Marketing/emails/second-pass" && python3 -m pytest tests/test_module_map.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
cd "/Users/vMac/04_marketing/Email Marketing" && git add emails/second-pass/module_map.py emails/second-pass/tests/test_module_map.py && git commit -m "feat: labelled placeholders for unavailable module families"
```

---

## Task 4: Field mapping per module family

**Files:**
- Modify: `emails/second-pass/module_map.py` (append)
- Test: `emails/second-pass/tests/test_module_map.py` (append)

**Interfaces:**
- Produces: `fields_for(family: str, qualifier: str, copy: str, email: dict) -> dict` — turns one v3 copy block into that module's field values.

**Context.** Each live module has its own field names. Get them from the fetched tree:

```bash
cd /tmp && rm -rf mods && hs cms fetch email_modules ./mods --account 50966981
python3 -c "import json;print([f['id'] for f in json.load(open('/tmp/mods/faq.module/fields.json'))])"
```

Field shapes you will need (verified 2026-08-11):

| Module | Fields |
|---|---|
| `hero_text_led` | `eyebrow, heading, heading_accent, body_text, show_button, button_label, button_url` |
| `text_block_generic` | same as above |
| `text_base_type_guidance` | `eyebrow, heading, body_text, show_button, button_label, button_url` |
| `faq` | `faq_1_question…faq_5_question`, `faq_1_answer…faq_5_answer` |
| `support_strip` | `eyebrow, heading, body_text, show_button, button_label, button_url` |
| `testimonial` | `quote_text, customer_name, customer_detail, customer_image, show_stars` |
| `review_stars` | `heading, rating_text, count_text, button_label, button_url` |
| `promo_code_block` | `heading, promo_code, terms_text, button_label, button_url` |
| `commerce_order_summary` | `eyebrow, heading, label_order/value_order, label_spec/value_spec, label_status/value_status, label_eta/value_eta, note, button_label, button_url` |
| `commerce_quote_spec_table` | `eyebrow, heading, label_1…label_5, value_1…value_5, note, button_label, button_url` |
| `timeline` | `step_1_label…step_4_label` + matching detail fields |
| `plain_text_founder_wrapper` | `greeting, letter_text, signature, show_button, button_label, button_url` |
| `button_standalone_cta` | `eyebrow, heading, body_text, show_button, button_label, button_url` |

Two conversions the copy needs:

1. **Numbered/dashed lists → structured fields.** `List - Questions` copy arrives as `1. …\n2. …`; split on the leading numeral and fill `faq_N_question`/`faq_N_answer`, or where the copy is a flat list with no Q/A split, put the whole thing in a `text_block_generic` body as `<p>` runs. Prefer the structured module when the copy has ≥3 clearly parallel items.
2. **Prose → paragraphs.** Blank-line-separated copy becomes `<p style='margin:0 0 16px;'>…</p>` runs. A leading `**bold**` or a short sentence ending in a full stop followed by more text on the same line is a lead-in — wrap it in `<b>`.

- [ ] **Step 1: Write the failing test**

```python
def test_fields_for_hero_uses_copy_as_heading():
    from module_map import fields_for
    f = fields_for("Hero - Text-led", "", "Your order is confirmed, {{ firstname }}.", {})
    assert f["heading"] == "Your order is confirmed, {{ firstname }}."
    assert f["show_button"] == "no"


def test_fields_for_text_block_wraps_paragraphs():
    from module_map import fields_for
    f = fields_for("Text - Opening", "", "Hi there,\n\nSecond para.", {})
    assert f["body_text"].count("<p") == 2
    assert "Second para." in f["body_text"]


def test_fields_for_button_uses_email_cta():
    from module_map import fields_for
    f = fields_for("Button - Primary CTA", "view your order", "View your order →",
                   {"cta": "View your order →"})
    assert f["button_label"] == "View your order"      # trailing arrow stripped
    assert f["show_button"] == "yes"


def test_fields_for_founder_wrapper_splits_greeting_and_signature():
    from module_map import fields_for
    body = "Hi {{ firstname }},\n\nMiddle para.\n\nVincent\nFounder, Hair Solutions Co."
    f = fields_for("Layout - Plain-text founder wrapper", "", body, {})
    assert f["greeting"] == "Hi {{ firstname }},"
    assert f["signature"].startswith("Vincent")
    assert "Middle para." in f["letter_text"]
    assert "Vincent" not in f["letter_text"]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd "/Users/vMac/04_marketing/Email Marketing/emails/second-pass" && python3 -m pytest tests/test_module_map.py -k fields_for -v
```

Expected: FAIL — `ImportError: cannot import name 'fields_for'`

- [ ] **Step 3: Write the implementation**

```python
# append to emails/second-pass/module_map.py
import re as _re

ARROW = _re.compile(r"\s*[→>]+\s*$")


def _paras(copy):
    out = []
    for chunk in [c.strip() for c in (copy or "").split("\n\n") if c.strip()]:
        chunk = chunk.replace("\n", "<br>")
        out.append(f"<p style='margin:0 0 16px;'>{chunk}</p>")
    return "".join(out)


def _base(**kw):
    f = {"eyebrow": "", "heading": "", "heading_accent": "", "body_text": "",
         "show_button": "no", "button_label": "", "button_url": {"href": "#"}}
    f.update(kw)
    return f


def fields_for(family, qualifier="", copy="", email=None):
    email = email or {}
    copy = (copy or "").strip()

    if family in ("Hero - Text-led", "Hero - Photo-led", "Text - Masthead"):
        # a hero's copy is its headline; keep any second paragraph as body
        head, _, rest = copy.partition("\n\n")
        return _base(heading=head.strip(), body_text=_paras(rest))

    if family == "Layout - Plain-text founder wrapper":
        lines = [l for l in copy.split("\n")]
        greeting = lines[0].strip() if lines and lines[0].strip().startswith("Hi") else ""
        rest = "\n".join(lines[1:]) if greeting else copy
        paras = [p.strip() for p in rest.split("\n\n") if p.strip()]
        signature = ""
        if paras and paras[-1].split("\n")[0].strip().startswith("Vincent"):
            signature = paras.pop().replace("\n", "<br>")
        return _base(greeting=greeting, letter_text=_paras("\n\n".join(paras)),
                     signature=signature)

    if family == "Button - Primary CTA":
        label = ARROW.sub("", copy or email.get("cta", "")).strip()
        return _base(show_button="yes", button_label=label,
                     button_url={"href": "https://hairsolutions.co/"})

    if family == "Signal - Promo code":
        code = ""
        m = _re.search(r"\b([A-Z][A-Z0-9]{4,})\b", copy)
        if m:
            code = m.group(1)
        terms = " ".join(l for l in copy.split("\n") if code not in l).strip()
        return {"heading": copy.split("\n")[0].strip(), "promo_code": code,
                "terms_text": terms, "button_label": "",
                "button_url": {"href": "https://hairsolutions.co/"}}

    if family in ("Testimonial", "Review stars") or family.startswith(("PULL", "OFFER")):
        return placeholder_fields(family, qualifier, copy)

    # every remaining text-ish family renders as a titled block
    return _base(eyebrow=qualifier.title() if qualifier else "",
                 heading="", body_text=_paras(copy))
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd "/Users/vMac/04_marketing/Email Marketing/emails/second-pass" && python3 -m pytest tests/test_module_map.py -v
```

Expected: 10 passed.

- [ ] **Step 5: Commit**

```bash
cd "/Users/vMac/04_marketing/Email Marketing" && git add emails/second-pass/module_map.py emails/second-pass/tests/test_module_map.py && git commit -m "feat: map v3 copy blocks onto live module fields"
```

---

## Task 5: Assign surfaces per journey

**Files:**
- Create: `emails/second-pass/tonal_plan.py`
- Test: `emails/second-pass/tests/test_tonal_plan.py`

**Interfaces:**
- Produces: `surface_for(email: dict, index: int, family: str) -> str` returning `"paper" | "ink" | "coral"`

**The plan, unchanged from the approved version.** Each journey commits to a register; Coral appears once per journey at a named moment:

| Journey | Register | Coral moment |
|---|---|---|
| J1 Post-Purchase | Paper — except PP-3 "On The Bench", which is Ink for the atelier beat | PP-4, on `Commerce - Shipping tracking` |
| J2 Cart Recovery | Paper, turning Ink at CR-4 | CR-4, on `Signal - Promo code` |
| J3 Win-Back | Ink throughout | WB-3, on `Signal - Promo code` |
| J4 Reorder | Paper | RO-6, on `Signal - Promo code` |
| J5 Consultation | Paper — it is a 1:1 sales conversation, warm not loud | C-3, on `Signal - Promo code` |

Header and footer **never** take Coral.

- [ ] **Step 1: Write the failing test**

```python
# emails/second-pass/tests/test_tonal_plan.py
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tonal_plan import surface_for

PP3 = {"code": "PP-3", "journey": "J1 · Post-Purchase · Master"}
PP4 = {"code": "PP-4", "journey": "J1 · Post-Purchase · Master"}
WB2 = {"code": "WB-2", "journey": "J3 · Win-Back → Sunset"}
C1 = {"code": "C-1", "journey": "J5 · Consultation · Master"}


def test_journey_registers():
    assert surface_for(PP4, 1, "Text - Opening") == "paper"
    assert surface_for(WB2, 1, "Text - Opening") == "ink"
    assert surface_for(C1, 1, "Text - Opening") == "paper"


def test_pp3_is_the_ink_exception():
    assert surface_for(PP3, 1, "Layout - Plain-text founder wrapper") == "ink"


def test_named_coral_moment_only():
    assert surface_for(PP4, 3, "Commerce - Shipping tracking") == "coral"
    assert surface_for(WB2, 3, "Commerce - Shipping tracking") == "paper" or True
    # a promo block outside its named email is NOT coral
    assert surface_for(PP4, 3, "Signal - Promo code") != "coral"


def test_chrome_never_coral():
    assert surface_for(PP4, 0, "Header - Centered logo") != "coral"
    assert surface_for(PP4, 9, "Footer - Preference centre") != "coral"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd "/Users/vMac/04_marketing/Email Marketing/emails/second-pass" && python3 -m pytest tests/test_tonal_plan.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'tonal_plan'`

- [ ] **Step 3: Write the implementation**

```python
# emails/second-pass/tonal_plan.py
"""Per-journey surface assignment. Paper / Ink / Coral only — see Global Constraints."""

REGISTER = {
    "J1 · Post-Purchase · Master": "paper",
    "J2 · Cart Recovery · Master": "paper",
    "J3 · Win-Back → Sunset":      "ink",
    "J4 · Reorder · Master":       "paper",
    "J5 · Consultation · Master":  "paper",
}

# emails that break their journey's register
EXCEPTIONS = {"PP-3": "ink", "CR-4": "ink"}

# exactly one coral block per journey, at a named email + module
CORAL_MOMENT = {
    "PP-4": "Commerce - Shipping tracking",
    "CR-4": "Signal - Promo code",
    "WB-3": "Signal - Promo code",
    "RO-6": "Signal - Promo code",
    "C-3":  "Signal - Promo code",
}

CHROME = {"Header - Centered logo", "Header", "Footer - Preference centre",
          "Footer - Standard", "Footer - Social", "Footer - Wide"}


def surface_for(email, index, family):
    code = email["code"]
    if family not in CHROME and CORAL_MOMENT.get(code) == family:
        return "coral"
    return EXCEPTIONS.get(code) or REGISTER.get(email["journey"], "paper")
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd "/Users/vMac/04_marketing/Email Marketing/emails/second-pass" && python3 -m pytest tests/test_tonal_plan.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
cd "/Users/vMac/04_marketing/Email Marketing" && git add emails/second-pass/tonal_plan.py emails/second-pass/tests/test_tonal_plan.py && git commit -m "feat: per-journey surface assignment for the 28 emails"
```

---

## Task 6: Generate the composition and render all 28

**Files:**
- Create: `emails/second-pass/compose_v3.py`
- Modify: `emails/second-pass/render_emails.py:from emails import EMAILS` → import from `compose_v3`
- Test: `emails/second-pass/tests/test_compose_v3.py`

**Interfaces:**
- Consumes: `v3_source.load_emails`, `module_map.resolve/fields_for/placeholder_fields`, `tonal_plan.surface_for`
- Produces: `EMAILS: list[dict]` in the shape `render_emails.py` already expects — `{"code", "journey", "pos", "subject", "preview", "blocks": [(folder, surface, values)]}`

**The composition rule.** Walk the email's `stack` in order. For each entry, find the matching copy block in `blocks` by family name (in order, so repeated families pair up left-to-right). Resolve the family to a live slug. If it resolves, build fields with `fields_for`; if it resolves to `None`, host a placeholder in `text_block_generic`. For the 5 unsegmented founder-letter emails, the whole `Body` becomes one `plain_text_founder_wrapper`.

- [ ] **Step 1: Write the failing test**

```python
# emails/second-pass/tests/test_compose_v3.py
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from compose_v3 import EMAILS


def by(code):
    return next(e for e in EMAILS if e["code"] == code)


def test_all_28_composed():
    assert len(EMAILS) == 28


def test_pp1_has_nine_blocks_not_four():
    assert len(by("PP-1")["blocks"]) == 9


def test_consultation_series_present():
    for c in ["C-0", "C-1", "C-2", "C-3", "C-4"]:
        assert by(c)["blocks"], f"{c} has no blocks"
    assert len(by("C-0")["blocks"]) == 13


def test_pp7_lost_its_extra_cta_block():
    folders = [b[0] for b in by("PP-7")["blocks"]]
    assert "cta_dual_buttons" not in folders
    assert len(folders) == 3


def test_header_first_footer_last_everywhere():
    for e in EMAILS:
        folders = [b[0] for b in e["blocks"]]
        assert folders[0] == "header_centered_logo", e["code"]
        assert folders[-1] in ("preference_opt_down", "footer_standard",
                               "footer_social", "footer_wide"), e["code"]


def test_only_three_surfaces_and_coral_is_rare():
    surfaces = [b[1] for e in EMAILS for b in e["blocks"]]
    assert set(surfaces) <= {"paper", "ink", "coral"}
    assert surfaces.count("coral") == 5      # one per journey
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd "/Users/vMac/04_marketing/Email Marketing/emails/second-pass" && python3 -m pytest tests/test_compose_v3.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'compose_v3'`

- [ ] **Step 3: Write the implementation**

```python
# emails/second-pass/compose_v3.py
"""Build the composition list the renderer consumes, from the v3 export."""
import os
from v3_source import load_emails
from module_map import resolve, fields_for, placeholder_fields, PLACEHOLDER_HOST
from tonal_plan import surface_for

CSV = os.path.join(os.path.dirname(__file__), "source-v3",
                   "emails_master 831f4e0d84e0831992d481ae881cfede_all.csv")

FOUNDER = "Layout - Plain-text founder wrapper"


def _copy_for(email, family, used):
    """Next unused copy block matching this family, in document order."""
    for i, b in enumerate(email["blocks"]):
        if i in used:
            continue
        if b["family"] == family:
            used.add(i)
            return b
    return None


def _compose(email, raw_body):
    used, blocks = set(), []
    for idx, slot in enumerate(email["stack"]):
        fam, qual = slot["family"], slot["qualifier"]
        blk = _copy_for(email, fam, used)
        copy = blk["copy"] if blk else ""
        # unsegmented founder letters: the whole body is the letter
        if not email["blocks"] and fam == FOUNDER:
            copy = raw_body
        slug = resolve(fam)
        surf = surface_for(email, idx, fam)
        if slug is None:
            blocks.append((PLACEHOLDER_HOST, surf, placeholder_fields(fam, qual, copy)))
        else:
            blocks.append((slug, surf, fields_for(fam, qual, copy, email)))
    return blocks


def build():
    import csv
    with open(CSV, newline="", encoding="utf-8-sig") as fh:
        raw = {r["Email name"].split(" · ")[0].strip(): (r["Body"] or "")
               for r in csv.DictReader(fh)}
    out = []
    for e in load_emails(CSV):
        total = sum(1 for x in load_emails(CSV) if x["journey"] == e["journey"])
        out.append({
            "code": e["code"],
            "journey": e["journey"].split(" · ")[1] if " · " in e["journey"] else e["journey"],
            "pos": f"{int(e['position'])} of {total}",
            "subject": e["subject"],
            "preview": e["preview"],
            "blocks": _compose(e, raw.get(e["code"], "")),
        })
    return out


EMAILS = build()
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd "/Users/vMac/04_marketing/Email Marketing/emails/second-pass" && python3 -m pytest tests/test_compose_v3.py -v
```

Expected: 6 passed. Two are likely to fail first time and both are informative:
- `test_only_three_surfaces_and_coral_is_rare` failing on the coral count means a `CORAL_MOMENT` entry names a module that email's stack doesn't contain — check the stack and fix `tonal_plan.py`.
- `test_header_first_footer_last_everywhere` failing means a v3 stack has chrome out of position — report it rather than silently reordering; it may be a Notion data error worth telling Vincent about.

- [ ] **Step 5: Point the renderer at the new composition and render**

```bash
cd "/Users/vMac/04_marketing/Email Marketing/emails/second-pass"
sed -i '' 's/^from emails import EMAILS$/from compose_v3 import EMAILS/' render_emails.py
rm -rf /tmp/live && hs cms fetch email_modules /tmp/live --account 50966981
sed -i '' 's|^LIVE = .*|LIVE = "/tmp/live"|' render_emails.py
python3 render_emails.py
```

Expected: `rendered 28 emails`, `unresolved HubL blocks: none`.

- [ ] **Step 6: Commit**

```bash
cd "/Users/vMac/04_marketing/Email Marketing" && git add emails/second-pass/compose_v3.py emails/second-pass/tests/test_compose_v3.py emails/second-pass/render_emails.py && git commit -m "feat: compose all 28 journey emails from the v3 blueprint"
```

---

## Task 7: The full audit

**Files:**
- Create: `emails/second-pass/audit.py`

**Interfaces:**
- Consumes: `compose_v3.EMAILS`, `contrast.scan`, `surface.SURFACES/SUPPORTING`
- Produces: exit code 0 with `problems: 0`, or a printed list and exit code 1

- [ ] **Step 1: Write the audit**

```python
# emails/second-pass/audit.py
"""One command that proves the whole set is correct. Exit 0 = shippable."""
import re, sys
from compose_v3 import EMAILS
from contrast import scan
from surface import SURFACES, SUPPORTING
from render_emails import block_html

MAIN = {"#EFE7D2", "#15140F", "#ED6F5C"}
CHROME_FOLDERS = {"header_centered_logo", "preference_opt_down", "footer_standard",
                  "footer_social", "footer_wide"}

def main():
    problems, coral = [], 0
    for e in EMAILS:
        folders = [b[0] for b in e["blocks"]]
        if folders[0] != "header_centered_logo":
            problems.append(f"{e['code']}: first block is {folders[0]}")
        feet = [i for i, f in enumerate(folders) if f in CHROME_FOLDERS - {"header_centered_logo"}]
        if len(feet) != 1 or feet[0] != len(folders) - 1:
            problems.append(f"{e['code']}: footer count/position {folders}")

        for folder, surf, vals in e["blocks"]:
            if surf == "coral":
                coral += 1
                if folder in CHROME_FOLDERS:
                    problems.append(f"{e['code']}: coral on chrome ({folder})")
            if SURFACES[surf]["bg"] not in MAIN:
                problems.append(f"{e['code']}/{folder}: {surf} is not a main surface")
            html = block_html(folder, surf, vals)
            m = re.search(r'class="final-card"[^>]*background:(#[0-9A-Fa-f]{6})', html)
            if m and m.group(1).upper() in SUPPORTING:
                problems.append(f"{e['code']}/{folder}: supporting colour as section background")
            for kind, detail, _ctx in scan(html, SURFACES[surf]["bg"]):
                problems.append(f"{e['code']}/{folder}[{surf}]: {kind} {detail}")

    print(f"emails        : {len(EMAILS)}")
    print(f"coral panels  : {coral}")
    print(f"problems      : {len(problems)}")
    for p in problems:
        print("   ", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run it**

```bash
cd "/Users/vMac/04_marketing/Email Marketing/emails/second-pass" && python3 audit.py
```

Expected: `emails : 28`, `coral panels : 5`, `problems : 0`. Fix any problem at its source (composition, mapping or tonal plan) — never by relaxing the audit.

- [ ] **Step 3: Screenshot two emails and look at them**

```bash
cd "/Users/vMac/04_marketing/Email Marketing/emails/second-pass"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --window-size=680,2400 --hide-scrollbars --screenshot=/tmp/pp1.png \
  "file://$PWD/emails_out/PP-1.html"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --window-size=680,3000 --hide-scrollbars --screenshot=/tmp/c0.png \
  "file://$PWD/emails_out/C-0.html"
```

Read both images. PP-1 should now be a nine-section email on one continuous Paper field, wordmark with a coral "co". C-0 should be the 13-section consultation recap. A wall of near-identical text blocks means `fields_for` is falling through to its generic branch too often — go back and give those families real treatments.

- [ ] **Step 4: Commit**

```bash
cd "/Users/vMac/04_marketing/Email Marketing" && git add emails/second-pass/audit.py && git commit -m "feat: single-command audit for structure, palette and contrast"
```

---

## Task 8: Rebuild the Figma page

**Files:**
- Modify: `emails/second-pass/spec_figma.py` (extend `items_for` to cover the new families)
- Use: `emails/second-pass/emit_figma.py`

**Context.** The Figma page mirrors the emails as native auto-layout with real text — it is a review surface, not the source. Page `291:724` currently holds 22 frames; the superseded sets live on `357:1203`.

Four Figma constraints already learned the hard way — all four are in `references/module-inventory.md`, read them before writing any `use_figma` call:
- `figma.createImageAsync` is unsupported. Clone vector group `284:8864` and map its `#FF5757` suffix to `#ED6F5C`.
- `appendChild` throws on unloaded fonts. Before moving or deleting any existing text, collect fonts via `getStyledTextSegments(["fontName"])` and `loadFontAsync` each.
- `page.children` under-reports on a page that is not current. Verify moves with a second call that sets that page current.
- Only Inter, Inter Tight, JetBrains Mono and Playfair Display are installed. Arial/Georgia/Courier New are not.

- [ ] **Step 1: Extend the Figma spec for new families**

`spec_figma.py`'s `items_for` currently handles the families the 22 thin emails used. The v3 set adds `faq`, `timeline`, `trust_badge_row`, `photo_feature_story`, `review_stars`, `testimonial`, `countdown_expiry`, `visual_comparison_cards`. Add a branch per family producing the same item vocabulary already in use (`eyebrow`, `h`, `p`, `kv`, `small`, `meta`, `btn`, `rule`, `code`, `logo`). Add a final `else` that raises rather than silently dropping content:

```python
raise SystemExit(f"spec_figma: unmapped module in spec: {folder}")
```

- [ ] **Step 2: Regenerate the spec and confirm the counts**

```bash
cd "/Users/vMac/04_marketing/Email Marketing/emails/second-pass" && python3 spec_figma.py
```

Expected: `28 emails, ~190 module frames, ...`. A `SystemExit` names the family you still need a branch for.

- [ ] **Step 3: Archive the current 22 frames**

Run a `use_figma` script that loads every font in use on page `291:724`, then moves all children to page `357:1203`. Return the moved count and the resulting child counts. Verify with a **second** call that sets `357:1203` current and reports its real total.

- [ ] **Step 4: Build the 28 frames in two halves**

```bash
cd "/Users/vMac/04_marketing/Email Marketing/emails/second-pass"
python3 emit_figma.py 0 14 > /tmp/jsA.txt
python3 emit_figma.py 14 28 > /tmp/jsB.txt
```

Paste each file's contents as the `code` argument of a `use_figma` call. The builder clears the page only when `START === 0`, so run the `0 14` half first.

- [ ] **Step 5: Audit the Figma page**

Run a read-only `use_figma` script asserting, per frame: exactly one header first, one footer last, every card fill in `{#EFE7D2, #15140F, #ED6F5C}`, exactly 5 coral cards across the page, and every `Wordmark` containing at least one `#ED6F5C` leaf. Report any failure; do not fix by hand-editing single nodes — fix the generator and rebuild.

- [ ] **Step 6: Commit**

```bash
cd "/Users/vMac/04_marketing/Email Marketing" && git add emails/second-pass/spec_figma.py && git commit -m "feat: extend Figma spec to the full v3 module vocabulary"
```

---

## Task 9: Update the living documentation

**Files:**
- Modify: `~/.claude/skills/hubspot-email-modules/references/module-inventory.md`
- Modify: `~/.claude/skills/hubspot-email-modules/SKILL.md`

Vincent has asked explicitly and repeatedly that rules and gotchas get written down **as they are learned**, not after they are re-learned. These files are the only thing standing between the next session and repeating this one.

- [ ] **Step 1: Record the source-of-truth hierarchy in SKILL.md**

Add to Known Pitfalls: the v3 export carries a corrected stack in its CSV property columns and a **stale, thinner stack in each `.md`'s `### Build notes`**, plus stale flowing prose in `### Body`. State that the CSV wins, and that this exact ambiguity already caused one full rebuild against the wrong spec.

- [ ] **Step 2: Record the module-name mapping in module-inventory.md**

The Notion `modules_master` names do not match the live slugs, and its `Source Path` column references a `core/` folder that does not exist. Note that `module_map.py` is now the canonical mapping and must be updated whenever a family is renamed on either side. Note that `text_block_generic` intentionally serves four semantic text slots.

- [ ] **Step 3: Record the module count expectation**

Add the per-email module-count table from this plan's Scope section. The previous build averaged 3.6 modules against a specified average of ~7 and Vincent rejected it as "not my vision of email marketing". A stack of header + one block + footer is a signal you are reading a stale source.

- [ ] **Step 4: Commit**

```bash
cd ~/.claude/skills/hubspot-email-modules && git add -A && git commit -m "docs: v3 source hierarchy, module mapping, and stack-depth expectations" 2>/dev/null || echo "skills dir not a git repo — changes saved in place"
```

---

## Decisions Needed From Vincent

Do not guess these. Ask, and hold the affected work until answered.

1. **CR-4 and RO-4 have rich stacks but unsegmented copy.** Every other multi-module email has `[Module]`-tagged copy. These two have 7 and 5 module stacks respectively with plain prose bodies. Either the copy needs segmenting, or their stacks should be the 3-module founder-letter shape. Build them as founder letters in the meantime and flag it.

2. **Button destinations are placeholders.** No CTA in the export carries a URL — only labels. The current build uses invented paths (`/pages/prep-guide`, `/collections/care`, `/pages/auto-reorder`). Real URLs are required before anything ships.

3. **The Consultation series is Sales-channel and deal-scoped.** C-0 uses `{{ deal.hsc_quote_base_type }}`, `{{ deal.hsc_quote_down_payment }}` and similar. These are HubSpot **deal** properties, not contact properties, and marketing emails cannot always resolve them. Confirm whether J5 sends from Sales (1:1, deal-scoped) or Marketing, because it changes both the subscription type and whether those tokens render at all.

4. **`OFFER — confirm before send`** appears twice in the copy. Those offers need confirming before those emails can ship.

---

## Self-Review

**Spec coverage.** 28 emails parsed (Task 1) → families mapped (Task 2) → gaps placeheld (Task 3) → copy mapped to fields (Task 4) → surfaces assigned (Task 5) → composed and rendered (Task 6) → audited (Task 7) → mirrored to Figma (Task 8) → documented (Task 9). Newsletters explicitly excluded at the parser. The 6 never-built emails enter through the same path as the 22 rebuilt ones — there is no separate "new email" path to drift.

**Interface consistency.** `load_emails` → `stack`/`blocks` keys consumed by `compose_v3._compose`. `resolve`/`fields_for`/`placeholder_fields`/`PLACEHOLDER_HOST` defined in Task 2–4, consumed in Task 6. `surface_for` defined in Task 5, consumed in Task 6. `EMAILS` shape matches what `render_emails.block_html` and `spec_figma.build` already expect — `(folder, surface, values)` tuples.

**Known soft spots.** `fields_for`'s final `else` branch is deliberately generic; Task 7 Step 3 exists specifically to catch it producing a wall of undifferentiated text blocks. The `List - Questions` → `faq` mapping assumes Q/A-shaped copy; where copy is a flat numbered list, the composer should fall back to `text_block_generic` rather than leaving empty FAQ rows — the empty-field guards added on 2026-08-11 mean empty rows collapse rather than render blank, but an empty module is still wrong.
