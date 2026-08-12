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
            m = re.search(r'class="final-card"[^>]*background:(#[0-9A-Fa-f]{6})', html)
            if m and m.group(1).upper() in SUPPORTING:
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
