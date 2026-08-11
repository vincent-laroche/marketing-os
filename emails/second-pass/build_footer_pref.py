"""Upgrade `preference_opt_down` into a real footer.

Notion's blueprint uses "Footer - Preference centre" as the terminal module on 19 of
the 20 journey emails, but the live module carried only eyebrow/heading/body/button —
no postal address, no unsubscribe, no permission reminder. Shipped as the sole footer
that is a compliance gap, not a styling one.

Additive: every existing field keeps its id and default, so current usages are
unchanged; the compliance block is appended below the opt-down ask.
"""
import json, os, shutil
from surface import surface_field, preamble, shell, ruled_eyebrow, button, hairline

SRC, OUT = "final-verify", "staging-footer/email_modules"
TXT = "font-family:Arial,Helvetica,sans-serif;"
MONO = "font-family:'Courier New',Courier,monospace;"

LINK = "color:{{ c.mu }};text-decoration:underline;"


def html():
    social = (
        '<td valign="middle" style="' + MONO + "font-size:11px;letter-spacing:1.5px;"
        'text-transform:uppercase;color:{{ c.tx }};">'
        "{% if module.instagram_url.href %}"
        '<a href="{{ module.instagram_url.href }}" style="color:{{ c.tx }};text-decoration:none;">Instagram</a>{% endif %}'
        '{% if module.facebook_url.href %}<span style="color:{{ c.mu }};">&nbsp;&nbsp;·&nbsp;&nbsp;</span>'
        '<a href="{{ module.facebook_url.href }}" style="color:{{ c.tx }};text-decoration:none;">Facebook</a>{% endif %}'
        '{% if module.youtube_url.href %}<span style="color:{{ c.mu }};">&nbsp;&nbsp;·&nbsp;&nbsp;</span>'
        '<a href="{{ module.youtube_url.href }}" style="color:{{ c.tx }};text-decoration:none;">YouTube</a>{% endif %}'
        "</td>"
    )
    return shell(
        # --- the opt-down ask (unchanged fields, restyled onto the surface system)
        ruled_eyebrow()
        + "{% if module.heading %}"
          '<h2 style="margin:0 0 12px;' + TXT + 'font-size:24px;line-height:1.25;font-weight:bold;'
          'letter-spacing:-0.3px;color:{{ c.tx }};">{{ module.heading }}</h2>{% endif %}'
        + "{% if module.body_text %}"
          '<div style="margin:0;' + TXT + 'font-size:16px;line-height:1.55;color:{{ c.mu }};">'
          "{{ module.body_text }}</div>{% endif %}"
        + "{% if module.button_label %}"
          '<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:22px 0 0;"><tr>'
          '<td style="background:{{ c.bb }};border-radius:999px;padding:13px 24px;">'
          '<a href="{{ module.button_url.href }}" style="' + TXT + 'font-size:13px;font-weight:bold;'
          'letter-spacing:0.5px;color:{{ c.bt }};text-decoration:none;display:inline-block;">'
          "{{ module.button_label }}</a></td></tr></table>{% endif %}"
        # --- the compliance block this module was missing entirely
        + hairline("28px 0 24px")
        + '<img src="{{ c.lg }}" alt="Hair Solutions Co." width="{{ module.logo_width }}"'
          ' style="display:block;width:{{ module.logo_width }}px;max-width:100%;height:auto;border:0;">'
        + '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"'
          ' style="margin:20px 0 0;"><tr>' + social + "</tr></table>"
        + hairline("20px 0")
        + '<p style="margin:0;' + TXT + 'font-size:12px;line-height:1.6;color:{{ c.tx }};font-weight:bold;">'
          "{{ module.company_name }}</p>"
        + '<p style="margin:4px 0 0;' + TXT + 'font-size:12px;line-height:1.6;color:{{ c.mu }};">'
          "{{ module.company_address }}</p>"
        + "{% if module.permission_note %}"
          '<p style="margin:14px 0 0;' + TXT + 'font-size:11px;line-height:1.6;color:{{ c.mu }};">'
          "{{ module.permission_note }}</p>{% endif %}"
        + '<p style="margin:14px 0 0;' + TXT + 'font-size:11px;line-height:1.6;color:{{ c.mu }};">'
          '<a href="{{ unsubscribe_link }}" style="' + LINK + '">Unsubscribe</a>'
          "&nbsp;&nbsp;·&nbsp;&nbsp;"
          '<a href="{{ subscription_preferences_link }}" style="' + LINK + '">Manage preferences</a>'
          "&nbsp;&nbsp;·&nbsp;&nbsp;"
          '<a href="{{ module.privacy_url.href }}" style="' + LINK + '">Privacy</a></p>',
        align="left",
    )


def txt(fid, label, default):
    return {"id": fid, "name": fid, "label": label, "required": False, "locked": False,
            "allow_new_line": False, "type": "text", "display_width": None, "default": default}


def url(fid, label, href):
    return {"id": fid, "name": fid, "label": label, "required": False, "locked": False,
            "supported_types": ["EXTERNAL", "CONTENT", "FILE", "EMAIL_ADDRESS", "BLOG"],
            "type": "url", "display_width": None,
            "default": {"type": "EXTERNAL", "href": href}}


ADDED = [
    txt("logo_width", "Wordmark width (px)", "132"),
    txt("company_name", "Company name", "Hair Solutions Co."),
    txt("company_address", "Postal address", "Ehitajate tee 110, Tallinn, Harjumaa 13517, Estonia"),
    txt("permission_note", "Permission reminder",
        "You are receiving this because you ordered from or subscribed to Hair Solutions Co."),
    url("privacy_url", "Privacy URL", "https://hairsolutions.co/policies/privacy-policy"),
    url("instagram_url", "Instagram URL", "https://instagram.com/hairsolutions.co"),
    url("facebook_url", "Facebook URL", "https://facebook.com/hairsolutions.co"),
    url("youtube_url", "YouTube URL", "https://youtube.com/@hairsolutions.co"),
]

if __name__ == "__main__":
    shutil.rmtree("staging-footer", ignore_errors=True)
    body = html()
    for folder, default in (("preference_opt_down.module", "bone"),
                            ("preference_opt_down_dark.module", "ink")):
        src, dst = os.path.join(SRC, folder), os.path.join(OUT, folder)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copytree(src, dst)
        open(os.path.join(dst, "module.html"), "w").write(preamble(default) + body)
        f = json.load(open(os.path.join(dst, "fields.json")))
        f = [x for x in f if x["id"] != "surface"]
        have = {x["id"] for x in f}
        # coral excluded: this is chrome, and the wordmark's "co" vanishes on coral
        f = [surface_field(default, ("coral",))] + f + [a for a in ADDED if a["id"] not in have]
        json.dump(f, open(os.path.join(dst, "fields.json"), "w"), indent=2)
        print("built", folder, "->", [x["id"] for x in f])
