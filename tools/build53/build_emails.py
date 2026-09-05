#!/usr/bin/env python3
"""Assemble the 53 emails of the CAMPAIGN-PLAN.md programme.

Build material : tools/build53/templates/<slug>.html (generated from the resolved
                 module previews by gen_templates.py — run it first)
Copy source    : emails_master CSV Body column (verbatim, AGENTS.md §1)
Output         : shopify-messaging/emails/<nn>-<slug>.html  (local artifacts only —
                 nothing is pushed, scheduled, or sent; AGENTS.md §2)

Conventions (verified 2026-08-19, see shopify-messaging/BUILD-LEDGER.md):
- <body> and the outer wrapper are background-color:transparent — no page background.
- Merge tags: {{ firstname }} -> {{ customer.first_name | default: "there" }}.
- Unsubscribe: {{ unsubscribe_url }} on every email; physical address on every email.
- Images: raw /v1/public/<key> URLs only (never ?variant=).
- UTM: utm_source=shopify_email&utm_medium=email&utm_campaign=<email-slug>
  (activity-ID suffix is appended at Phase 5 when campaigns exist).
- Reality-dependent tokens ({{ dynamic: ... }}, [PULL ...], [OFFER ...]) render as
  loud placeholders that fail review visibly — never silently invented.
"""
import csv, html, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import module_map as mm

ROOT = mm.ROOT
TEMPLATES = os.path.join(ROOT, "tools", "build53", "templates")
ASSET_MAP = json.load(open(os.path.join(ROOT, "tools", "build53", "asset_map.json"), encoding="utf-8"))
# Overridable so a reproducibility test can build to a scratch directory and diff,
# instead of overwriting the committed tree to find out whether it would change it.
OUT_DIR = os.environ.get("BUILD53_OUT_DIR") or os.path.join(ROOT, "shopify-messaging", "emails")

ASSETS_BASE = "https://assets.hairsolutions.co/v1/public/"
# The wordmark: header_centered_logo's fields.json defaults to Cloudinary; footer_social's
# defaults to the HubSpot portal CDN. HubSpot access is lost (AGENTS.md §3) and that URL is
# portal-tied, so every logo is normalised to this one constant.
# Host decided 2026-09-05 by Vincent (#134): email images live on R2 hsc-media-origin, served
# by the hsc-media-delivery Worker. Content-addressed per BUILD-LEDGER: the key's sha256 is of
# the uploaded bytes, so a re-encode is a new key. Raw /v1/public/ only — never ?variant=,
# which emits AVIF that many email clients cannot render.
# Uploaded and verified 2026-09-05: HTTP 200, image/png, 16,400 bytes, sha256 matches source.
LOGO_URL = (ASSETS_BASE + "approved/brand/wordmark-dark-on-transparent/"
            "cfcbef6a17911dd479598a3341973ed83492746fd68288030b04f19a757ed233.png")
DEAD_LOGO_HOST = "hubspotusercontent"
ADDRESS = "Ehitajate tee 110, Tallinn, Harjumaa 13517, Estonia"  # footer_wide spelling;
# footer_standard's "Eahitajate tee" is a typo — normalised at render, recorded in ledger.
PREFERENCES_URL = "https://hairsolutions.co/pages/edit-notifications"
UNSUB = "{{ unsubscribe_url }}"

def utm(url, campaign):
    if not url.startswith("https://"):
        return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}utm_source=shopify_email&utm_medium=email&utm_campaign={campaign}"

def slugify(name):
    s = name.split(" · ")[0].lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

# ---------------------------------------------------------------- destinations
# CTA destinations verified live 2026-08-19 (HTTP 200) unless marked TOKEN/PLACEHOLDER.
BLOG = {
    "NL-01": "https://hairsolutions.co/pages/base-materials-explained-lace-skin-mono-and-hybrid",
    "BR-1":  "https://hairsolutions.co/pages/base-materials-explained-lace-skin-mono-and-hybrid",
    "NL-06": "https://hairsolutions.co/pages/hair-density-color-hair-type-and-hairline-options",
    "NL-11": "https://hairsolutions.co/pages/lace-front-hair-systems-complete-guide",
    "NL-16": "https://hairsolutions.co/pages/complete-hair-system-maintenance-guide",
}
PRODUCTS = {
    "lace-elite":    "https://hairsolutions.co/products/lace-elite-full-swiss-lace-mens-hair-system",
    "lace-pro-ld":   "https://hairsolutions.co/products/lace-pro-ld-swiss-lace-mens-hair-system",
    "micro-skin-md": "https://hairsolutions.co/products/micro-skin-md-006mm-v-loop-mens-thin-skin",
    "mono-fusion-lf":"https://hairsolutions.co/products/mono-fusion-lf-mens-mono-hair-system-pu-perimeter-lace-front",
    "mono-pro":      "https://hairsolutions.co/products/mono-pro-fine-welded-monofilament-mens-hair-system",
}
BEST = "https://hairsolutions.co/collections/best-sellers"
MENS = "https://hairsolutions.co/collections/mens-hair-systems"
ALL = "https://hairsolutions.co/collections/all"
CONTACT = "https://hairsolutions.co/pages/contact-us"
REVIEWS = PRODUCTS["lace-elite"]  # no public all-reviews page exists; Judge.me widget
# renders on product pages. Recorded in ledger.
# Genuinely unresolved destinations render as loud '#' placeholders (fail loudly):
TODO_REVIEW_PAGE = "#TODO-review-destination"      # PP-7: no public review-submission page
TODO_UGC_PAGE = "#TODO-ugc-upload-destination"     # PP-7b: /pages/share-your-look is 404

DESTINATIONS = {  # email prefix -> primary CTA destination
    "CR-1": "{{ checkout.url }}", "CR-4": "{{ checkout.url }}",
    "CR-2": REVIEWS, "CR-3": CONTACT,
    "BR-1": BLOG["BR-1"],
    "PP-1": "#TODO-customer-order-url",      # per-order URL — automation object, Phase 5
    "PP-2": "https://hairsolutions.co/pages/scalp-preparation-and-patch-testing-before-attachment",
    "PP-3": "https://hairsolutions.co/pages/production-times-shipping-times-and-package-tracking",
    "PP-4": "#TODO-tracking-url",            # per-shipment — automation object, Phase 5
    "PP-5": "https://hairsolutions.co/pages/complete-hair-system-maintenance-guide",
    "PP-6": BEST,
    "PP-7": TODO_REVIEW_PAGE,
    "PP-7b": TODO_UGC_PAGE,
    "RO-1": "https://hairsolutions.co/pages/complete-hair-system-maintenance-guide",
    "RO-2": ALL,   # care collections are not published to the online store (404) — ledger
    "RO-3": MENS, "RO-4": MENS, "RO-5": CONTACT, "RO-6": MENS,
    "C-0": CONTACT, "C-1": CONTACT, "C-2": CONTACT, "C-3": CONTACT, "C-4": None,
    "W-1": "https://hairsolutions.co/pages/how-to-choose-your-first-hair-system",
    "W-2": "https://hairsolutions.co/pages/what-is-a-hair-system-and-how-does-it-work",
    "W-3": BEST, "W-4": REVIEWS, "W-5": CONTACT,
    "WB-1": None, "WB-2": "https://hairsolutions.co/pages/blog",
    "WB-3": MENS, "WB-4": None,
    "NL-01": BLOG["NL-01"], "NL-02": REVIEWS, "NL-03": BEST, "NL-04": "https://hairsolutions.co/pages/blog",
    "NL-05": MENS, "NL-06": BLOG["NL-06"], "NL-07": REVIEWS, "NL-08": BEST,
    "NL-09": "https://hairsolutions.co/pages/production-times-shipping-times-and-package-tracking",
    "NL-10": MENS, "NL-11": BLOG["NL-11"], "NL-12": REVIEWS, "NL-13": MENS,
    "NL-14": REVIEWS, "NL-15": MENS, "NL-16": BLOG["NL-16"], "NL-17": CONTACT,
    "NL-18": BEST, "NL-19": None, "NL-20": ALL,
}

