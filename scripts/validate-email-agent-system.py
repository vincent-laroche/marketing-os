#!/usr/bin/env python3
"""Validate the project-local Email Marketing agent contracts without dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / ".codex" / "agents"
CONTRACT = "docs/agent-system/EMAIL_MARKETING_AGENT_CONTRACT.md"
EXPECTED = {
    "email-project-manager",
    "email-lifecycle-architect",
    "email-producer",
    "email-deliverability-release-reviewer",
    "email-audience-consent-steward",
    "email-design-module-specialist",
    "email-preview-qa-engineer",
    "campaign-os-engineer",
    "shopify-messaging-campaign-operator",
    "shopify-flow-automation-builder",
    "email-performance-analyst",
    "shopify-notification-template-specialist",
}
APPROVED_TOOLS = {"Read", "Glob", "Grep", "Bash", "Agent", "Write", "Edit"}
OPERATORS = {
    "shopify-messaging-campaign-operator",
    "shopify-flow-automation-builder",
    "shopify-notification-template-specialist",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def parse_frontmatter(path: Path, errors: list[str]) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        fail(errors, f"{path.name}: missing YAML frontmatter")
        return {}, text
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields, text


def tools(value: str) -> set[str]:
    return set(re.findall(r'"([^"\\]+)"', value))


def main() -> int:
    errors: list[str] = []
    definitions = sorted(AGENTS.glob("*.md"))
    names: list[str] = []
    for path in definitions:
        frontmatter, text = parse_frontmatter(path, errors)
        name = frontmatter.get("name", "")
        names.append(name)
        if not name or not frontmatter.get("description"):
            fail(errors, f"{path.name}: requires name and description")
        if CONTRACT not in text:
            fail(errors, f"{path.name}: missing shared contract reference")
        for required in ("## Output contract", "## Stopping condition", "MailerLite"):
            if required not in text:
                fail(errors, f"{path.name}: missing required marker {required!r}")
        declared = tools(frontmatter.get("tools", ""))
        if not declared or not declared <= APPROVED_TOOLS:
            fail(errors, f"{path.name}: uses an unapproved or empty tools list")
        if name in OPERATORS and "explicit approval" not in text.lower():
            fail(errors, f"{path.name}: external operator lacks explicit approval gate")
    if set(names) != EXPECTED:
        missing = sorted(EXPECTED - set(names))
        unexpected = sorted(set(names) - EXPECTED)
        if missing:
            fail(errors, f"missing definitions: {', '.join(missing)}")
        if unexpected:
            fail(errors, f"unexpected definitions: {', '.join(unexpected)}")
    if len(names) != len(set(names)):
        fail(errors, "agent names must be unique")
    manager = AGENTS / "email-project-manager.md"
    if manager.exists() and "Do not mutate GitHub" not in manager.read_text(encoding="utf-8"):
        fail(errors, "email-project-manager must remain recommendation-only")
    if errors:
        print("Email Marketing agent validation failed:", *[f"- {item}" for item in errors], sep="\n")
        return 1
    print(f"Email Marketing agent validation passed: {len(definitions)} definitions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
