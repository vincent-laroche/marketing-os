#!/usr/bin/env python3
"""Module mapping gate for the 53-email programme (CAMPAIGN-PLAN.md Phase 1 gate).

Parses every Module Stack in emails_master, resolves each named module family to a
rendered artifact in "Email Reference File/Atelier Zero — Resolved HTML Module Previews",
and fails if anything is unresolved. Aliases resolve through ALIASES below; the two
sanctioned ones (Review stars, Signal - Countdown) are recorded in modules_master.

Usage: python3 tools/build53/module_map.py [--json]
"""
import csv, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF = os.path.join(ROOT, "Email Reference File")
EMAILS_CSV = os.path.join(REF, "emails_master 831f4e0d84e0831992d481ae881cfede_all.csv")
PREVIEWS = os.path.join(REF, "Atelier Zero — Resolved HTML Module Previews (102)")

# Module Stack family name -> preview slug (file: <category>--<slug>_<shade>.module.html)
FAMILY_TO_SLUG = {
    "Header - Centered logo": "header_centered_logo",
    "Hero - Text-led": "hero_text_led",
    "Hero - Photo-led": "hero_photo_led",
    "Text - Opening": "text_opening",
    "Text - Masthead": "text_masthead",
    "Text - Section": "text_section",
    "Text - Why it matters": "text_why_it_matters",
    "Text - Next step": "text_next_step",
    "Text - Five changes": "text_five_changes",
    "Text - Founder pillars": "text_founder_pillars",
    "Text - Customer snapshot": "text_customer_snapshot",
    "Text - Base type guidance": "text_base_type_guidance",
    "Text - Offer discount": "text_offer_discount",
    "Text - Reassurance": "text_reassurance",
    "Layout - Plain-text founder wrapper": "layout_founder_wrapper",
    "Button - Primary CTA": "button_primary_cta",
    "Button - Final CTA": "button_final_cta",
    "Photo - Feature story": "photo_feature_story",
    "Photo - Founder note": "photo_founder_note",
    "Photo - Logo system": "photo_logo_system",
    "Testimonial": "testimonial",
    "Quote - Centered": "quote_centered",
    "Quote - Accent bar": "quote_accent_bar",
    "Signal - Promo code": "signal_promo_code",
    "Signal - Offer deadline": "signal_offer_deadline",
    "Signal - Review stars": "signal_review_stars",
    "Stat bars": "stat_bars",
    "Proof": "proof",
    "List - Questions": "list_questions",
    "List - Trust strip": "list_trust_strip",
    "List - Support strip": "list_support_strip",
    "List - Belief": "list_belief",
    "Comparison": "comparison",
    "FAQ": "faq",
    "Timeline": "timeline",
    "Grid - Collections 4": "grid_collections_4",
    "Grid - Collections 6": "grid_collections_6",
    "Product - 3-up grid": "product_3up_grid",
    "Product - Dynamic recommendations": "product_dynamic_recommendations",
    "Product - Goal-based recommendation": "product_goal_based_recommendation",
    "Commerce - Cart line items": "commerce_cart_line_items",
    "Commerce - Order summary": "commerce_order_summary",
    "Commerce - Quote and spec table": "commerce_quote_spec_table",
    "Commerce - Shipping tracking": "commerce_shipping_tracking",
    "Commerce - Viewed product": "commerce_viewed_product",
    "Commerce - Billing details": "commerce_billing_details",
    "Commerce - Checkout summary": "commerce_checkout_summary",
    "Column - Image and text": "column_image_and_text",
    "Footer - Social": "footer_social",
    "Footer - Standard": "footer_standard",
    "Footer - Preference centre": "footer_preference_centre",
    "Footer - Wide": "footer_wide",
}

# Names appearing in stacks that are aliases for the modules above (recorded in
# modules_master 2026-08-19). Anything landing here must stay resolvable forever.
ALIASES = {
    "Review stars": "Signal - Review stars",          # -> signal_review_stars
    "Signal - Countdown": "Signal - Offer deadline",  # -> signal_offer_deadline (static date, intended)
    "Header": "Header - Centered logo",               # legacy bare name (PP-7b, normalised 2026-08-19)
    "M10 Support strip": "List - Support strip",      # legacy M-code (PP-7b, normalised 2026-08-19)
}


def parse_stack(stack):
    """Return ordered list of (required: bool, raw: str) from a Module Stack string."""
    out = []
    for m in re.finditer(r"\(([^()]*)\)|\[([^\[\]]*)\]", stack):
        paren, bracket = m.group(1), m.group(2)
        out.append((paren is not None, (paren if paren is not None else bracket).strip()))
    return out

def family_of(raw):
    """Strip the qualifier after ' → ' or ': ' (e.g. 'Text - Offer discount: incentive')."""
    for sep in (" → ", ": ", "->"):
        if sep in raw:
            return raw.split(sep, 1)[0].strip()
    return raw.strip()

def resolve(family):
    """Return (slug, via_alias) or (None, False)."""
    if family in FAMILY_TO_SLUG:
        return FAMILY_TO_SLUG[family], False
    if family in ALIASES and ALIASES[family] in FAMILY_TO_SLUG:
        return FAMILY_TO_SLUG[ALIASES[family]], True
    return None, False

def preview_exists(slug):
    hits = [f for f in os.listdir(PREVIEWS) if f.endswith(f"--{slug}_light.module.html")
            or f.endswith(f"--{slug}_dark.module.html")]
    shades = {f.rsplit("_", 1)[1].split(".")[0] for f in hits}
    return shades == {"light", "dark"}, sorted(hits)

def main():
    with open(EMAILS_CSV, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    unresolved, aliases_used, report = [], {}, []
    for r in rows:
        name, stack = r["Email name"], r["Module Stack"]
        mods = parse_stack(stack)
        if not mods:
            unresolved.append((name, "<unparseable stack>", stack))
            continue
        for required, raw in mods:
            fam = family_of(raw)
            slug, via_alias = resolve(fam)
            if slug is None:
                unresolved.append((name, raw, fam))
                continue
            ok, files = preview_exists(slug)
            if via_alias:
                aliases_used.setdefault(fam, slug)
            if not ok:
                unresolved.append((name, raw, f"{fam} -> {slug} (preview missing: {files})"))
            report.append({"email": name, "raw": raw, "required": required,
                           "family": fam, "slug": slug, "alias": via_alias})
    if "--json" in sys.argv:
        print(json.dumps(report, indent=1, ensure_ascii=False))
        return
    print(f"Emails: {len(rows)}   module instances resolved: {len(report)}")
    print(f"Aliases resolved: {aliases_used if aliases_used else 'none needed'}")
    if unresolved:
        print(f"\nUNRESOLVED ({len(unresolved)}):")
        for name, raw, why in unresolved:
            print(f"  {name}: [{raw}] -> {why}")
        sys.exit(1)
    print("\nGATE GREEN: every module in all 53 Module Stacks resolves to a rendered "
          "preview artifact (light + dark). Zero unresolved aliases.")

if __name__ == "__main__":
    main()
