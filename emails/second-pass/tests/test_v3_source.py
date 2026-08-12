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
