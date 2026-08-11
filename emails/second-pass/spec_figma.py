"""Turn the composed emails into a structural spec Figma can build natively.

Figma is the review surface, so the frames are real text nodes on real auto-layout —
not a flattened screenshot. Type maps to the design system's stated intent rather than
the email-safe fallbacks, because those fonts exist here:
    eyebrow  -> JetBrains Mono Regular      (the live monospace eyebrow convention)
    heading  -> Inter Tight Bold
    accent   -> Playfair Display Italic
    body     -> Inter Regular
"""
import json, re, html as htmllib
from emails import EMAILS
from surface import SURFACES
from render_emails import defaults, OPT_DOWN_ASK

PARA = re.compile(r"<p[^>]*>(.*?)</p>", re.S)


def clean(s):
    """HTML fragment -> plain text, keeping <br> as a line break."""
    if not s:
        return ""
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return htmllib.unescape(s).strip()


def paras(rich):
    found = [clean(m.group(1)) for m in PARA.finditer(rich or "")]
    return [p for p in found if p] or ([clean(rich)] if clean(rich) else [])


def bold_runs(rich):
    """Which leading fragment of each paragraph was <b>-wrapped, for run styling."""
    out = []
    for m in PARA.finditer(rich or ""):
        b = re.match(r"\s*<b>(.*?)</b>", m.group(1), re.S)
        out.append(clean(b.group(1)) if b else None)
    return out


def val(ctx, k, d=""):
    v = ctx.get(k, d)
    return v if isinstance(v, str) else d


