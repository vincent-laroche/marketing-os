import json
from pathlib import Path
import re
import subprocess
from typing import List, Optional

from .build_manifest import build_records


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "tools" / "email-preview" / "package.json"
LOCK = ROOT / "tools" / "email-preview" / "package-lock.json"
CONFIG = ROOT / "tools" / "email-preview" / "preview-config.json"
REVIEW = ROOT / ".github" / "workflows" / "email-preview-review.yml"
PUBLISH = ROOT / ".github" / "workflows" / "email-preview-publish.yml"


def _mapping(text: str, heading: str, indent: int = 0) -> dict:
    lines = text.splitlines()
    marker = " " * indent + heading + ":"
    for index, line in enumerate(lines):
        if line == marker:
            result = {}
            for candidate in lines[index + 1:]:
                if not candidate.strip() or candidate.lstrip().startswith("#"):
                    continue
                leading = len(candidate) - len(candidate.lstrip())
                if leading <= indent:
                    break
                if leading == indent + 2:
                    match = re.match(r"\s*([A-Za-z0-9_-]+):\s*(.*?)\s*$", candidate)
                    if not match:
                        raise ValueError(f"invalid {heading} mapping entry")
                    result[match.group(1)] = match.group(2)
            return result
        if line == marker + " {}":
            return {}
    raise ValueError(f"missing {heading} mapping")


def _job(text: str, name: str) -> str:
    match = re.search(rf"(?ms)^  {re.escape(name)}:\n(.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)", text)
    if not match:
        raise ValueError(f"missing {name} job")
    return "  " + name + ":\n" + match.group(1)


def workflow_errors(review: str, publish: str) -> List[str]:
    errors: List[str] = []
    try:
        if set(_mapping(review, "on")) != {"pull_request"}:
            errors.append("private review workflow trigger is not exactly pull_request")
        if _mapping(review, "permissions") != {"actions": "read", "contents": "read", "pull-requests": "write", "issues": "write"}:
            errors.append("private review workflow permissions are not exact")
        if set(_mapping(review, "jobs")) != {"render"}:
            errors.append("private review workflow job set is not exact")
        if set(_mapping(publish, "on")) != {"workflow_dispatch"}:
            errors.append("public publication workflow trigger is not exactly workflow_dispatch")
        if _mapping(publish, "permissions"):
            errors.append("public publication workflow must have empty global permissions")
        if set(_mapping(publish, "jobs")) != {"build", "deploy", "ledger"}:
            errors.append("public publication workflow job set is not exact")
        expected_jobs = {
            "build": {"contents": "read", "pull-requests": "read"},
            "deploy": {"pages": "write", "id-token": "write"},
            "ledger": {"contents": "write", "pull-requests": "write", "actions": "read"},
        }
        for name, expected in expected_jobs.items():
            if _mapping(_job(publish, name), "permissions", 4) != expected:
                errors.append(f"public {name} job permissions are not exact")
    except ValueError as error:
        errors.append(str(error))
    approved_actions = {
        "review": {
            "actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09",
            "actions/setup-node@a0853c24544627f65ddf259abe73b1d18a591444",
            "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02",
            "actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093",
            "actions/github-script@ed597411d8f924073f98dfc5c65a23a2325f34cd",
        },
        "publish": {
            "actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09",
            "actions/setup-node@a0853c24544627f65ddf259abe73b1d18a591444",
            "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02",
            "actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093",
            "actions/configure-pages@983d7736d9b0ae728b81ab479565c72886d7745b",
            "actions/upload-pages-artifact@7b1f4a764d45c48632c6b24a0339c27f5614fb0b",
            "actions/deploy-pages@d6db90164ac5ed86f2b6aed7e0febac5b3c0c03e",
        },
    }
    for name, text in (("review", review), ("publish", publish)):
        uses = re.findall(r"\buses:\s*([^\s]+)", text)
        if not uses or not set(uses).issubset(approved_actions[name]) or not approved_actions[name].issubset(set(uses)):
            errors.append(f"{name} workflow action set or pin is not approved")
    if "retention-days: 14" not in review:
        errors.append("private review artifact retention is not 14 days")
    for required in ("preview_public", "git merge-base --is-ancestor", "publication-ledger.json", "read-back"):
        if required not in publish:
            errors.append(f"public publication workflow is missing {required}")
    return errors


def tracked_output_errors(tracked: List[str]) -> List[str]:
    errors = []
    if any(path.startswith("email-previews/") and path != "email-previews/publication-ledger.json" for path in tracked):
        errors.append("generated public preview evidence is tracked")
    if any(path.startswith("tools/email-preview/") and ("node_modules/" in path or path.endswith((".zip", ".tar", ".gz", ".dmg"))) for path in tracked):
        errors.append("preview dependency or browser binaries are tracked")
    return errors


def validate() -> List[str]:
    errors: List[str] = []
    package = json.loads(PACKAGE.read_text(encoding="utf-8"))
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    root_lock = lock.get("packages", {}).get("", {})
    for key in ("dependencies", "devDependencies", "engines"):
        if package.get(key, {}) != root_lock.get(key, {}):
            errors.append(f"package-lock root {key} is stale")
    if package.get("scripts", {}).get("typecheck") != "tsc -p tsconfig.json --noEmit":
        errors.append("preview package lacks the exact typecheck command")
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    if config.get("outputs") != ["rendered.html", "desktop.png", "mobile.png"]:
        errors.append("preview output contract is not exact")
    selections = config.get("selections", [])
    if len(selections) != 53 or len({item.get("email_code") for item in selections}) != 53:
        errors.append("preview configuration does not cover 53 unique Emails")

    review = REVIEW.read_text(encoding="utf-8")
    publish = PUBLISH.read_text(encoding="utf-8")
    errors.extend(workflow_errors(review, publish))

    tracked = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True).stdout.decode().split("\0")
    errors.extend(tracked_output_errors(tracked))
    try:
        build_records()
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"Campaign OS preview publication validation failed: {error}")
    return errors


def main(argv: Optional[List[str]] = None) -> int:
    if argv:
        raise ValueError("validate_repository takes no arguments")
    errors = validate()
    if errors:
        for error in errors:
            print(error)
        return 1
    print("repository preview publication contract: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
