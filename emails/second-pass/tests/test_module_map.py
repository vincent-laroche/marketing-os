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
