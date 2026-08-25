#!/usr/bin/env python3
"""Build static, inert review previews for Social Media OS publications."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOCIAL_ROOT = ROOT / "social-media"
VALIDATOR = ROOT / "tools" / "social_os" / "validate_social_os.py"
MANIFEST_BUILDER = ROOT / "tools" / "social_os" / "build_manifest.py"

CSS = """
:root { color-scheme: light; font-family: system-ui, -apple-system, sans-serif; }
body { margin: 0; background: #f4f1ea; color: #151411; }
main { max-width: 900px; margin: 0 auto; padding: 32px 20px 64px; }
.card { background: #fffdf8; border: 1px solid #c7bfac; border-radius: 12px; padding: 24px; box-shadow: 0 6px 24px #15141114; }
.meta { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin: 20px 0; }
.meta div { background: #f6efd9; border-radius: 8px; padding: 12px; }
.meta small { display: block; color: #5a5448; font-size: 11px; text-transform: uppercase; letter-spacing: .08em; }
.meta strong { display: block; margin-top: 5px; }
.preview-copy { white-space: pre-wrap; border-left: 4px solid #ea6452; padding: 12px 16px; background: #f6efd9; }
.notice { color: #5a5448; font-size: 13px; }
code { overflow-wrap: anywhere; }
"""


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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(record, output_dir: Path, generated_at: str) -> Path:
    data = record.data
    title = html.escape(str(data.get("title", "Untitled publication")))
    platform = html.escape(str(data.get("platform", "Unknown")))
    stage = html.escape(str(data.get("stage", "Unknown")))
    body = html.escape(record.body.strip())
    source_path = html.escape(record.path.relative_to(ROOT).as_posix())
    source_digest = record.digest
    destination = html.escape(str(data.get("destination_url", "#")))
    # Deliberately render destination as inert text; preview artifacts must not navigate to it.
    output = f"""<!doctype html>
<html lang=\"en\">
<head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>{title} — {platform}</title><style>{CSS}</style></head>
<body><main><section class=\"card\">
<p class=\"notice\">INERT REVIEW PREVIEW · This artifact is not scheduled or published.</p>
<h1>{title}</h1>
<div class=\"meta\">
<div><small>Platform</small><strong>{platform}</strong></div>
<div><small>Stage</small><strong>{stage}</strong></div>
<div><small>Format</small><strong>{html.escape(str(data.get('format', '')))}</strong></div>
<div><small>Publish date</small><strong>{html.escape(str(data.get('publish_date') or 'Not scheduled'))}</strong></div>
</div>
<h2>Publication source</h2>
<div class=\"preview-copy\">{body or 'No publication body has been authored yet.'}</div>
<h2>Review metadata</h2>
<ul>
<li>Publication key: <code>{html.escape(str(data.get('key', '')))}</code></li>
<li>Content concept: <code>{html.escape(str(data.get('content_key', '')))}</code></li>
<li>Destination (inert text only): <code>{destination}</code></li>
<li>Source: <code>{source_path}</code></li>
<li>Source SHA-256: <code>{source_digest}</code></li>
<li>Generated at: <code>{html.escape(generated_at)}</code></li>
</ul>
<p class=\"notice\">A merge, approval, preview, or date does not constitute scheduling or publication. Live evidence must be recorded separately after an explicitly approved platform operation.</p>
</section></main></body></html>
"""
    filename = f"{data['key'].replace(':', '__')}.html"
    path = output_dir / filename
    path.write_text(output, encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="directory for generated previews")
    args = parser.parse_args()

    subprocess.run([sys.executable, str(VALIDATOR)], check=True)
    validator = load_validator()
    records = [record for record in validator.load_records([]) if record.kind == "publication"]
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    args.output.mkdir(parents=True, exist_ok=True)
    outputs = [render(record, args.output, generated_at) for record in records]
    index = {
        "artifact_type": "social-publication-previews",
        "generated_at": generated_at,
        "publication_count": len(outputs),
        "files": [path.name for path in outputs],
        "source_digests": {path.name: digest(path) for path in outputs},
        "publishing": "disabled",
    }
    (args.output / "provenance.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Social publication previews: PASS ({len(outputs)} previews)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
