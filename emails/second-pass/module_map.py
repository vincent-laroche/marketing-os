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
