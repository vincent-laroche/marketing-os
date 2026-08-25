#!/usr/bin/env python3
"""Generate build templates from the 104 resolved module previews.

For each module slug used by the 53-email programme, takes the light preview shell,
finds every fields.json default rendered inside it, and replaces the default text with
a {{slot:<field>}} marker. Output: tools/build53/templates/<slug>.html (shell) plus
<slug>.styles.html when the module carries its own <style> block.

Idempotent: rewrites templates/ on every run.
"""
import html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF = os.path.join(ROOT, "Email Reference File")
PREVIEWS = os.path.join(REF, "Atelier Zero — Resolved HTML Module Previews (102)")
TRIOS = os.path.join(REF, "emails_modules_hubspot versionr")
OUT = os.path.join(ROOT, "tools", "build53", "templates")

def flex_pattern(s):
    """Regex matching a default string as rendered in HTML: quotes/dashes/&/whitespace-flexible."""
    out = []
    for ch in s:
        if ch in "'\u2019":
            out.append(r"(?:'|&#39;|&#x27;|&rsquo;|\u2019)")
        elif ch in "\"\u201c\u201d":
            out.append(r"(?:\"|&quot;|&#34;|\u201c|\u201d|&#8220;|&#8221;)")
        elif ch in "-\u2013\u2014":
            out.append(r"(?:-|&#45;|\u2013|\u2014|&ndash;|&mdash;|&#8211;|&#8212;)")
        elif ch == "&":
            out.append(r"(?:&|&amp;)")
        elif ch.isspace():
            out.append(r"\s+")
        elif ch == "<":
            out.append(r"\s*<\s*")
        elif ch == ">":
            out.append(r"\s*>\s*")
        else:
            out.append(re.escape(ch))
    return "".join(out)

def sub_once(frag, pattern, marker):
    new, n = re.subn(pattern, marker, frag, count=1)
    return new, n > 0

def extract(slug):
    """Return (style_blocks, shell_fragment) for the light preview of slug."""
    hits = [f for f in os.listdir(PREVIEWS) if f.endswith(f"--{slug}_light.module.html")]
    if not hits:
        raise FileNotFoundError(slug)
    doc = open(os.path.join(PREVIEWS, hits[0]), encoding="utf-8").read()
    body = doc[doc.find("<body"):]
    body = body[body.find(">") + 1:body.rfind("</body>")]
    styles = re.findall(r"<style>.*?</style>", body, re.S)
    frag = re.sub(r"<style>.*?</style>", "", body, flags=re.S)
    # three resolved previews still carry the source module's HubL comment blocks
    # ({# ... #}) — they render as visible text in an email client. Strip them here so
    # a regeneration cannot reintroduce them.
    frag = re.sub(r"\{#.*?#\}", "", frag, flags=re.S)
    frag = re.sub(r"\n{3,}", "\n", frag)
    return styles, frag.strip()



# Two previews bake a sample value into markup that has no matching field position, so
# neither the default-text pass nor the empty-default pass can reach it. Both shipped
# wrong content: an unverified "4.8 out of 5" rating in 10 emails, and a second,
# conflicting button label alongside the approved CTA. Slot them explicitly.
LITERAL_SLOTS = {
    "signal_review_stars": [(">4.8 out of 5<", ">{{slot:rating_text}}<")],
    "text_base_type_guidance": [(">Book a consultation</a>", ">{{slot:fallback_cta_label}}</a>")],
}

def _tokens(doc):
    """(tag_texts, gaps) — gaps[i] is the text between tag i-1 and tag i.

    Comments and <style> blocks are dropped from the tag stream so the HubL source and
    the rendered preview line up; their real character offsets are kept for insertion.
    """
    tags, gaps, spans, last = [], [], [], 0
    for m in re.finditer(r"<[^>]+>", doc):
        t = m.group(0)
        if t.startswith("<!--") or re.match(r"</?style", t, re.I):
            continue
        tags.append(t.split()[0].lstrip("<").rstrip(">/").lower())
        gaps.append(doc[last:m.start()])
        spans.append((last, m.start()))
        last = m.end()
    gaps.append(doc[last:])
    spans.append((last, len(doc)))
    return tags, gaps, spans

