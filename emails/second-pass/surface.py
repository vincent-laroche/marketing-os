"""Atelier Zero surface-token system for HubSpot email modules.

Shared by the pilot builder and the full-library rollout.
One module = one card = one `surface` choice. Every other colour derives from it.
"""

LOGO_DARK = "https://50966981.fs1.hubspotusercontent-na1.net/hubfs/50966981/Logos/logo-v5-dark.png"
LOGO_LIGHT = "https://50966981.fs1.hubspotusercontent-na1.net/hubfs/50966981/Logos/logo-v5-light.png"

# bg  = card surface
# tx  = strong text        mu = muted text        dv = divider hairline
# sc  = soft-fill sub-card (one step off the parent surface)
# bb  = button fill        bt = button label
# ac  = accent rule (ruled eyebrow, coral bar)
# iv  = inverse fill  — a block that must contrast with the surface (solid ink
#       primary button, ghost-button outline). Flips with the register, so it
#       never disappears the way a hardcoded #15140F would on an Ink card.
# it  = text sitting on `iv`
# lg  = wordmark asset appropriate for this surface
SURFACES = {
    "bone":       dict(bg="#F7F1DE", tx="#15140F", mu="#5A5448", dv="#DDD2B6",
                       sc="#EFE7D2", bb="#ED6F5C", bt="#15140F", ac="#ED6F5C",
                       iv="#15140F", it="#F7F1DE", lg=LOGO_DARK),
    "paper":      dict(bg="#EFE7D2", tx="#15140F", mu="#5A5448", dv="#DDD2B6",
                       sc="#F7F1DE", bb="#ED6F5C", bt="#15140F", ac="#ED6F5C",
                       iv="#15140F", it="#F7F1DE", lg=LOGO_DARK),
    "paper_dark": dict(bg="#DDD2B6", tx="#15140F", mu="#5A5448", dv="#5A5448",
                       sc="#EFE7D2", bb="#ED6F5C", bt="#15140F", ac="#ED6F5C",
                       iv="#15140F", it="#F7F1DE", lg=LOGO_DARK),
    "ink":        dict(bg="#15140F", tx="#F7F1DE", mu="#DDD2B6", dv="#2A2620",
                       sc="#2A2620", bb="#ED6F5C", bt="#15140F", ac="#ED6F5C",
                       iv="#F7F1DE", it="#15140F", lg=LOGO_LIGHT),
    "ink_soft":   dict(bg="#2A2620", tx="#F7F1DE", mu="#DDD2B6", dv="#15140F",
                       sc="#15140F", bb="#ED6F5C", bt="#15140F", ac="#ED6F5C",
                       iv="#F7F1DE", it="#15140F", lg=LOGO_LIGHT),
    # Coral carries a whole block. Coral-on-coral would erase the button and the
    # accent rule, so on this surface only, the button flips to Ink and the accent
    # rule becomes Ink. Muted == strong here: hierarchy comes from weight/size,
    # because there is no muted tone that stays legible on Coral.
    "coral":      dict(bg="#ED6F5C", tx="#15140F", mu="#15140F", dv="#F08E7C",
                       sc="#F08E7C", bb="#15140F", bt="#F7F1DE", ac="#15140F",
                       iv="#15140F", it="#F7F1DE", lg=LOGO_DARK),
}

KEYS = ["bg", "tx", "mu", "dv", "sc", "bb", "bt", "ac", "iv", "it", "lg"]

ORDER = ["bone", "paper", "paper_dark", "ink", "ink_soft", "coral"]

CHOICES = [
    ["bone",       "Bone — light (default card)"],
    ["paper",      "Paper — light, one step down"],
    ["paper_dark", "Paper Dark — light, two steps down"],
    ["ink",        "Ink — dark (default dark card)"],
    ["ink_soft",   "Ink Soft — dark, one step up"],
    ["coral",      "Coral — accent block (use sparingly)"],
]


