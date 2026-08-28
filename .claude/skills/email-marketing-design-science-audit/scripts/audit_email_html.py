#!/usr/bin/env python3
"""Run deterministic triage checks on an HTML marketing email."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


HEX_RE = re.compile(r"#[0-9a-fA-F]{3,6}\b")
WIDTH_RE = re.compile(r"(?:width=['\"]?|\bwidth\s*:\s*)(\d{3,4})", re.I)
FONT_SIZE_RE = re.compile(r"font-size\s*:\s*(\d+)px", re.I)
CTA_TEXT_RE = re.compile(r"\b(click here|buy now|last chance|hurry|guaranteed|claim your transformation)\b", re.I)
UNSUPPORTED_RE = re.compile(
    r"\b(display\s*:\s*(?:grid|flex)|position\s*:\s*sticky|<script\b|<form\b|<video\b|<iframe\b|"
    r"background-image\s*:|var\(|@import\b)",
    re.I,
)


class EmailParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.images: list[dict[str, str | None]] = []
        self.links: list[dict[str, str | None]] = []
        self.tables = 0
        self.current_link: dict[str, str | None] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if tag == "img":
            self.images.append({"src": attr.get("src"), "alt": attr.get("alt"), "width": attr.get("width"), "height": attr.get("height")})
        elif tag == "a":
            self.current_link = {"href": attr.get("href"), "text": ""}
            self.links.append(self.current_link)
        elif tag == "table":
            self.tables += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self.current_link = None

    def handle_data(self, data: str) -> None:
        if self.current_link is not None:
            current = self.current_link.get("text") or ""
            self.current_link["text"] = (current + data).strip()


def issue(severity: str, category: str, message: str, fix: str) -> dict[str, str]:
    return {"severity": severity, "category": category, "message": message, "fix": fix}


def audit_html(html: str) -> dict[str, object]:
    parser = EmailParser()
    parser.feed(html)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    lower = html.lower()
    issues: list[dict[str, str]] = []

    if "<table" not in lower:
        issues.append(issue("P1", "rendering", "No table structure found.", "Use presentation tables for email layout."))
    if "<script" in lower or "<form" in lower or "<video" in lower:
        issues.append(issue("P0", "email-client", "Unsupported interactive HTML found.", "Remove scripts/forms/video and provide static email-safe fallback."))

    unsupported = sorted(set(match.group(0) for match in UNSUPPORTED_RE.finditer(html)))
    for token in unsupported:
        issues.append(issue("P1", "email-client", f"Unsupported or risky pattern found: {token}", "Replace with conservative inline/table-based email HTML."))

    widths = [int(match.group(1)) for match in WIDTH_RE.finditer(html)]
    too_wide = sorted({value for value in widths if value > 600})
    for value in too_wide:
        issues.append(issue("P1", "mobile-rendering", f"Width exceeds 600px: {value}px.", "Keep main email wrapper and critical images at 600px or less."))

    missing_alt = [img for img in parser.images if img.get("alt") is None]
    if missing_alt:
        issues.append(issue("P1", "accessibility", f"{len(missing_alt)} image(s) missing alt attributes.", "Add meaningful alt text or empty alt for decorative images."))

    image_count = len(parser.images)
    word_count = len(re.findall(r"\b\w+\b", text))
    if image_count and word_count < 80:
        issues.append(issue("P1", "accessibility-deliverability", "Email appears image-heavy with limited live text.", "Use live text for headings, CTAs, product details, and disclaimers."))

    vague_links = [link for link in parser.links if CTA_TEXT_RE.search(link.get("text") or "")]
    if vague_links:
        issues.append(issue("P2", "cta-copy", "CTA/link text includes vague, spammy, or pressure language.", "Use descriptive, calm CTA labels tied to the next useful step."))

    tiny_fonts = sorted({int(match.group(1)) for match in FONT_SIZE_RE.finditer(html) if int(match.group(1)) < 14})
    if tiny_fonts:
        issues.append(issue("P2", "accessibility", f"Small font sizes found: {tiny_fonts}.", "Keep body text at least 14px desktop and usually 16px mobile."))

    compliance_terms = ["unsubscribe", "preferences", "manage your preferences"]
    if not any(term in lower for term in compliance_terms):
        issues.append(issue("P0", "compliance", "No obvious unsubscribe/preferences language found.", "Ensure marketing email includes required unsubscribe or preferences link."))
    if not any(term in lower for term in ["address", "mailing", "postal"]):
        issues.append(issue("P1", "compliance", "No obvious sender address language found.", "Ensure sender identity and physical mailing address are present where required."))

    colors = sorted({color.upper() for color in HEX_RE.findall(html)})
    return {
        "summary": {
            "tables": parser.tables,
            "images": image_count,
            "links": len(parser.links),
            "word_count": word_count,
            "unique_hex_colors": colors,
            "max_width_found": max(widths) if widths else None,
            "issue_count": len(issues),
        },
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html_file", help="Path to an HTML email file")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    path = Path(args.html_file).expanduser()
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    html = path.read_text(encoding="utf-8", errors="replace")
    report = audit_html(html)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Email HTML audit")
        print("================")
        for key, value in report["summary"].items():  # type: ignore[union-attr]
            print(f"{key}: {value}")
        print("\nIssues")
        for item in report["issues"]:  # type: ignore[union-attr]
            print(f"- {item['severity']} {item['category']}: {item['message']} Fix: {item['fix']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