def email_prefix(name):
    m = re.match(r"([A-Z]+-\w+)", name)
    return m.group(1) if m else name


# ---------------------------------------------------------------- body parsing
def is_marker_line(line):
    """A line like '[Text - Masthead]' or '[A] + [B] (note)' where every bracket
    group resolves to a known module family. PULL/OFFER lines are content."""
    s = line.strip()
    if not s.startswith("["):
        return False
    groups = re.findall(r"\[([^\[\]]*)\]", s)
    if not groups:
        return False
    remainder = re.sub(r"\[[^\[\]]*\]", "", s).strip()
    if remainder and not (remainder.startswith("(") and remainder.endswith(")") or remainder == "+"):
        # text after the last bracket that isn't a (note)
        if not re.fullmatch(r"(\+\s*)*(\([^()]*\))?\s*", remainder):
            return False
    fams = []
    for g in groups:
        fam = mm.family_of(re.split(r"\s+—\s+", g)[0].strip())
        slug, _ = mm.resolve(fam)
        if slug is None:
            return False
        fams.append(fam)
    return fams

def parse_body(body):
    """Return (preamble_notes, blocks) where blocks = [(families, copy_text)]."""
    lines = body.split("\n")
    preamble, blocks = [], []
    cur_fams, cur_lines = None, []
    def flush():
        nonlocal cur_fams, cur_lines
        if cur_fams is not None:
            blocks.append((cur_fams, "\n".join(cur_lines).strip("\n")))
        cur_fams, cur_lines = None, []
    for line in lines:
        fams = is_marker_line(line)
        if fams is not None and fams is not False:
            flush()
            cur_fams = fams
        elif cur_fams is None:
            if line.strip():
                preamble.append(line.strip())
        else:
            cur_lines.append(line)
    flush()
    return preamble, blocks

# ------------------------------------------------------------- copy structuring
FIRSTNAME = '{{ customer.first_name | default: "there" }}'

def translate_tokens(text, abandoned_checkout=False):
    """Reference-copy tokens -> Shopify Messaging Liquid. Known tokens translate;
    everything else stays verbatim (rendered loud downstream)."""
    text = re.sub(r"\{\{\s*firstname\s*\}\}", FIRSTNAME, text)
    text = re.sub(
        r"\{\{\s*personalization_token\(\s*['\"]contact\.firstname['\"]\s*,\s*['\"](.*?)['\"]\s*\)\s*\}\}",
        r'{{ customer.first_name | default: "\1" }}', text)
    # {{ last_viewed_product }} is deck shorthand for "the item they were looking at".
    # Its Shopify binding depends on which automation sends the email, so it is only
    # translated where that binding is known: checkout abandonment (CR-*), where
    # abandoned_checkout.* is populated. CR-3 carried this by hand until the
    # return-to-palette decision (2026-09-05).
    #
    # BR-1 is BROWSE abandonment — a different automation type with a different event
    # payload (J2-CART-RECOVERY-READY.md). abandoned_checkout.* would not resolve there,
    # so its token is deliberately left to render loud rather than bound to a guess.
    if abandoned_checkout:
        text = re.sub(r"\{\{\s*last_viewed_product\s*\}\}",
                      '{{ abandoned_checkout.line_items.first.product_title '
                      '| default: "Your selected system" }}', text)
    return text

def paragraphs(copy):
    """Split a copy block into paragraphs; classify each."""
    out = []
    for chunk in re.split(r"\n\s*\n", copy.strip()):
        lines = [l.rstrip() for l in chunk.strip().split("\n") if l.strip()]
        if not lines:
            continue
        if all(re.match(r"^[-·•]\s+", l) for l in lines):
            out.append(("ul", [re.sub(r"^[-·•]\s+", "", l) for l in lines]))
        elif all(re.match(r"^\d+[.)]\s+", l) for l in lines):
            out.append(("ol", [re.sub(r"^\d+[.)]\s+", "", l) for l in lines]))
        elif len(lines) == 1 and (lines[0].lstrip().startswith("{{") or
                re.match(r"^\[(PULL|OFFER)", lines[0].strip())):
            out.append(("placeholder", lines))
        else:
            out.append(("p", lines))
    return out

def esc(t):
    return html.escape(t, quote=False)

def loud(text):
    """A build placeholder that fails review visibly. Text stays verbatim."""
    return (f'<div style="border:2px dashed #EA6452;border-radius:8px;padding:10px 14px;margin:4px 0;'
            f'font-family:\'Courier New\',Courier,monospace;font-size:13px;line-height:1.5;color:#151411;'
            f'background-color:transparent;">{esc(text)}</div>')

def paras_html(paras):
    """Render parsed paragraphs as self-contained inline-styled HTML."""
    out = []
    for kind, lines in paras:
        if kind == "p":
            out.append(f'<p style="margin:0 0 12px;padding:0;">{esc(" ".join(lines))}</p>')
        elif kind == "ul":
            lis = "".join(f'<li style="margin:0 0 6px;padding:0;">{esc(i)}</li>' for i in lines)
            out.append(f'<ul style="margin:0 0 12px;padding:0 0 0 20px;">{lis}</ul>')
        elif kind == "ol":
            lis = "".join(f'<li style="margin:0 0 6px;padding:0;">{esc(i)}</li>' for i in lines)
            out.append(f'<ol style="margin:0 0 12px;padding:0 0 0 20px;">{lis}</ol>')
        else:
            out.extend(loud(l) for l in lines)
    if out:
        out[-1] = out[-1].replace("margin:0 0 12px", "margin:0", 1)
    return "".join(out)

# ------------------------------------------------------------ template filling
def load_template(slug):
    return open(os.path.join(TEMPLATES, slug + ".html"), encoding="utf-8").read()

def fill(tpl, values):
    for k, v in values.items():
        tpl = tpl.replace("{{slot:%s}}" % k, v)
    return tpl

def drop_empty_slots(tpl):
    """Remove structural elements whose only content is an unfilled slot."""
    for _ in range(400):
        m = re.search(r"\{\{slot:([\w.]+)\}\}", tpl)
        if not m:
            break
        slot = m.group(0)
        esc_slot = re.escape(slot)
        for pat in (r"<img [^>]*" + esc_slot + r"[^>]*/?>",
                    r"<p[^>]*>((?!<p).)*?" + esc_slot + r"((?!<p).)*?</p>",
                    r"<a [^>]*>((?!<a).)*?" + esc_slot + r"((?!<a).)*?</a>",
                    r"<img [^>]*" + esc_slot + r"[^>]*/?>",
                    r"<div[^>]*>((?!<div).)*?" + esc_slot + r"((?!<div).)*?</div>",
                    r"<td[^>]*>((?!<t[dr]).)*?" + esc_slot + r"((?!<t[dr]).)*?</td>",
                    r"<tr[^>]*>((?!<tr).)*?" + esc_slot + r"((?!<tr).)*?</tr>"):
            new = re.sub(pat, "", tpl, count=1, flags=re.S)
            if new != tpl:
                tpl = new
                break
        else:
            tpl = tpl.replace(slot, "", 1)  # bare fallback; validator checks the result
    return tpl

def render(slug, values):
    return drop_empty_slots(fill(load_template(slug), values))

# ------------------------------------------------------------------- renderers
def first_line(paras):
    if paras and paras[0][0] == "p":
        return " ".join(paras[0][1])
    return ""

def r_heading_body(slug, copy, ctx=None, heading_field="heading", body_field="body_text",
                   greeting_to_body=True, **kw):
    paras = paragraphs(copy)
    values = {}
    first = first_line(paras)
    if first and not (greeting_to_body and re.match(r"^(Hi|Hey|Dear)\b", first)) \
            and len(paras) >= 1 and slug != "text_opening" or (slug in ("hero_text_led",) and first):
        values[heading_field] = esc(first)
        paras = paras[1:]
    if paras:
        values[body_field] = paras_html(paras)
    return render(slug, values)

