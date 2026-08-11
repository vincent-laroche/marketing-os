"""Roll the surface system out to every remaining twin-file module family.

Safe because all twin pairs were verified structurally identical (only hex values
differ): the LIGHT module is tokenised, and the resulting HTML is written to BOTH
folders. Only the fields.json `surface` default differs (bone vs ink), so existing
email instances in either folder keep rendering exactly as before.
"""
import json, os, re, shutil, sys
from surface import surface_field, preamble, ORDER
from contrast import bad_surfaces

SRC, OUT = "verify2", "staging-rollout/email_modules"

# already migrated in the pilot
DONE = {"header_centered_logo", "footer_standard", "text_block_generic",
        "hero_text_led", "button_standalone_cta"}
# these already carry their own `color` choice field and are not twin files
SKIP = {"divider_rounded_link", "divider_full_band"}
NO_CORAL = {"header_centered_logo", "footer_standard", "footer_social", "footer_wide",
            "photo_logo_system", "preheader_bar", "header_hero"}

PILL = "border-radius:999px"


HEX = re.compile(r"#[0-9A-Fa-f]{6}")
TAG = re.compile(r"<(/?)(\w+)([^>]*)>", re.S)
VOID = {"img", "br", "hr", "meta", "input"}

BG_RE = re.compile(r"((?<!-)background(?:-color)?\s*:\s*)(#[0-9A-Fa-f]{6})", re.I)
BGATTR_RE = re.compile(r'(bgcolor\s*=\s*")(#[0-9A-Fa-f]{6})', re.I)
BD_RE = re.compile(r"(solid\s+)(#[0-9A-Fa-f]{6})", re.I)
FG_RE = re.compile(r"((?<!background-)(?<!-)color\s*:\s*)(#[0-9A-Fa-f]{6})", re.I)


def fill_token(hexv, attrs):
    """What a background/bgcolor hex means, from the element it sits on."""
    h = hexv.upper()
    # the 600px card itself — `final-card` class on most, bare on cart-recovery/*
    if "width:600px" in attrs.replace(" ", ""):
        return "bg"
    hairline = bool(re.search(r'height\s*=\s*"?1\b|height:1px|font-size:1px', attrs, re.I))
    if hairline:
        return "ac" if h == "#ED6F5C" else "dv"
    if h == "#ED6F5C":
        return "bb"          # a coral pill/band that is not a hairline is a button fill
    if h == "#15140F":
        return "iv"          # solid inverse primary
    if h in ("#EFE7D2", "#DDD2B6", "#2A2620", "#F7F1DE"):
        return "sc"          # nested soft-fill sub-card
    return None


BORDER_TOKEN = {"#DDD2B6": "dv", "#2A2620": "dv", "#ED6F5C": "ac", "#15140F": "tx"}
# text colour, given the token of the nearest ancestor fill
TEXT_ON_FILL = {"bb": "bt", "iv": "it", "ac": "bt"}
TEXT_TOKEN = {"#15140F": "tx", "#5A5448": "mu", "#ED6F5C": "ac",
              "#DDD2B6": "mu", "#F7F1DE": "tx", "#2A2620": "mu"}


def tokenise(html, name):
    """Rewrite hardcoded hexes as {{ c.* }}, using the tag tree for context.

    Regex-with-lookbehind cannot tell a filled pill from a ghost pill, nor find a
    button whose fill is a `bgcolor` attribute two tags up. Both produced text that
    rendered invisible on some surfaces, so context comes from an actual tag stack.
    """
    unknown = []
    stack = ["bg"]          # token of the nearest ancestor that paints a background
    out, last = [], 0
    for m in TAG.finditer(html):
        closing, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if closing:
            if len(stack) > 1:
                stack.pop()
            continue

        own = None
        new = attrs

        def sub_fill(mm):
            nonlocal own
            k = fill_token(mm.group(2), attrs)
            if k is None:
                unknown.append((name, mm.group(2), "fill"))
                return mm.group(0)
            own = k
            return mm.group(1) + "{{ c.%s }}" % k

        new = BG_RE.sub(sub_fill, new)
        new = BGATTR_RE.sub(sub_fill, new)

        def sub_border(mm):
            k = BORDER_TOKEN.get(mm.group(2).upper())
            if k is None:
                unknown.append((name, mm.group(2), "border"))
                return mm.group(0)
            return mm.group(1) + "{{ c.%s }}" % k

        new = BD_RE.sub(sub_border, new)

        behind = own or stack[-1]

        def sub_text(mm):
            k = TEXT_ON_FILL.get(behind) or TEXT_TOKEN.get(mm.group(2).upper())
            if k is None:
                unknown.append((name, mm.group(2), "text"))
                return mm.group(0)
            return mm.group(1) + "{{ c.%s }}" % k

        new = FG_RE.sub(sub_text, new)

        out.append(html[last:m.start()])
        out.append("<%s%s%s>" % (closing, m.group(2), new))
        last = m.end()
        if tag not in VOID and not attrs.rstrip().endswith("/"):
            stack.append(own or stack[-1])
    out.append(html[last:])
    return "".join(out), unknown


