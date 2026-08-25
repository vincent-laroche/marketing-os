#!/usr/bin/env python3
"""Compile Social Media OS Markdown records into a deterministic JSON manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOCIAL_ROOT = ROOT / "social-media"
VALIDATOR = ROOT / "tools" / "social_os" / "validate_social_os.py"


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


def body_sections(body: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current = "body"
    buffer: list[str] = []
    for line in body.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            sections[current] = "\n".join(buffer).strip()
            current = match.group(1).strip().lower().replace(" ", "_")
            buffer = []
        else:
            buffer.append(line)
    sections[current] = "\n".join(buffer).strip()
    return {key: value for key, value in sections.items() if value}


def source_record(validator, kind: str, path: Path) -> dict:
    data, body = validator.parse_frontmatter(path)
    relative = path.relative_to(ROOT).as_posix()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    record = {
        "type": kind,
        "key": data.get("key"),
        "title": data.get("title"),
        "stage": data.get("stage"),
        "channel": data.get("channel"),
        "objective": data.get("objective"),
        "funnel": data.get("funnel"),
        "priority": data.get("priority"),
        "primary_kpi": data.get("primary_kpi"),
        "source_path": relative,
        "source_sha256": digest,
        "body_sections": body_sections(body),
    }
    for field in (
        "campaign_key",
        "content_key",
        "initiative_key",
        "platform",
        "format",
        "content_pillar",
        "publish_date",
        "feed_order",
        "preview_template",
        "asset_keys",
        "copy_readiness",
        "creative_readiness",
        "accessibility",
        "tracking_readiness",
        "claims_review",
        "rights_review",
        "provider",
        "provider_id",
        "approved_url",
        "thumbnail_url",
        "sha256",
        "rights_status",
        "consent_status",
        "permitted_uses",
        "expires_on",
        "reuse_potential",
        "next_platform",
        "next_format",
        "hypothesis",
        "test_variable",
        "success_threshold",
    ):
        if field in data:
            record[field] = data[field]
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write manifest to this path; stdout otherwise")
    args = parser.parse_args()

    validator = load_validator()
    records = []
    for kind, path in validator.record_paths():
        records.append(source_record(validator, kind, path))
    records.sort(key=lambda item: (item["type"], item["key"] or ""))
    payload = {
        "schema_version": 1,
        "generated_from": "social-media/",
        "records": records,
        "record_count": len(records),
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
