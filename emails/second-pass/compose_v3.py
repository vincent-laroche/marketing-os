"""Build the composition list the renderer consumes, from the v3 export."""
import os
from v3_source import load_emails
from module_map import resolve, fields_for, placeholder_fields, PLACEHOLDER_HOST
from tonal_plan import surface_for, CHROME

CSV = os.path.join(os.path.dirname(__file__), "source-v3",
                   "emails_master 831f4e0d84e0831992d481ae881cfede_all.csv")

FOUNDER = "Layout - Plain-text founder wrapper"
BUTTON = "Button - Primary CTA"


def _copy_for(email, family, used):
    """Next unused copy block matching this family, in document order."""
    for i, b in enumerate(email["blocks"]):
        if i in used:
            continue
        if b["family"] == family:
            used.add(i)
            return b
    return None


def _compose(email, raw_body):
    used, blocks = set(), []
    for idx, slot in enumerate(email["stack"]):
        fam, qual = slot["family"], slot["qualifier"]
        blk = _copy_for(email, fam, used)
        copy = blk["copy"] if blk else ""
        # unsegmented founder letters: the whole body is the letter
        founder_case = not email["blocks"] and fam == FOUNDER
        if founder_case:
            copy = raw_body
        slug = resolve(fam)
        surf = surface_for(email, idx, fam)
        # Correction #4: a stack slot with no matching copy block must render
        # a visible bracketed placeholder, never blank real-module fields.
        # This matters for CR-4 and RO-4, whose bodies are unsegmented
        # (founder letters) but whose stacks keep extra commerce/promo/text
        # slots beyond the letter itself — those slots have no per-family
        # copy to draw on. Chrome (header/footer) is exempt: it never carries
        # inline copy by design in the v3 export (confirmed across all 28
        # emails) and its own module defaults are structural, not fabricated
        # business facts. The CTA button is exempt too: fields_for already
        # falls back to the email's own `cta` column, which is real content,
        # not blank.
        unmatched = blk is None and not founder_case and fam not in CHROME and fam != BUTTON
        if slug is None or unmatched:
            blocks.append((PLACEHOLDER_HOST, surf, placeholder_fields(fam, qual, copy)))
        else:
            blocks.append((slug, surf, fields_for(fam, qual, copy, email)))
    return blocks


def build():
    import csv
    with open(CSV, newline="", encoding="utf-8-sig") as fh:
        raw = {r["Email name"].split(" · ")[0].strip(): (r["Body"] or "")
               for r in csv.DictReader(fh)}
    all_emails = load_emails(CSV)
    totals = {}
    for e in all_emails:
        totals[e["journey"]] = totals.get(e["journey"], 0) + 1
    out = []
    for e in all_emails:
        out.append({
            "code": e["code"],
            "journey": e["journey"].split(" · ")[1] if " · " in e["journey"] else e["journey"],
            "pos": f"{int(e['position'])} of {totals[e['journey']]}",
            "subject": e["subject"],
            "preview": e["preview"],
            "blocks": _compose(e, raw.get(e["code"], "")),
        })
    return out


EMAILS = build()
