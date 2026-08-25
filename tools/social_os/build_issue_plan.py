#!/usr/bin/env python3
"""Compile Social Media OS source records into a dry-run GitHub Issue plan."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "tools" / "social_os" / "validate_social_os.py"

TITLE_PREFIX = {
    "campaign": "Campaign",
    "content": "Content",
    "publication": "Publication",
    "asset": "Asset",
    "experiment": "Experiment",
    "evergreen": "Evergreen",
}


def load_validator():
    import importlib.util

    spec = importlib.util.spec_from_file_location("social_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load validator from {VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def parent_key(record) -> str | None:
    data = record.data
    return data.get("content_key") or data.get("campaign_key") or data.get("initiative_key")


def labels(record) -> list[str]:
    data = record.data
    values = ["os:social", f"type:{record.kind}", f"stage:{data.get('stage')}"]
    for field in ("platform", "format", "content_pillar", "objective", "funnel", "priority"):
        value = data.get(field)
        if isinstance(value, str) and value:
            values.append(f"{field.replace('_', '-')}:" + value.lower().replace(" ", "-"))
    return values


def issue_body(record) -> str:
    data = record.data
    lines = [
        f"<!-- social-os-key: {data.get('key', '')} -->",
        "<!-- Generated source snapshot. Human evidence sections must be preserved. -->",
        "",
        f"## Source\n`{record.path.relative_to(ROOT).as_posix()}`",
        f"\n## Source SHA-256\n`{record.digest}`",
        f"\n## Stage\n{data.get('stage', '')}",
        f"\n## Parent\n`{parent_key(record) or 'none'}`",
        "\n## Blockers\n",
        "## Evidence\n",
        "## Decisions\n",
        "## Results\n",
        "## Learnings\n",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="output JSON path")
    args = parser.parse_args()

    subprocess.run([sys.executable, str(VALIDATOR)], check=True)
    validator = load_validator()
    records = validator.load_records([])
    records.sort(key=lambda record: (record.kind, record.data.get("key", "")))
    issues = []
    for record in records:
        data = record.data
        issues.append(
            {
                "operation": "upsert-by-key",
                "key": data.get("key"),
                "title": f"{TITLE_PREFIX[record.kind]}: {data.get('title', '')}",
                "parent_key": parent_key(record),
                "labels": labels(record),
                "body": issue_body(record),
                "source_path": record.path.relative_to(ROOT).as_posix(),
                "source_sha256": record.digest,
            }
        )
    payload = {
        "schema_version": 1,
        "repository": "vincent-laroche/email-marketing-ops",
        "mode": "dry-run",
        "external_mutation": False,
        "issue_count": len(issues),
        "issues": issues,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Social Issue plan: PASS ({len(issues)} dry-run records)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
