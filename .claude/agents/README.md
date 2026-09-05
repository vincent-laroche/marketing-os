# Claude Code agent suite — generated

These twelve definitions are generated from `.codex/agents/`. **Do not edit them
by hand.** Change the Codex definition, then run:

```bash
python3 tools/sync_claude_agents.py
```

`.codex/agents/` stays the single source of truth: the operating contract, the
routing guide, and every prompt body live there, and `tools/validate_project_agents.py`
enforces the permission classes against it. Duplicating the prompts into a second
editable tree is how the two suites would quietly drift apart.

This README is not generated. The sync only reclaims files carrying its own
provenance marker, so hand-written files in this directory survive.

## Why a separate tree at all

Claude Code reads project subagents from `.claude/agents/`; it never looks in
`.codex/`. The prompt bodies are copied byte for byte, so the two suites behave
identically. Only the frontmatter is translated.

## What the translation changes

| Field | Codex | Claude Code | Why |
|---|---|---|---|
| `tools` | YAML list | comma-separated string | The documented Claude Code format; a list is undocumented. Both failure modes are worth avoiding: if the entries resolve to nothing Claude Code refuses to launch the agent, and if the field is dropped entirely the agent **inherits every tool** — which would hand a read-only reviewer `Write` and `Edit`. This is the one incompatibility that matters. |
| `description` | unquoted | double-quoted | `email-project-manager` says *"router for Project #4; use it to …"*. Unquoted, YAML reads ` #` as a comment and keeps only *"router for Project"* — discarding the routing trigger Claude Code selects on. The repository validator parses frontmatter by hand, so it never saw the loss. **Worth quoting in the Codex source too.** |
| `disallowedTools` | YAML list | comma-separated string | Supported by both; same meaning. |
| `maxTurns` | int | int | Supported by both; carried through unchanged. |
| `name` | — | verbatim | Unchanged, so routing language stays identical. |
| `color` | — | added | Claude Code shows it in the task list. Blue = read-only, green = local-write, orange = approval-gated, so a running agent's blast radius is visible without opening its definition. |

## Verifying

```bash
python3 tools/sync_claude_agents.py --check   # fails if the trees diverge
python3 tools/validate_project_agents.py      # permission classes, headings, snippets
python3 -m unittest discover -s tests         # includes body-parity and boundary tests
```

## Known gap

`Bash` is in the tool list of every read-only and approval-gated agent, and Bash
can write files. Those two permission classes are therefore enforced by the
contract's prose, not by the tool allowlist — in either suite. If that gap needs
closing, the lever is a `permissions.deny` block in `.claude/settings.json` or a
`permissionMode` on the individual agents, not a change to this generator.
