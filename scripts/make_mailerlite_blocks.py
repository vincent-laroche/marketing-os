#!/usr/bin/env python3
"""Atelier Zero full-document previews -> MailerLite Code-block fragments.

Three transforms, all from the pristine source folder so errors never accumulate:
  1. Fragment    - Code block takes body inner HTML only, no <!doctype>/<head>/<body>.
  2. Palette     - Atelier Zero ships a near-miss palette; map every colour to its real
                   brand token. ROLE MATTERS: #F6EFD9 is the light CARD SURFACE (50 uses on
                   .az-module-shell) -> Paper. #EDE3CC is TEXT ON DARK CARDS (never a
                   surface) -> Bone. Getting these two backwards makes light cards drift.
  3. Geometry    - Outer wrapper vertical padding creates gaps; zero it so cards stack flush.
Brand authority: 08_brand/brand-design-system/specs/PLATFORM_EMAIL.md
"""
import re, json, pathlib, collections

SRC = pathlib.Path("/Users/vMac/04_marketing/email_marketing/Email Reference File/Atelier Zero — Resolved HTML Module Previews (102)")
OUT = pathlib.Path(__file__).resolve().parent.parent / "mailerlite-blocks"
FORBIDDEN = ("script", "embed", "frame", "iframe", "form", "input", "object", "textarea")

PALETTE = {
    "#F6EFD9": "#EFE7D2",  # light CARD SURFACE -> Paper
    "#EDE3CC": "#F7F1DE",  # text on dark cards -> Bone
    "#151411": "#15140F",  # -> Ink
    "#181714": "#15140F",  # -> Ink
    "#25221D": "#2A2620",  # -> Ink Soft
    "#3A362F": "#2A2620",  # -> Ink Soft
    "#333533": "#2A2620",  # -> Ink Soft
    "#C7BFAC": "#DDD2B6",  # -> Paper Dark
    "#DDD4BF": "#DDD2B6",  # -> Paper Dark
    "#807B6B": "#5A5448",  # -> Ink Mute
    "#EA6452": "#ED6F5C",  # -> Coral
}
GEOMETRY = [(r'padding:7px 16px', 'padding:0 16px'), (r'padding:7px 0', 'padding:0 16px')]

OUT.mkdir(exist_ok=True)
report, counts = [], collections.Counter()

for f in sorted(SRC.glob("*.html")):
    raw = f.read_text(encoding="utf-8")
    m = re.search(r"<body[^>]*>(.*)</body>", raw, re.S | re.I)
    frag = (m.group(1) if m else raw).strip()
    frag = re.sub(r"</?(?:html|head|body)[^>]*>", "", frag, flags=re.I).strip()

    for bad, good in PALETTE.items():
        for v in (bad, bad.lower()):
            if v in frag:
                counts[f"{bad} -> {good}"] += frag.count(v)
                frag = frag.replace(v, good)
    for rx, repl in GEOMETRY:
        frag, n = re.subn(rx, repl, frag)
        counts["geometry: flush stack"] += n

    hits = sorted({t for t in FORBIDDEN if re.search(rf"<\s*{t}\b", frag, re.I)})
    name = f.name.replace(".module.html", "")
    (OUT / f"{name}.html").write_text(frag + "\n", encoding="utf-8")
    report.append({"module": name, "bytes": len(frag), "forbidden": hits})

(OUT / "_index.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
print(f"converted: {len(report)}   forbidden-tag violations: {sum(1 for r in report if r['forbidden'])}")
for k, v in counts.most_common():
    print(f"  {k:34s} {v}")

surf = collections.Counter()
for p in OUT.glob("*.html"):
    if p.name.startswith("_"): continue
    for c in re.findall(r'az-module-shell[^>]*?background-color:(#[0-9A-Fa-f]{6})', p.read_text(encoding="utf-8")):
        surf[c.upper()] += 1
print("\ncard surfaces in use (should be Paper #EFE7D2 / Ink #15140F only):")
for c, n in surf.most_common():
    print(f"  {c} {n}")
