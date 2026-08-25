#!/usr/bin/env python3
"""Validate Social Media OS source records without contacting external platforms."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SOCIAL_ROOT = ROOT / "social-media"
TEMPLATE_MANIFEST = SOCIAL_ROOT / "templates" / "manifest.json"

STAGES = {
    "Idea",
    "Brief",
    "Creating",
    "Editing",
    "Review",
    "Approved",
    "Scheduled",
    "Published",
    "Measuring",
    "Complete",
    "Blocked",
}
OBJECTIVES = {"Reach", "Engagement", "Traffic", "Leads", "Sales", "Retention", "Trust"}
FUNNELS = {"Awareness", "Consideration", "Conversion", "Retention"}
PRIORITIES = {"P0", "P1", "P2", "P3"}
CHANNELS = {"Social", "Cross-channel"}
PLATFORMS = {"Instagram", "TikTok", "Facebook"}
FORMATS = {"Short Video", "Carousel", "Static", "Story", "Text-Link", "Live"}
READINESS = {"Needs Work", "Ready", "N/A"}
REVIEW = {"N/A", "Required", "Approved", "Blocked"}
KEY_RE = re.compile(r"^[a-z][a-z0-9-]*(?::[a-z][a-z0-9-]*)+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

EXPECTED_BY_PATH = {
    "campaign": "campaign",
    "content": "content",
    "publication": "publication",
    "asset": "asset",
    "experiment": "experiment",
    "evergreen": "evergreen",
}


@dataclass
class Record:
    kind: str
    path: Path
    data: dict[str, Any]
    body: str
    digest: str


class ValidationError(Exception):
    pass


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"", "null", "Null", "NULL", "~"}:
        return None
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(part) for part in inner.split(",")]
    if value.startswith("\"") and value.endswith("\""):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        raise ValidationError("missing opening YAML front-matter delimiter")

    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
    if end is None:
        raise ValidationError("missing closing YAML front-matter delimiter")

    data: dict[str, Any] = {}
    for line_number, line in enumerate(lines[1:end], start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in line or line[:1].isspace():
            raise ValidationError(f"invalid front-matter line {line_number}: {line!r}")
        key, value = line.split(":", 1)
        key = key.strip()
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key):
            raise ValidationError(f"invalid field name {key!r}")
        if key in data:
            raise ValidationError(f"duplicate field {key!r}")
        data[key] = parse_scalar(value)

    body = "\n".join(lines[end + 1 :]).strip() + "\n"
    return data, body


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify(path: Path) -> str | None:
    relative = path.relative_to(SOCIAL_ROOT).parts
    if not relative or any(part.startswith("_") for part in relative):
        return None
    if len(relative) == 3 and relative[0] == "campaigns" and relative[2] == "campaign.md":
        return "campaign"
    if len(relative) == 5 and relative[0] == "campaigns" and relative[2] == "content" and relative[4] == "concept.md":
        return "content"
    if len(relative) == 6 and relative[0] == "campaigns" and relative[2] == "content" and relative[4] == "publications":
        return "publication"
    if len(relative) == 4 and relative[0] == "campaigns" and relative[2] == "experiments":
        return "experiment"
    if len(relative) == 2 and relative[0] == "evergreen":
        return "evergreen"
    if len(relative) == 2 and relative[0] == "assets" and relative[1].endswith(".md"):
        return "asset"
    return None


def record_paths() -> list[tuple[str, Path]]:
    result: list[tuple[str, Path]] = []
    for path in sorted(SOCIAL_ROOT.rglob("*.md")):
        kind = classify(path)
        if kind:
            result.append((kind, path))
    return result


def require_string(data: dict[str, Any], field: str, path: Path, errors: list[str]) -> str | None:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}: {field} must be a non-empty string")
        return None
    return value.strip()


def require_enum(data: dict[str, Any], field: str, allowed: set[str], path: Path, errors: list[str]) -> str | None:
    value = require_string(data, field, path, errors)
    if value is not None and value not in allowed:
        errors.append(f"{path}: {field}={value!r} is not one of {sorted(allowed)}")
    return value


def require_date_or_null(data: dict[str, Any], field: str, path: Path, errors: list[str]) -> None:
    value = data.get(field)
    if value is None:
        return
    if not isinstance(value, str) or not DATE_RE.fullmatch(value):
        errors.append(f"{path}: {field} must be YYYY-MM-DD or null")
        return
    try:
        date.fromisoformat(value)
    except ValueError:
        errors.append(f"{path}: {field} is not a real calendar date")


def split_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        if value.strip().lower() in {"none", "null", "n/a"}:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def validate_common(record: Record, errors: list[str]) -> None:
    data, path = record.data, record.path
    record_type = require_string(data, "type", path, errors)
    if record_type != record.kind:
        errors.append(f"{path}: type={record_type!r} does not match path kind {record.kind!r}")
    key = require_string(data, "key", path, errors)
    if key is not None and not KEY_RE.fullmatch(key):
        errors.append(f"{path}: key={key!r} is not a lowercase namespaced key")
    require_string(data, "title", path, errors)
    require_enum(data, "stage", STAGES, path, errors)
    require_enum(data, "channel", CHANNELS, path, errors)
    require_enum(data, "objective", OBJECTIVES, path, errors)
    require_enum(data, "funnel", FUNNELS, path, errors)
    require_enum(data, "priority", PRIORITIES, path, errors)
    require_string(data, "primary_kpi", path, errors)


def validate_record_specific(record: Record, errors: list[str]) -> None:
    data, path = record.data, record.path
    if record.kind == "campaign":
        pillars = split_list(data.get("content_pillars"))
        if not pillars:
            errors.append(f"{path}: content_pillars must contain at least one pillar")
        require_date_or_null(data, "production_start", path, errors)
        require_date_or_null(data, "campaign_end", path, errors)
        initiative = data.get("initiative_key")
        if initiative is not None and (not isinstance(initiative, str) or not KEY_RE.fullmatch(initiative)):
            errors.append(f"{path}: initiative_key must be a namespaced key or null")

    elif record.kind == "content":
        require_string(data, "campaign_key", path, errors)
        require_enum(data, "content_pillar", {
            "Education",
            "Product & Solutions",
            "Customer Stories / Social Proof",
            "Questions & Objections",
            "Brand & Founder",
            "Lifestyle / Identity",
            "Promotion",
            "Trend / Entertainment",
        }, path, errors)
        require_enum(data, "format", FORMATS, path, errors)
        require_enum(data, "reuse_potential", {"High", "Medium", "Low", "No"}, path, errors)

    elif record.kind == "publication":
        require_enum(data, "platform", PLATFORMS, path, errors)
        require_string(data, "content_key", path, errors)
        require_enum(data, "format", FORMATS, path, errors)
        require_date_or_null(data, "publish_date", path, errors)
        feed_order = data.get("feed_order")
        if feed_order is not None and not isinstance(feed_order, int):
            errors.append(f"{path}: feed_order must be an integer or null")
        require_enum(data, "copy_readiness", READINESS, path, errors)
        require_enum(data, "creative_readiness", READINESS, path, errors)
        require_enum(data, "accessibility", READINESS, path, errors)
        require_enum(data, "tracking_readiness", READINESS, path, errors)
        require_enum(data, "claims_review", REVIEW, path, errors)
        require_enum(data, "rights_review", REVIEW, path, errors)
        destination = data.get("destination_url")
        if not isinstance(destination, str) or not destination.strip():
            errors.append(f"{path}: destination_url must be an inert URL or an approved URL")
        template = require_string(data, "preview_template", path, errors)
        if template is not None and not re.fullmatch(r"[a-z0-9-]+", template):
            errors.append(f"{path}: preview_template must be a template id")
        asset_keys = data.get("asset_keys")
        if asset_keys is not None and not isinstance(asset_keys, (str, list)):
            errors.append(f"{path}: asset_keys must be a comma-separated string, list, or null")
        stage = data.get("stage")
        if stage in {"Scheduled", "Published", "Measuring", "Complete"}:
            platform_id = data.get("platform_id")
            if not isinstance(platform_id, str) or not platform_id.strip():
                errors.append(f"{path}: {stage} publication requires platform_id")
        if stage in {"Published", "Measuring", "Complete"}:
            readback = data.get("live_readback")
            if not isinstance(readback, str) or not readback.strip():
                errors.append(f"{path}: {stage} publication requires live_readback evidence")

    elif record.kind == "asset":
        require_enum(data, "provider", {"Cloudinary", "Other approved provider"}, path, errors)
        require_string(data, "provider_id", path, errors)
        for field in ("approved_url", "thumbnail_url"):
            value = data.get(field)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                errors.append(f"{path}: {field} must be a URL or null")
        digest = require_string(data, "sha256", path, errors)
        if digest is not None and not SHA256_RE.fullmatch(digest):
            errors.append(f"{path}: sha256 must be a 64-character lowercase hexadecimal digest")
        require_enum(data, "rights_status", REVIEW, path, errors)
        require_enum(data, "consent_status", REVIEW, path, errors)
        if not split_list(data.get("permitted_uses")):
            errors.append(f"{path}: permitted_uses must contain at least one permitted use")
        require_date_or_null(data, "expires_on", path, errors)

    elif record.kind == "experiment":
        require_string(data, "hypothesis", path, errors)
        require_string(data, "campaign_key", path, errors)
        require_string(data, "test_variable", path, errors)
        require_string(data, "success_threshold", path, errors)

    elif record.kind == "evergreen":
        require_string(data, "content_key", path, errors)
        require_enum(data, "reuse_potential", {"High", "Medium", "Low", "No"}, path, errors)
        require_string(data, "next_platform", path, errors)
        require_string(data, "next_format", path, errors)


def validate_templates(errors: list[str]) -> set[str]:
    if not TEMPLATE_MANIFEST.exists():
        errors.append(f"{TEMPLATE_MANIFEST}: missing template manifest")
        return set()
    try:
        payload = json.loads(TEMPLATE_MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{TEMPLATE_MANIFEST}: invalid JSON: {exc}")
        return set()
    templates = payload.get("templates")
    if not isinstance(templates, list) or not templates:
        errors.append(f"{TEMPLATE_MANIFEST}: templates must be a non-empty list")
        return set()
    ids: set[str] = set()
    for item in templates:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            errors.append(f"{TEMPLATE_MANIFEST}: every template must have a string id")
            continue
        template_id = item["id"]
        if template_id in ids:
            errors.append(f"{TEMPLATE_MANIFEST}: duplicate template id {template_id!r}")
        ids.add(template_id)
    return ids


def validate_relationships(records: list[Record], errors: list[str]) -> None:
    by_key: dict[str, Record] = {}
    for record in records:
        key = record.data.get("key")
        if not isinstance(key, str):
            continue
        if key in by_key:
            errors.append(f"duplicate record key {key!r}: {by_key[key].path} and {record.path}")
        else:
            by_key[key] = record

    template_ids = validate_templates(errors)
    for record in records:
        data, path = record.data, record.path
        if record.kind == "content":
            parent = data.get("campaign_key")
            if isinstance(parent, str) and (parent not in by_key or by_key[parent].kind != "campaign"):
                errors.append(f"{path}: campaign_key {parent!r} does not reference a campaign")
        elif record.kind == "publication":
            parent = data.get("content_key")
            if isinstance(parent, str) and (parent not in by_key or by_key[parent].kind != "content"):
                errors.append(f"{path}: content_key {parent!r} does not reference a content concept")
            template = data.get("preview_template")
            if isinstance(template, str) and template not in template_ids:
                errors.append(f"{path}: preview_template {template!r} is absent from the template manifest")
            for asset_key in split_list(data.get("asset_keys")):
                if asset_key not in by_key or by_key[asset_key].kind != "asset":
                    errors.append(f"{path}: asset key {asset_key!r} does not reference an asset record")
        elif record.kind == "experiment":
            parent = data.get("campaign_key")
            if isinstance(parent, str) and parent not in by_key:
                errors.append(f"{path}: campaign_key {parent!r} does not reference a known record")
        elif record.kind == "evergreen":
            parent = data.get("content_key")
            if isinstance(parent, str) and (parent not in by_key or by_key[parent].kind != "content"):
                errors.append(f"{path}: content_key {parent!r} does not reference a content concept")


def load_records(errors: list[str]) -> list[Record]:
    records: list[Record] = []
    for kind, path in record_paths():
        try:
            data, body = parse_frontmatter(path)
        except (OSError, UnicodeError, ValidationError) as exc:
            errors.append(f"{path}: {exc}")
            continue
        record = Record(kind=kind, path=path, data=data, body=body, digest=sha256(path))
        records.append(record)
        validate_common(record, errors)
        validate_record_specific(record, errors)
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable validation output")
    args = parser.parse_args()

    errors: list[str] = []
    records = load_records(errors)
    validate_relationships(records, errors)
    result = {
        "valid": not errors,
        "record_count": len(records),
        "records_by_type": {kind: sum(record.kind == kind for record in records) for kind in EXPECTED_BY_PATH},
        "errors": errors,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif errors:
        print("Social Media OS validation: FAIL")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"Social Media OS validation: PASS ({len(records)} source records)")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
