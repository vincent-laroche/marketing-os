import json
from datetime import datetime
from pathlib import Path
import re
import subprocess
from typing import Any, Callable, Dict, Mapping
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = ROOT / "email-previews" / "publication-ledger.json"
LEDGER_REPO_PATH = "email-previews/publication-ledger.json"
ISSUE_REPORT_PATH = ROOT / "github-campaign-os" / "issue-sync-report.json"

PUBLISHED_KEYS = {
    "event",
    "email_code", "campaign_key", "source_path", "source_commit_sha", "canonical_issue",
    "canonical_pr", "persona", "states", "output_sha256", "publication_timestamp",
    "canonical_url", "pages_deployment_id", "workflow_run_id", "workflow_attempt",
}
WITHDRAWN_KEYS = {
    "event", "email_code", "campaign_key", "source_path", "source_commit_sha",
    "canonical_issue", "canonical_pr", "publication_timestamp", "former_canonical_url",
    "withdrawn_source_commit_sha", "withdrawn_pages_deployment_id",
    "pages_deployment_id", "workflow_run_id", "workflow_attempt", "reason",
}
OUTPUT_KEYS = {"rendered.html", "desktop.png", "mobile.png"}
CODE = re.compile(r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")
CAMPAIGN = re.compile(r"^campaign:[A-Za-z0-9_-]+$")
SOURCE = re.compile(r"^shopify-messaging/emails/[0-9]+-[a-z0-9-]+\.html$")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")
TOKEN = re.compile(r"^[A-Za-z0-9._-]+$")
STATE = re.compile(r"^[a-z0-9-]+$")


def _exact_canonical_url(raw: str, email_code: str) -> bool:
    try:
        parsed = urlsplit(raw)
    except (TypeError, ValueError):
        return False
    if parsed.scheme != "https" or parsed.username or parsed.password or parsed.port or parsed.query or parsed.fragment:
        return False
    expected = {
        ("vincent-laroche.github.io", f"/email-marketing-ops/{email_code}/detail.html"),
        ("email-preview.hairsolutions.co", f"/{email_code}/detail.html"),
    }
    return (parsed.hostname, parsed.path) in expected


def _verify_commit(entry: Mapping[str, Any]) -> None:
    sha = entry["source_commit_sha"]
    source = entry["source_path"]
    commands = (
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        ["git", "merge-base", "--is-ancestor", sha, "origin/main"],
        ["git", "cat-file", "-e", f"{sha}:{source}"],
    )
    for command in commands:
        completed = subprocess.run(command, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        if completed.returncode != 0:
            raise ValueError("publication source revision is not a committed ancestor with the exact Email source")


def preview_urls(
    ledger: Mapping[str, Any],
    expected: Mapping[str, Mapping[str, Any]],
    commit_validator: Callable[[Mapping[str, Any]], None] = _verify_commit,
) -> Dict[str, str]:
    if set(ledger) != {"schema_version", "events"} or ledger.get("schema_version") != 2 or not isinstance(ledger.get("events"), list):
        raise ValueError("invalid publication ledger")
    latest: Dict[str, Mapping[str, Any]] = {}
    identities = set()
    prior_timestamp = None
    for entry in ledger["events"]:
        if not isinstance(entry, dict) or entry.get("event") not in {"published", "withdrawn"}:
            raise ValueError("invalid publication ledger entry")
        expected_keys = PUBLISHED_KEYS if entry["event"] == "published" else WITHDRAWN_KEYS
        if set(entry) != expected_keys:
            raise ValueError("invalid publication ledger entry")
        code = entry["email_code"]
        scalars_valid = (
            isinstance(code, str) and CODE.fullmatch(code)
            and isinstance(entry["campaign_key"], str) and CAMPAIGN.fullmatch(entry["campaign_key"])
            and isinstance(entry["source_path"], str) and SOURCE.fullmatch(entry["source_path"])
            and isinstance(entry["source_commit_sha"], str) and SHA40.fullmatch(entry["source_commit_sha"])
            and type(entry["canonical_issue"]) is int and entry["canonical_issue"] > 0
            and type(entry["canonical_pr"]) is int and entry["canonical_pr"] > 0
            and isinstance(entry["publication_timestamp"], str) and entry["publication_timestamp"].endswith("Z")
            and all(isinstance(entry[key], str) and TOKEN.fullmatch(entry[key]) for key in ("pages_deployment_id", "workflow_run_id", "workflow_attempt"))
        )
        if not scalars_valid:
            raise ValueError("invalid publication ledger entry")
        try:
            timestamp = datetime.fromisoformat(entry["publication_timestamp"].replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError("publication timestamp is invalid") from error
        if timestamp.tzinfo is None:
            raise ValueError("publication timestamp must include a timezone")
        authority = expected.get(code)
        if authority is None:
            raise ValueError("publication Email is not canonical")
        if entry["campaign_key"] != authority["campaign_key"] or entry["source_path"] != authority["source_path"] or entry["canonical_issue"] != authority["canonical_issue"]:
            raise ValueError("publication identity does not match Campaign OS authority")
        identity = (entry["event"], code, entry["source_commit_sha"])
        if identity in identities:
            raise ValueError("duplicate Email and source SHA publication identity")
        if prior_timestamp is not None and timestamp < prior_timestamp:
            raise ValueError("publication ledger is not append-ordered")
        identities.add(identity)
        prior_timestamp = timestamp
        commit_validator(entry)
        if entry["event"] == "published":
            outputs = entry["output_sha256"]
            states = entry["states"]
            if not isinstance(entry["persona"], str) or not STATE.fullmatch(entry["persona"]):
                raise ValueError("publication persona is invalid")
            if not isinstance(states, list) or not states or states != sorted(set(states)) or not all(isinstance(state, str) and STATE.fullmatch(state) for state in states):
                raise ValueError("publication states must be unique and deterministic")
            if not isinstance(outputs, dict) or set(outputs) != OUTPUT_KEYS or not all(isinstance(value, str) and SHA64.fullmatch(value) for value in outputs.values()):
                raise ValueError("publication output digests are invalid")
            if not _exact_canonical_url(entry["canonical_url"], code):
                raise ValueError("canonical URL does not identify the exact approved Email detail page")
            latest[code] = entry
        else:
            active = latest.get(code)
            if (
                active is None
                or entry["reason"] not in {"owner-requested", "safety-rollback"}
                or not isinstance(entry["withdrawn_source_commit_sha"], str)
                or not SHA40.fullmatch(entry["withdrawn_source_commit_sha"])
                or not isinstance(entry["withdrawn_pages_deployment_id"], str)
                or not TOKEN.fullmatch(entry["withdrawn_pages_deployment_id"])
                or entry["former_canonical_url"] != active["canonical_url"]
                or entry["withdrawn_source_commit_sha"] != active["source_commit_sha"]
                or entry["withdrawn_pages_deployment_id"] != active["pages_deployment_id"]
            ):
                raise ValueError("withdrawal requires the exact active public Email")
            latest.pop(code)
    return {code: entry["canonical_url"] for code, entry in latest.items()}


def load_preview_urls(expected: Mapping[str, Mapping[str, Any]]) -> Dict[str, str]:
    working = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    try:
        merged_bytes = subprocess.run(
            ["git", "show", f"origin/main:{LEDGER_REPO_PATH}"], cwd=ROOT, check=True, capture_output=True,
        ).stdout
        merged = json.loads(merged_bytes.decode("utf-8"))
    except (subprocess.CalledProcessError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("canonical merged-main publication ledger is unavailable") from error
    return merged_preview_urls(working, merged, expected)


def merged_preview_urls(
    working: Mapping[str, Any],
    merged: Mapping[str, Any],
    expected: Mapping[str, Mapping[str, Any]],
    commit_validator: Callable[[Mapping[str, Any]], None] = _verify_commit,
) -> Dict[str, str]:
    preview_urls(working, expected, commit_validator)
    # Schema v2 is introduced by the same pull request that first needs to prove
    # its manifest against merged main. The only accepted migration baseline is
    # the exact, empty v1 ledger; a populated or otherwise shaped v1 document is
    # rejected rather than silently translated.
    if merged == {"schema_version": 1, "publications": []}:
        merged = {"schema_version": 2, "events": []}
    merged_urls = preview_urls(merged, expected, commit_validator)
    merged_events = merged["events"]
    if working["events"][:len(merged_events)] != merged_events:
        raise ValueError("publication ledger rewrites merged append-only history")
    return merged_urls