def r_text_opening(slug, copy, ctx=None, **kw):
    # greeting + paragraphs all live in body_text; heading stays only if the block
    # leads with a non-greeting single line followed by more copy
    paras = paragraphs(copy)
    values = {}
    if paras and paras[0][0] == "p" and not re.match(r"^(Hi|Hey|Dear)\b", " ".join(paras[0][1])) \
            and len(paras) > 1:
        values["heading"] = esc(" ".join(paras[0][1]))
        paras = paras[1:]
    values["body_text"] = paras_html(paras)
    return render(slug, values)

def r_masthead(slug, copy, ctx=None, **kw):
    paras = paragraphs(copy)
    values = {"title": esc(first_line(paras))}
    rest = paras[1:]
    if rest:
        values["date_text"] = esc(" ".join(rest[0][1]))
    return render(slug, values)

def r_button(slug, copy, ctx=None, **kw):
    paras = paragraphs(copy)
    label = first_line(paras) or ctx["cta"].split(" / ")[0]
    dest = ctx["dest"]
    values = {"button_text": esc(label)}
    if dest:
        values["button_url"] = esc(dest)
    # headline/body_text slots: only if extra copy lines exist beyond the label
    extra = [p for p in paras[1:] if p[0] == "p"]
    if extra:
        values["body_text"] = paras_html(extra)
    return render(slug, values)

def r_founder_wrapper(slug, copy, ctx=None, **kw):
    paras = paragraphs(copy)
    tpl = load_template(slug)
    # greeting: the preview renders the default token as the literal text "Hi there,"
    if paras and paras[0][0] == "p" and re.match(r"^(Hi|Hey|Dear)", paras[0][1][0]):
        tpl = tpl.replace("Hi there,", esc(paras[0][1][0]), 1)
        paras = ([("p", paras[0][1][1:])] if len(paras[0][1]) > 1 else []) + paras[1:]
        paras = [p for p in paras if p[1]]
    # trailing sign-off lines live in the signature slots, not the body
    sig_name, sig_role = "Vincent", "Founder, Hair Solutions Co."
    while paras and paras[-1][0] == "p" and ", ".join(paras[-1][1]).strip() in (
            "Vincent", "Founder, Hair Solutions Co.", "Vincent, Founder, Hair Solutions Co."):
        paras.pop()
    values = {"body_text": paras_html(paras),
              "signature_name": esc(sig_name), "signature_role": esc(sig_role)}
    return drop_empty_slots(fill(tpl, values))

def r_static(slug, copy, ctx, **kw):
    """Headers/footers: sample content is the intended content; fix compliance links."""
    tpl = load_template(slug)
    # static modules: fields.json defaults ARE the intended content — fill them
    skip = {"ig_url", "fb_url", "yt_url"} if slug == "footer_social" else set()
    values = {}
    for fname, fld in load_fields(slug).items():
        if fname in skip:
            continue
        d = fld.get("default")
        if isinstance(d, str) and d.strip():
            # `richtext` defaults already contain HTML (footer_preference_centre's body_text
            # is "<p>You can hear from us less often…</p>"). Escaping them emitted a literal
            # &lt;p&gt; into the compliance footer of 19 emails (#142). Only `text` defaults
            # are plain strings that need escaping.
            values[fname] = d if fld.get("type") == "richtext" else esc(d)
        elif isinstance(d, dict):
            if d.get("src"):
                src = d["src"]
                # Both static modules carrying an image use `logo_image`, and it is always
                # the wordmark: the header's field default points at Cloudinary and the
                # footer's at the dead HubSpot portal. Rewriting only the HubSpot host left
                # 30 Cloudinary references in place, so normalise every logo to the one
                # approved R2 object (#134, decided 2026-09-05).
                if fname == "logo_image" or DEAD_LOGO_HOST in src:
                    src = LOGO_URL
                values[fname] = esc(src)
            elif d.get("href"):
                values[fname] = esc(d["href"])
            if d.get("alt"):
                values[fname + ".alt"] = esc(d["alt"])
    tpl = fill(tpl, values)
    tpl = drop_empty_slots(tpl)
    tpl = re.sub(r'href="#"([^>]*)>([^<]*[Uu]nsubscribe[^<]*)<',
                 'href="{{ unsubscribe_url }}"\\1>\\2<', tpl)
    tpl = re.sub(r'href="#"([^>]*)>([^<]*[Mm]anage preferences[^<]*)<',
                 'href="' + PREFERENCES_URL + '"\\1>\\2<', tpl)
    tpl = re.sub(r'href="#"([^>]*)>([^<]*[Pp]references[^<]*)<',
                 'href="' + PREFERENCES_URL + '"\\1>\\2<', tpl)
    tpl = tpl.replace("Eahitajate tee", "Ehitajate tee")
    tpl = tpl.replace('href="#"', 'href="' + PREFERENCES_URL + '"')  # remaining # links are preference options
    if slug == "footer_social":
        # no public social profiles exist for the store (verified 2026-08-19) —
        # drop the social icon links rather than point at instagram.com/ roots
        tpl = re.sub(r'<a href="https://(instagram|facebook|youtube)\.com/"[^>]*>.*?</a>',
                     "", tpl, flags=re.S)
        tpl = tpl.replace("&nbsp;&middot;&nbsp;", " ", 3)
        tpl = re.sub(r'href="#"([^>]*)>([^<]*[Uu]nsubscribe[^<]*)<',
                     'href="{{ unsubscribe_url }}"\\1>\\2<', tpl)
        tpl = re.sub(r'href="#"([^>]*)>([^<]*[Mm]anage preferences[^<]*)<',
                     'href="' + PREFERENCES_URL + '"\\1>\\2<', tpl)
    return tpl

def r_qa(slug, copy, ctx=None, max_items=4, q_pat=None, a_pat=None, **kw):
    """faq / list_questions: 'Q — A' or '· item' lines into numbered slots."""
    paras = paragraphs(copy)
    values, items, head, tail = {}, [], [], []
    for kind, lines in paras:
        if kind in ("ul", "ol"):
            items.extend(lines)
        elif kind == "p":
            joined = " ".join(lines)
            qa = re.split(r"\s+—\s+", joined, maxsplit=1)
            if len(qa) == 2 and len(items) + len([1]) <= max_items:
                items.append(joined)
            elif not items:
                head.append(joined)
            else:
                tail.append(joined)
        else:
            tail.extend(lines)
    qa_pairs = [re.split(r"\s+—\s+", i, maxsplit=1) for i in items]
    for i, pair in enumerate(qa_pairs[:max_items], 1):
        if len(pair) == 2 and q_pat:
            values[q_pat % i] = esc(pair[0].strip())
            values[a_pat % i] = esc(pair[1].strip())
        else:
            # single-slot target (no separate answer field): keep the line whole —
            # writing pair[0] alone dropped the half after the em dash.
            values[(q_pat or a_pat) % i] = esc(" — ".join(x.strip() for x in pair))
    if head:
        if "heading" in load_fields(slug):
            values["heading"] = esc(head[0])
            if len(head) > 1:
                values["body_text" if "body_text" in load_fields(slug) else "intro_text"] = paras_html([("p", head[1:])])
        else:
            values["body_text"] = paras_html([("p", head)])
    if tail:
        field = "closing_text" if "closing_text" in load_fields(slug) else "body_text"
        values[field] = paras_html([("p", tail)] if all(not l.startswith("{{") and not l.startswith("[") for l in tail) else paragraphs("\n".join(tail)))
    return render(slug, values)

_FIELDS_CACHE = {}
def load_fields(slug):
    if slug not in _FIELDS_CACHE:
        p = os.path.join(mm.REF, "emails_modules_hubspot versionr", slug + "_light.module", "fields.json")
        _FIELDS_CACHE[slug] = {f["name"]: f for f in json.load(open(p, encoding="utf-8"))}
    return _FIELDS_CACHE[slug]

def r_list_questions(slug, copy, ctx, **kw):
    return r_qa(slug, copy, ctx, max_items=6, q_pat=None, a_pat="question_%d")

