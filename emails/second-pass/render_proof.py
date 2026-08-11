"""Render the pilot modules across all 6 surfaces into one proof sheet.

Implements just enough HubL to render these modules faithfully offline:
  {%- set ... -%} preamble (stripped; `c` supplied from surface.py)
  {{ c.KEY }} / {{ module.KEY }} / {{ module.KEY.href }}
  {% if EXPR %} ... {% endif %}   (nesting-aware)
"""
import json, os, re
from surface import SURFACES, ORDER

STAGE = "staging/email_modules"

SAMPLE = {
    "logo_url": {"href": "https://hairsolutions.co/"},
    "logo_width": "150",
    "preheader_note": "Post-purchase · Email 5 of 6",
    "tagline": "Hand-made hair systems, fitted to you and shipped worldwide.",
    "company_name": "Hair Solutions Co.",
    "company_address": "Ehitajate tee 110, Tallinn, Harjumaa 13517, Estonia",
    "permission_note": "You are receiving this because you ordered from or subscribed to Hair Solutions Co.",
    "privacy_url": {"href": "#"},
    "instagram_url": {"href": "#"}, "facebook_url": {"href": "#"}, "youtube_url": {"href": "#"},
    "eyebrow": "Maintenance calendar",
    "heading": "Ninety days, three appointments,",
    "heading_accent": "one routine.",
    "body_text": ("Your system is at its best when the cycle is predictable. Here is the "
                  "rhythm we recommend for a lace base worn daily."),
    "show_button": "yes",
    "button_label": "Open my calendar",
    "button_url": {"href": "#"},
}

CTA_SAMPLE = dict(SAMPLE, eyebrow="Ready when you are",
                  heading="Secure your priority slot",
                  body_text="Each master artisan ventilates four systems a month. "
                            "Book now to hold your delivery window.",
                  button_label="Schedule appointment")


def resolve(expr, ctx):
    expr = expr.strip()
    m = re.match(r"^module\.(\w+)(?:\.(\w+))?\s*==\s*'([^']*)'$", expr)
    if m:
        v = ctx.get(m.group(1))
        if m.group(2):
            v = (v or {}).get(m.group(2))
        return v == m.group(3)
    m = re.match(r"^module\.(\w+)(?:\.(\w+))?$", expr)
    if m:
        v = ctx.get(m.group(1))
        if m.group(2):
            v = (v or {}).get(m.group(2))
        return bool(v)
    return True


def strip_ifs(html, ctx):
    """Resolve {% if %}/{% endif %} pairs, innermost first."""
    # the condition must not run past its own `%}` — otherwise an outer `if` can
    # swallow a nested one's opener and mis-pair with the nested `endif`.
    pat = re.compile(r"\{%-?\s*if\s+((?:(?!%\}).)+?)\s*-?%\}"
                     r"((?:(?!\{%-?\s*(?:if|endif)\b).)*?)\{%-?\s*endif\s*-?%\}", re.S)
    while True:
        new = pat.sub(lambda m: m.group(2) if resolve(m.group(1), ctx) else "", html)
        if new == html:
            return new
        html = new


def render(html, surface, ctx):
    html = re.sub(r"\{%-?\s*set\b.*?-?%\}", "", html, flags=re.S)
    html = re.sub(r"\{%-?\s*if not c.*?endif\s*-?%\}", "", html, flags=re.S)
    c = SURFACES[surface]
    html = re.sub(r"\{\{\s*c\.(\w+)\s*\}\}", lambda m: c[m.group(1)], html)
    html = strip_ifs(html, ctx)

    def var(m):
        v = ctx.get(m.group(1))
        if m.group(2):
            v = (v or {}).get(m.group(2), "#")
        return "" if v is None else str(v)

    html = re.sub(r"\{\{\s*module\.(\w+)(?:\.(\w+))?\s*\}\}", var, html)
    html = html.replace("{{ unsubscribe_link }}", "#").replace("{{ subscription_preferences_link }}", "#")
    return html


if __name__ == '__main__':
    PILOT = [("header_centered_logo", "Header — centred wordmark", SAMPLE),
             ("hero_text_led", "Hero — text-led", SAMPLE),
             ("text_block_generic", "Text block — generic", SAMPLE),
             ("button_standalone_cta", "CTA — standalone", CTA_SAMPLE),
             ("footer_standard", "Footer — standard (redesigned)", SAMPLE)]

    LABELS = {"bone": "Bone #F7F1DE", "paper": "Paper #EFE7D2", "paper_dark": "Paper Dark #DDD2B6",
              "ink": "Ink #15140F", "ink_soft": "Ink Soft #2A2620", "coral": "Coral #ED6F5C"}

    out = ["""<meta charset="utf-8"><title>Atelier Zero — surface proof sheet</title>
    <style>
     body{margin:0;background:#EFE7D2;font-family:-apple-system,Segoe UI,Arial,sans-serif;padding:40px 24px 80px}
     h1{font-size:26px;margin:0 0 6px;color:#15140F;letter-spacing:-.4px}
     .sub{color:#5A5448;font-size:14px;margin:0 0 40px;max-width:760px;line-height:1.6}
     /* scoped to .sec — a bare `h2` rule here cascades into the modules' own <h2>
        and silently uppercases their headings (text-transform is not set inline). */
     .sec{font-size:15px;margin:48px 0 4px;color:#15140F;text-transform:uppercase;letter-spacing:1.6px;
        font-family:'Courier New',monospace;border-top:1px solid #DDD2B6;padding-top:20px;font-weight:700}
     .note{font-family:'Courier New',monospace;font-size:10px;color:#5A5448;margin:2px 0 0}
     .grid{display:flex;flex-wrap:wrap;gap:22px;margin-top:18px}
     .cell{width:600px;max-width:100%}
     .cap{font-family:'Courier New',monospace;font-size:10px;letter-spacing:1.4px;text-transform:uppercase;
          color:#5A5448;margin:0 0 8px}
    </style>
    <h1>Atelier Zero — email surface system</h1>
    <p class="sub">Every module now takes one <b>surface</b> choice. Text, muted text, dividers, sub-cards,
    the button fill and the wordmark all derive from it. Same module, six surfaces — no twin files needed.
    On <b>Coral</b> the button flips to Ink and the accent rule goes Ink, because coral-on-coral disappears.</p>"""]

    DISSOLVE = ("paper", "  — same value as the email body, so the card edge dissolves")

    for fam, title, ctx in PILOT:
        out.append(f"<p class='sec'>{title}</p><div class='grid'>")
        src = open(os.path.join(STAGE, fam + ".module", "module.html")).read()
        for s in ORDER:
            note = DISSOLVE[1] if s == DISSOLVE[0] else ""
            out.append(f"<div class='cell'><p class='cap'>{LABELS[s]}{note}</p>{render(src, s, ctx)}</div>")
        out.append("</div>")

    open("proof.html", "w").write("\n".join(out))
    print("wrote proof.html")
