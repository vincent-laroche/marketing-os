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


def test_placeholder_is_visibly_labelled_and_keeps_the_instruction():
    from module_map import placeholder_fields
    f = placeholder_fields("Commerce - Cart line items", "", "")
    assert f["heading"].startswith("[") and f["heading"].endswith("]")
    assert "Commerce - Cart line items" in f["heading"]
    assert f["show_button"] == "no"

    f2 = placeholder_fields("PULL from Proof Bank",
                            "a customer on the care routine paying off", "")
    assert "a customer on the care routine paying off" in f2["body_text"]


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


def test_fields_for_testimonial_uses_quote_text_not_placeholder_shape():
    """Correction 1: Testimonial must not go through placeholder_fields (which
    returns text_block_generic-shaped keys like `body_text`). The bracketed
    Proof Bank instruction must survive verbatim in the real `quote_text` field,
    and no name/detail/rating may be fabricated."""
    from module_map import fields_for
    copy = "[PULL from Proof Bank: a first-order quote that answers the \"will it look real\" doubt]"
    f = fields_for("Testimonial", "", copy, {})
    assert f["quote_text"] == copy
    assert "body_text" not in f
    assert f["customer_name"] == ""
    assert f["customer_detail"] == ""
    assert f["show_stars"] == "no"


def test_fields_for_review_stars_never_returns_a_fabricated_rating():
    """Correction 1: Review stars must not go through placeholder_fields, and the
    live module's `rating` choice field only offers "3"/"4"/"5" — never a real
    rating we haven't been given — so it must come back empty, never "5"."""
    from module_map import fields_for
    copy = "[PULL from Proof Bank: aggregate rating]"
    f = fields_for("Review stars", "", copy, {})
    assert f["rating"] == ""
    assert copy in f["body_text"] or copy in f["heading"]
    assert f["button_label"] == ""
    assert "quote_text" not in f
