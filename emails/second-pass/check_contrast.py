"""Catch surfaces where a tokenised module renders something invisible.

The transform is mechanical, so the failure mode is not a syntax error — it is an
element whose fill or text now equals whatever sits behind it. Walks the tag tree
keeping a stack of backgrounds, so a button label is judged against its pill and
not against the card.
"""
import json, glob, os, re
from surface import SURFACES

STAGE = "staging-rollout/email_modules"
TOK = re.compile(r"\{\{\s*c\.(\w+)\s*\}\}")
TAG = re.compile(r"<(/?)(\w+)([^>]*)>", re.S)
VOID = {"img", "br", "hr", "meta", "input"}

BG = re.compile(r"(?<!-)background(?:-color)?\s*:\s*(#[0-9A-Fa-f]{6})", re.I)
FG = re.compile(r"(?<!background-)(?<!-)color\s*:\s*(#[0-9A-Fa-f]{6})", re.I)
BD = re.compile(r"solid\s+(#[0-9A-Fa-f]{6})", re.I)
BGATTR = re.compile(r'bgcolor\s*=\s*"(#[0-9A-Fa-f]{6})"', re.I)


def lum(h):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def scan(html, card):
    """Yield (kind, detail, context) for anything that renders invisibly."""
    stack = [card]
    out = []
    for m in TAG.finditer(html):
        closing, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if closing:
            if len(stack) > 1:
                stack.pop()
            continue
        bgm = BG.search(attrs) or BGATTR.search(attrs)
        fgm = FG.search(attrs)
        bdm = BD.search(attrs)
        behind = stack[-1]
        own = bgm.group(1).upper() if bgm else None
        ctx = re.sub(r"\s+", " ", attrs)[:64]

        # a filled block that matches whatever is behind it
        if own and own == behind.upper() and "border-radius:16px" not in attrs:
            out.append(("fill invisible", f"{own} on {behind}", ctx))
        if bdm and bdm.group(1).upper() == behind.upper():
            out.append(("border invisible", f"{bdm.group(1)} on {behind}", ctx))
        # text judged against its OWN fill if it has one, else the nearest ancestor
        surface_behind = own or behind
        if fgm:
            r = ratio(fgm.group(1), surface_behind)
            hair = "height:1px" in attrs.replace(" ", "")
            if r < 2.0 and not hair:
                out.append((f"text {r:.1f}:1", f"{fgm.group(1)} on {surface_behind}", ctx))
        if tag not in VOID and not attrs.rstrip().endswith("/"):
            stack.append(own or behind)
    return out


issues = []
for d in sorted(glob.glob(STAGE + "/**/*.module", recursive=True)):
    name = d.replace(STAGE + "/", "")
    if name.endswith("_dark.module"):
        continue                      # byte-identical html to its light twin
    html = open(os.path.join(d, "module.html")).read()
    offered = [c[0] for c in json.load(open(os.path.join(d, "fields.json")))[0]["choices"]]
    body = html.split("-%}")[-1]
    for surf in offered:
        c = SURFACES[surf]
        resolved = TOK.sub(lambda m: c.get(m.group(1), "#000000"), body)
        for kind, detail, ctx in scan(resolved, c["bg"]):
            issues.append((name, surf, kind, detail, ctx))

print(f"{len(issues)} real collisions\n")
for n, s, kind, detail, ctx in issues:
    print(f"{n:40s} {s:11s} {kind:18s} {detail:22s} {ctx[:50]}")
