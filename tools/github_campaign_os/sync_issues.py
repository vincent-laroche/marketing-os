import argparse
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple

from .gh_client import GitHubClient, GitHubError


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "github-campaign-os" / "manifest.json"
REPORT = ROOT / "github-campaign-os" / "issue-sync-report.json"
REPO = "vincent-laroche/marketing-os"
KEY_RE = re.compile(r"<!-- campaign-os-key: ([^ ]+) -->")


def key_from_body(body: Optional[str]) -> Optional[str]:
    match = KEY_RE.search(body or "")
    return match.group(1) if match else None


def replace_generated(existing: str, desired: str) -> str:
    output = existing
    for start, end in (("<!-- campaign-os-snapshot:start -->", "<!-- campaign-os-snapshot:end -->"), ("<!-- campaign-os-authority:start -->", "<!-- campaign-os-authority:end -->")):
        desired_match = re.search(re.escape(start) + r".*?" + re.escape(end), desired, flags=re.S)
        existing_match = re.search(re.escape(start) + r".*?" + re.escape(end), output, flags=re.S)
        if desired_match and existing_match:
            output = output[:existing_match.start()] + desired_match.group(0) + output[existing_match.end():]
    return output


def plan(manifest: Dict[str, Any], issues: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    by_key: Dict[str, Dict[str, Any]] = {}
    duplicates = []
    for issue in issues:
        key = key_from_body(issue.get("body"))
        if not key:
            continue
        if key in by_key:
            duplicates.append(key)
        by_key[key] = issue
    if duplicates:
        raise GitHubError("duplicate Campaign OS keys: " + ", ".join(sorted(set(duplicates))))
    actions = []
    for record in manifest["records"]:
        current = by_key.get(record["key"])
        if current is None:
            actions.append({"action": "create", "key": record["key"], "record": record})
            continue
        desired_body = replace_generated(current.get("body") or "", record["issue_body"])
        current_labels = {item["name"] if isinstance(item, dict) else item for item in current.get("labels", [])}
        desired_labels = sorted(current_labels | set(record["labels"]))
        if current.get("title") != record["title"] or current.get("body") != desired_body or current_labels != set(desired_labels):
            actions.append({"action": "update", "key": record["key"], "number": current["number"], "record": record, "body": desired_body, "labels": desired_labels})
    return actions, by_key


def ensure_labels(client: GitHubClient, labels: List[str]) -> None:
    existing = {item["name"] for item in client.paginate(f"/repos/{REPO}/labels")}
    colors = {"area:": "1D76DB", "asset:": "8250DF", "flag:": "D93F0B", "risk:": "B60205"}
    for label in sorted(set(labels) - existing):
        color = next((value for prefix, value in colors.items() if label.startswith(prefix)), "0E8A16")
        client.request("POST", f"/repos/{REPO}/labels", {"name": label, "color": color, "description": "Email Marketing Campaign OS"})


def run(apply: bool, write_report: bool = True) -> Dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    client = GitHubClient()
    repository = client.request("GET", f"/repos/{REPO}")
    if repository.get("private"):
        raise GitHubError("Campaign OS repository must be public")
    issues = [item for item in client.paginate(f"/repos/{REPO}/issues?state=all") if "pull_request" not in item]
    actions, by_key = plan(manifest, issues)
    if apply:
        ensure_labels(client, [label for record in manifest["records"] for label in record["labels"]])
        for action in actions:
            record = action["record"]
            payload = {"title": record["title"], "body": record["issue_body"], "labels": record["labels"]}
            if action["action"] == "create":
                created = client.request("POST", f"/repos/{REPO}/issues", payload)
                by_key[record["key"]] = created
            else:
                payload["body"] = action["body"]
                payload["labels"] = action["labels"]
                updated = client.request("PATCH", f"/repos/{REPO}/issues/{action['number']}", payload)
                by_key[record["key"]] = updated
        # Native sub-issue relationships are added only after every parent exists.
        for record in manifest["records"]:
            if not record.get("parent_key"):
                continue
            parent = by_key[record["parent_key"]]
            child = by_key[record["key"]]
            try:
                client.request("POST", f"/repos/{REPO}/issues/{parent['number']}/sub_issues", {"sub_issue_id": child["id"]})
            except GitHubError as exc:
                if "already" not in str(exc).lower() and "422" not in str(exc):
                    raise
    current = [item for item in client.paginate(f"/repos/{REPO}/issues?state=all") if "pull_request" not in item] if apply else issues
    current_by_key = {key_from_body(item.get("body")): item for item in current if key_from_body(item.get("body"))}
    report = {
        "repository": REPO, "private": False, "mode": "apply" if apply else "dry-run",
        "manifest_records": len(manifest["records"]), "remote_campaign_os_issues": len(current_by_key),
        "planned_actions": [{"action": item["action"], "key": item["key"]} for item in actions],
        "issues": {key: item["number"] for key, item in sorted(current_by_key.items())},
    }
    if write_report:
        REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Synchronize canonical Campaign OS Issues")
    parser.add_argument("--apply", action="store_true", help="Apply planned changes; default is dry-run")
    args = parser.parse_args(argv)
    report = run(args.apply)
    print(json.dumps({"mode": report["mode"], "planned_actions": len(report["planned_actions"]), "remote_campaign_os_issues": report["remote_campaign_os_issues"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