def r_faq(slug, copy, ctx, **kw):
    return r_qa(slug, copy, ctx, max_items=4, q_pat="question_%d", a_pat="answer_%d")

def r_strip(slug, copy, ctx=None, label_pat="item_%d_label", text_pat="item_%d_text", max_items=4, **kw):
    """list_trust_strip / list_support_strip: 'Label — text' or plain lines."""
    paras = paragraphs(copy)
    items = []
    for kind, lines in paras:
        if kind in ("ul", "ol"):
            items.extend(lines)
        elif kind == "p":
            items.extend(lines)
        else:
            items.extend(lines)
    values = {}
    for i, item in enumerate(items[:max_items], 1):
        pair = re.split(r"\s+—\s+|:\s+", item, maxsplit=1)
        if len(pair) > 1 and len(pair[0].strip()) <= 40 and not pair[0].rstrip().endswith(("?", ".", "!")):
            values[label_pat % i] = esc(pair[0].strip())
            values[text_pat % i] = esc(pair[1].strip())
        else:
            values[label_pat % i] = esc(item.strip())
    if len(items) > max_items:
        values["closing_text"] = esc(" ".join(items[max_items:]))
    return render(slug, values)

def r_quote(slug, copy, ctx=None, **kw):
    paras = paragraphs(copy)
    values = {}
    if paras:
        kind, lines = paras[0]
        if kind == "placeholder":
            values["quote" if "quote" in load_fields(slug) else "quote_text"] = loud(" ".join(lines))
        else:
            values["quote" if "quote" in load_fields(slug) else "quote_text"] = esc(" ".join(lines))
    if len(paras) > 1 and paras[1][0] == "p":
        values["attribution"] = esc(re.sub(r"^[—-]\s*", "", " ".join(paras[1][1])))
    return render(slug, values)

def r_testimonial(slug, copy, ctx=None, **kw):
    paras = paragraphs(copy)
    values, n = {}, 0
    for kind, lines in paras:
        if n >= 3:
            break
        text = " ".join(lines)
        m = re.match(r"[\"“](.*?)[\"”]\s*[—-]\s*(.+)", text)
        n += 1
        if kind == "placeholder":
            values[f"testimonial_{n}_quote"] = loud(text)
        elif m:
            values[f"testimonial_{n}_quote"] = esc(m.group(1))
            values[f"testimonial_{n}_attribution"] = esc(m.group(2))
        else:
            values[f"testimonial_{n}_quote"] = esc(text)
    return render(slug, values)

    tpl = re.sub(r'href="#"([^>]*)>([^<]*[Pp]references[^<]*)<',
                 f'href="{PREFERENCES_URL}"\\1>\\2<', tpl)
    tpl = tpl.replace("Eahitajate tee", "Ehitajate tee")
    if slug == "footer_social":
        # no public social profiles exist for the store (verified 2026-08-19) —
        # drop the social row rather than link instagram.com/ roots
        tpl = re.sub(r'<a href="https://instagram\.com/".*?(?=<a href="\{\{|<a href="#")', "", tpl, flags=re.S)
        tpl = re.sub(r'<a href="https://(instagram|facebook|youtube)\.com/"[^>]*>.*?</a>(&nbsp;·&nbsp;|\s|&nbsp;)*',
                     "", tpl, flags=re.S)
        tpl = re.sub(r'href="#"([^>]*)>([^<]*[Uu]nsubscribe[^<]*)<', f'href="{UNSUB}"\\1>\\2<', tpl)
        tpl = re.sub(r'href="#"([^>]*)>([^<]*[Mm]anage preferences[^<]*)<',
                     f'href="{PREFERENCES_URL}"\\1>\\2<', tpl)
    return tpl


def r_promo_code(slug, copy, ctx=None, **kw):
    values = {}
    m = re.search(r"Code:\s*(\S+)", copy)
    if m:
        values["promo_code"] = esc(m.group(1))
    m = re.search(r"(Valid[^\n]*)", copy)
    if m:
        values["promo_detail"] = esc(m.group(1).strip())
    rest = [p for p in paragraphs(copy)
            if p[0] != "placeholder" and not any("Code:" in l or l.startswith("Valid") for l in p[1])]
    if rest:
        values["body_text"] = paras_html(rest)
    return render(slug, values)

def r_deadline(slug, copy, ctx=None, **kw):
    paras = paragraphs(copy)
    values = {}
    texts = [" ".join(l) for k, l in paras]
    if paras and paras[0][0] == "placeholder":
        values["deadline_text"] = loud(texts[0])
    elif texts:
        values["deadline_text"] = esc(texts[0])
    if len(texts) > 1:
        values["body_text"] = paras_html([("p", texts[1:])])
    return render(slug, values)

def r_review_stars(slug, copy, ctx=None, **kw):
    paras = paragraphs(copy)
    values = {}
    texts = [" ".join(l) for k, l in paras]
    if not texts or paras[0][0] == "placeholder":
        # never invent a rating — fail loudly until Proof Bank supplies one
        values["rating_text"] = loud(texts[0] if texts else "[PULL from Proof Bank: current average rating + review count]")
    else:
        values["rating_text"] = esc(texts[0])
        if len(texts) > 1:
            values["count_text"] = esc(texts[1])
    return render(slug, values)

def r_offer(slug, copy, ctx=None, **kw):
    paras = paragraphs(copy)
    values = {}
    m = re.search(r"(\d+)\s*%", copy)
    if m and "[OFFER" not in copy:
        values["percentage"] = m.group(1) + "%"
    code = re.search(r"Code:\s*(\S+)", copy)
    if code:
        values["discount_code"] = esc(code.group(1))
    body_paras = []
    for kind, lines in paras:
        if kind == "placeholder":
            values.setdefault("body_text", "")
            values["body_text"] += loud(" ".join(lines))
        elif kind == "p" and not any(l.startswith("Code:") for l in lines):
            body_paras.append((kind, lines))
    if body_paras:
        first = first_line(body_paras)
        if first and len(body_paras) > 1:
            values["heading"] = esc(first)
            body_paras = body_paras[1:]
        values["body_text"] = paras_html(body_paras) + values.get("body_text", "")
    if ctx.get("dest") and ctx["dest"].startswith("http"):
        values["button_url"] = esc(ctx["dest"])
    return render(slug, values)

def inject_before_cell_end(frag, extra):
    idx = frag.rfind("</td></tr></table></td></tr></table>")
    if idx == -1:
        return frag + extra
    return frag[:idx] + extra + frag[idx:]


def r_commerce(slug, copy, ctx=None, **kw):
    """Commerce modules: keep chrome, replace dynamic payload with a loud token block."""
    paras = paragraphs(copy)
    values = {}
    head, rest = [], []
    for kind, lines in paras:
        for l in lines:
            (rest if (l.strip().startswith("{{") or l.strip().startswith("[")) else head).append(l)
    if head:
        first = head[0].rstrip(":")
        if len(first) < 60:
            values["heading"] = esc(first)
            head = head[1:]
    louds = "".join(loud(l) for l in rest) if rest else ""
    if head:
        louds = paras_html([("p", head)]) + louds
    if louds:
        if "note" in load_fields(slug):
            values["note"] = louds
        elif "fallback_body" in load_fields(slug):
            values["fallback_body"] = louds
    fields = load_fields(slug)
    if "button_text" in fields and ctx.get("cta"):
        values["button_text"] = esc(ctx["cta"].split(" / ")[0])
        if ctx.get("dest"):
            values["button_url"] = esc(ctx["dest"])
    return render(slug, values)

