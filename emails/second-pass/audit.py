# emails/second-pass/audit.py
"""One command that proves the whole set is correct. Exit 0 = shippable."""
import re, sys
from compose_v3 import EMAILS
from contrast import scan
from surface import SURFACES, SUPPORTING
from render_emails import block_html

MAIN = {"#EFE7D2", "#15140F", "#ED6F5C"}
CHROME_FOLDERS = {"header_centered_logo", "preference_opt_down", "footer_standard",
                  "footer_social", "footer_wide"}

CARD_RE = re.compile(r'class="final-card"[^>]*background:(#[0-9A-Fa-f]{6})')


def card_bg(html):
    """The rendered block's own final-card background, or None if the block
    emitted no card at all — i.e. it renders no visible content. A module whose
    conditional wrapping swallows its own opening tags (a `{% if
    module.button_label %}` gating the entire card, not just the button) leaves
    only a stray handful of closing tags behind, and this regex simply fails to
    match. That is a real, shippability-blocking finding, not a false negative:
    verified against every folder in the live set that no block with real
    content ever lacks a final-card match, and no block lacking one ever carries
    real content either (see task-7-report.md's false-positive check)."""
    m = CARD_RE.search(html)
    return m.group(1).upper() if m else None


def main():
    problems, coral = [], 0
    for e in EMAILS:
        folders = [b[0] for b in e["blocks"]]
        if folders[0] != "header_centered_logo":
            problems.append(f"{e['code']}: first block is {folders[0]}")
        feet = [i for i, f in enumerate(folders) if f in CHROME_FOLDERS - {"header_centered_logo"}]
        if len(feet) != 1 or feet[0] != len(folders) - 1:
            problems.append(f"{e['code']}: footer count/position {folders}")

        for folder, surf, vals in e["blocks"]:
            if surf == "coral":
                coral += 1
                if folder in CHROME_FOLDERS:
                    problems.append(f"{e['code']}: coral on chrome ({folder})")
            if SURFACES[surf]["bg"] not in MAIN:
                problems.append(f"{e['code']}/{folder}: {surf} is not a main surface")
            html = block_html(folder, surf, vals)
            bg = card_bg(html)
            if bg is None:
                problems.append(
                    f"{e['code']}/{folder}: BLANK RENDER — no visible content "
                    "(known upstream module-template bug: {% if module.button_label %} "
                    "gates the whole card, not just the button — see task-7-report.md; "
                    "this is not a composition/mapping/tonal-plan defect)")
            elif bg in SUPPORTING:
                problems.append(f"{e['code']}/{folder}: supporting colour as section background")
            for kind, detail, _ctx in scan(html, SURFACES[surf]["bg"]):
                problems.append(f"{e['code']}/{folder}[{surf}]: {kind} {detail}")

    print(f"emails        : {len(EMAILS)}")
    print(f"coral panels  : {coral}")
    print(f"problems      : {len(problems)}")
    for p in problems:
        print("   ", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
