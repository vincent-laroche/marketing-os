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