def _replace_items_table(html_frag, inner):
    """Swap the item-rows table's contents for `inner`, matching tags by depth.

    The cart module's static item rows are placeholders. Shopify fills the cart from
    `abandoned_checkout.line_items` at send time, so the rows must be a Liquid loop, not
    three fixed slots. A non-greedy regex cannot be used here: the rows contain nested
    tables, so the first `</table>` is not the right one.
    """
    m = re.search(r'<table[^>]*margin-top:16px;"[^>]*>', html_frag)
    if not m:
        return html_frag, False
    i = m.end()
    depth, j = 1, i
    for t in re.finditer(r"<(/?)table\b", html_frag[i:]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            j = i + t.start()
            break
    else:
        return html_frag, False
    return html_frag[:i] + inner + html_frag[j:], True


def r_cart_line_items(slug, copy, ctx=None, **kw):
    """Cart module: chrome from the template, line items from Shopify Liquid.

    `r_commerce` renders a loud placeholder for the dynamic payload, which is right for
    modules whose content a human must supply. It is wrong here: the payload is Shopify's
    own abandoned-checkout data, and the Liquid to read it is fixed. That loop was
    hand-written into the four J2 emails by 72811bf and never returned to the builder,
    which is what made the builder unable to reproduce them (#141).
    """
    # {{ cart_contents }} is a deck shorthand meaning "the cart goes here". The Liquid
    # loop below supplies exactly that, so the token is dropped from the copy before
    # rendering rather than scrubbed out of the HTML afterwards. Dropping it early also
    # fixes the inline case (CR-2 writes "Still in your cart: {{ cart_contents }}" on one
    # line, so the token would otherwise end up inside the heading).
    copy = re.sub(r"\s*\{\{\s*cart_contents\s*\}\}", "", copy or "").strip()
    # This module's CTA returns the customer to their own cart. The per-email destination is
    # a product or collection page, which is the wrong target here — recovering a cart means
    # going to the checkout, not to a listing. Committed CR-2 was corrected by hand to
    # {{ checkout.url }} for exactly this reason (#141).
    ctx = {**(ctx or {}), "dest": "{{ checkout.url }}"}
    frag = r_commerce(slug, copy, ctx, **kw)
    liquid = os.path.join(TEMPLATES, slug + ".liquid.html")
    if not os.path.exists(liquid):
        return frag
    inner = open(liquid, encoding="utf-8").read().strip()
    frag, _ = _replace_items_table(frag, inner)
    return frag
    inner = open(liquid, encoding="utf-8").read().strip()
    frag, ok = _replace_items_table(frag, inner)
    if ok:
        # The loud {{ cart_contents }} placeholder existed only to mark this payload as
        # unresolved. Real Liquid now resolves it, so the placeholder must go.
        # At renderer time the token is still bare inside loud()'s div; the inline <span>
        # is only added later by loud_inline_tokens() at document assembly. Tolerate both.
        frag = re.sub(r'<div style="border:2px dashed #EA6452[^"]*">'
                      r'(?:<span[^>]*>)?\s*\{\{\s*cart_contents\s*\}\}\s*'
                      r'(?:</span>)?</div>',
                      "", frag)
        frag = re.sub(r'<div class="hsc-rt"[^>]*>\s*</div>', "", frag)
    return frag

def r_products(slug, copy, ctx=None, max_cards=3, card_pat="product_%d", **kw):
    """Product grids: match copy-mentioned products to verified assets; else loud."""
    values = {}
    fields = load_fields(slug)
    paras = paragraphs(copy)
    if paras and paras[0][0] == "p" and "heading" in fields:
        values["heading"] = esc(first_line(paras))
        paras = paras[1:]
    matched = []
    for key, url in PRODUCTS.items():
        title = key.replace("-", " ")
        if re.search(re.escape(title), copy, re.I):
            matched.append((key, url))
    for i, (key, url) in enumerate(matched[:max_cards], 1):
        base = card_pat % i
        if base + "_image" in fields:
            values[base + "_image"] = ASSETS_BASE + ASSET_MAP["products"][key]
            values[base + "_image.alt"] = "Hair Solutions Co. " + key.replace("-", " ").title()
        for suf in ("_title", "_heading"):
            if base + suf in fields:
                values[base + suf] = esc(key.replace("-", " ").title())
        if base + "_url" in fields:
            values[base + "_url"] = esc(utm(url, ctx["campaign"]))
    leftover = [p for p in paras if p[0] == "placeholder"]
    if leftover and "body_text" in fields:
        values["body_text"] = paras_html(leftover)
    return render(slug, values)

def r_image_text(slug, copy, ctx=None, **kw):
    """column_image_and_text / photo_feature_story / hero_photo_led / commerce_viewed_product."""
    paras = paragraphs(copy)
    values = {}
    fields = load_fields(slug)
    text_paras = [p for p in paras if p[0] != "placeholder"]
    img_notes = [" ".join(l) for k, l in paras if k == "placeholder" and "image" in " ".join(l).lower()]
    if text_paras:
        first = first_line(text_paras)
        head_field = "headline" if "headline" in fields else ("heading" if "heading" in fields else None)
        if head_field and first and len(text_paras) > 1:
            values[head_field] = esc(first)
            text_paras = text_paras[1:]
        if "body_text" in fields and text_paras:
            values["body_text"] = paras_html(text_paras)
        elif text_paras:
            card_fields = [f for f in fields if re.match(r"card\d_text", f)]
            for i, p in enumerate(text_paras):
                if i < len(card_fields):
                    values[card_fields[i]] = esc(" ".join(p[1]))
    if "button_text" in fields and ctx.get("cta"):
        values["button_text"] = esc(ctx["cta"].split(" / ")[0])
        if ctx.get("dest"):
            values["button_url"] = esc(ctx["dest"])
    out = render(slug, values)
    for note in img_notes:
        out = inject_before_cell_end(out, loud(note))
    return out

def _two_sided(lines):
    """Does this copy actually contrast two things? The module frames column A as
    'The old routine' and column B as 'With Atelier Zero', so splitting a plain option
    list down the middle asserts a contrast the copy never makes."""
    joined = " ".join(lines).lower()
    return bool(re.search(r"\bvs\.?\b|\bversus\b|\bbefore\b.*\bafter\b|\binstead of\b", joined))

def r_comparison(slug, copy, ctx=None, **kw):
    paras = paragraphs(copy)
    lines = []
    for kind, ls in paras:
        lines.extend(ls)
    items = [l for l in lines if " — " in l or "–" in l] or lines
    values = {}
    if _two_sided(items):
        half = (len(items) + 1) // 2
        cols = {"a": items[:half], "b": items[half:]}
        for col, its in cols.items():
            for i, item in enumerate(its[:3], 1):
                values[f"column_{col}_item_{i}"] = esc(item.strip())
    else:
        # a plain option list: fill one column in order and blank both column labels
        # so the 'old routine / with Atelier Zero' framing is not asserted. Anything
        # past row 3 is picked up by carry_overflow and appended verbatim.
        values["column_a_label"] = ""
        values["column_b_label"] = ""
        for i, item in enumerate(items[:3], 1):
            values[f"column_a_item_{i}"] = esc(item.strip())
    out = render(slug, values)
    trailing = [l for l in lines if l not in items]
    if trailing:
        out = inject_before_cell_end(out, paras_html([("p", trailing)]))
    return out

def r_timeline(slug, copy, ctx=None, **kw):
    paras = paragraphs(copy)
    lines = []
    for kind, ls in paras:
        lines.extend(ls)
    values = {}
    steps = [l for l in lines if re.match(r"^(Day|Week|Step|\d)", l)]
    rest = [l for l in lines if l not in steps]
    for i, s in enumerate(steps[:4], 1):
        pair = re.split(r"\s+—\s+|:\s+", s, maxsplit=1)
        values[f"step_{i}_time"] = esc(pair[0].strip())
        if len(pair) > 1:
            values[f"step_{i}_label"] = esc(pair[1].strip())
    if rest:
        if "heading" in load_fields(slug):
            values["heading"] = esc(rest[0])
            rest = rest[1:]
        if rest:
            bf = "body_text" if "body_text" in load_fields(slug) else "step_4_text"
            values[bf] = esc(" ".join(rest))
    return render(slug, values)

def r_stat_bars(slug, copy, ctx=None, **kw):
    paras = paragraphs(copy)
    values = {}
    flat = [(kind, l) for kind, ls in paras for l in ls]
    stats = []
    for kind, l in flat:
        m = re.match(r"(.+?)\s+—\s+(.+)", l)
        if m and kind != "placeholder":
            stats.append((m.group(1), m.group(2)))
    for i, (label, value) in enumerate(stats[:3], 1):
        values[f"bar_{i}_label"] = esc(label.strip())
        values[f"bar_{i}_value"] = esc(value.strip())
        pm = re.search(r"(\d+)\s*%", value)
        if pm:
            values[f"bar_{i}_percent"] = pm.group(1)
    others = [l for k, l in flat if not any(l.startswith(s[0]) for s in stats)]
    if others:
        values["body_text"] = paras_html(paragraphs("\n".join(others)))
    return render(slug, values)

def r_dynamic(slug, copy, ctx=None, **kw):
    """text_customer_snapshot / text_base_type_guidance: choice-branch modules.
    Replace the sample narrative, keep the card + CTA slots."""
    paras = paragraphs(copy)
    tpl = load_template(slug)
    tpl = re.sub(r'<p style="margin:0 0 12px;font-size:16px;line-height:1\.6;color:#25221D;">.*?</p>',
                 "", tpl, flags=re.S)
    body = paras_html(paras) if paras else ""
    if body:
        tpl = inject_before_cell_end(tpl, '<div style="font-size:16px;line-height:1.6;color:#25221D;">'
                                     + body + "</div>")
    fields = load_fields(slug)
    values = {}
    cta = ctx.get("cta") or ""
    usable_cta = cta and "/" not in cta and "No button" not in cta
    if "cta_label" in fields and usable_cta:
        values["cta_label"] = esc(cta)
    # fallback_cta_label was hardcoded in the preview ("Book a consultation"); it is now a
    # slot, so the approved CTA governs and no email carries two conflicting button labels.
    if usable_cta:
        values["fallback_cta_label"] = esc(cta)
    for uf in ("cta_url", "fallback_cta_url"):
        if uf in fields:
            dest = ctx.get("dest") or CONTACT
            values[uf] = esc(dest if dest.startswith(("http", "{{")) else CONTACT)
    return drop_empty_slots(fill(tpl, values))

def r_generic(slug, copy, ctx=None, **kw):
    fields = load_fields(slug)
    paras = paragraphs(copy)
    values = {}
    head_field = next((f for f in ("heading", "headline", "title") if f in fields), None)
    body_field = next((f for f in ("body_text", "intro_text", "fallback_body") if f in fields), None)
    if head_field and paras and paras[0][0] == "p" and len(paras) > 1 \
            and not re.match(r"^(Hi|Hey|Dear)\b", " ".join(paras[0][1])):
        values[head_field] = esc(first_line(paras))
        paras = paras[1:]
    if body_field and paras:
        values[body_field] = paras_html(paras)
    elif paras:
        return inject_before_cell_end(render(slug, values), paras_html(paras))
    return render(slug, values)


RENDERERS = {
    "text_opening": r_text_opening,
    "text_masthead": r_masthead,
    "layout_founder_wrapper": r_founder_wrapper,
    "button_primary_cta": r_button,
    "button_final_cta": r_button,
    "header_centered_logo": r_static,
    "footer_social": r_static,
    "footer_standard": r_static,
    "footer_wide": r_static,
    "footer_preference_centre": r_static,
    "faq": r_faq,
    "list_questions": r_list_questions,
    "list_trust_strip": lambda s, c, ctx, **k: r_strip(s, c, ctx, "item_%d_label", "item_%d_text", 4),
    "list_support_strip": lambda s, c, ctx, **k: r_strip(s, c, ctx, "item_%d_label", "item_%d_value", 3),
    "quote_centered": r_quote,
    "quote_accent_bar": r_quote,
    "testimonial": r_testimonial,
    "signal_promo_code": r_promo_code,
    "signal_offer_deadline": r_deadline,
    "signal_review_stars": r_review_stars,
    "text_offer_discount": r_offer,
    "comparison": r_comparison,
    "timeline": r_timeline,
    "stat_bars": r_stat_bars,
    "text_customer_snapshot": r_dynamic,
    "text_base_type_guidance": r_dynamic,
    "product_3up_grid": lambda s, c, ctx, **k: r_products(s, c, ctx, 3, "product_%d"),
    "grid_collections_4": lambda s, c, ctx, **k: r_products(s, c, ctx, 4, "card_%d"),
    "product_dynamic_recommendations": lambda s, c, ctx, **k: r_products(s, c, ctx, 2, "product_%d"),
}
for _s in ("commerce_cart_line_items", "commerce_order_summary", "commerce_quote_spec_table",
           "commerce_shipping_tracking", "commerce_viewed_product"):
    RENDERERS[_s] = r_commerce
RENDERERS["commerce_cart_line_items"] = r_cart_line_items
for _s in ("column_image_and_text", "photo_feature_story", "hero_photo_led"):
    RENDERERS[_s] = r_image_text
for _s in ("text_section", "text_reassurance", "hero_text_led", "photo_founder_note",
           "text_five_changes", "text_founder_pillars", "list_belief", "proof"):
    RENDERERS.setdefault(_s, r_heading_body)


def squash(s):
    """norm_text with every space removed — tag stripping leaves stray whitespace."""
    return re.sub(r"\s+", "", norm_text(s))

def _module_copy_lines(copy):
    """Content lines of one module's copy block, marker lines excluded."""
    out = []
    for line in copy.split("\n"):
        t = line.strip()
        if not t or is_marker_line(line) or t.startswith(("⚠️", "📎")):
            continue
        out.append(t)
    return out

def carry_overflow(frag, copy, slug):
    """Nothing in an approved Body may be dropped because a module ran out of slots.

    Renderers write into a fixed number of template slots; copy beyond that count was
    being discarded silently (W-2's base-type lines, PP-2's numbered steps). Any content
    line that did not reach the fragment is appended to it instead. Real prose renders as
    prose; build tokens ([PULL ...], {{ dynamic: ... }}) render loud so review sees them.
    Returns (fragment, carried_lines).
    """
    if frag is None:
        return frag, []
    rendered = squash(frag)
    carried = []
    for line in _module_copy_lines(copy):
        for probe in coverage_probes(line):
            if squash(probe) and squash(probe) in rendered:
                break
        else:
            carried.append(line)
    if not carried:
        return frag, []
    blocks = []
    for line in carried:
        if line.startswith(("[", "{{")) or "PULL" in line or "OFFER" in line:
            blocks.append(loud(line))
        else:
            blocks.append(paras_html([("p", [line])]))
    return inject_before_cell_end(frag, "".join(blocks)), carried

def render_module(slug, copy, ctx):
    return RENDERERS.get(slug, r_generic)(slug, copy, ctx)


# ------------------------------------------------------------------ assembly
STATIC_MODULES = {"header_centered_logo", "footer_social", "footer_standard",
                  "footer_wide", "footer_preference_centre"}

def compliance_strip(html_doc, campaign):
    """Append whatever compliance pieces the footers didn't cover."""
    need_addr = "Ehitajate tee" not in html_doc and "Eahitajate tee" not in html_doc
    need_unsub = "unsubscribe_url" not in html_doc
    if not (need_addr or need_unsub):
        return ""
    parts = []
    if need_addr:
        parts.append(f"Hair Solutions Co.<br>{ADDRESS}")
    links = []
    if need_unsub:
        links.append(f'<a href="{UNSUB}" style="color:#25221D;text-decoration:underline;">Unsubscribe</a>')
    links.append(f'<a href="{PREFERENCES_URL}" style="color:#25221D;text-decoration:underline;">Manage preferences</a>')
    links.append('<a href="https://hairsolutions.co/policies/privacy-policy" style="color:#25221D;text-decoration:underline;">Privacy</a>')
    parts.append(" &middot; ".join(links))
    return ('<table border="0" cellpadding="0" cellspacing="0" role="presentation" '
            'style="background-color:transparent;border-collapse:collapse;margin:0;" width="100%">'
            '<tr><td align="center" style="padding:7px 16px 24px;">'
            '<div style="font-family:\'Helvetica Neue\',Helvetica,Arial,sans-serif;font-size:11px;'
            'line-height:1.7;color:#25221D;text-align:center;">'
            + "<br>".join(parts) + "</div></td></tr></table>")

def loud_inline_tokens(doc):
    """Any leftover non-Shopify {{ token }} becomes an inline loud marker."""
    # Real Shopify Messaging variables. Anything else is an unresolved deck placeholder and
    # is marked loud. The abandoned-checkout loop variables belong here: they are emitted by
    # r_cart_line_items as genuine Liquid, and marking them loud wrapped live Shopify
    # variables in placeholder chrome (#141).
    keep = ("customer.first_name", "unsubscribe_url", "checkout.url", "unsubscribe_link",
            "line_item.", "abandoned_checkout.")
    def repl(m):
        tok = m.group(0)
        if any(k in tok for k in keep):
            return tok
        # the token text is already escaped at this point (esc/paras_html/loud all ran) —
        # escaping again produced "&amp;amp;", which renders literally in the client.
        # unescape first so the round trip is idempotent.
        return (f'<span style="background-color:#F6EFD9;border-bottom:2px dashed #EA6452;'
                f'font-family:\'Courier New\',Courier,monospace;font-size:90%;">'
                f'{esc(html.unescape(tok))}</span>')
    return re.sub(r"\{\{[^{}]*\}\}", repl, doc)

def founder_split(body, stack_fams):
    """No-marker founder body: narrative to the wrapper, special lines to modules."""
    assignment = {}
    wrapper_paras = []
    special = {}
    for kind, lines in paragraphs(body):
        keep, move = [], []
        for l in lines:
            s = l.strip()
            if s == "{{ cart_contents }}":
                special.setdefault("commerce_cart_line_items", []).append(s)
            elif re.match(r"^Code:\s*\S+", s) or re.match(r"^Valid\b", s):
                special.setdefault("signal_promo_code", []).append(s)
            elif "free shipping" in s.lower() and "text_offer_discount" in stack_fams:
                special.setdefault("text_offer_discount", []).append(s)
            else:
                keep.append(l)
        if keep:
            wrapper_paras.append("\n".join(keep))
    assignment["layout_founder_wrapper"] = "\n\n".join(wrapper_paras)
    for k, v in special.items():
        assignment[k] = "\n".join(v)
    return assignment

def assemble(row):
    name = row["Email name"]
    prefix = email_prefix(name)
    campaign = slugify(name)
    cta = row["CTA"].strip()
    dest = DESTINATIONS.get(prefix)
    ctx = {"cta": cta,
           "dest": utm(dest, campaign) if dest and dest.startswith("http") else dest,
           "campaign": campaign, "name": name}
    stack = [(req, mm.family_of(raw), mm.resolve(mm.family_of(raw))[0])
             for req, raw in mm.parse_stack(row["Module Stack"])]
    preamble, blocks = parse_body(row["Body"])
    queues = {}
    for fams, copy in blocks:
        for fam in fams:
            key = mm.resolve(mm.family_of(fam))[0] or fam
            queues.setdefault(key, []).append(copy)
    modules, styles, notes, deviations = [], {}, [], []
    founder_mode = not blocks
    founder_assign = founder_split(row["Body"], {s for _, _, s in stack}) if founder_mode else {}
    for required, fam, slug in stack:
        if slug is None:
            notes.append(f"BLOCKER: unresolved module family {fam}")
            continue
        copy = None
        if founder_mode:
            copy = founder_assign.get(slug)
        if copy is None and queues.get(slug):
            copy = queues[slug].pop(0)
        if copy is None and slug in STATIC_MODULES:
            copy = ""
        if copy is None and slug in ("button_primary_cta", "button_final_cta") and "No button" not in cta:
            copy = cta.split(" / ")[0]
        if copy is None:
            if required:
                notes.append(f"BLOCKER: required module ({fam}) has no copy block")
            else:
                deviations.append(f"dropped optional [{fam}] — no copy block")
            continue
        # Only the checkout-abandonment journey has abandoned_checkout.* populated.
        # email_prefix() returns the full code ("CR-3"), so match the family.
        copy_t = translate_tokens(copy, abandoned_checkout=prefix.startswith("CR-"))
        # The cart module resolves {{ cart_contents }} into a Shopify Liquid loop over
        # abandoned_checkout.line_items, so the token is not copy that went missing.
        # Without this, carry_overflow() sees it absent from the render and re-appends it
        # verbatim after the rendered items — which is how it survived the renderer's own
        # strip (#141).
        if slug == "commerce_cart_line_items":
            copy_t = re.sub(r"\s*\{\{\s*cart_contents\s*\}\}", "", copy_t).strip()
        if slug == "comparison" and copy_t.strip() and not _two_sided([copy_t]) \
                and not copy_t.strip().startswith(("{{", "[")):
            deviations.append("(Comparison) copy is an option list, not a two-sided "
                              "comparison — column labels blanked; consider FAQ or "
                              "List - Questions for this slot")
        frag = render_module(slug, copy_t, ctx)
        frag, carried = carry_overflow(frag, copy_t, slug)
        if carried:
            deviations.append("overflow carried into (%s): %d line(s) beyond the module's "
                              "slots, appended verbatim" % (fam, len(carried)))
        sp = os.path.join(TEMPLATES, slug + ".styles.html")
        if os.path.exists(sp):
            styles[slug] = open(sp, encoding="utf-8").read()
        modules.append((fam, frag))
    if founder_mode and " / " in cta:
        first, second = [c.strip() for c in cta.split(" / ", 1)]
        d1 = ctx["dest"] or TODO_REVIEW_PAGE
        dual = (f'<div style="padding-top:16px;"><a href="{esc(d1)}" style="color:#151411;font-weight:700;">{esc(first)}</a>'
                f' &nbsp;&middot;&nbsp; <a href="mailto:info@hairsolutions.co" style="color:#151411;font-weight:700;">{esc(second)}</a></div>')
        modules = [(f, inject_before_cell_end(fr, dual) if f == "Layout - Plain-text founder wrapper" else fr)
                   for f, fr in modules]
        deviations.append(f"dual CTA rendered in-wrapper: '{first}' -> {d1}; '{second}' -> mailto:info@hairsolutions.co")
    return name, preamble, modules, styles, notes, deviations, ctx

def email_doc(row, preamble, modules, styles):
    name = row["Email name"]
    preheader = esc(row["Preview Text"].strip()) or ""
    comments = "\n".join("<!-- BUILD NOTE: " + esc(translate_tokens(p)) + " -->" for p in preamble)
    style_block = "\n".join(dict.fromkeys(styles.values()))
    parts = ["<!-- module: " + fam + " -->\n" + frag for fam, frag in modules]
    body_inner = "\n".join(parts)
    head = (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="color-scheme" content="light">\n'
        '<meta name="supported-color-schemes" content="light">\n'
        "<title>" + esc(name) + "</title>\n" + style_block + "\n</head>\n"
        '<body style="margin:0;padding:0;background-color:transparent;">\n'
        + comments + "\n"
        '<div style="display:none;font-size:1px;line-height:1px;max-height:0;max-width:0;'
        'opacity:0;overflow:hidden;mso-hide:all;">' + preheader
        + "&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;</div>\n"
        '<table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%" '
        'style="background-color:transparent;border-collapse:collapse;margin:0;">\n'
        '<tr><td align="center" style="padding:0;">\n'
        + body_inner + "\n")
    tail = "\n</td></tr></table>\n</body>\n</html>\n"
    doc = head + compliance_strip(head, slugify(name)) + tail
    return loud_inline_tokens(doc)


# ------------------------------------------------------------------ validator
KEEP_IMAGE_HOSTS = ("assets.hairsolutions.co", "res.cloudinary.com")

def norm_text(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def body_content_lines(body):
    """Content lines of the Body: no markers, no ops preamble, tokens translated.

    The preamble is everything before the first module marker — the GATED warnings and
    the 📋 TEMPLATE / FILL CHECKLIST operator notes. Those are build instructions for
    whoever fills the edition, never email copy; they are emitted as HTML build-note
    comments by email_doc(). Validating them as body copy reported false losses.
    """
    preamble, blocks = parse_body(body)
    out = []
    for _fams, copy in blocks:
        for line in copy.split("\n"):
            s = line.strip()
            if not s or s.startswith(("⚠️", "📎")):
                continue
            out.append(translate_tokens(s))
    return out

def coverage_probes(line):
    """Acceptable renderings of a copy line (label-stripped forms allowed)."""
    yield line
    if line.endswith(":"):
        yield line[:-1]  # module headings drop the trailing colon
    m = re.match(r"^Code:\s*(\S+)", line)
    if m:
        yield m.group(1)
    m = re.match(r"^[-·•]\s+(.*)", line)
    if m:
        yield m.group(1)
    m = re.match(r"^\d+[.)]\s+(.*)", line)
    if m:
        yield m.group(1)  # numbered lines render as <ol> items, without the "1. " prefix

# Deck shorthand that a renderer resolves into real Shopify Liquid rather than into text.
# The copy line will not appear in the output, so coverage is proved by the presence of the
# markup it was replaced by — never by ignoring the line.
RESOLVED_TOKENS = {
    "{{ cart_contents }}": "abandoned_checkout.line_items",
    "{{ last_viewed_product }}": "abandoned_checkout.line_items.first.product_title",
}

def coverage_misses(row, doc):
    text = squash(doc)
    misses = []
    for line in body_content_lines(row["Body"]):
        for probe in coverage_probes(line):
            if squash(probe) in text:
                break
        else:
            resolved = next((mark for tok, mark in RESOLVED_TOKENS.items()
                             if tok in line and mark in doc), None)
            if resolved:
                continue
            misses.append(line)
    return misses

def validate(row, doc, used_slugs):
    issues = []
    if "{{slot:" in doc:
        issues.append("leftover template slot(s): " +
                      ", ".join(sorted(set(re.findall(r"\{\{slot:([\w.]+)\}\}", doc)))))
    for slug in used_slugs:
        if slug in STATIC_MODULES:
            continue
        for fname, fld in load_fields(slug).items():
            if fname in ("signature_name", "signature_role", "company_name",
                         "company_address", "logo_image", "photo", "logo_url"):
                continue  # identity/brand defaults are intended content
            d = fld.get("default")
            if not isinstance(d, str) or len(re.sub(r"<[^>]+>", "", d)) < 12:
                continue
            probe = norm_text(re.sub(r"<[^>]+>", " ", d))
            intended = norm_text(translate_tokens(row["Body"] + "\n" + row.get("CTA", "")))
            if probe and probe in norm_text(doc) and probe not in intended:
                issues.append("sample default leaked (%s.%s): %s" % (slug, fname, probe[:60]))
    for mline in coverage_misses(row, doc):
        issues.append("copy not found: " + mline[:90])
    if "{{ unsubscribe_url }}" not in doc and "{{ unsubscribe_link }}" not in doc:
        issues.append("no unsubscribe token")
    if "Ehitajate tee" not in doc and "Eahitajate tee" not in doc:
        issues.append("no physical address")
    if '<body style="margin:0;padding:0;background-color:transparent;' not in doc:
        issues.append("page background regression")
    if "@media only screen and (max-width:480px)" not in doc:
        issues.append("no mobile media query")
    for img in re.findall(r"<img [^>]*>", doc):
        if "alt=" not in img:
            issues.append("img without alt: " + img[:80])
        m = re.search('src="([^"]+)"', img)
        if m and not m.group(1).startswith(("http", "{{")):
            issues.append("img src not absolute: " + m.group(1)[:80])
        elif m and m.group(1).startswith("http") and not any(h in m.group(1) for h in KEEP_IMAGE_HOSTS):
            issues.append("img host not approved: " + m.group(1)[:80])

    if "?variant=" in doc:
        issues.append("?variant= URL (AVIF trap)")
    size_kb = len(doc.encode("utf-8")) / 1024
    if size_kb > 500:
        issues.append("over Shopify 500KB custom-code limit (%.0f KB)" % size_kb)
    return issues, size_kb

# ----------------------------------------------------------------------- main
BUILD_ORDER_PREFIXES = (
    ["CR-1", "CR-2", "CR-3", "CR-4", "BR-1"]                      # J2
    + ["PP-1", "PP-2", "PP-3", "PP-4", "PP-5", "PP-6", "PP-7", "PP-7b"]  # J1
    + ["W-1", "W-2", "W-3", "W-4", "W-5"]                          # W
    + ["RO-1", "RO-2", "RO-3", "RO-4", "RO-5", "RO-6"]            # J4
    + ["WB-1", "WB-2", "WB-3", "WB-4"]                            # J3
    + ["C-0", "C-1", "C-2", "C-3", "C-4"]                         # J5
    + ["NL-%02d" % i for i in range(1, 21)]                       # N
)

def main():
    only = None
    if len(sys.argv) > 1 and sys.argv[1] != "--check-links":
        only = sys.argv[1]
    rows = list(csv.DictReader(open(mm.EMAILS_CSV, encoding="utf-8-sig")))
    def order_key(r):
        p = email_prefix(r["Email name"])
        return BUILD_ORDER_PREFIXES.index(p) if p in BUILD_ORDER_PREFIXES else 999
    rows = [r for r in rows if email_prefix(r["Email name"]) in BUILD_ORDER_PREFIXES]
    rows.sort(key=order_key)
    assert len(rows) == 53, len(rows)
    os.makedirs(OUT_DIR, exist_ok=True)
    ledger = []
    n_green = n_blocked = 0
    for i, row in enumerate(rows, 1):
        name = row["Email name"]
        if only and not name.startswith(only):
            continue
        name, preamble, modules, styles, notes, deviations, ctx = assemble(row)
        doc = email_doc(row, preamble, modules, styles)
        used_slugs = [mm.resolve(mm.family_of(f))[1] and mm.resolve(mm.family_of(f))[0]
                      for _, f in [(None, fam) for fam, _ in modules]]
        used_slugs = [mm.resolve(mm.family_of(fam))[0] for fam, _ in modules]
        issues, size_kb = validate(row, doc, used_slugs)
        blockers = [n for n in notes if n.startswith("BLOCKER")] + \
                   [i2 for i2 in issues if i2.startswith("copy not found")]
        status = "BLOCKED" if any(n.startswith("BLOCKER") for n in notes) else \
                 ("GREEN" if not issues else "ISSUES")
        if status == "GREEN":
            n_green += 1
        if status == "BLOCKED":
            n_blocked += 1
        fname = "%02d-%s.html" % (i, slugify(name))
        open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8").write(doc)
        ledger.append({
            "file": fname, "email": name, "status": status, "size_kb": round(size_kb, 1),
            "modules": [fam for fam, _ in modules],
            "gated": any(p.startswith(("⚠️", "📎")) for p in preamble),
            "preamble_notes": preamble,
            "blockers": [n for n in notes if n.startswith("BLOCKER")],
            "issues": issues, "deviations": deviations,
            "loud_placeholders": doc.count("border:2px dashed #EA6452"),
        })
        print("%-58s %-7s %5.1fKB  modules:%2d  loud:%d  issues:%d" %
              (name[:58], status, size_kb, len(modules), ledger[-1]["loud_placeholders"], len(issues)))
        for it in issues:
            print("     !", it[:150])
        for d in deviations:
            print("     ~", d[:150])
    json.dump(ledger, open(os.path.join(ROOT, "shopify-messaging", "build-ledger.json"), "w"),
              indent=1, ensure_ascii=False)
    print("\n%d GREEN  %d BLOCKED  %d ISSUES  (ledger: shopify-messaging/build-ledger.json)"
          % (n_green, n_blocked, len(ledger) - n_green - n_blocked))

if __name__ == "__main__":
    main()
