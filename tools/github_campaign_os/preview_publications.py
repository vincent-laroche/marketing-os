import json
from datetime import datetime
from pathlib import Path
import re
import subprocess
from typing import Any, Callable, Dict, Mapping
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = ROOT / "email-previews" / "publication-ledger.json"
ISSUE_REPORT_PATH = ROOT / "github-campaign-os" / "issue-sync-report.json"

ENTRY_KEYS = {
    "email_code", "campaign_key", "source_path", "source_commit_sha", "canonical_issue",
    "canonical_pr", "persona", "states", "output_sha256", "publication_timestamp",
    "canonical_url", "pages_deployment_id", "workflow_run_id", "workflow_attempt",
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
        ["git", "merge-base", "--is-ancestor", sha, "HEAD"],
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
    if set(ledger) != {"schema_version", "publications"} or ledger.get("schema_version") != 1 or not isinstance(ledger.get("publications"), list):
        raise ValueError("invalid publication ledger")
    latest: Dict[str, Mapping[str, Any]] = {}
    identities = set()
    prior_timestamp = ""
    for entry in ledger["publications"]:
        if not isinstance(entry, dict) or set(entry) != ENTRY_KEYS:
            raise ValueError("invalid publication ledger entry")
        code = entry["email_code"]
        outputs = entry["output_sha256"]
        states = entry["states"]
        scalars_valid = (
            isinstance(code, str) and CODE.fullmatch(code)
            and isinstance(entry["campaign_key"], str) and CAMPAIGN.fullmatch(entry["campaign_key"])
            and isinstance(entry["source_path"], str) and SOURCE.fullmatch(entry["source_path"])
            and isinstance(entry["source_commit_sha"], str) and SHA40.fullmatch(entry["source_commit_sha"])
            and type(entry["canonical_issue"]) is int and entry["canonical_issue"] > 0
            and type(entry["canonical_pr"]) is int and entry["canonical_pr"] > 0
            and isinstance(entry["persona"], str) and STATE.fullmatch(entry["persona"])
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
        if not isinstance(states, list) or not states or states != sorted(set(states)) or not all(isinstance(state, str) and STATE.fullmatch(state) for state in states):
            raise ValueError("publication states must be unique and deterministic")
        if not isinstance(outputs, dict) or set(outputs) != OUTPUT_KEYS or not all(isinstance(value, str) and SHA64.fullmatch(value) for value in outputs.values()):
            raise ValueError("publication output digests are invalid")
        if not _exact_canonical_url(entry["canonical_url"], code):
            raise ValueError("canonical URL does not identify the exact approved Email detail page")
        authority = expected.get(code)
        if authority is None:
            raise ValueError("publication Email is not canonical")
        if entry["campaign_key"] != authority["campaign_key"] or entry["source_path"] != authority["source_path"] or entry["canonical_issue"] != authority["canonical_issue"]:
            raise ValueError("publication identity does not match Campaign OS authority")
        identity = (code, entry["source_commit_sha"])
        if identity in identities:
            raise ValueError("duplicate Email and source SHA publication identity")
        if entry["publication_timestamp"] < prior_timestamp:
            raise ValueError("publication ledger is not append-ordered")
        identities.add(identity)
        prior_timestamp = entry["publication_timestamp"]
        commit_validator(entry)
        latest[code] = entry
    return {code: entry["canonical_url"] for code, entry in latest.items()}


def load_preview_urls(expected: Mapping[str, Mapping[str, Any]]) -> Dict[str, str]:
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    return preview_urls(ledger, expected)
