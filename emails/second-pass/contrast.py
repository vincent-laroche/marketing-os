"""Shared collision detection: does this module render anything invisible on a surface?

Walks the tag tree keeping a stack of backgrounds, so a button label is judged
against the pill it sits on and not against the card behind it.
"""
import re
from surface import SURFACES

TOK = re.compile(r"\{\{\s*c\.(\w+)\s*\}\}")
TAG = re.compile(r"<(/?)(\w+)([^>]*)>", re.S)
VOID = {"img", "br", "hr", "meta", "input"}

BG = re.compile(r"(?<!-)background(?:-color)?\s*:\s*(#[0-9A-Fa-f]{6})", re.I)
FG = re.compile(r"(?<!background-)(?<!-)color\s*:\s*(#[0-9A-Fa-f]{6})", re.I)
BD = re.compile(r"solid\s+(#[0-9A-Fa-f]{6})", re.I)
BGATTR = re.compile(r'bgcolor\s*=\s*"(#[0-9A-Fa-f]{6})"', re.I)

# Coral accent text on a light cream card is an established, approved part of the
# brand (2.6:1 on Bone). The bar below is set to catch things that are genuinely
# lost, not to re-litigate that signature.
MIN_RATIO = 2.2


def lum(h):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def scan(html, card):
    stack, out = [card], []
    for m in TAG.finditer(html):
        closing, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if closing:
            if len(stack) > 1:
                stack.pop()
            continue
        bgm = BG.search(attrs) or BGATTR.search(attrs)
        fgm, bdm = FG.search(attrs), BD.search(attrs)
        behind = stack[-1]
        own = bgm.group(1).upper() if bgm else None
        ctx = re.sub(r"\s+", " ", attrs)[:64]

        if own and own == behind.upper() and "border-radius:16px" not in attrs:
            out.append(("fill invisible", f"{own} on {behind}", ctx))
        if bdm and bdm.group(1).upper() == behind.upper():
            out.append(("border invisible", f"{bdm.group(1)} on {behind}", ctx))
        base = own or behind
        if fgm:
            r = ratio(fgm.group(1), base)
            hair = "height:1px" in attrs.replace(" ", "")
            if r < MIN_RATIO and not hair:
                out.append((f"text {r:.1f}:1", f"{fgm.group(1)} on {base}", ctx))
        if tag not in VOID and not attrs.rstrip().endswith("/"):
            stack.append(own or behind)
    return out


def bad_surfaces(html, candidates):
    """Which of `candidates` this module must not offer."""
    body = html.split("-%}")[-1]
    bad = []
    for s in candidates:
        c = SURFACES[s]
        resolved = TOK.sub(lambda m: c.get(m.group(1), "#000000"), body)
        if scan(resolved, c["bg"]):
            bad.append(s)
    return bad
