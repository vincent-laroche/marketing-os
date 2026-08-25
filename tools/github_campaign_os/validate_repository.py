import json
from pathlib import Path
import subprocess
from typing import List, Optional

from .build_manifest import build_records


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "tools" / "email-preview" / "package.json"
LOCK = ROOT / "tools" / "email-preview" / "package-lock.json"
CONFIG = ROOT / "tools" / "email-preview" / "preview-config.json"
REVIEW = ROOT / ".github" / "workflows" / "email-preview-review.yml"
PUBLISH = ROOT / ".github" / "workflows" / "email-preview-publish.yml"


def validate() -> List[str]:
    errors: List[str] = []
    package = json.loads(PACKAGE.read_text(encoding="utf-8"))
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    root_lock = lock.get("packages", {}).get("", {})
    for key in ("dependencies", "devDependencies", "engines"):
        if package.get(key, {}) != root_lock.get(key, {}):
            errors.append(f"package-lock root {key} is stale")
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    if config.get("outputs") != ["rendered.html", "desktop.png", "mobile.png"]:
        errors.append("preview output contract is not exact")
    selections = config.get("selections", [])
    if len(selections) != 53 or len({item.get("email_code") for item in selections}) != 53:
        errors.append("preview configuration does not cover 53 unique Emails")

    review = REVIEW.read_text(encoding="utf-8")
    publish = PUBLISH.read_text(encoding="utf-8")
    if "workflow_dispatch:" in review or "pages: write" in review or "retention-days: 14" not in review:
        errors.append("private review workflow has unsafe trigger, permission, or retention policy")
    if "workflow_dispatch:" not in publish or any(trigger in publish for trigger in ("pull_request:", "push:", "schedule:")):
        errors.append("public publication workflow is not manual-only")
    for required in ("preview_public", "git merge-base --is-ancestor", "pages: write", "id-token: write", "publication-ledger.json", "read-back"):
        if required not in publish:
            errors.append(f"public publication workflow is missing {required}")

    tracked = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True).stdout.decode().split("\0")
    leaked = [path for path in tracked if path.startswith("email-previews/") and path != "email-previews/publication-ledger.json"]
    if leaked:
        errors.append("generated public preview evidence is tracked")
    binaries = [path for path in tracked if path.startswith("tools/email-preview/") and ("node_modules/" in path or path.endswith((".zip", ".tar", ".gz", ".dmg")))]
    if binaries:
        errors.append("preview dependency or browser binaries are tracked")
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
