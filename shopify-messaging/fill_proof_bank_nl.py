#!/usr/bin/env python3
"""Phase 4 (CAMPAIGN-PLAN.md): fill the Proof Bank quote slots across the 20
newsletter editions (NL-01..NL-20) using the 87 extracted, published Judge.me
reviews (proof-bank/proof-bank.json).

Scope, deliberately narrow — only what the plan calls "unblocked now":
  - Quote/testimonial placeholders ("[PULL from Proof Bank: ... quote ... angle]")
    -> filled with a real review (author + body), matched to the requested angle
       by keyword overlap against the 26 "quotable" (body >= 120 chars) reviews.
  - "aggregate rating" placeholders -> filled with the honest, computable figure:
    "4.5 average across 87 published reviews (Judge.me)" -- NOT a re-inflated
    number, NOT a verified-buyer claim (none of the 87 carry one).

Explicitly NOT touched, left as-is, and reported at the end:
  - "verified figures/metrics" placeholders (knots per system, build hours, QC
    pass rate, average time to locked spec, re-bond interval, etc.) -- Judge.me
    review text has no such data. Needs real operational numbers from Vincent.
  - "consented customer photo / UGC photo" placeholders -- proof-bank.json is
    text-only; no photo asset exists to pull.

Each review is used at most once across all NL editions (tracked via the
proof-bank.json "used_in" field, which this script also updates on disk so a
future run doesn't reuse an already-placed quote). Run with --dry-run first.
"""
import json
import os
import re
import sys

# Derived from this file's location, not hard-coded. The previous absolute paths pointed at
# /Users/vMac/04_marketing/email_marketing, which stopped existing when the repository was
# consolidated — so this stage silently did nothing while build_emails.py happily produced
# newsletters with empty Proof Bank slots (#144).
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMAILS_DIR = os.path.join(ROOT, "shopify-messaging", "emails")
PROOF_BANK_JSON = os.path.join(ROOT, "proof-bank", "proof-bank.json")

for _required in (EMAILS_DIR, PROOF_BANK_JSON):
    if not os.path.exists(_required):
        # Fail loudly. Proceeding leaves the newsletters looking built but unfilled, which is
        # exactly how the broken paths went unnoticed.
        raise SystemExit(f"fill_proof_bank_nl: required path is missing: {_required}")

DRY = "--dry-run" in sys.argv

QUOTE_DIV_RE = re.compile(
    r'(<div style="font-family:\'Helvetica Neue\',Helvetica,Arial,sans-serif;'
    r'font-style:italic;font-size:16px;line-height:1\.6;color:#25221D;'
    r'padding-bottom:8px;">)&#8220;&#8221;(</div>)'
    r'(<div style="font-family:\'Helvetica Neue\',Helvetica,Arial,sans-serif;'
    r'font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;'
    r'color:#151411;">)&#8212; (</div>)'
)
# The literal characters in the files are the actual glyphs, not entities -- match those too.
QUOTE_DIV_RE_LITERAL = re.compile(
    r'(<div style="font-family:\'Helvetica Neue\',Helvetica,Arial,sans-serif;'
    r'font-style:italic;font-size:16px;line-height:1\.6;color:#25221D;'
    r'padding-bottom:8px;">)“”(</div>)'
    r'(<div style="font-family:\'Helvetica Neue\',Helvetica,Arial,sans-serif;'
    r'font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;'
    r'color:#151411;">)— (</div>)'
)

PLACEHOLDER_RE = re.compile(
    r'<div style="border:2px dashed #EA6452;[^"]*">\[PULL from Proof Bank:\s*([^\]]*)\]</div>'
)

AGGREGATE_RATING_TEXT = "4.5 average across 87 published reviews (Judge.me)"


def is_metrics_or_photo(angle: str) -> bool:
    a = angle.lower()
    return ("verified metric" in a or "verified figure" in a or "photo" in a)


def is_aggregate_rating(angle: str) -> bool:
    a = angle.lower()
    return "aggregate" in a and "rating" in a


def keyword_score(angle: str, review: dict) -> int:
    text = (review["title"] + " " + review["body"]).lower()
    angle_l = angle.lower()
    score = 0
    keyword_map = {
        "hairline": ["hairline", "nobody", "no one can tell", "blends"],
        "nobody noticed": ["no one can tell", "nobody", "blends perfectly"],
        "natural": ["natural", "hairline blends"],
        "quality": ["quality"],
        "craftsmanship": ["quality", "well made", "well-made"],
        "value": ["price", "worth", "value", "decent for the price"],
        "first-order": ["ordered this after", "so glad i went", "first"],
        "first order": ["ordered this after", "so glad i went"],
        "will it look real": ["no one can tell", "natural", "blends"],
        "base-choice": ["base is", "base was", "thin", "comfortable"],
        "base choice": ["base is", "thin", "comfortable"],
        "density": ["hair quality", "looks natural", "thick"],
        "colour-match": ["color match", "colour match"],
        "color-match": ["color match"],
        "longevity": ["months", "still in good condition", "sweating", "holds"],
        "routine": ["application", "practice", "routine", "wearing for"],
        "reorder": ["again", "second", "ordered again", "repeat"],
        "second one": ["second", "again"],
        "confidence": ["comfortable", "style it however", "confidence"],
        "style": ["style it however", "look"],
        "comfort": ["comfortable"],
        "consultation": ["research", "went with this one"],
        "care routine": ["application", "practice", "routine"],
        "rotating": ["wearing for", "switched"],
        "switched": ["switched from another brand"],
        "repeat customer": ["again", "second", "3 months", "6 weeks"],
        "difference": ["better", "way better", "switched"],
        "came back": ["switched", "way better"],
        "early wearer": ["been wearing for about", "6 weeks", "ordered this after"],
        "day-one vs day-90": ["3 months", "still in good condition"],
    }
    for key, terms in keyword_map.items():
        if key in angle_l:
            for t in terms:
                if t in text:
                    score += 2
    # generic overlap fallback
    for word in re.findall(r"[a-z]{5,}", angle_l):
        if word in text:
            score += 1
    return score


