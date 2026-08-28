#!/usr/bin/env python3
"""Measure and check an email shade sequence.

Usage:
  shade_sequence.py "B B P P B I B"
  shade_sequence.py BBPPBIB --mood quiet

Letters: B Bone, P Paper, I Ink, C Coral block, S seam card (counts as Bone-weight air).
Exit 0 if no blocking issue, 1 if any issue is found.
"""
import argparse, re, sys

VALID = "BPICS"
# Ranges measured from the 13 approved renders, not chosen. They overlap heavily,
# which is the finding: density describes energy, it does not identify mood and it
# does not gate quality. Passing --mood reports fit; it never fails a build.
MOODS = {
    "quiet":      (0.14, 0.33),
    "editorial":  (0.25, 0.50),
    "framed":     (0.25, 0.75),
    "punctuated": (0.14, 0.38),
}

def parse(raw):
    letters = [c for c in re.sub(r"[^A-Za-z]", "", raw).upper()]
    bad = sorted({c for c in letters if c not in VALID})
    if bad:
        sys.exit(f"error: unknown shade letter(s) {', '.join(bad)}; use {', '.join(VALID)}")
    if not letters:
        sys.exit("error: empty sequence")
    return letters

def runs(seq):
    out, cur = [], [seq[0]]
    for c in seq[1:]:
        if c == cur[-1]:
            cur.append(c)
        else:
            out.append(cur); cur = [c]
    out.append(cur)
    return out

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sequence", help='e.g. "B B P P B I B"')
    ap.add_argument("--mood", choices=sorted(MOODS), help="check density against a mood")
    a = ap.parse_args()

    seq = parse(a.sequence)
    n = len(seq)
    rr = runs(seq)
    # Seams exist to manufacture switches, so counting them inflates energy and
    # makes every seam-using email read as "busy". Density is measured on the
    # content sequence; seams are reported separately.
    content = [c for c in seq if c != "S"]
    cn = len(content) or 1
    switches = sum(1 for i in range(1, cn) if content[i] != content[i-1])
    density = switches / cn
    ink = seq.count("I"); coral = seq.count("C"); seams = seq.count("S")
    longest_ink = max((len(r) for r in rr if r[0] == "I"), default=0)

    print(f"blocks {n} ({cn} content + {n-cn} seam)  switches {switches}  density {density:.2f}")
    print(f"runs   {' '.join(r[0] + str(len(r)) for r in rr)}")
    print(f"ink    {ink} ({ink/cn:.0%} of content)   coral {coral}   seams {seams}")

    # Only genuine defects fail. Density is reported, never gated: the approved set
    # spans 0.14-0.75, so any global band flags real, shipped work as broken.
    issues = []
    if longest_ink >= 3:
        issues.append(f"ink as wallpaper: {longest_ink} consecutive Ink blocks")
    if coral > 1:
        issues.append(f"coral spent {coral} times; at most one block per email")
    if seq[0] == "S" or seq[-1] == "S":
        issues.append("a seam opens or closes the email; it belongs between content blocks")
    if any(len(r) > 1 for r in rr if r[0] == "S"):
        issues.append("two seams in a row: a gap with decoration in it")
    if seq[0] == "C" or seq[-1] == "C":
        issues.append("coral used as a header or footer")

    if a.mood:
        lo, hi = MOODS[a.mood]
        fit = "within" if lo <= density <= hi else "outside"
        print(f"mood   {a.mood}: {density:.2f} {fit} observed range {lo:.2f}-{hi:.2f}")

    if issues:
        print("\nissues:", file=sys.stderr)
        for i in issues:
            print(f"  - {i}", file=sys.stderr)
        return 1
    print("\nno issues")
    return 0

if __name__ == "__main__":
    sys.exit(main())
