"""Phase 0 kill gate for the Unlayer drag-and-drop build.

The Unlayer Optimize plan caps custom tools at 5. There are 52 Atelier Zero modules.
One tool per module is therefore impossible; the only viable design is a small number
of parameterised tools, each carrying a module dropdown, whose property schema is the
UNION of the field slots of every module it covers.

This script answers the one question that decides whether the approach is viable:

    do the 52 modules collapse into at most 5 archetypes, and is the union field
    count per archetype small enough to be a usable property panel?

It writes nothing and touches no external service. Run it and read the tables.

    python3 tools/unlayer/archetypes.py

Field slots are compared by their SHAPE, not their literal name: repeating groups
(item_1_name, item_2_name, ...) collapse to a single indexed slot (item_#_name), so a
module with three cart rows and one with five are the same shape at different arities.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULES = REPO / "Email Reference File" / "emails_modules_hubspot versionr"

# Unlayer Optimize entitlement, verified in console.unlayer.com for project 289096.
TOOL_CAP = 5

# A property panel much beyond this stops being usable, even with grouping.
UNION_WARN = 24

# Archetype assignment, by module slug. Grouped by field SHAPE rather than by
# scope/family: what a tool's property schema must express is the union of its
# members' slots, so shape is the only thing that actually constrains the design.
ARCHETYPES: dict[str, list[str]] = {
    "az-simple": [
        # eyebrow / heading / body / single optional link
        "button_final_cta",
        "button_primary_cta",
        "hero_text_led",
        "layout_founder_wrapper",
        "product_goal_based_recommendation",
        "quote_accent_bar",
        "quote_centered",
        "signal_offer_deadline",
        "signal_promo_code",
        "signal_review_stars",
        "text_base_type_guidance",
        "text_customer_snapshot",
        "text_masthead",
        "text_next_step",
        "text_offer_discount",
        "text_opening",
        "text_section",
    ],
    "az-list": [
        # repeating label/text pairs, N items
        "comparison",
        "faq",
        "list_belief",
        "list_questions",
        "list_support_strip",
        "list_trust_strip",
        "proof",
        "stat_bars",
        "text_five_changes",
        "text_founder_pillars",
        "text_reassurance",
        "text_why_it_matters",
        "timeline",
    ],
    "az-commerce": [
        # order/cart/spec tables: line rows + totals + one action url
        "commerce_billing_details",
        "commerce_cart_line_items",
        "commerce_checkout_summary",
        "commerce_order_summary",
        "commerce_quote_spec_table",
        "commerce_shipping_tracking",
        "commerce_viewed_product",
        "product_3up_grid",
        "product_dynamic_recommendations",
    ],
    "az-media": [
        # image-bearing cards and grids
        "column_image_and_text",
        "grid_collections_4",
        "grid_collections_6",
        "hero_photo_led",
        "photo_feature_story",
        "photo_founder_note",
        "photo_logo_system",
        "testimonial",
    ],
    "az-structural": [
        # header, footers, social row
        "footer_preference_centre",
        "footer_social",
        "footer_standard",
        "footer_wide",
        "header_centered_logo",
    ],
}

INDEXED = re.compile(r"(?<=_)\d+(?=_|$)")


def slot_shape(name: str) -> str:
    """Collapse a repeating group index so arity differences don't look like new slots."""
    return INDEXED.sub("#", name)


def load_modules() -> dict[str, list[dict]]:
    """Every *_light.module fields.json, keyed by module slug.

    Light and dark are the same schema; dark is a theme property on the tool, not a
    separate module, so only the light variant defines the shape.
    """
    out: dict[str, list[dict]] = {}
    for d in sorted(MODULES.iterdir()):
        if not d.is_dir() or not d.name.endswith("_light.module"):
            continue
        fj = d / "fields.json"
        if not fj.exists():
            print(f"  !! {d.name} has no fields.json", file=sys.stderr)
            continue
        out[d.name[: -len("_light.module")]] = json.loads(fj.read_text())
    return out


def main() -> int:
    mods = load_modules()
    assigned = {m: a for a, members in ARCHETYPES.items() for m in members}

    print(f"modules discovered : {len(mods)}")
    print(f"archetypes defined : {len(ARCHETYPES)} (cap {TOOL_CAP})")
    print()

    missing = sorted(set(mods) - set(assigned))
    unknown = sorted(set(assigned) - set(mods))
    dupes = [m for m, c in Counter(
        m for members in ARCHETYPES.values() for m in members).items() if c > 1]

    ok = True

    if len(ARCHETYPES) > TOOL_CAP:
        print(f"FAIL: {len(ARCHETYPES)} archetypes exceeds the {TOOL_CAP}-tool cap.")
        ok = False
    if missing:
        print(f"FAIL: {len(missing)} module(s) unassigned: {', '.join(missing)}")
        ok = False
    if unknown:
        print(f"FAIL: {len(unknown)} assigned slug(s) do not exist: {', '.join(unknown)}")
        ok = False
    if dupes:
        print(f"FAIL: module(s) in more than one archetype: {', '.join(dupes)}")
        ok = False

    # Per-archetype union analysis: this is what a single tool's property panel must carry.
    print(f"{'archetype':16s} {'mods':>4s} {'union':>5s} {'max':>4s}  types")
    print("-" * 72)
    unions: dict[str, dict[str, set[str]]] = {}
    for arch, members in ARCHETYPES.items():
        union: dict[str, set[str]] = defaultdict(set)
        biggest = 0
        for m in members:
            fields = mods.get(m)
            if fields is None:
                continue
            biggest = max(biggest, len(fields))
            for f in fields:
                union[slot_shape(f["name"])].add(f["type"])
        unions[arch] = union
        types = ",".join(sorted({t for ts in union.values() for t in ts}))
        flag = "  <-- heavy" if len(union) > UNION_WARN else ""
        print(f"{arch:16s} {len(members):4d} {len(union):5d} {biggest:4d}  {types}{flag}")
        if len(union) > UNION_WARN:
            ok = False

    # A slot whose type is inconsistent across members cannot be one property editor.
    print()
    conflicts = {
        arch: {s: ts for s, ts in u.items() if len(ts) > 1}
        for arch, u in unions.items()
    }
    if any(conflicts.values()):
        print("Type conflicts (same slot, different field types across members):")
        for arch, c in conflicts.items():
            for slot, ts in sorted(c.items()):
                print(f"  {arch:16s} {slot:28s} {sorted(ts)}")
                ok = False
    else:
        print("No slot-level type conflicts. Every union slot maps to one property editor.")

    print()
    print("Field types in use across all modules:")
    all_types = Counter(f["type"] for fs in mods.values() for f in fs)
    for t, n in all_types.most_common():
        print(f"  {t:10s} {n:4d}")

    print()
    print("PASS — the 52 modules fit the 5-tool cap." if ok
          else "FAIL — see above. Do not proceed to Phase 1.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