def surface_field(default="bone", exclude=()):
    """`exclude` drops surfaces that are invalid for this module.

    Structural modules (header, footer) exclude Coral: the wordmark's "co" suffix
    is Coral in both logo assets, so it vanishes on a Coral card. Coral is also
    reserved for a single offer/milestone block, never for chrome.
    """
    return {
        "id": "surface", "name": "surface", "label": "Card surface",
        "help_text": ("Sets the card colour. Text, dividers, sub-cards and the button "
                      "derive from it automatically. Coral is the loudest surface in the "
                      "system — at most one per email."),
        "required": False, "locked": False, "type": "choice", "display": "select",
        "multiple": False, "display_width": None,
        "choices": [list(c) for c in CHOICES if c[0] not in exclude], "default": default,
    }


def preamble(default="bone"):
    """One-line HubL preamble. Emits no output, defines `c`."""
    rows = []
    for k in ORDER:
        s = SURFACES[k]
        body = ",".join('"%s":"%s"' % (key, s[key]) for key in KEYS)
        rows.append('"%s":{%s}' % (k, body))
    table = "{" + ",".join(rows) + "}"
    return ("{%- set SURF = " + table + " -%}"
            "{%- set c = SURF[module.surface] -%}"
            '{%- if not c %}{% set c = SURF["' + default + '"] %}{% endif -%}')


MQ = ("<style>@media only screen and (max-width:480px){.final-card{width:100%!important}"
      ".final-pad{padding:24px!important}.final-card td{box-sizing:border-box}"
      ".stack{display:block!important;width:100%!important}}</style>")


def shell(inner, align="left", pad="32px"):
    """Standard module shell. Outer table transparent; only .final-card is coloured."""
    return (
        MQ
        + '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"'
          ' style="width:100%;background:transparent;border-radius:16px;overflow:hidden;border-collapse:separate;">'
          '<tr><td align="center" style="padding:0;border-radius:16px;">'
          '<table role="presentation" class="final-card" width="600" cellpadding="0" cellspacing="0" border="0"'
          ' style="width:600px;max-width:100%;background:{{ c.bg }};border-radius:16px;overflow:hidden;border-collapse:separate;">'
          '<tr><td class="final-pad" style="padding:' + pad + ';text-align:' + align + ';'
          'font-family:Arial,Helvetica,sans-serif;color:{{ c.tx }};font-size:16px;line-height:1.55;">'
        + inner
        + "</td></tr></table></td></tr></table>"
    )


def ruled_eyebrow(var="module.eyebrow"):
    """Signature section opener: 22px accent rule, 10px gap, tracked mono label."""
    return (
        "{% if " + var + " %}"
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 14px;"><tr>'
        '<td width="22" valign="middle" style="padding:0 10px 0 0;">'
        '<table role="presentation" width="22" cellpadding="0" cellspacing="0" border="0"><tr>'
        '<td height="1" style="background:{{ c.ac }};font-size:1px;line-height:1px;">&nbsp;</td>'
        "</tr></table></td>"
        '<td valign="middle" style="font-family:\'Courier New\',Courier,monospace;font-size:11px;'
        "letter-spacing:1.5px;text-transform:uppercase;color:{{ c.tx }};\">{{ " + var + " }}</td>"
        "</tr></table>{% endif %}"
    )


def button(align="left", top="24px"):
    m = "margin:%s auto 0;" % top if align == "center" else "margin:%s 0 0;" % top
    return (
        "{% if module.show_button == 'yes' %}"
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="' + m + '"><tr>'
        '<td style="background:{{ c.bb }};border-radius:999px;padding:13px 24px;">'
        '<a href="{{ module.button_url.href }}" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;'
        'font-weight:bold;letter-spacing:0.5px;color:{{ c.bt }};text-decoration:none;display:inline-block;">'
        "{{ module.button_label }}</a></td></tr></table>{% endif %}"
    )


def hairline(margin="24px 0"):
    return ('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"'
            ' style="margin:' + margin + ';"><tr><td height="1"'
            ' style="background:{{ c.dv }};font-size:1px;line-height:1px;">&nbsp;</td></tr></table>')
