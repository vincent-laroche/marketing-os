#!/usr/bin/env python3
"""Validate the project-local Email Marketing agent suite."""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = Path(".codex/agents")
SHARED_FILES = ("EMAIL-AGENT-CONTRACT.md", "ROUTING.md")

EXPECTED_ROLES = {
    "campaign-os-engineer": "local-write",
    "email-audience-consent-steward": "read-only",
    "email-deliverability-release-reviewer": "read-only",
    "email-design-module-specialist": "local-write",
    "email-lifecycle-architect": "read-only",
    "email-performance-analyst": "read-only",
    "email-preview-qa-engineer": "local-write",
    "email-producer": "local-write",
    "email-project-manager": "read-only",
    "shopify-flow-automation-builder": "approval-gated",
    "shopify-messaging-campaign-operator": "approval-gated",
    "shopify-notification-template-specialist": "approval-gated",
}

REQUIRED_HEADINGS = (
    "## Mission",
    "## Invoke when",
    "## Mandatory inputs",
    "## Operating pass",
    "## Stop conditions",
    "## Hard boundaries",
    "## Output contract",
)

WRITE_TOOLS = {"Write", "Edit", "NotebookEdit"}
FORBIDDEN_SNIPPETS = (
    "/Users/vMac/07_design/email_marketing",
    "MAILERLITE_API_KEY",
    "SHOPIFY_ACCESS_TOKEN",
    "create a MailerLite campaign",
    "create a MailerLite automation",
    "restore a MailerLite campaign",
    "986 matched",
    "205 engaged",
    "14 ready",
    "39 blocked",
)


@dataclass(frozen=True)
class Definition:
    path: Path
    metadata: dict[str, object]
    body: str

    @property
    def name(self) -> str:
        return str(self.metadata.get("name", ""))

    @property
    def tools(self) -> set[str]:
        value = self.metadata.get("tools", [])
        return set(value) if isinstance(value, list) else set()


def _parse_scalar(raw: str) -> object:
    value = raw.strip()
    if value.startswith("["):
        parsed = ast.literal_eval(value)
        if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
            raise ValueError("tool list must contain only strings")
        return parsed
    if value.isdigit():
        return int(value)
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return ast.literal_eval(value)
    return value


def parse_definition(path: Path) -> Definition:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(?P<meta>.*?)\n---\n(?P<body>.*)\Z", text, re.DOTALL)
    if not match:
        raise ValueError("missing complete YAML-style frontmatter")
    metadata: dict[str, object] = {}
    for line in match.group("meta").splitlines():
        if not line.strip():
            continue
        key, separator, raw = line.partition(":")
        if not separator or not key.strip():
            raise ValueError(f"invalid frontmatter line: {line!r}")
        metadata[key.strip()] = _parse_scalar(raw)
    return Definition(path=path, metadata=metadata, body=match.group("body"))


def load_definitions(root: Path = ROOT) -> dict[str, Definition]:
    agent_dir = root / AGENT_DIR
    if not agent_dir.exists():
        return {}
    definitions: dict[str, Definition] = {}
    for path in sorted(agent_dir.glob("*.md")):
        if path.name in SHARED_FILES:
            continue
        try:
            definition = parse_definition(path)
        except (SyntaxError, ValueError) as exc:
            definitions[f"__invalid__:{path.name}"] = Definition(
                path=path,
                metadata={"parse_error": str(exc)},
                body="",
            )
            continue
        key = definition.name or f"__unnamed__:{path.name}"
        if key in definitions:
            key = f"__duplicate__:{path.name}"
        definitions[key] = definition
    return definitions


def discovered_names(root: Path = ROOT) -> set[str]:
    return {
        definition.name
        for definition in load_definitions(root).values()
        if definition.name
    }


