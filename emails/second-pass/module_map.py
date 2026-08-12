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
    "Comparison":                         "visual_comparison_cards",  # chosen over live `comparison` (2-column head-to-head) because C-2 needs 2–3 options
    "Grid - Collections 4":               "grid_collections_4",
    "Timeline":                           "timeline",
    "FAQ":                                "faq",                    # alias for List - Questions

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


# --- fields_for: v3 copy block -> live module field values -----------------
#
# ctx = defaults(folder) then ctx.update(values) downstream, so any field left
# out of the dict this returns silently keeps that module's demo placeholder
# content. Field names below are verified against /tmp/live/<module>/fields.json
# (see task-4-report.md for the module-by-module check).

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

    # --- Correction 1: Testimonial and Review stars use their OWN real field
    # names, never placeholder_fields()'s text_block_generic-shaped keys.
    # Both modules exist in the live account to carry real Proof Bank quotes,
    # but the Proof Bank is empty as of 2026-08-11 — every block currently
    # arrives as a bracketed copy-desk instruction. That instruction must
    # survive verbatim into the field the module actually renders, and no
    # name, detail, or star rating may ever be invented to fill the gap.

    if family == "Testimonial":
        # testimonial.module fields: quote_text, customer_name, customer_detail,
        # customer_image, show_stars. No heading/body_text/eyebrow exist here.
        quote = copy if copy else f"[ {family} — no Proof Bank content supplied ]"
        return {"quote_text": quote, "customer_name": "", "customer_detail": "",
                "show_stars": "no"}

    if family == "Review stars":
        # review_stars.module fields: eyebrow, rating, heading, body_text,
        # button_label, button_url. `rating` is a choice field offering only
        # "3"/"4"/"5" (verified in fields.json) — there is no real aggregate
        # rating to report, so it must never be set to a fabricated value.
        body = _paras(copy) if copy else \
            f"<p style='margin:0;'>[ {family} — no Proof Bank content supplied ]</p>"
        return {"eyebrow": "", "rating": "", "heading": f"[ {family} ]",
                "body_text": body, "button_label": "",
                "button_url": {"href": "#"}}

    if family.startswith(("PULL", "OFFER")):
        # Defensive only: after the Task 1 fix these bracketed instructions no
        # longer parse as their own family — they arrive as copy text inside
        # another family's block (handled by the branches above). Kept in case
        # a stray one ever slips through unparsed.
        return placeholder_fields(family, qualifier, copy)

    # every remaining text-ish family renders as a titled block
    return _base(eyebrow=qualifier.title() if qualifier else "",
                 heading="", body_text=_paras(copy))
