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


def test_annotated_tag_lines_are_parsed():
    # Twelve real tag lines carry (recommended) or (optional) annotations
    cr2 = next(e for e in load_emails(CSV) if e["code"] == "CR-2")
    assert len(cr2["blocks"]) > 0
    # Annotation should not appear in any block's copy
    assert not any("(recommended)" in b["copy"] for b in cr2["blocks"])
    assert not any("(optional)" in b["copy"] for b in cr2["blocks"])


def test_copy_desk_instructions_are_preserved_not_boundaries():
    # CR-2 has: [Testimonial]\n[PULL from Proof Bank: ...]\n
    # PULL from Proof Bank is not in the stack, so it should be copy, not a boundary
    cr2 = next(e for e in load_emails(CSV) if e["code"] == "CR-2")
    stack_families = {s["family"] for s in cr2["stack"]}

    # PULL from Proof Bank should NOT be in the stack (it's a copy-desk instruction)
    assert "PULL from Proof Bank" not in stack_families

    # Testimonial should be in the stack
    assert "Testimonial" in stack_families

    # Testimonial's copy should contain the [PULL from Proof Bank] instruction
    testimonial_block = next((b for b in cr2["blocks"] if b["family"] == "Testimonial"), None)
    assert testimonial_block is not None
    assert "PULL from Proof Bank" in testimonial_block["copy"]


def test_no_leaked_boundary_text_in_blocks():
    # Verify no block's copy contains a line starting with [ that names a valid module family
    emails = load_emails(CSV)
    for email in emails:
        stack_families = {s["family"] for s in email["stack"]}
        for block in email["blocks"]:
            lines = block["copy"].split("\n")
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("["):
                    # Extract the family name (text between [ and ])
                    if "]" in stripped:
                        candidate_family = stripped[1:stripped.index("]")]
                        # This should NOT be in the stack
                        assert candidate_family not in stack_families, \
                            f"Email {email['code']}: leaked boundary text '[{candidate_family}]' in {block['family']}'s copy"


def test_unrecognized_annotation_does_not_make_boundary():
    # A bracketed line with an unrecognized trailing annotation
    # (not "recommended" or "optional") should NOT be treated as a boundary;
    # it should survive in the preceding block's copy, not be dropped
    body = ("[Hero]\nHello\n\n"
            "[Text - Offer discount] (recommended — only if W-1 carried an incentive)\n"
            "This is copy for Text - Offer discount.\n")
    families = {"Hero", "Text - Offer discount"}
    blocks = parse_body(body, families)
    # Should have only 1 block because the line with unrecognized annotation
    # is NOT treated as a boundary
    assert len(blocks) == 1
    assert blocks[0]["family"] == "Hero"
    # The entire bracketed line with unrecognized annotation should survive in Hero's copy
    assert "[Text - Offer discount] (recommended — only if W-1 carried an incentive)" in blocks[0]["copy"]
    assert "This is copy for Text - Offer discount" in blocks[0]["copy"]
