"""Collapse every module from six selectable surfaces down to three.

The module bodies are already tokenised (`{{ c.* }}`), so nothing about their markup
changes — only which surfaces they may be set to, and what those surfaces resolve to.
Bone, Paper Dark and Ink Soft stop being selectable and go back to being derived
supporting values (dividers, inset fills, text-on-dark).

Safe for existing content: an instance still holding a retired value ("bone",
"paper_dark", "ink_soft") misses the lookup table, and the module's own
`{% if not c %}` guard falls it back to that file's default.
"""
import json, os, re, shutil, sys
from surface import surface_field, preamble, SURFACES, SUPPORTING

SRC, OUT = "live3", "staging-collapse/email_modules"

PRE = re.compile(r"^\{%-\s*set SURF =.*?\{%\s*endif\s*-%\}", re.S)

NO_CORAL = {"header_centered_logo", "footer_standard", "footer_social", "footer_wide",
            "photo_logo_system", "preference_opt_down", "header_hero"}
SKIP = {"divider_rounded_link.module", "divider_full_band.module"}


def family(folder):
    return (folder.split("/")[-1]
            .replace("_dark.module", "").replace("_light.module", "").replace(".module", ""))


def main():
    shutil.rmtree("staging-collapse", ignore_errors=True)
    done, untokenised, bg_violations = 0, [], []

    for root, dirs, files in os.walk(SRC):
        if "module.html" not in files:
            continue
        rel = os.path.relpath(root, SRC)
        if rel in SKIP:
            continue
        html = open(os.path.join(root, "module.html")).read()
        if not PRE.match(html):
            untokenised.append(rel)
            continue

        dark = rel.endswith("_dark.module")
        default = "ink" if dark else "paper"
        fam = family(rel)
        excl = ("coral",) if fam in NO_CORAL else ()

        body = PRE.sub("", html, count=1)

        # a supporting colour hardcoded as a section background would defeat the rule
        for m in re.finditer(r'background(?:-color)?\s*:\s*(#[0-9A-Fa-f]{6})', body):
            if m.group(1).upper() in SUPPORTING:
                bg_violations.append(f"{rel}: {m.group(1)}")

        dst = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copytree(root, dst)
        open(os.path.join(dst, "module.html"), "w").write(preamble(default) + body)

        fields = json.load(open(os.path.join(dst, "fields.json")))
        fields = [f for f in fields if f["id"] != "surface"]
        json.dump([surface_field(default, excl)] + fields,
                  open(os.path.join(dst, "fields.json"), "w"), indent=2)
        done += 1

    print(f"collapsed {done} module folders to 3 surfaces")
    print("not tokenised (skipped):", untokenised or "none")
    print("supporting colour used as a background:", bg_violations or "none")

    # prove no retired surface value survives anywhere
    left = []
    for root, _, files in os.walk(OUT):
        for fn in files:
            if fn != "fields.json":
                continue
            f = json.load(open(os.path.join(root, fn)))
            ch = [c[0] for c in f[0]["choices"]] if f and f[0]["id"] == "surface" else []
            bad = [c for c in ch if c not in ("paper", "ink", "coral")]
            if bad:
                left.append((os.path.relpath(root, OUT), bad))
    print("retired choices remaining:", left or "none")


if __name__ == "__main__":
    main()