def _metadata_list(definition: Definition, key: str) -> set[str]:
    value = definition.metadata.get(key, [])
    if isinstance(value, list):
        return set(value)
    if isinstance(value, str):
        return {part.strip() for part in value.split(",") if part.strip()}
    return set()


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def validate_definition(definition: Definition, permission: str) -> list[str]:
    errors: list[str] = []
    label = definition.path.name
    metadata = definition.metadata
    body = definition.body
    lower = body.lower()

    if "parse_error" in metadata:
        return [f"{label}: {metadata['parse_error']}"]
    if definition.path.stem != definition.name:
        errors.append(f"{label}: filename must match agent name {definition.name!r}")
    description = metadata.get("description")
    if not isinstance(description, str) or len(description.strip()) < 80:
        errors.append(f"{label}: description must be precise and at least 80 characters")
    if permission not in str(description).lower():
        errors.append(f"{label}: description must name permission class {permission!r}")
    max_turns = metadata.get("maxTurns")
    if not isinstance(max_turns, int) or not 25 <= max_turns <= 60:
        errors.append(f"{label}: maxTurns must be an integer from 25 through 60")
    if "Agent" in definition.tools:
        errors.append(f"{label}: specialist agents must not expose the Agent delegation tool")

    disallowed = _metadata_list(definition, "disallowedTools")
    if permission == "read-only":
        unsafe = definition.tools & WRITE_TOOLS
        if unsafe:
            errors.append(f"{label}: read-only agent exposes write tools {sorted(unsafe)}")
        if not WRITE_TOOLS.issubset(disallowed):
            errors.append(f"{label}: read-only agent must disallow Write, Edit, and NotebookEdit")
    elif permission == "local-write":
        if not {"Write", "Edit"}.issubset(definition.tools):
            errors.append(f"{label}: local-write agent must expose Write and Edit")
        if "NotebookEdit" not in disallowed:
            errors.append(f"{label}: local-write agent must disallow NotebookEdit")
    elif permission == "approval-gated":
        if not {"Write", "Edit"}.isdisjoint(definition.tools):
            errors.append(f"{label}: approval-gated external operator must not expose local write tools")
        for phrase in (
            "explicit current-task approval",
            "re-fetch",
            "never schedule",
            "never activate",
            "never send",
        ):
            if phrase not in lower:
                errors.append(f"{label}: approval-gated operator is missing {phrase!r}")

    for heading in REQUIRED_HEADINGS:
        if heading not in body:
            errors.append(f"{label}: missing required heading {heading!r}")
    if ".codex/agents/EMAIL-AGENT-CONTRACT.md" not in body:
        errors.append(f"{label}: missing shared contract reference")
    if ".codex/agents/ROUTING.md" not in body:
        errors.append(f"{label}: missing routing reference")
    if "campaign-os-key" not in body or "Issue" not in body:
        errors.append(f"{label}: must resolve work through an Issue and campaign-os-key")
    if "standard evidence packet" not in lower:
        errors.append(f"{label}: output must require the standard evidence packet")
    if "do not delegate" not in lower or "do not spawn" not in lower:
        errors.append(f"{label}: missing no-delegation/no-child-agent boundary")
    if _word_count(body) < 900:
        errors.append(f"{label}: role prompt is too shallow ({_word_count(body)} words; minimum 900)")
    for snippet in FORBIDDEN_SNIPPETS:
        if snippet.lower() in lower:
            errors.append(f"{label}: contains forbidden stale or unsafe text {snippet!r}")
    return errors


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    agent_dir = root / AGENT_DIR
    for filename in SHARED_FILES:
        if not (agent_dir / filename).is_file():
            errors.append(f"missing shared agent file: {AGENT_DIR / filename}")

    definitions = load_definitions(root)
    actual = {definition.name for definition in definitions.values() if definition.name}
    missing = sorted(set(EXPECTED_ROLES) - actual)
    unexpected = sorted(actual - set(EXPECTED_ROLES))
    if missing:
        errors.append(f"missing project agents: {', '.join(missing)}")
    if unexpected:
        errors.append(f"unexpected project agents: {', '.join(unexpected)}")
    if len(definitions) != len(EXPECTED_ROLES):
        errors.append(
            f"expected exactly {len(EXPECTED_ROLES)} runnable definitions, found {len(definitions)}"
        )

    seen: set[str] = set()
    for key, definition in definitions.items():
        if key.startswith("__"):
            errors.append(f"{definition.path.name}: invalid or duplicate definition ({key})")
            continue
        if definition.name in seen:
            errors.append(f"{definition.path.name}: duplicate agent name {definition.name!r}")
            continue
        seen.add(definition.name)
        permission = EXPECTED_ROLES.get(definition.name)
        if permission:
            errors.extend(validate_definition(definition, permission))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    errors = validate(args.root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"{len(EXPECTED_ROLES)} project agents validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
