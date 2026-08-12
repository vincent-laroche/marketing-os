import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from compose_v3 import EMAILS, CSV, CHROME, BUTTON, FOUNDER, PLACEHOLDER_HOST, _copy_for
from v3_source import load_emails


def by(code):
    return next(e for e in EMAILS if e["code"] == code)


def _unmatched_slots(raw_email):
    """Stack slots with no matching per-family copy block, excluding chrome
    (never carries inline copy by design) and the CTA button (has its own
    real fallback to the email's `cta` column). Mirrors the exemption logic
    in compose_v3._compose's `unmatched` check."""
    used, out = set(), []
    for idx, slot in enumerate(raw_email["stack"]):
        fam = slot["family"]
        blk = _copy_for(raw_email, fam, used)
        founder_case = not raw_email["blocks"] and fam == FOUNDER
        if blk is None and not founder_case and fam not in CHROME and fam != BUTTON:
            out.append(idx)
    return out


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


def test_cr4_coral_promo_block_is_not_blank():
    """CR-4's body is an unsegmented founder letter, but its stack keeps the
    full 7-block v3 shape (Correction #4), including a `Signal - Promo code`
    slot with no matching copy that also happens to be the email's one
    designated coral moment. Regression guard: that slot must never compose
    to a real module with blank fields — it must be a visible, non-empty
    placeholder."""
    e = by("CR-4")
    coral_blocks = [b for b in e["blocks"] if b[1] == "coral"]
    assert len(coral_blocks) == 1, "CR-4 should carry exactly its one designated coral block"
    folder, surface, values = coral_blocks[0]
    assert folder == PLACEHOLDER_HOST, (
        "CR-4's coral slot has no matching copy and must render as a labelled "
        f"placeholder, not the real module '{folder}' with blank fields")
    assert (values.get("heading") or "").strip(), "CR-4 coral placeholder has a blank heading"
    assert (values.get("body_text") or "").strip(), "CR-4 coral placeholder has blank body_text"


def test_ro4_unmatched_slot_is_not_blank():
    """RO-4 is likewise an unsegmented founder letter keeping its full
    5-block stack. Its non-chrome, non-button `Text - Customer snapshot`
    slot has no matching copy and must render visible placeholder content,
    not a real module with an empty body."""
    raw = next(x for x in load_emails(CSV) if x["code"] == "RO-4")
    unmatched = _unmatched_slots(raw)
    assert unmatched, "RO-4 should have at least one unmatched non-chrome slot"
    e = by("RO-4")
    for idx in unmatched:
        folder, surface, values = e["blocks"][idx]
        assert folder == PLACEHOLDER_HOST, (
            f"RO-4 slot {idx} has no matching copy and must render as a "
            f"labelled placeholder, not the real module '{folder}' with blank fields")
        assert (values.get("heading") or "").strip(), f"RO-4 slot {idx} placeholder has a blank heading"
        assert (values.get("body_text") or "").strip(), f"RO-4 slot {idx} placeholder has blank body_text"


def test_unmatched_slots_never_render_blank_real_modules():
    """General invariant across all 28 emails, not just CR-4/RO-4: a stack
    slot with no matching copy (excluding chrome and the CTA button, which
    have their own legitimate no-copy paths) must always compose to the
    placeholder host with visible heading/body text — never a real,
    content-bearing module left blank. Guards against a future edit to
    module_map.py or tonal_plan.py silently reintroducing empty fields."""
    raw_by_code = {r["code"]: r for r in load_emails(CSV)}
    checked_any = False
    for e in EMAILS:
        raw = raw_by_code[e["code"]]
        for idx in _unmatched_slots(raw):
            folder, surface, values = e["blocks"][idx]
            checked_any = True
            assert folder == PLACEHOLDER_HOST, (
                f"{e['code']} slot {idx} is unmatched but rendered as real "
                f"module '{folder}' instead of a placeholder")
            assert (values.get("heading") or "").strip(), \
                f"{e['code']} slot {idx} placeholder has a blank heading"
            assert (values.get("body_text") or "").strip(), \
                f"{e['code']} slot {idx} placeholder has blank body_text"
    assert checked_any, "no unmatched slots found across the 28 emails — regression scenario missing"
