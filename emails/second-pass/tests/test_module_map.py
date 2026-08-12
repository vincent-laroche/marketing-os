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


def test_missing_families_reports_the_four_unavailable():
    """Round 2: Review stars joins the unavailable list. Its live module hardcodes
    five star glyphs in module.html regardless of the `rating` field, and the Proof
    Bank is empty, so there is no field mapping that can honestly avoid fabricating
    a rating. Renamed from test_missing_families_reports_exactly_three; the count
    change (3 -> 4) is explicitly authorised by the coordinator's round-2 note."""
    assert sorted(missing_families(load_emails(CSV))) == [
        "Commerce - Cart line items",
        "Commerce - Viewed product",
        "Product - Dynamic recommendations",
        "Review stars",
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


def test_fields_for_review_stars_now_routes_to_placeholder_fields():
    """Round 2 supersedes round 1's test_fields_for_review_stars_never_returns_a_
    fabricated_rating: Vincent ruled Review stars unavailable (its live module
    hardcodes five star glyphs no matter what `rating` is set to, so no field
    value could ever honestly satisfy "never fabricate a rating"). fields_for must
    no longer touch review_stars' fields at all — it goes through the same
    placeholder_fields() path as the three commerce modules with no live source,
    and the instruction text still survives, visibly, in the placeholder body."""
    from module_map import fields_for
    copy = "[PULL from Proof Bank: aggregate rating]"
    f = fields_for("Review stars", "", copy, {})
    assert "rating" not in f
    assert "quote_text" not in f
    assert f["heading"] == "[ Review stars ]"
    assert copy in f["body_text"]
    assert f["show_button"] == "no"


def test_fields_for_founder_wrapper_and_button_cta_have_no_inert_keys():
    """Correction #4: these two branches must return exactly the fields their
    target module actually has — no leftover text_block_generic-shaped keys
    (eyebrow/heading/heading_accent/body_text) that don't exist in
    plain_text_founder_wrapper or button_standalone_cta's fields.json."""
    from module_map import fields_for
    fw = fields_for("Layout - Plain-text founder wrapper", "", "Hi,\n\nBody.\n\nVincent", {})
    assert set(fw.keys()) == {"greeting", "letter_text", "signature",
                               "show_button", "button_label", "button_url"}

    cta = fields_for("Button - Primary CTA", "", "Shop now →", {})
    assert set(cta.keys()) == {"eyebrow", "heading", "body_text",
                                "show_button", "button_label", "button_url"}


def test_fields_for_order_summary_splits_label_colon_value_lines():
    from module_map import fields_for
    copy = ("Order number: {{ order_number }}\n"
            "What you ordered: {{ product_summary }}\n"
            "Estimated dispatch: {{ estimated_ship_date }}")
    f = fields_for("Commerce - Order summary", "", copy, {})
    assert f["label_order"] == "Order number"
    assert f["value_order"] == "{{ order_number }}"
    assert f["value_spec"] == "{{ product_summary }}"
    # only 3 lines of copy for 4 slots (order, spec, status, eta) -> the 4th
    # (eta) is the unused one and must be blanked, not left at its demo default
    assert f["label_eta"] == ""
    assert f["value_eta"] == ""


def test_fields_for_shipping_tracking_splits_label_colon_value_lines():
    from module_map import fields_for
    copy = "Tracking: {{ tracking_number }}\nCarrier: {{ carrier }}\nExpected: {{ estimated_delivery_date }}"
    f = fields_for("Commerce - Shipping tracking", "", copy, {})
    assert f["label_carrier"] == "Tracking"
    assert f["value_carrier"] == "{{ tracking_number }}"
    assert f["value_eta"] == "{{ estimated_delivery_date }}"


def test_fields_for_trust_strip_splits_on_middot_and_blanks_unused():
    from module_map import fields_for
    copy = "Handcrafted to your spec · 14-day inspection window · Direct line to the founder"
    f = fields_for("List - Trust strip", "", copy, {})
    assert f["item_1_label"] == "Handcrafted to your spec"
    assert f["item_2_label"] == "14-day inspection window"
    assert f["item_3_label"] == "Direct line to the founder"
    assert f["item_4_label"] == ""          # unused slot: 'Secure Payment' must not leak in
    assert "item_1_icon" not in f           # icons are left at their live defaults


def test_fields_for_faq_qa_shaped_copy_fills_question_and_answer():
    from module_map import fields_for
    copy = ('"Will it actually look real?"\n'
            'At conversation distance, a well-fitted lace front is not detectable.\n\n'
            '"Will it hold?"\n'
            'With clean prep, a bond holds 7 to 14 days.')
    f = fields_for("List - Questions", "the three answers", copy, {})
    assert f["faq_1_question"] == "Will it actually look real?"
    assert "not detectable" in f["faq_1_answer"]
    assert f["faq_2_question"] == "Will it hold?"
    assert f["faq_3_question"] == ""        # unused slots blanked


def test_fields_for_faq_flat_numbered_list_fills_question_only_not_empty_faq_rows():
    """PP-1 shape: a numbered list of steps, not real questions. Confirmed against
    /tmp/live/faq.module/module.html that an empty faq_N_answer collapses cleanly
    (each row is gated on faq_N_question truthy; the answer cell just renders
    empty, no broken markup) — so filling question-only is safe, not a silent drop."""
    from module_map import fields_for
    copy = ("1. Production starts — the base is cut and the hair is hand-tied to your spec\n"
            "2. I email you when it goes into production\n"
            "3. I email you when it ships, with tracking\n"
            "4. It should be at your door around {{ estimated_delivery_date }}\n\n"
            "No filler emails in between — only the real steps.")
    f = fields_for("List - Questions", "what happens next timeline", copy, {})
    assert f["faq_1_question"] == "Production starts — the base is cut and the hair is hand-tied to your spec"
    assert f["faq_1_answer"] == ""
    assert f["faq_4_question"] == "It should be at your door around {{ estimated_delivery_date }}"
    # the trailing aside is not dropped — it becomes its own 5th entry, not folded
    # away, since there is a free slot for it
    assert f["faq_5_question"] == "No filler emails in between — only the real steps."


def test_fields_for_timeline_folds_fifth_step_into_fourth_slot():
    """C-0's copy has 5 numbered steps; timeline.module only has 4 slots. The
    fifth step must not be silently dropped — it's folded into step_4_text."""
    from module_map import fields_for
    copy = ("1. You approve the spec (or tell me what to change)\n"
            "2. Down payment confirms your build slot\n"
            "3. Handcrafted to your spec — 3–4 weeks\n"
            "4. Inspected against your spec, then dispatched\n"
            "5. Delivered, with a 14-day inspection window")
    f = fields_for("Timeline", "production window", copy, {})
    assert f["step_1_heading"] == "You approve the spec (or tell me what to change)"
    assert f["step_4_heading"] == "Inspected against your spec, then dispatched"
    assert "Delivered, with a 14-day inspection window" in f["step_4_text"]
    assert "step_5_heading" not in f        # timeline.module genuinely has no 5th slot


def test_fields_for_quote_spec_table_splits_intro_and_token():
    from module_map import fields_for
    copy = "Your last specification, still on file:\n{{ last_order_specification }}"
    f = fields_for("Commerce - Quote and spec table", "", copy, {})
    assert f["heading"] == "Your last specification, still on file"
    assert f["value_1"] == "{{ last_order_specification }}"
    assert f["label_1"]                     # a sensible label, not left blank
    assert f["value_2"] == ""               # unused pairs blanked, not '$580.00' etc.


def test_fields_for_comparison_carries_dynamic_instruction_visibly():
    """visual_comparison_cards has no body field, so C-2's `{{ dynamic: ... }}`
    instruction must ride in card_1_name, with cards 2/3 blanked so 'Option B'/
    'Option C' never render."""
    from module_map import fields_for
    copy = "{{ dynamic: the 2–3 options discussed on the call }}"
    f = fields_for("Comparison", "their shortlist", copy, {})
    assert copy in f["card_1_name"]
    assert f["card_2_name"] == ""
    assert f["card_3_name"] == ""


def test_fields_for_every_key_is_real_across_all_28_emails():
    """The single most valuable regression test in this file: for every block
    with non-empty copy across the 28 real emails, every key fields_for returns
    must exist in the fields.json of the module that block actually renders
    through (its resolved module, or text_block_generic — PLACEHOLDER_HOST —
    when the family maps to None). This is the exact class of bug this whole
    task was about: a field name that doesn't exist is silently ignored by
    ctx.update() downstream, and the module's fabricated demo default ships
    instead. Reads schemas from /tmp/live. That path is the live source of
    truth (deliberately not vendored into the repo — a checked-in copy would
    drift from the live account and this test would validate against fiction).
    /tmp is ephemeral, so this MUST fail loudly, not skip, when the tree is
    missing — a skip here would silently disable the single most valuable
    guard in this suite and the run would still report green."""
    import json as _json
    live_dir = "/tmp/live"
    assert os.path.isdir(live_dir), (
        f"{live_dir} not found — fetch the live module tree first: "
        f"hs cms fetch email_modules {live_dir} --account 50966981"
    )

    from module_map import fields_for, resolve, PLACEHOLDER_HOST

    def field_ids(folder):
        path = os.path.join(live_dir, f"{folder}.module", "fields.json")
        return {f["id"] for f in _json.load(open(path))}

    emails = load_emails(CSV)
    checked = 0
    for e in emails:
        for b in e["blocks"]:
            if not b["copy"].strip():
                continue
            folder = resolve(b["family"]) or PLACEHOLDER_HOST
            valid = field_ids(folder)
            result = fields_for(b["family"], b["qualifier"], b["copy"], e)
            unknown = set(result.keys()) - valid
            assert not unknown, (
                f"{e['code']} / {b['family']!r} -> {folder}.module: "
                f"fields_for returned unreal keys {unknown}"
            )
            checked += 1
    assert checked > 0, "no non-empty-copy blocks were found to check"
