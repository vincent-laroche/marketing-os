#!/usr/bin/env python3
"""Measure how a text run actually breaks in an email card, using real font metrics.

Email clients have no `text-wrap: balance`, so line balance has to be designed in.
This measures greedy wrapping (what every client does) at the true content width and
reports the ragged-ness, so a break decision is made from numbers, not from squinting.

  python3 scripts/measure_lines.py --text "..." --size 15 --width 500
  python3 scripts/measure_lines.py --audit mailerlite-blocks/wb1_question_list.html
"""
import argparse, pathlib, re, sys
from PIL import ImageFont

FONTS = {
    ("sans", False): "/System/Library/Fonts/Supplemental/Arial.ttf",
    ("sans", True):  "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ("mono", False): "/System/Library/Fonts/Supplemental/Courier New.ttf",
    ("mono", True):  "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
    ("serif", True): "/System/Library/Fonts/Supplemental/Georgia Bold Italic.ttf",
}
CARD, PAD = 568, 34
CONTENT = CARD - PAD * 2          # 500px — the standard card measure


def load(family="sans", bold=False, size=15):
    path = FONTS.get((family, bold)) or FONTS[("sans", False)]
    if not pathlib.Path(path).exists():
        sys.exit(f"missing font: {path}")
    return ImageFont.truetype(path, size)


def w(font, s, tracking=0.0):
    """Width in px, including letter-spacing which PIL does not model."""
    return font.getlength(s) + tracking * max(len(s) - 1, 0)


def wrap(text, font, width, tracking=0.0):
    """Greedy wrap — the algorithm every email client uses. Honours explicit <br/>."""
    out = []
    for para in re.split(r"<br\s*/?>", text):
        # split on breaking whitespace ONLY — U+00A0 is glue and must not split
        words, line = [x for x in re.split(r"[ \t\n\r]+", para) if x], ""
        for word in words:
            trial = f"{line} {word}".strip()
            if w(font, trial, tracking) <= width or not line:
                line = trial
            else:
                out.append(line)
                line = word
        out.append(line)
    return out


def report(text, font, width, tracking=0.0, label=""):
    lines = wrap(text, font, width, tracking)
    widths = [w(font, l, tracking) for l in lines]
    longest = max(widths) if widths else 0
    shortest_last = widths[-1] if widths else 0
    ratio = (shortest_last / longest) if longest else 1.0
    if label:
        print(f"\n{label}")
    print(f"  measure {width:.0f}px · {len(lines)} line(s)")
    for l, lw in zip(lines, widths):
        bar = "#" * int(lw / longest * 42) if longest else ""
        print(f"    {lw:6.1f}px {int(lw/longest*100):3d}%  {bar:<42} |{l}|")
    verdict = "OK" if len(lines) < 2 or ratio >= 0.45 else "RAGGED"
    print(f"  last/longest = {ratio:.0%}  -> {verdict}")
    return lines, ratio


def best_breaks(text, font, width, tracking=0.0):
    """Try every split at a clause boundary; rank by how even the resulting lines are."""
    # candidate break points: after ? . , ; : or em dash
    tokens = text.split()
    cands = []
    for i in range(1, len(tokens)):
        if re.search(r"[?.,;:—]$|&mdash;$", tokens[i - 1]):
            cands.append(i)
    results = []
    for i in cands:
        a, b = " ".join(tokens[:i]), " ".join(tokens[i:])
        parts = [a, b]
        lines = []
        for p in parts:
            lines += wrap(p, font, width, tracking)
        widths = [w(font, l, tracking) for l in lines]
        longest = max(widths)
        spread = (longest - min(widths)) / longest
        results.append((spread, len(lines), a, b))
    results.sort()
    return results


DESKTOP_CONTENT = 500   # 568 card - 34px padding each side
MOBILE_CONTENT  = 220   # 320 viewport - 16px wrapper - 34px card padding, each side


def _plain(html):
    t = re.sub(r"<span[^>]*>.*?</span>", "", html)          # eyebrow em-dash spacer
    t = re.sub(r"<br\s*/?>", "\x00", t)                     # keep the break, tag-strip would eat it
    t = re.sub(r"<[^>]+>", "", t)
    # merge tags render as their fallback, not as the literal token
    t = re.sub(r"\{\$[a-z_]+\|default\(([^)]*)\)\}", r"\1", t)
    t = re.sub(r"\{\$[a-z_]+\}", "there", t)
    t = (t.replace("&mdash;", "—").replace("&rsquo;", "’").replace("&nbsp;", "\u00a0")
          .replace("&amp;", "&").replace("&rarr;", "→"))
    return t.replace("\x00", "<br/>")


