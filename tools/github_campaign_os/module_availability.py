"""Resolve canonical `Missing Modules` labels against approved module artifacts.

`Email Reference File/` is the source of truth. A label counts as available only
when an approved module trio (`module.html` + `fields.json` + `meta.json`) exists
for it in both the light and the dark variant. Nothing here invents, renames or
composes a module; it only records which approved artifact answers which label.

Resolution is attempted in three ordered modes, and a label that survives all
three stays unresolved so the dependency remains visible:

1. `exact-label`     — the label equals an artifact's declared `meta.json` label.
2. `folded-label`    — the label matches once punctuation and case are folded
                       away (`Grid - Collections 4` vs `Grid - Collections (4)`).
3. `documented-alias`— one of the two renames recorded in ALIASES below.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .model import fingerprint

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "Email Reference File"
MODULES = REFERENCE / "emails_modules_hubspot versionr"
CSV_PATH = next(REFERENCE.glob("emails_master*_all.csv"))
VARIANTS = ("light", "dark")

# Labels the emails database uses that the approved artifact records under a
# different name. Both are renames of an existing approved module, not new
# modules, and neither may be extended without authoritative evidence.
ALIASES = {
    "Review stars": "Signal - Review stars",
    "Signal - Countdown": "Signal - Offer deadline",
}


def fold(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", label.lower())


def artifacts() -> Dict[str, Dict[str, str]]:
    """Approved module artifacts keyed by declared label, then by variant."""
    found: Dict[str, Dict[str, str]] = {}
    for meta_path in sorted(MODULES.rglob("meta.json")):
        directory = meta_path.parent
        if not (directory / "module.html").exists() or not (directory / "fields.json").exists():
            continue
        declared = json.loads(meta_path.read_text(encoding="utf-8")).get("label", "").strip()
        match = re.match(r"^(?P<label>.*?)\s*-\s*(?P<variant>Light|Dark)$", declared)
        if not match:
            continue
        found.setdefault(match.group("label").strip(), {})[match.group("variant").lower()] = directory.name
    return found


def complete(found: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    """Only artifacts approved in both variants may satisfy a requirement."""
    return {label: dirs for label, dirs in found.items() if set(dirs) == set(VARIANTS)}


def resolve(label: str, available: Dict[str, Dict[str, str]], folded: Dict[str, str]) -> Tuple[Optional[str], Optional[str]]:
    if label in available:
        return label, "exact-label"
    canonical = folded.get(fold(label))
    if canonical:
        return canonical, "folded-label"
    alias = ALIASES.get(label)
    if alias and alias in available:
        return alias, "documented-alias"
    return None, None


def requirements(raw: str) -> List[str]:
    """Split a `Missing Modules` cell into individual labels."""
    return [part.strip() for part in re.split(r"[,;|\n]", raw) if part.strip()]


def build() -> Dict[str, object]:
    import csv

    found = artifacts()
    available = complete(found)
    folded: Dict[str, str] = {}
    for label in available:
        key = fold(label)
        if key in folded:
            raise ValueError(f"module labels {folded[key]!r} and {label!r} fold to the same key")
        folded[key] = label

    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    emails = []
    for row in rows:
        raw = (row.get("Missing Modules") or "").strip()
        if not raw:
            continue
        code = row["Email name"].split("·")[0].strip()
        resolved, unresolved = [], []
        for label in requirements(raw):
            canonical, mode = resolve(label, available, folded)
            if canonical is None:
                unresolved.append(label)
            else:
                resolved.append({"required": label, "artifact": canonical, "mode": mode})
        emails.append({"email_code": code, "resolved": resolved, "unresolved": unresolved})

    inventory = {
        label: {
            "variants": {variant: dirs[variant] for variant in VARIANTS},
            "fingerprint": fingerprint(
                {variant: (MODULES / dirs[variant] / "module.html").read_text(encoding="utf-8") for variant in VARIANTS}
            ),
        }
        for label, dirs in sorted(available.items())
    }
    return {
        "schema_version": 1,
        "authority": str(CSV_PATH.relative_to(ROOT)),
        "artifact_root": str(MODULES.relative_to(ROOT)),
        "aliases": ALIASES,
        "artifacts": inventory,
        "emails": emails,
    }
