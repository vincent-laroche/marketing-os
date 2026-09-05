#!/usr/bin/env python3
"""Generate the Claude Code agent suite from the Codex definitions.

`.codex/agents/` is the source of truth. Claude Code reads `.claude/agents/`,
and its frontmatter schema differs in one way that matters: `tools` is a
comma-separated string, not a YAML list. A list may fail to resolve, and a
subagent whose tool list resolves to nothing either fails to launch or falls
back to inheriting every tool — which would silently hand a read-only reviewer
Write and Edit. So the mapping is mechanical, and the prompt bodies are copied
byte for byte.

    python3 tools/sync_claude_agents.py            # write .claude/agents/
    python3 tools/sync_claude_agents.py --check    # fail if out of sync
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_project_agents import (  # noqa: E402
    EXPECTED_ROLES,
    SHARED_FILES,
    parse_definition,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / ".codex/agents"
TARGET_DIR = ROOT / ".claude/agents"

# Claude Code renders this beside the subagent in the task list and transcript.
# Colour encodes the permission class so a running agent's blast radius is
# visible without opening its definition.
CLASS_COLOR = {
    "read-only": "blue",
    "local-write": "green",
    "approval-gated": "orange",
}

# Must stay byte-identical to the note emitted by the codex-agents-to-claude
# skill, so running either generator leaves the tree in the same state.
GENERATED_NOTE = (
    "<!-- Generated from ../../.codex/agents/{filename} — the Codex definition "
    "is the source of truth. Edit it there, then re-run the agent sync. -->\n"
)
# Stable substring identifying a file this script wrote, so cleanup never
# touches a hand-written one.
MARKER = "the Codex definition is the source of truth"


def _quote(value: str) -> str:
    """Emit a double-quoted YAML scalar.

    Unquoted, YAML reads ' #' as the start of a comment and drops the rest of
    the line. `email-project-manager` says "router for Project #4; use it to
    ..." — a real YAML consumer such as Claude Code keeps only "router for
    Project", losing the routing trigger. The repository validator parses
    frontmatter by hand and so never saw the loss.
    """
    if value[:1] in {'"', "'"} and value[-1:] == value[:1] and len(value) > 1:
        return value
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _as_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return []


def render(path: Path) -> str:
    """Return the Claude Code definition for one Codex agent file."""
    definition = parse_definition(path)
    metadata = definition.metadata

    name = str(metadata.get("name", ""))
    permission = EXPECTED_ROLES.get(name, "")

    lines = [
        "---",
        f"name: {name}",
        f"description: {_quote(str(metadata.get('description', '')))}",
    ]

    tools = _as_list(metadata.get("tools"))
    if tools:
        lines.append(f"tools: {', '.join(tools)}")

    disallowed = _as_list(metadata.get("disallowedTools"))
    if disallowed:
        lines.append(f"disallowedTools: {', '.join(disallowed)}")

    max_turns = metadata.get("maxTurns")
    if isinstance(max_turns, int):
        lines.append(f"maxTurns: {max_turns}")

    color = CLASS_COLOR.get(permission)
    if color:
        lines.append(f"color: {color}")

    lines.append("---")
    lines.append("")
    lines.append(GENERATED_NOTE.format(filename=path.name).rstrip("\n"))
    lines.append("")

    return "\n".join(lines) + definition.body


def sources() -> list[Path]:
    return [
        path
        for path in sorted(SOURCE_DIR.glob("*.md"))
        if path.name not in SHARED_FILES
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the generated files match the Codex source; write nothing",
    )
    args = parser.parse_args()

    if not SOURCE_DIR.is_dir():
        print(f"FAIL: {SOURCE_DIR} not found", file=sys.stderr)
        return 2

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    stale: list[str] = []
    written = 0

    for source in sources():
        expected = render(source)
        target = TARGET_DIR / source.name
        current = target.read_text(encoding="utf-8") if target.exists() else None

        if current == expected:
            continue
        if args.check:
            stale.append(target.relative_to(ROOT).as_posix())
            continue
        target.write_text(expected, encoding="utf-8")
        written += 1

    known = {source.name for source in sources()}
    for orphan in sorted(TARGET_DIR.glob("*.md")):
        if orphan.name in known:
            continue
        # Only reclaim files this script produced. The directory is a normal
        # part of the repo — the hand-written README lives here too, and
        # deleting it for having no Codex twin destroys real work.
        if MARKER not in orphan.read_text(encoding="utf-8"):
            continue
        if args.check:
            stale.append(f"{orphan.relative_to(ROOT).as_posix()} (no Codex source)")
        else:
            orphan.unlink()

    if args.check:
        if stale:
            print("FAIL: .claude/agents is out of sync with .codex/agents", file=sys.stderr)
            for item in stale:
                print(f"  - {item}", file=sys.stderr)
            print("Run: python3 tools/sync_claude_agents.py", file=sys.stderr)
            return 1
        print(f"OK: {len(known)} Claude agents match their Codex sources")
        return 0

    print(f"OK: {len(known)} Claude agents generated ({written} changed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
