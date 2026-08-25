#!/usr/bin/env python3
"""Build an inert Instagram feed planning grid from approved source metadata."""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "tools" / "social_os" / "validate_social_os.py"

CSS = """
:root { color-scheme: light; font-family: system-ui, -apple-system, sans-serif; }
body { margin: 0; background: #f4f1ea; color: #151411; }
main { max-width: 1120px; margin: 0 auto; padding: 28px 16px 56px; }
header { display: flex; justify-content: space-between; align-items: end; gap: 16px; margin-bottom: 20px; }
.grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
.tile { aspect-ratio: 1 / 1; background: #f6efd9; border: 1px solid #c7bfac; display: flex; flex-direction: column; justify-content: space-between; padding: 14px; box-sizing: border-box; }
.tile small { color: #5a5448; }
.tile strong { font-size: 16px; }
.empty { padding: 40px; background: #fffdf8; border: 1px solid #c7bfac; }
.notice { color: #5a5448; font-size: 13px; }
@media (max-width: 640px) { .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } header { display: block; } }
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="output HTML path")
    args = parser.parse_args()

    subprocess.run([sys.executable, str(VALIDATOR)], check=True)
    validator = load_validator()
    records = [
        record
        for record in validator.load_records([])
        if record.kind == "publication"
        and record.data.get("platform") == "Instagram"
        and record.data.get("format") != "Story"
        and isinstance(record.data.get("feed_order"), int)
    ]
    records.sort(key=lambda record: record.data["feed_order"], reverse=True)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    tiles = []
    for record in records:
        data = record.data
        tiles.append(
            """<article class=\"tile\"><small>#{order} · {format}</small><strong>{title}</strong><small>{pillar}<br>{stage} · {date}</small></article>""".format(
                order=html.escape(str(data.get("feed_order"))),
                format=html.escape(str(data.get("format", ""))),
                title=html.escape(str(data.get("title", "Untitled publication"))),
                pillar=html.escape(str(data.get("content_pillar", ""))),
                stage=html.escape(str(data.get("stage", ""))),
                date=html.escape(str(data.get("publish_date") or "Not scheduled")),
            )
        )
    content = "\n".join(tiles) if tiles else '<div class="empty">No Instagram feed publications have a numeric feed order yet.</div>'
    output = f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>Instagram Feed Planner</title><style>{CSS}</style></head>
<body><main><header><div><p class=\"notice\">INERT PLANNING PREVIEW · This artifact does not publish or schedule content.</p><h1>Instagram Feed Planner</h1></div><p class=\"notice\">{len(records)} ordered publications · generated {html.escape(generated_at)}</p></header><section class=\"grid\">{content}</section></main></body></html>
"""
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    provenance = {
        "artifact_type": "instagram-feed-grid",
        "generated_at": generated_at,
        "publication_count": len(records),
        "source_paths": [record.path.relative_to(ROOT).as_posix() for record in records],
        "publishing": "disabled",
    }
    args.output.with_suffix(".provenance.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Instagram feed grid: PASS ({len(records)} ordered publications)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
