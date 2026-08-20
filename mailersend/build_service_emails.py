#!/usr/bin/env python3
"""Render the three Hair Solutions Co. MailerSend service-email templates.

    python3 build_service_emails.py            # write mailersend/emails/SVC-*.html
    python3 build_service_emails.py --check    # fail if the files are stale

Source design: Figma "Email Design System" file 9Il504CQE8jLaUTBVzphqc, canvas
225:357, frames 284:21673 (V2 Structured & Detailed), 284:21682 (V3 Branded &
Warm) and 284:21691 (V4 reorder). Geometry, section order, radii, paddings and
copy come from those frames verbatim.

Colour does NOT come from Figma. Per AGENTS.md #1 the authority for email colour
is the rendered Atelier Zero module previews in `Email Reference File/`, and the
three deviations that forces are recorded in DESIGN-NOTES.md.

Output is a Twig template, not finished HTML: it is uploaded raw in the `html`
field of POST /v1/email and rendered by MailerSend against `personalization`.
Only the subset `{{ a.b }}`, `{% for %}` and `{% if x == true %}` is used, which
is also everything `send_service_email.render()` can preview locally.

Stdlib only, per AGENTS.md #7.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "emails"

# --------------------------------------------------------------------------
# Palette — Atelier Zero, as rendered in the module previews (AGENTS.md #1).
# Do not substitute values from brand-design-system/specs/*.
# --------------------------------------------------------------------------
# The email paints no wallpaper. The body and the outer wrapper are transparent
# so the client's own background shows through the 12px gutter — hard rule, set
# 2026-08-19 by Vincent, see AGENTS.md #5. Only cards and insets carry colour.
PAGE  = "transparent"
CARD  = "#F6EFD9"   # every card surface
INSET = "#EDE3CC"   # recessed panel inside a card
INK   = "#151411"   # headings
BODY  = "#25221D"   # body copy
MUTED = "#807B6B"   # metadata, captions, mono labels
RULE  = "#C7BFAC"   # hairlines, dividers, card borders
CORAL = "#EA6452"   # accent, CTA fill, price

# Type. Matches the shipped MailerSend templates and the Figma type stacks.
SANS  = "'Inter','Helvetica Neue',Helvetica,Arial,sans-serif"
TIGHT = "'Inter Tight','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO  = "'JetBrains Mono','Courier New',Courier,monospace"
SERIF = "'Playfair Display',Georgia,'Times New Roman',Times,serif"

# Wrapper arithmetic: CARD_W + 2 * GUTTER = 600.
CARD_W = 576
GUTTER = 12

# Radius by section role (Figma Email Design System).
R_NAV, R_HERO, R_XL, R_2XL, R_PILL = 8, 12, 16, 20, 999

LOGO = "https://hairsolutions.co/cdn/shop/files/logo-v5-dark.png"
MONOGRAM = "https://hairsolutions.co/cdn/shop/files/monogram-dark-on-light-bg-1200x1200.png"

URLS = {
    "shop": "https://hairsolutions.co/collections/mens-hair-systems",
    "orders": "https://hairsolutions.co/pages/help-center-orders-shipping",
    "account": "https://hairsolutions.co/pages/profile",
    "help": "https://hairsolutions.co/pages/help-center",
    "about": "https://hairsolutions.co/pages/about-us-hair-solutions-co",
    "guides": "https://hairsolutions.co/pages/blog",
    "contact": "https://hairsolutions.co/pages/contact-us",
    "privacy": "https://hairsolutions.co/policies/privacy-policy",
    "production": "https://hairsolutions.co/pages/production-times-shipping-times-and-package-tracking",
}

# Verified sender identity. The postal address is the operating address used by
# every shipped Hair Solutions Co. email; the Figma comp shows a placeholder.
POSTAL = "Ehitajate tee 110, Tallinn, Estonia"

UTM = "utm_source=mailersend&amp;utm_medium=transactional&amp;utm_campaign="

SOCIALS = [
    ("Instagram", "https://www.instagram.com/hairsolutionsco/"),
    ("YouTube", "https://www.youtube.com/@hairsolutionsco"),
    ("Facebook", "https://www.facebook.com/hairsolutionsco"),
    ("Website", "https://hairsolutions.co"),
]


# --------------------------------------------------------------------------
# Primitives
# --------------------------------------------------------------------------
def card(inner: str, radius: int, bg: str = CARD, border: str = RULE) -> str:
    """One flush-stacked card in the column. Vertical gutter padding is zero —
    the stack has no gaps; abutting hairlines and differing radii do the
    separating."""
    edge = f"1px solid {border}" if border else "none"
    return (
        f'<tr><td align="center" style="padding:0 {GUTTER}px;">'
        f'<table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" '
        f'class="az-card" style="max-width:{CARD_W}px;background-color:{bg};border:{edge};'
        f'border-radius:{radius}px;border-collapse:separate;">{inner}</table>'
        f"</td></tr>"
    )


def pad(content: str, padding: str, align: str = "left") -> str:
    return (f'<tr><td class="az-pad" align="{align}" style="padding:{padding};">'
            f"{content}</td></tr>")


def eyebrow(text: str, color: str = MUTED, align: str = "left") -> str:
    return (f'<div style="font-family:{MONO};font-size:11px;font-weight:600;'
            f"letter-spacing:0.9px;text-transform:uppercase;line-height:17px;"
            f'color:{color};text-align:{align};">{text}</div>')


def heading(text: str, size: int, leading: int, align: str = "left",
            tracking: str = "-0.3px") -> str:
    return (f'<div style="font-family:{TIGHT};font-weight:800;font-size:{size}px;'
            f"line-height:{leading}px;letter-spacing:{tracking};color:{INK};"
            f'text-align:{align};">{text}</div>')


def body(text: str, align: str = "left", size: int = 16, leading: int = 24,
         color: str = BODY, top: int = 0, max_w: int | None = None) -> str:
    inner = (f'<div style="font-family:{SANS};font-size:{size}px;line-height:{leading}px;'
             f'color:{color};text-align:{align};">{text}</div>')
    if max_w:
        # Outlook ignores max-width on a div and falls back to the full measure,
        # which is the same rag we already ship. Everywhere else it holds.
        inner = (f'<div style="max-width:{max_w}px;margin:0 auto;">{inner}</div>')
    if top:
        inner = f'<div style="padding-top:{top}px;">{inner}</div>'
    return inner


def button(label: str, url: str, campaign: str) -> str:
    """Coral pill. Ink label — Bone on Coral fails contrast."""
    return (
        '<table role="presentation" border="0" cellpadding="0" cellspacing="0" '
        'align="center" style="margin:0 auto;border-collapse:separate;"><tr>'
        f'<td style="background-color:{CORAL};border-radius:{R_PILL}px;">'
        f'<a href="{url}?{UTM}{campaign}" target="_blank" rel="noopener noreferrer" '
        f'style="display:inline-block;padding:19px 34px;font-family:{TIGHT};font-weight:600;'
        f"font-size:15px;letter-spacing:0.3px;line-height:1;color:{INK};text-decoration:none;"
        f'background-color:{CORAL};border-radius:{R_PILL}px;min-height:44px;box-sizing:border-box;">'
        f"{label} &rarr;</a></td></tr></table>"
    )


def link(text: str, url: str, campaign: str, size: int = 12, color: str = BODY,
         weight: int = 400, family: str = SANS, underline: bool = True) -> str:
    deco = "underline" if underline else "none"
    return (f'<a href="{url}?{UTM}{campaign}" target="_blank" rel="noopener noreferrer" '
            f'style="font-family:{family};font-size:{size}px;font-weight:{weight};'
            f'color:{color};text-decoration:{deco};">{text}</a>')


def columns(cells: list[str], gap: int) -> str:
    """Fixed-width column row with real spacer cells — no border-spacing, which
    Outlook drops. `.az-col` stacks the cells on mobile."""
    out = ['<table role="presentation" border="0" cellpadding="0" cellspacing="0" '
           'width="100%" style="border-collapse:collapse;"><tr>']
    for i, cell in enumerate(cells):
        if i:
            out.append(f'<td class="az-gap" width="{gap}" style="width:{gap}px;'
                       f'font-size:0;line-height:0;">&nbsp;</td>')
        out.append(f'<td class="az-col" valign="top" style="vertical-align:top;">{cell}</td>')
    out.append("</tr></table>")
    return "".join(out)


def inset(inner: str, padding: str, radius: int = 12, bg: str = INSET,
          fill_height: bool = False) -> str:
    # Sibling <td> in a grid row are equal height already; without height:100%
    # the inset inside a short cell floats and the row reads ragged.
    h = 'height="100%" ' if fill_height else ""
    hs = "height:100%;" if fill_height else ""
    return (f'<table role="presentation" border="0" cellpadding="0" cellspacing="0" '
            f'width="100%" {h}style="background-color:{bg};border-radius:{radius}px;'
            f'{hs}border-collapse:separate;"><tr><td class="az-inset" '
            f'style="padding:{padding};">{inner}</td></tr></table>')


def img(src: str, alt: str, width: int, radius: int = 0, height: str = "auto",
        center: bool = False) -> str:
    # format=jpg forces JPEG off the .webp originals — Outlook cannot decode WebP.
    sep = "&" if "?" in src else "?"
    src = f"{src}{sep}width={width * 2}&format=jpg"
    r = f"border-radius:{radius}px;" if radius else ""
    # display:block + a fixed width is left-aligned; text-align on the parent has
    # no effect on it, so a centred logo needs auto margins of its own.
    m = "margin:0 auto;" if center else ""
    return (f'<img src="{src}" alt="{alt}" width="{width}" '
            f'style="display:block;border:0;outline:none;width:{width}px;max-width:100%;'
            f'height:{height};{m}{r}" />')


def cover(src: str, alt: str, width: int, height: int, radius: int = 8) -> str:
    """Fixed-height crop. Email has no object-fit, so the box is a background
    image with a transparent spacer holding the height; the <img> fallback keeps
    it meaningful when backgrounds are stripped."""
    sep = "&" if "?" in src else "?"
    src2 = f"{src}{sep}width={width * 2}&height={height * 2}&crop=center&format=jpg"
    return (f'<table role="presentation" border="0" cellpadding="0" cellspacing="0" '
            f'width="100%" style="border-collapse:separate;"><tr>'
            f'<td height="{height}" style="height:{height}px;border-radius:{radius}px;'
            f'background-image:url({src2});background-size:cover;background-position:center;'
            f'background-color:{INSET};font-size:0;line-height:0;">'
            f'<img src="{src2}" alt="{alt}" width="{width}" height="{height}" '
            f'style="display:block;width:100%;max-width:100%;height:{height}px;'
            f'border:0;border-radius:{radius}px;" /></td></tr></table>')


# --------------------------------------------------------------------------
# Shared sections
# --------------------------------------------------------------------------
def preheader_band(text: str, coral: bool = False, browser_link: bool = False) -> str:
    """Figma draws this card in pure white. Pure white is not a permitted email
    surface, so it takes the card tone; the hairline and the 8px radius carry
    the separation instead."""
    if coral:
        inner = pad(eyebrow(text, color=CARD, align="center"), "11px 24px", "center")
        return card(inner, R_NAV, bg=CORAL, border=CORAL)
    if browser_link:
        row = (
            '<table role="presentation" border="0" cellpadding="0" cellspacing="0" '
            'width="100%" style="border-collapse:collapse;"><tr>'
            f'<td class="az-col" align="left" style="vertical-align:middle;">'
            f"{eyebrow(text, color=CORAL)}</td>"
            f'<td class="az-col" align="right" style="vertical-align:middle;">'
            f'<a href="{{{{ view_in_browser_url }}}}" target="_blank" rel="noopener noreferrer" '
            f'style="font-family:{MONO};font-size:11px;font-weight:600;letter-spacing:0.9px;'
            f'text-transform:uppercase;color:{MUTED};text-decoration:none;">View in browser</a>'
            "</td></tr></table>"
        )
        return card(pad(row, "12px 24px"), R_NAV)
    return card(pad(eyebrow(text, align="center"), "12px 24px", "center"), R_NAV)


def nav_logo_only(campaign: str, rule: bool = False) -> str:
    logo = (f'<a href="https://hairsolutions.co?{UTM}{campaign}" target="_blank" '
            f'rel="noopener noreferrer">{img(LOGO, "Hair Solutions Co.", 160, center=True)}</a>')
    inner = pad(f'<div style="text-align:center;">{logo}</div>',
                "24px 24px 16px 24px" if rule else "24px", "center")
    if rule:
        inner += pad(f'<div style="height:1px;line-height:1px;font-size:0;'
                     f'background-color:{RULE};">&nbsp;</div>', "0 24px 20px 24px")
    return card(inner, R_NAV)


def nav_logo_left(campaign: str) -> str:
    links = " ".join(
        f'<a href="{URLS[k]}?{UTM}{campaign}" target="_blank" rel="noopener noreferrer" '
        f'style="font-family:{TIGHT};font-size:11px;font-weight:600;letter-spacing:1.9px;'
        f'text-transform:uppercase;color:{c};text-decoration:none;'
        f'padding-left:14px;white-space:nowrap;">{t}</a>'
        for k, t, c in (("shop", "Shop", INK), ("orders", "Order support", INK),
                        ("account", "Account", INK), ("help", "Help", CORAL))
    )
    row = (
        '<table role="presentation" border="0" cellpadding="0" cellspacing="0" '
        'width="100%" style="border-collapse:collapse;"><tr>'
        f'<td class="az-col" align="left" width="54" style="vertical-align:middle;">'
        f'<a href="https://hairsolutions.co?{UTM}{campaign}" target="_blank" '
        f'rel="noopener noreferrer">{img(MONOGRAM, "Hair Solutions Co.", 54, radius=6)}</a></td>'
        f'<td class="az-col az-navlinks" align="right" style="vertical-align:middle;'
        f'padding-left:12px;">{links}</td>'
        "</tr></table>"
    )
    return card(pad(row, "20px 24px"), R_NAV)


def divider_solid() -> str:
    return card(pad(f'<div style="height:1px;line-height:1px;font-size:0;'
                    f'background-color:{RULE};">&nbsp;</div>', "24px 40px"), R_XL)


def divider_dashed() -> str:
    # A real dashed border, not an image: it survives image blocking and dark mode.
    return card(pad(f'<div style="height:0;line-height:0;font-size:0;'
                    f'border-top:1px dashed {RULE};">&nbsp;</div>', "24px 40px"), R_XL)


def divider_coral_dot() -> str:
    dot = (f'<table role="presentation" border="0" cellpadding="0" cellspacing="0" '
           f'style="border-collapse:separate;"><tr><td width="8" height="8" '
           f'style="width:8px;height:8px;background-color:{CORAL};border-radius:4px;'
           f'font-size:0;line-height:0;">&nbsp;</td></tr></table>')
    rule_cell = (f'<div style="height:1px;line-height:1px;font-size:0;'
                 f'background-color:{RULE};">&nbsp;</div>')
    row = ('<table role="presentation" border="0" cellpadding="0" cellspacing="0" '
           'width="100%" style="border-collapse:collapse;"><tr>'
           f'<td style="vertical-align:middle;">{rule_cell}</td>'
           f'<td width="40" align="center" style="width:40px;vertical-align:middle;">{dot}</td>'
           f'<td style="vertical-align:middle;">{rule_cell}</td>'
           "</tr></table>")
    return card(pad(row, "24px 40px"), R_XL)


def selection_block(title: str) -> str:
    """`Your Selection` / `Confirmed Selection` — the ordered line items.

    One inset per item. The Figma comp shows a single item; a real order has
    several, so this loops. `{% for %}` is the whole reason service mail lives on
    MailerSend rather than MailerLite (API-SURFACE.md #3)."""
    row = (
        '<table role="presentation" border="0" cellpadding="0" cellspacing="0" '
        'width="100%" style="border-collapse:collapse;"><tr>'
        '<td class="az-thumb" width="100" valign="top" '
        'style="width:100px;vertical-align:top;padding-right:18px;">'
        "{% if item.has_image == true %}"
        + img("{{ item.image }}", "{{ item.name }}", 100, radius=8)
        + "{% endif %}</td>"
        '<td valign="top" style="vertical-align:top;">'
        f'<div style="font-family:{TIGHT};font-weight:800;font-size:16px;line-height:21px;'
        f'letter-spacing:-0.2px;color:{INK};">{{{{ item.name }}}}</div>'
        "{% if item.has_spec == true %}"
        f'<div style="padding-top:6px;font-family:{SANS};font-size:13px;line-height:19px;'
        f'color:{MUTED};">{{{{ item.spec }}}}</div>{{% endif %}}'
        '<table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" '
        'style="border-collapse:collapse;"><tr>'
        f'<td align="left" style="padding-top:10px;font-family:{MONO};font-size:11px;'
        f'font-weight:700;letter-spacing:0.6px;color:{MUTED};">QTY: {{{{ item.qty }}}}</td>'
        f'<td align="right" style="padding-top:10px;font-family:{SERIF};font-weight:700;'
        f'font-size:18px;line-height:22px;color:{CORAL};">{{{{ item.price }}}}</td>'
        "</tr></table></td></tr></table>"
    )
    items = ("{% for item in items %}"
             f'<div style="padding-top:12px;">{inset(row, "16px")}</div>'
             "{% endfor %}")
    inner = pad(
        f'<div style="font-family:{TIGHT};font-weight:800;font-size:18px;line-height:24px;'
        f'letter-spacing:-0.2px;color:{INK};">{title}</div>'
        f'<div style="padding-top:8px;">{items}</div>',
        "32px 32px 36px 32px")
    return card(inner, R_2XL)


def totals_block() -> str:
    """Not in the Figma comp. An order confirmation that shows line prices and no
    total is a support ticket, so the money is closed out here."""
    rows = ("{% for row in totals.rows %}"
            '<table role="presentation" border="0" cellpadding="0" cellspacing="0" '
            'width="100%" style="border-collapse:collapse;"><tr>'
            f'<td align="left" style="padding:7px 0;font-family:{SANS};font-size:13px;'
            f'line-height:19px;color:{MUTED};">{{{{ row.label }}}}</td>'
            f'<td align="right" style="padding:7px 0;font-family:{SANS};font-size:13px;'
            f'line-height:19px;color:{BODY};">{{{{ row.value }}}}</td>'
            "</tr></table>{% endfor %}")
    total = ('<table role="presentation" border="0" cellpadding="0" cellspacing="0" '
             'width="100%" style="border-collapse:collapse;"><tr>'
             f'<td align="left" style="padding:12px 0 0 0;border-top:1px solid {RULE};'
             f'font-family:{TIGHT};font-weight:800;font-size:15px;line-height:21px;'
             f'color:{INK};">{{{{ totals.total_label }}}}</td>'
             f'<td align="right" style="padding:12px 0 0 0;border-top:1px solid {RULE};'
             f'font-family:{TIGHT};font-weight:800;font-size:15px;line-height:21px;'
             f'color:{INK};">{{{{ totals.total }}}}</td>'
             "</tr></table>")
    return card(pad(inset(rows + total, "20px"), "0 32px 32px 32px"), R_2XL)


def summary_block(title: str) -> str:
    """V3 `Your Order Summary` — the key/value status panel, driven by data so
    the same template covers `order received` and every later production state."""
    rows = ("{% for row in summary_rows %}"
            '<table role="presentation" border="0" cellpadding="0" cellspacing="0" '
            'width="100%" style="border-collapse:collapse;"><tr>'
            f'<td align="left" style="padding:5px 0;font-family:{MONO};'
            f'font-size:11px;font-weight:700;letter-spacing:0.7px;text-transform:uppercase;'
            f'color:{MUTED};">{{{{ row.label }}}}</td>'
            f'<td align="right" style="padding:5px 0;font-family:{SANS};'
            f'font-weight:700;font-size:14px;line-height:20px;color:{INK};'
            f'text-transform:uppercase;">{{{{ row.value }}}}</td>'
            "</tr></table>{% endfor %}")
    inner = pad(
        f'<div style="font-family:{TIGHT};font-weight:800;font-size:20px;line-height:26px;'
        f'letter-spacing:-0.3px;color:{INK};">{title}</div>'
        f'<div style="padding-top:16px;">{inset(rows, "20px")}</div>',
        "40px")
    return card(inner, R_2XL)


def recommendations_block(title: str, campaign: str) -> str:
    """V2 three-up chips. Collapses entirely when the payload sends none."""
    chip = (
        '<table role="presentation" border="0" cellpadding="0" cellspacing="0" '
        'width="100%" style="border-collapse:collapse;"><tr>'
        '<td width="52" valign="middle" '
        'style="width:52px;vertical-align:middle;padding-right:10px;">'
        + img("{{ rec.image }}", "{{ rec.name }}", 52, radius=6) +
        "</td>"
        '<td valign="middle" style="vertical-align:middle;">'
        f'<a href="{{{{ rec.url }}}}" target="_blank" rel="noopener noreferrer" '
        f'style="font-family:{TIGHT};font-weight:800;font-size:12px;line-height:16px;'
        f'color:{INK};text-decoration:none;">{{{{ rec.name }}}}</a>'
        f'<div style="padding-top:3px;font-family:{MONO};font-size:10px;line-height:14px;'
        f'letter-spacing:0.5px;text-transform:uppercase;color:{MUTED};">{{{{ rec.label }}}}</div>'
        "</td></tr></table>"
    )
    cell = inset(chip, "12px", fill_height=True)
    grid = ("{% for rec in recommendations %}"
            f'<td class="az-col" valign="top" style="vertical-align:top;padding:6px;">{cell}</td>'
            "{% endfor %}")
    inner = pad(
        f'<div style="font-family:{TIGHT};font-weight:800;font-size:16px;line-height:22px;'
        f'letter-spacing:-0.2px;color:{INK};">{title}</div>'
        '<div style="padding-top:10px;">'
        '<table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" '
        f'class="az-grid" style="border-collapse:collapse;margin:0 -6px;"><tr>{grid}</tr></table></div>',
        "32px 20px")
    return "{% if has_recommendations == true %}" + card(inner, R_2XL) + "{% endif %}"


def resources_block() -> str:
    """V3 two-up cards. The comp labels these `Care Guide` and `Application
    Supplies`; the catalogue has no consumables SKUs, so they are data-driven
    links and the fixture points them at real guide pages."""
    cell = inset(
        cover("{{ res.image }}", "{{ res.title }}", 221, 180)
        + f'<div style="padding-top:14px;font-family:{TIGHT};font-weight:800;font-size:16px;'
          f'line-height:21px;letter-spacing:-0.2px;color:{INK};">{{{{ res.title }}}}</div>'
          f'<div style="padding-top:4px;"><a href="{{{{ res.url }}}}" target="_blank" '
          f'rel="noopener noreferrer" style="font-family:{SERIF};font-weight:600;font-size:16px;'
          f'color:{CORAL};text-decoration:none;">{{{{ res.cta_label }}}}</a></div>',
        "16px", fill_height=True)
    grid = ("{% for res in resources %}"
            f'<td class="az-col" valign="top" style="vertical-align:top;padding:10px;">{cell}</td>'
            "{% endfor %}")
    inner = pad('<table role="presentation" border="0" cellpadding="0" cellspacing="0" '
                'width="100%" class="az-grid" style="border-collapse:collapse;margin:0 -10px;">'
                f"<tr>{grid}</tr></table>", "14px")
    return "{% if has_resources == true %}" + card(inner, R_2XL) + "{% endif %}"


def care_row_block() -> str:
    """V4 three-up priced row."""
    cell = inset(
        cover("{{ rec.image }}", "{{ rec.name }}", 146, 120)
        + f'<div style="padding-top:10px;font-family:{TIGHT};font-weight:800;font-size:13px;'
          f'line-height:18px;color:{INK};">{{{{ rec.name }}}}</div>'
          f'<div style="padding-top:2px;font-family:{SERIF};font-weight:600;font-size:13px;'
          f'line-height:18px;color:{CORAL};">{{{{ rec.label }}}}</div>',
        "12px", fill_height=True)
    grid = ("{% for rec in recommendations %}"
            f'<td class="az-col" valign="top" style="vertical-align:top;padding:6px;">'
            f'<a href="{{{{ rec.url }}}}" target="_blank" rel="noopener noreferrer" '
            f'style="text-decoration:none;">{cell}</a></td>'
            "{% endfor %}")
    inner = pad('<table role="presentation" border="0" cellpadding="0" cellspacing="0" '
                'width="100%" class="az-grid" style="border-collapse:collapse;margin:0 -6px;">'
                f"<tr>{grid}</tr></table>", "14px")
    return "{% if has_recommendations == true %}" + card(inner, R_2XL) + "{% endif %}"


def service_notice(campaign: str) -> str:
    """Why there is no unsubscribe.

    The Figma footers carry `Unsubscribe` and `Manage Preferences`. These three
    emails are service mail about an order the customer placed, not marketing —
    there is nothing to opt out of, and offering it would imply their order
    updates can be switched off. The link slot keeps the comp's three-up shape
    and carries the genuinely useful destinations instead."""
    return (f'<div style="font-family:{SANS};font-size:12px;line-height:19px;color:{MUTED};'
            f'text-align:center;">This is a service email about order '
            f"{{{{ order_number }}}}, sent because you placed that order at "
            f"hairsolutions.co. It is not marketing, so there is nothing to unsubscribe "
            f"from &mdash; your marketing preferences are separate and unaffected.</div>")


def footer_minimal(campaign: str) -> str:
    """V2 `MINIMAL LEGAL STRIP`."""
    links = ' <span style="color:%s;">&middot;</span> ' % RULE
    row = links.join([
        link("Order status", "{{ order_status_url }}", campaign),
        link("Contact us", URLS["contact"], campaign),
        link("Privacy policy", URLS["privacy"], campaign),
    ]).replace("{{ order_status_url }}?" + UTM + campaign, "{{ order_status_url }}")
    inner = pad(f'<div style="text-align:center;">{row}</div>', "32px 32px 0 32px", "center")
    inner += pad(service_notice(campaign), "16px 32px 8px 32px", "center")
    inner += pad(f'<div style="font-family:{SANS};font-size:11px;line-height:17px;'
                 f'color:{MUTED};text-align:center;">&copy; 2026 Hair Solutions Co. '
                 f"&middot; {POSTAL}</div>", "0 32px 32px 32px", "center")
    return card(inner, R_XL)


def footer_centered(campaign: str) -> str:
    """V3 `SIMPLE CENTERED` — wordmark, legal line, link pair."""
    logo = (f'<a href="https://hairsolutions.co?{UTM}{campaign}" target="_blank" '
            f'rel="noopener noreferrer">{img(LOGO, "Hair Solutions Co.", 200, center=True)}</a>')
    inner = pad(f'<div style="text-align:center;">{logo}</div>', "40px 40px 20px 40px", "center")
    inner += pad(service_notice(campaign), "0 40px 16px 40px", "center")
    row = (' <span style="color:%s;">&middot;</span> ' % RULE).join([
        link("Order status", "{{ order_status_url }}", campaign),
        link("Contact us", URLS["contact"], campaign),
    ]).replace("{{ order_status_url }}?" + UTM + campaign, "{{ order_status_url }}")
    inner += pad(f'<div style="text-align:center;">{row}</div>', "0 40px 14px 40px", "center")
    inner += pad(f'<div style="font-family:{SANS};font-size:11px;line-height:17px;'
                 f"letter-spacing:0.5px;color:{MUTED};text-align:center;\">&copy; 2026 "
                 f"Hair Solutions Co. &middot; {POSTAL}</div>", "0 40px 40px 40px", "center")
    return card(inner, R_XL)


def footer_nav_social(campaign: str) -> str:
    """V4 `NAV & SOCIAL ROW`.

    The comp uses raster social glyphs. Text links carry the same information,
    stay legible with images blocked, and cost no extra hosted assets."""
    nav = (' <span style="color:%s;">&nbsp;</span> ' % RULE).join(
        link(t, URLS[k], campaign, size=13, color=INK, weight=600, underline=False)
        for k, t in (("shop", "Shop systems"), ("about", "Our story"),
                     ("guides", "Guides"), ("contact", "Contact"))
    )
    social = (' <span style="color:%s;">&middot;</span> ' % RULE).join(
        link(name, url, campaign, size=12, color=MUTED) for name, url in SOCIALS
    )
    inner = pad(f'<div style="text-align:center;">{nav}</div>', "36px 32px 0 32px", "center")
    inner += pad(f'<div style="height:1px;line-height:1px;font-size:0;'
                 f'background-color:{RULE};">&nbsp;</div>', "26px 32px")
    inner += pad(f'<div style="text-align:center;">{social}</div>', "0 32px 22px 32px", "center")
    inner += pad(service_notice(campaign), "0 32px 14px 32px", "center")
    inner += pad(f'<div style="font-family:{SANS};font-size:11px;line-height:17px;'
                 f"color:{MUTED};text-align:center;\">&copy; 2026 Hair Solutions Co. "
                 f"&middot; {POSTAL}</div>", "0 32px 36px 32px", "center")
    return card(inner, R_XL)


# --------------------------------------------------------------------------
# Document shell
# --------------------------------------------------------------------------
HEAD = """<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1.0" />
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<meta name="color-scheme" content="light" />
<meta name="supported-color-schemes" content="light" />
<title>__TITLE__</title>
<!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript><![endif]-->
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Inter+Tight:wght@600;800&family=JetBrains+Mono:wght@400;600;700&family=Playfair+Display:wght@600;700&display=swap');
body{margin:0;padding:0;width:100%!important;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;}
table{border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0;}
img{-ms-interpolation-mode:bicubic;}
a{color:inherit;}
@media only screen and (max-width:620px){
  .az-wrap{width:100%!important;}
  .az-card{max-width:100%!important;}
  .az-pad{padding-left:22px!important;padding-right:22px!important;}
  .az-inset{padding-left:16px!important;padding-right:16px!important;}
  .az-col{display:block!important;width:100%!important;max-width:100%!important;box-sizing:border-box!important;padding-left:0!important;padding-right:0!important;}
  .az-col > table{margin-left:auto!important;margin-right:auto!important;}
  .az-thumb{width:76px!important;padding-right:14px!important;}
  .az-thumb img{width:76px!important;}
  .az-grid{margin:0!important;}
  .az-gap{display:none!important;}
  .az-navlinks{padding-top:14px!important;text-align:center!important;}
}
</style>
</head>
<body style="margin:0;padding:0;background-color:__PAGE__;">
<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:transparent;">__PREVIEW__&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;</div>
<table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color:__PAGE__;"><tr><td align="center" style="padding:24px 0;">
<table role="presentation" border="0" cellpadding="0" cellspacing="0" class="az-wrap" width="600" style="width:600px;max-width:600px;">
"""

TAIL = """</table>
</td></tr></table>
</body>
</html>
"""


def document(title: str, preview: str, sections: list[str]) -> str:
    head = (HEAD.replace("__TITLE__", title)
                .replace("__PREVIEW__", preview)
                .replace("__PAGE__", PAGE))
    return head + "\n".join(sections) + "\n" + TAIL


# --------------------------------------------------------------------------
# The three emails. Copy is verbatim from the Figma frames.
# --------------------------------------------------------------------------
def svc1_order_confirmed() -> str:
    """Figma 284:21673 — Transactional V2, Structured & Detailed."""
    c = "order-confirmed"
    title = pad(
        heading("Thank You. Your Order Is Confirmed.", 32, 38, "center")
        + body("We have received your order and will begin reviewing the details for "
               "processing. You will receive another email when your order moves forward "
               "or when tracking information becomes available.",
               align="center", top=16, color=MUTED, max_w=480),
        "48px 44px", "center")
    return document(
        "Your order is confirmed",
        "Order confirmed. Review the details below.",
        [
            preheader_band("Order confirmed. Review the details below."),
            nav_logo_only(c),
            card(title, R_2XL),
            selection_block("Your Selection"),
            totals_block(),
            divider_solid(),
            recommendations_block("Recommended for Your Order", c),
            footer_minimal(c),
        ])


def svc2_specification_review() -> str:
    """Figma 284:21682 — Transactional V3, Branded & Warm. The production update."""
    c = "specification-review"
    title = pad(
        f'<div style="height:2px;line-height:2px;font-size:0;background-color:{CORAL};'
        f'width:100%;">&nbsp;</div>'
        + f'<div style="padding-top:16px;">'
        + heading("Your Selection Is Now in Our Care", 28, 34)
        + "</div>"
        + body("Thank you for choosing Hair Solutions Co. We have received your order and "
               "are reviewing the submitted details. For custom or specification-sensitive "
               "products, this review helps ensure the order is prepared according to the "
               "information provided.", top=16, size=15, leading=22, color=MUTED),
        "48px 44px")
    return document(
        "Your selection is now in our care",
        "We are reviewing your order specifications.",
        [
            preheader_band("We are reviewing order specifications.", browser_link=True),
            nav_logo_left(c),
            card(title, R_2XL),
            summary_block("Your Order Summary"),
            divider_dashed(),
            resources_block(),
            footer_centered(c),
        ])


def svc3_reorder_received() -> str:
    """Figma 284:21691 — Transactional V4, reorder."""
    c = "reorder-received"
    title = pad(
        heading("Your Reorder Has Been Received", 32, 38, "center")
        + body("We have received your new order and will process it using the "
               "specifications shown below. Even when reordering a familiar system, "
               "please review each detail carefully.",
               align="center", top=16, color=MUTED, max_w=480)
        + f'<div style="padding-top:26px;">'
        + button("Review Specifications", "{{ order_status_url }}", c).replace(
            "{{ order_status_url }}?" + UTM + c, "{{ order_status_url }}")
        + "</div>",
        "48px 44px", "center")
    return document(
        "Your reorder has been received",
        "We received your reorder. Please verify the specifications.",
        [
            preheader_band("We received your reorder. Please verify the specifications.",
                           coral=True),
            nav_logo_only(c, rule=True),
            card(title, R_2XL),
            selection_block("Confirmed Selection"),
            totals_block(),
            divider_coral_dot(),
            care_row_block(),
            footer_nav_social(c),
        ])


TEMPLATES = {
    "SVC-1-order-confirmed.html": svc1_order_confirmed,
    "SVC-2-specification-review.html": svc2_specification_review,
    "SVC-3-reorder-received.html": svc3_reorder_received,
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any file on disk differs from the build")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stale = []
    for name, fn in TEMPLATES.items():
        html = fn()
        path = OUT_DIR / name
        current = path.read_text() if path.exists() else None
        if args.check:
            if current != html:
                stale.append(name)
            continue
        if current == html:
            print(f"unchanged  {path.relative_to(HERE.parent)}  ({len(html):,} bytes)")
            continue
        path.write_text(html)
        print(f"wrote      {path.relative_to(HERE.parent)}  ({len(html):,} bytes)")

    if args.check:
        if stale:
            print("STALE: " + ", ".join(stale), file=sys.stderr)
            return 1
        print("all templates match the build")
    return 0


if __name__ == "__main__":
    sys.exit(main())