def items_for(folder, ctx):
    it = []
    if folder == "header_centered_logo":
        it.append({"t": "logo", "align": "center"})
        if val(ctx, "preheader_note"):
            it.append({"t": "meta", "s": val(ctx, "preheader_note"), "align": "center"})
        return it

    if folder == "plain_text_founder_wrapper":
        it.append({"t": "p", "s": val(ctx, "greeting")})
        bl = bold_runs(ctx.get("letter_text"))
        for i, p in enumerate(paras(ctx.get("letter_text"))):
            it.append({"t": "p", "s": p, "bold": bl[i] if i < len(bl) else None})
        if val(ctx, "signature"):
            # the signature carries a <br> between name and role
            it.append({"t": "sig", "s": clean(val(ctx, "signature"))})
        if ctx.get("show_button") == "yes" and val(ctx, "button_label"):
            it.append({"t": "btn", "s": val(ctx, "button_label")})
        return it

    if folder in ("commerce_order_summary", "commerce_shipping_tracking",
                  "commerce_quote_spec_table"):
        if val(ctx, "eyebrow"):
            it.append({"t": "eyebrow", "s": val(ctx, "eyebrow")})
        if val(ctx, "heading"):
            it.append({"t": "h", "s": val(ctx, "heading")})
        pairs = ([("label_order", "value_order"), ("label_spec", "value_spec"),
                  ("label_status", "value_status"), ("label_eta", "value_eta")]
                 if folder == "commerce_order_summary" else
                 [("label_carrier", "value_carrier"), ("label_tracking", "value_tracking"),
                  ("label_eta", "value_eta")]
                 if folder == "commerce_shipping_tracking" else
                 [(f"label_{i}", f"value_{i}") for i in range(1, 6)])
        for lk, vk in pairs:
            if val(ctx, lk):
                it.append({"t": "kv", "k": val(ctx, lk), "v": val(ctx, vk)})
        if clean(ctx.get("note")):
            it.append({"t": "small", "s": clean(ctx.get("note"))})
        if val(ctx, "button_label"):
            it.append({"t": "btn", "s": val(ctx, "button_label")})
        return it

    if folder == "promo_code_block":
        if val(ctx, "heading"):
            it.append({"t": "h", "s": val(ctx, "heading")})
        it.append({"t": "code", "s": val(ctx, "promo_code")})
        if clean(ctx.get("terms_text")):
            it.append({"t": "small", "s": clean(ctx.get("terms_text"))})
        if val(ctx, "button_label"):
            it.append({"t": "btn", "s": val(ctx, "button_label")})
        return it

    if folder in ("text_block_generic", "text_base_type_guidance"):
        if val(ctx, "eyebrow"):
            it.append({"t": "eyebrow", "s": val(ctx, "eyebrow")})
        if val(ctx, "heading"):
            it.append({"t": "h", "s": val(ctx, "heading"), "accent": val(ctx, "heading_accent")})
        bl = bold_runs(ctx.get("body_text"))
        for i, p in enumerate(paras(ctx.get("body_text"))):
            it.append({"t": "p", "s": p, "bold": bl[i] if i < len(bl) else None})
        if ctx.get("show_button") == "yes" and val(ctx, "button_label"):
            it.append({"t": "btn", "s": val(ctx, "button_label")})
        return it

    if folder == "cta_dual_buttons":
        it.append({"t": "btnrow", "primary": val(ctx, "primary_label"),
                   "secondary": val(ctx, "secondary_label")})
        return it

    if folder in ("preference_opt_down", "footer_standard"):
        ask = False
        if val(ctx, "eyebrow"):
            it.append({"t": "eyebrow", "s": val(ctx, "eyebrow")}); ask = True
        if val(ctx, "heading"):
            it.append({"t": "h", "s": val(ctx, "heading")}); ask = True
        for p in paras(ctx.get("body_text")):
            it.append({"t": "p", "s": p}); ask = True
        if val(ctx, "button_label"):
            it.append({"t": "btn", "s": val(ctx, "button_label")}); ask = True
        if folder == "footer_standard" and val(ctx, "tagline"):
            it.append({"t": "logo", "align": "left"})
            it.append({"t": "p", "s": val(ctx, "tagline"), "muted": True})
        else:
            # the divider only separates an opt-down ask from the compliance block;
            # with no ask above it, it is an orphan rule floating at the card top
            if ask:
                it.append({"t": "rule"})
            it.append({"t": "logo", "align": "left"})
        it.append({"t": "meta", "s": "INSTAGRAM   ·   FACEBOOK   ·   YOUTUBE"})
        it.append({"t": "rule"})
        it.append({"t": "small", "s": val(ctx, "company_name"), "strong": True})
        it.append({"t": "small", "s": val(ctx, "company_address")})
        if val(ctx, "permission_note"):
            it.append({"t": "small", "s": val(ctx, "permission_note")})
        it.append({"t": "small", "s": "Unsubscribe  ·  Manage preferences  ·  Privacy",
                   "link": True})
        return it
    raise SystemExit("unmapped module in spec: " + folder)


def build():
    out = []
    for e in EMAILS:
        mods = []
        for folder, surf, vals in e["blocks"]:
            ctx = defaults(folder)
            if folder == "preference_opt_down":
                for k in OPT_DOWN_ASK:
                    ctx[k] = ""
            ctx.update(vals)
            c = SURFACES[surf]
            mods.append({
                "name": folder, "surface": surf,
                "bg": c["bg"], "tx": c["tx"], "mu": c["mu"], "dv": c["dv"],
                "bb": c["bb"], "bt": c["bt"], "ac": c["ac"],
                "logoTone": "light" if surf in ("ink", "ink_soft") else "dark",
                "items": items_for(folder, ctx),
            })
        out.append({"code": e["code"], "journey": e["journey"], "pos": e["pos"],
                    "subject": e["subject"], "preview": e["preview"], "modules": mods})
    return out


if __name__ == "__main__":
    spec = build()
    json.dump(spec, open("figma_spec.json", "w"), indent=1)
    n = sum(len(e["modules"]) for e in spec)
    t = sum(len(m["items"]) for e in spec for m in e["modules"])
    print(f"{len(spec)} emails, {n} module frames, {t} content items -> figma_spec.json")