def audit(path):
    """Report line balance for every text run in a built block, desktop and mobile."""
    html = pathlib.Path(path).read_text()
    bad = 0
    for m in re.finditer(r'<div style="(font-family:[^"]*)">(.*?)</div>', html, re.S):
        style, inner = m.group(1), m.group(2)
        text = _plain(inner).strip()
        if not text or "height:1px" in style:
            continue
        fam = ("mono" if "Courier" in style else "serif" if "Georgia" in style else "sans")
        size = float(re.search(r"font-size:(\d+)px", style).group(1))
        bold = "font-weight:700" in style
        tr = re.search(r"letter-spacing:(-?[\d.]+)px", style)
        tracking = float(tr.group(1)) if tr else 0.0
        mw = re.search(r"max-width:(\d+)px", style)
        width = float(mw.group(1)) if mw else DESKTOP_CONTENT
        # enforced roles: 15px body copy, and the 22px pull quote
        role_body = (fam == "sans" and size == 15 and not bold) or (fam == "serif" and size == 22)
        font = load(fam, bold, int(size))
        for tag, wd in (("desktop", width), ("mobile", min(MOBILE_CONTENT, width))):
            lines = wrap(text, font, wd, tracking)
            ws = [w(font, l, tracking) for l in lines]
            ratio = min(ws) / max(ws) if len(ws) > 1 else 1.0
            lone = len(lines) > 1 and len(lines[-1].split()) == 1
            # balance is a short-run concern; in a 4+ line paragraph only a lone last word is a defect
            # A short line is only acceptable as the LAST line of its paragraph; mid-paragraph
            # it reads as a hole, and min/max alone will happily prefer the version with one.
            # Measured per <br/>-delimited segment: a line that ends at a deliberate break is
            # short by design, not by accident. Desktop only - at the ~220px mobile measure a
            # 22px quote gets ~11 characters per line and is inherently ragged.
            hole = False
            if tag == "desktop":
                for seg in re.split(r"<br\s*/?>", text):
                    sl = wrap(seg, font, wd, tracking)
                    sw = [w(font, l, tracking) for l in sl]
                    if len(sw) > 2 and min(sw[:-1]) < max(sw) * 0.6:
                        hole = True
            fail = role_body and ((len(lines) in (2, 3) and ratio < 0.45) or lone or hole)
            bad += fail
            if fail:
                print(f"  RAGGED {pathlib.Path(path).name} [{tag} {wd:.0f}px] "
                      f"{len(lines)}L min/max {ratio:.0%}{' LONE WORD' if lone else ''}")
                for l in lines:
                    print(f"         |{l}|")
    return bad


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--text")
    ap.add_argument("--size", type=float, default=15)
    ap.add_argument("--width", type=float, default=CONTENT)
    ap.add_argument("--family", default="sans")
    ap.add_argument("--bold", action="store_true")
    ap.add_argument("--tracking", type=float, default=0.0)
    ap.add_argument("--suggest", action="store_true")
    ap.add_argument("--audit", nargs="+")
    a = ap.parse_args()
    if a.audit:
        total = 0
        for f_ in sorted(a.audit):
            total += audit(f_)
        print(("OK - no ragged runs" if not total else f"{total} ragged run(s)"))
        sys.exit(1 if total else 0)
    if not a.text:
        sys.exit("need --text")
    txt = a.text.replace("&rsquo;", "’").replace("&mdash;", "—").replace("&nbsp;", "\u00a0")
    f = load(a.family, a.bold, int(a.size))
    report(txt, f, a.width, a.tracking, label=f"{a.family}{' bold' if a.bold else ''} {a.size:g}px")
    if a.suggest:
        print("\n  candidate breaks (most even first):")
        for spread, n, x, y in best_breaks(txt, f, a.width, a.tracking)[:5]:
            print(f"    spread {spread:.0%}  {n} lines")
            print(f"      |{x}|")
            print(f"      |{y}|")
