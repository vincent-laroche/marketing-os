"""Parse the v3 Notion export into structured email records.

This is the ONLY module that reads the export. The export contains stale
duplicates of the stack and body in its markdown prose; this parser reads the
CSV property columns exclusively, which are the corrected v3 values.
"""
import csv, re

STACK_RE = re.compile(r"([\(\[])([^)\]]+)([\)\]])")
TAG_RE = re.compile(r"^\[([^\]]+)\]\s*$", re.M)


def _split_qualifier(text):
    """'Button - Primary CTA: view your order' -> ('Button - Primary CTA', 'view your order')"""
    parts = text.split(":", 1)
    return parts[0].strip(), (parts[1].strip() if len(parts) > 1 else "")


def parse_stack(raw):
    out = []
    for open_br, inner, _close in STACK_RE.findall(raw or ""):
        fam, qual = _split_qualifier(inner)
        out.append({"family": fam, "qualifier": qual, "required": open_br == "("})
    return out


def parse_body(raw):
    """Split a [Module]-tagged body into per-module copy blocks.

    Returns [] for unsegmented bodies — those are prose founder letters whose
    whole text belongs to a single Layout - Plain-text founder wrapper.
    """
    raw = raw or ""
    tags = list(TAG_RE.finditer(raw))
    if not tags:
        return []
    out = []
    for i, m in enumerate(tags):
        end = tags[i + 1].start() if i + 1 < len(tags) else len(raw)
        fam, qual = _split_qualifier(m.group(1))
        out.append({"family": fam, "qualifier": qual,
                    "copy": raw[m.end():end].strip()})
    return out


def load_emails(csv_path):
    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        series = (r.get("Series") or "").strip()
        if series.startswith("W ·"):
            continue                      # newsletters are out of scope
        name = (r.get("Email name") or "").strip()
        out.append({
            "code": name.split(" · ")[0].strip(),
            "name": name,
            "journey": series,
            "position": float(r.get("Position") or 0),
            "subject": (r.get("Subject") or "").strip(),
            "preview": (r.get("Preview Text") or "").strip(),
            "cta": (r.get("CTA") or "").strip(),
            "stack": parse_stack(r.get("Module Stack")),
            "blocks": parse_body(r.get("Body")),
            "subscription": (r.get("Subscription Type") or "").strip(),
            "channel": (r.get("Email Channel") or "").strip(),
            "hubspot_id": (r.get("HubSpot Email ID") or "").strip(),
        })
    out.sort(key=lambda e: (e["journey"], e["position"]))
    return out