def families():
    fams = []
    for d in sorted(os.listdir(SRC)):
        if d.endswith(".module") and not d.endswith("_dark.module"):
            base = d[:-len(".module")]
            if base in DONE or base in SKIP:
                continue
            if os.path.isdir(os.path.join(SRC, base + "_dark.module")):
                fams.append((base, base + ".module", base + "_dark.module"))
    cr = os.path.join(SRC, "cart-recovery")
    for d in sorted(os.listdir(cr)) if os.path.isdir(cr) else []:
        if d.endswith("_light.module"):
            base = d[:-len("_light.module")]
            dk = base + "_dark.module"
            if os.path.isdir(os.path.join(cr, dk)):
                fams.append(("cart-recovery/" + base,
                             "cart-recovery/" + d, "cart-recovery/" + dk))
    return fams


# `preheader_bar` shipped its own neutral/coral `style` choice, which the surface
# field now does properly. Collapse it rather than leaving two competing controls.

# Modules whose image field is the brand wordmark. Colour tokenisation cannot fix
# these: the logo is an asset, not a hex, so on Ink they kept rendering the dark
# wordmark on a dark card. Derive the asset from the surface, exactly as the pilot
# header/footer do, and keep only an editable width.
LOGO_FIELDS = {
    "footer_social": ["logo_image"],
    "footer_wide": ["logo_image"],
    "photo_logo_system": ["logo_1_image", "logo_2_image"],
    "header_hero": ["logo"],
}


def derive_logos(html, fields, names):
    for f in names:
        html = html.replace("{{ module.%s.src }}" % f, "{{ c.lg }}")
        html = html.replace("{{ module.%s.alt }}" % f, "Hair Solutions Co.")
        html = html.replace("{{ module.%s.width }}" % f, "{{ module.%s_width }}" % f)
    keep = [x for x in fields if x["id"] not in names]
    widths = [{"id": f + "_width", "name": f + "_width", "label": "Wordmark width (px)",
               "required": False, "locked": False, "allow_new_line": False,
               "type": "text", "display_width": None, "default": "132"} for f in names]
    return html, widths + keep


def collapse_preheader(html):
    html = re.sub(r"\{%\s*if module\.style == 'coral'\s*%\}#[0-9A-Fa-f]{6}"
                  r"\{%\s*else\s*%\}#F7F1DE\{%\s*endif\s*%\}", "{{ c.bg }}", html)
    html = re.sub(r"\{%\s*if module\.style == 'coral'\s*%\}#[0-9A-Fa-f]{6}"
                  r"\{%\s*else\s*%\}#[0-9A-Fa-f]{6}\{%\s*endif\s*%\}", "{{ c.tx }}", html)
    return html


if __name__ == "__main__":
    shutil.rmtree("staging-rollout", ignore_errors=True)
    all_unknown, n, restricted = [], 0, []
    for base, light, dark in families():
        src_light = os.path.join(SRC, light)
        html = open(os.path.join(src_light, "module.html")).read()
        if "set SURF" in html:
            continue
        short = base.split("/")[-1]
        if short == "preheader_bar":
            html = collapse_preheader(html)
        logo_names = LOGO_FIELDS.get(short, [])
        if logo_names:
            html, _ = derive_logos(html, [], logo_names)
        toks, unk = tokenise(html, base)
        all_unknown += unk

        # Offer only surfaces this module actually renders well on. Derived from
        # the collision checker, not a hand-kept list, so it stays true as modules
        # change. Bone and Ink must always survive — they are the migration defaults.
        cand = [s for s in ORDER if not (s == "coral" and short in NO_CORAL)]
        bad = set(bad_surfaces(preamble("bone") + toks, cand))
        assert not ({"bone", "ink"} & bad), f"{base}: default surface failed — {bad}"
        excl = tuple(s for s in ORDER if s not in cand or s in bad)
        if bad:
            restricted.append((base, sorted(bad)))

        for folder, default in ((light, "bone"), (dark, "ink")):
            dst = os.path.join(OUT, folder)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(os.path.join(SRC, folder), dst)
            # both folders get the SAME html; only the default differs
            open(os.path.join(dst, "module.html"), "w").write(
                preamble(default) + toks)
            f = json.load(open(os.path.join(dst, "fields.json")))
            f = [x for x in f if x["id"] != "surface"]
            if logo_names:
                _, f = derive_logos("", f, logo_names)
            if short == "preheader_bar":
                f = [x for x in f if x["id"] != "style"]
            json.dump([surface_field(default, excl)] + f,
                      open(os.path.join(dst, "fields.json"), "w"), indent=2)
        n += 1
        print(f"  {base}")

    print(f"\n{n} families tokenised ({n*2} folders)")
    if restricted:
        print("\nsurfaces withheld (would render poorly):")
        for b, ss in restricted:
            print(f"   {b:38s} -{','.join(ss)}")
    if all_unknown:
        print("\n*** UNMAPPED HEXES — fix before upload ***")
        for a in dict.fromkeys(all_unknown):
            print("   ", a)
        sys.exit(1)
    left = 0
    for root, _, fs in os.walk(OUT):
        for fn in fs:
            if fn == "module.html":
                t = open(os.path.join(root, fn)).read()
                body = t.split("-%}")[-1]
                left += len(HEX.findall(body))
    print(f"hardcoded hexes remaining in module bodies: {left}")