def main():
    proof_bank = json.load(open(PROOF_BANK_JSON))
    quotable = [r for r in proof_bank if len(r["body"]) >= 120 and not r.get("used_in")]

    import glob
    nl_files = sorted(glob.glob(f"{EMAILS_DIR}/*-nl-*.html"))

    report = {"filled_quotes": [], "filled_ratings": [], "skipped": []}

    for path in nl_files:
        html = open(path, encoding="utf-8").read()
        original_html = html

        placeholders = list(PLACEHOLDER_RE.finditer(html))
        for m in placeholders:
            angle = m.group(1).strip()
            full_match = m.group(0)

            if is_metrics_or_photo(angle):
                report["skipped"].append((path.split("/")[-1], angle, "metrics/photo -- no source data"))
                continue

            if is_aggregate_rating(angle):
                html = html.replace(full_match, AGGREGATE_RATING_TEXT, 1)
                report["filled_ratings"].append((path.split("/")[-1], angle))
                continue

            # Quote-type: find the nearest preceding empty quote/author pair and fill it,
            # then remove the instruction box.
            idx = html.find(full_match)
            preceding = html[:idx]
            quote_match = None
            for pat in (QUOTE_DIV_RE, QUOTE_DIV_RE_LITERAL):
                matches = list(pat.finditer(preceding))
                if matches:
                    quote_match = matches[-1]
                    used_pat = pat
                    break

            scored = sorted(quotable, key=lambda r: -keyword_score(angle, r))
            generic_angle = ("period's theme" in angle.lower()
                              or "strongest consented review line" in angle.lower()
                              or "reply is worth quoting" in angle.lower())
            if not scored:
                report["skipped"].append((path.split("/")[-1], angle, "no unused quotable reviews left"))
                continue
            if keyword_score(angle, scored[0]) == 0 and not generic_angle:
                report["skipped"].append((path.split("/")[-1], angle, "no confident review match"))
                continue

            # Generic angle (no specific theme to match): take the highest-rated
            # unused review rather than force a keyword match that doesn't exist.
            chosen = max(quotable, key=lambda r: int(r["rating"])) if generic_angle else scored[0]

            if quote_match:
                quotable.remove(chosen)
                for r in proof_bank:
                    if r["review_id"] == chosen["review_id"]:
                        r["used_in"] = path.split("/")[-1]
                quote_html = (
                    quote_match.group(1) + "“" + chosen["body"] + "”" + quote_match.group(2)
                    + quote_match.group(3) + "— " + chosen["author"] + f" ({chosen['rating']}★, {chosen['product']})"
                    + quote_match.group(4)
                )
                html = html[:quote_match.start()] + quote_html + html[quote_match.end():]
                html = html.replace(full_match, "", 1)
                report["filled_quotes"].append((path.split("/")[-1], angle, chosen["author"], chosen["review_id"]))
            else:
                # Standalone pull-quote module: no separate quote/author div pair.
                # Replace the placeholder box's own text in place, styled as the
                # quote itself (parent div is already italic/large per the module).
                quotable.remove(chosen)
                for r in proof_bank:
                    if r["review_id"] == chosen["review_id"]:
                        r["used_in"] = path.split("/")[-1]
                inline = f"“{chosen['body']}” — {chosen['author']} ({chosen['rating']}★, {chosen['product']})"
                html = html.replace(full_match, inline, 1)
                report["filled_quotes"].append((path.split("/")[-1], angle, chosen["author"], chosen["review_id"]))

        if html != original_html and not DRY:
            open(path, "w", encoding="utf-8").write(html)

    if not DRY:
        json.dump(proof_bank, open(PROOF_BANK_JSON, "w"), indent=2)

    print(f"{'[DRY RUN] ' if DRY else ''}Filled {len(report['filled_quotes'])} quotes, "
          f"{len(report['filled_ratings'])} rating placeholders. "
          f"Skipped {len(report['skipped'])}.")
    print("\n--- filled quotes ---")
    for f, angle, author, rid in report["filled_quotes"]:
        print(f"  {f}: [{angle[:50]}...] -> {author} ({rid[:8]})")
    print("\n--- filled ratings ---")
    for f, angle in report["filled_ratings"]:
        print(f"  {f}: [{angle}]")
    print("\n--- skipped (needs real data or no confident match) ---")
    for f, angle, reason in report["skipped"]:
        print(f"  {f}: [{angle[:60]}] -- {reason}")


if __name__ == "__main__":
    main()