def empty_default_slots(slug, frag, fields):
    """Give fields whose default is empty a slot too.

    A field with an empty default renders as nothing in the preview, so the default-text
    match cannot find it and the field silently got no slot — renderers then wrote into a
    slot that did not exist (comparison's column_*_item_*, timeline's step_*_label/text)
    and that copy was dropped from the email.

    module.html is the HubL source of the same markup. Where its tag stream lines up with
    the preview's exactly, the gap holding `{{ module.<field> }}` in the source is the gap
    the field belongs in in the preview. Modules whose tag streams do not align (the
    `{% if %}` branch modules, some image modules) are left as they are.
    """
    empties = [f["name"] for f in fields
               if isinstance(f.get("default"), str) and not f["default"].strip()]
    if not empties:
        return frag, []
    src_path = os.path.join(TRIOS, slug + "_light.module", "module.html")
    if not os.path.exists(src_path):
        return frag, []
    src = re.sub(r"\{#.*?#\}", "", open(src_path, encoding="utf-8").read(), flags=re.S)
    s_tags, s_gaps, _ = _tokens(src)
    f_tags, f_gaps, f_spans = _tokens(frag)
    if s_tags != f_tags:
        return frag, []
    edits, placed = [], []
    for name in empties:
        pat = re.compile(r"\{\{\s*module\.%s\s*\}\}" % re.escape(name))
        idx = [i for i, g in enumerate(s_gaps) if pat.search(g)]
        if len(idx) != 1:
            continue
        i = idx[0]
        if f_gaps[i].strip():           # the preview rendered something there already
            continue
        edits.append((f_spans[i], "{{slot:%s}}" % name))
        placed.append(name)
    for (a, b), marker in sorted(edits, reverse=True):
        frag = frag[:a] + marker + frag[b:]
    return frag, placed


def main():
    os.makedirs(OUT, exist_ok=True)
    for old in os.listdir(OUT):
        os.unlink(os.path.join(OUT, old))
    trios = sorted(d[:-len("_light.module")] for d in os.listdir(TRIOS) if d.endswith("_light.module"))
    report = []
    for slug in trios:
        fields = json.load(open(os.path.join(TRIOS, slug + "_light.module", "fields.json"), encoding="utf-8"))
        styles, frag = extract(slug)
        placed = []
        for fld in fields:
            name, typ = fld["name"], fld["type"]
            default = fld.get("default")
            if default is None:
                continue
            targets = []  # (search_text, marker)
            if isinstance(default, dict):
                src = default.get("src") or default.get("href")
                if src:
                    targets.append((src, "{{slot:%s}}" % name))
                alt = default.get("alt")
                if alt:
                    targets.append((alt, "{{slot:%s.alt}}" % name))
            elif isinstance(default, (str, int, float)):
                text = str(default)
                if not text.strip():
                    continue
                if typ == "choice":
                    continue  # branch selector, not rendered content
                targets.append((text, "{{slot:%s}}" % name))
            else:
                continue
            hit_any = False
            for text, marker in targets:
                new, hit = sub_once(frag, flex_pattern(text), marker)
                if hit:
                    frag = new
                    hit_any = True
            placed.append((name, typ, hit_any))
        frag, empties = empty_default_slots(slug, frag, fields)
        for literal, marker in LITERAL_SLOTS.get(slug, []):
            if literal not in frag:
                raise SystemExit("LITERAL_SLOTS out of date for %s: %r not found" % (slug, literal))
            frag = frag.replace(literal, marker, 1)
        open(os.path.join(OUT, slug + ".html"), "w", encoding="utf-8").write(frag + "\n")
        if styles:
            open(os.path.join(OUT, slug + ".styles.html"), "w", encoding="utf-8").write("\n".join(styles) + "\n")
        missing = [n for n, t, h in placed if not h]
        report.append((slug, len(placed), missing, empties))
    for slug, total, missing, empties in report:
        flag = "  UNPLACED: " + ",".join(missing) if missing else ""
        flag += ("  EMPTY-DEFAULT SLOTTED: " + ",".join(empties)) if empties else ""
        print(f"{slug}: {total} fields{flag}")

if __name__ == "__main__":
    main()
