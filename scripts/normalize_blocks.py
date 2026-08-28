#!/usr/bin/env python3
"""Normalise Atelier Zero fragments to the real brand palette + flush-stack geometry.

Two systemic defects in the Atelier Zero output:
  1. Near-miss palette — every colour is a few points off the brand token, so modules
     from different families never quite match (e.g. #181714 vs #15140F Ink).
  2. Outer wrappers carry vertical padding, which puts gaps between stacked cards.
Brand authority: 08_brand/brand-design-system/specs/PLATFORM_EMAIL.md
"""
import re, pathlib, collections

SRC = pathlib.Path(__file__).resolve().parent.parent / "mailerlite-blocks"

PALETTE = {
    "#EDE3CC": "#EFE7D2",  # -> Paper
    "#F6EFD9": "#F7F1DE",  # -> Bone
    "#151411": "#15140F",  # -> Ink
    "#181714": "#15140F",  # -> Ink
    "#3A362F": "#2A2620",  # -> Ink Soft
    "#333533": "#2A2620",  # -> Ink Soft
    "#25221D": "#2A2620",  # -> Ink Soft (secondary text; same lightness, real token)
    "#C7BFAC": "#DDD2B6",  # -> Paper Dark
    "#DDD4BF": "#DDD2B6",  # -> Paper Dark
    "#807B6B": "#5A5448",  # -> Ink Mute
    "#EA6452": "#ED6F5C",  # -> Coral
}

# Flush stacking: kill vertical padding on the outer wrapper cell, keep side gutter.
GEOMETRY = [
    (re.compile(r'padding:7px 16px'), 'padding:0 16px'),
    (re.compile(r'padding:7px 0'),    'padding:0 16px'),
]

changed, counts = 0, collections.Counter()
for p in sorted(SRC.glob("*.html")):
    if p.name.startswith("_"):
        continue
    s = orig = p.read_text(encoding="utf-8")
    for bad, good in PALETTE.items():
        for variant in (bad, bad.lower()):
            if variant in s:
                counts[f"{bad} -> {good}"] += s.count(variant)
                s = s.replace(variant, good)
    for rx, repl in GEOMETRY:
        s, n = rx.subn(repl, s)
        if n:
            counts["geometry: flush stack"] += n
    if s != orig:
        p.write_text(s, encoding="utf-8")
        changed += 1

print(f"files rewritten: {changed}")
for k, v in counts.most_common():
    print(f"  {k:34s} {v}")

leftover = collections.Counter()
for p in SRC.glob("*.html"):
    if p.name.startswith("_"): continue
    for h in re.findall(r'#[0-9A-Fa-f]{6}', p.read_text(encoding="utf-8")):
        leftover[h.upper()] += 1
print("\nremaining palette after normalisation:")
for h, n in leftover.most_common():
    print(f"  {h} {n}")
