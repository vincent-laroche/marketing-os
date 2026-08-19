#!/usr/bin/env python3
"""Shared Atelier Zero email primitives — the single source of the WB-1 standard.

Extracted 2026-08-19 so `build_wb1.py` and `build_module_library.py` cannot drift. Every rule
encoded here was paid for once; do not re-derive it inline in a builder.

AUTHORITY
  1. brand-design-system/specs/PLATFORM_EMAIL.md  — palette roles, surfaces, type roles, voice
  2. Figma Email Design System 9Il504CQE8jLaUTBVzphqc + DESIGN.md — radius, spacing, shadow only
     (the spec is silent on radius, so radius comes from here)

THE RULES, and why each exists
  * CARD + 2*GUTTER = 600. Card max-width 576, wrapper cell `padding:0 12px` with ZERO vertical
    padding. The inset is what makes flush-stacked rounded corners read as separate cards; any
    vertical wrapper padding breaks the stack and is a MAJOR.
  * Radius is ROLE-BASED, never one uniform value. nav 8 / hero 12 / footer,divider,blog 16 /
    title,content,cta 20 / pill 999. A single radius across an email is a MAJOR.
  * Every card carries a 1px hairline in a NAMED token. rgba() in a border is a MAJOR - Outlook's
    Word engine cannot parse it and may fall back to black. Never pre-composite the alpha either:
    that invents off-palette values (#DED6C2, #E5DFCD ...) which are not brand tokens.
  * Three role-locked type stacks, verbatim. 'Helvetica Neue' and SF Mono are NOT in the system.
  * Five sizes, two weights. Count styles, not families.
  * Optical compensation on titles: -0.3px on light, +0.2px on Ink. Light-on-dark irradiates, so
    identical CSS reads heavier and tighter; tracking is the only lever Arial gives us.
  * Surfaces: Paper, Bone or Ink (Coral for at most one accent block, never header/footer).
    Bone became legal 2026-08-19. Paper Dark and Ink Soft are NEVER section surfaces, and Bone
    must never sit directly adjacent to Paper.
"""

# ---- palette (PLATFORM_EMAIL.md) ------------------------------------------
PAPER, INK, BONE = "#EFE7D2", "#15140F", "#F7F1DE"
PAPER_DARK, INK_SOFT, INK_MUTE, CORAL = "#DDD2B6", "#2A2620", "#5A5448", "#ED6F5C"

SURFACES = {"Bone": BONE, "Paper": PAPER, "Ink": INK}

# ---- type: three role-locked stacks ---------------------------------------
SANS = "Arial, Helvetica, sans-serif"                      # headings, body, buttons, footer
MONO = "'Courier New', Courier, monospace"                 # metadata + eyebrow labels ONLY
SERIF = "Georgia, 'Times New Roman', Times, serif"         # pull quote, founder note ONLY
# scale: 11 eyebrow/meta · 12 fine print · 15 body/label · 22 quote · 26 title

# ---- geometry -------------------------------------------------------------
RADIUS = {"nav": 8, "hero": 12, "footer": 16, "divider": 16, "blog": 16,
          "content": 20, "title": 20, "cta": 20}
GUTTER = 12
CARD = 600 - GUTTER * 2                                    # 576
HAIRLINE = {PAPER: PAPER_DARK, INK: INK_SOFT, BONE: PAPER_DARK}
RULE = HAIRLINE

# ---- approved assets ------------------------------------------------------
LOGO_INK = ("https://storage.mlcdn.com/account_image/2582639/"
            "KFEEEOLO86h7tNAsKTXCNm7jzoBw1XZ4S3TXEZD9.png")   # ink letterforms, for light
LOGO_BONE = ("https://storage.mlcdn.com/account_image/2582639/"
             "6YZqwFXIewpePuTHcJLQmFlttJt1y0sAAo1GkX5f.png")  # bone letterforms, for Ink
ADDRESS = "Ehitajate tee 110, Tallinn, Estonia"


def is_dark(surface):
    return surface == INK


def shell(surface, inner, role="content"):
    r = RADIUS[role]
    return (f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%"'
            f' style="background-color:transparent;border-collapse:collapse;margin:0;">'
            f'<tr><td align="center" style="padding:0 {GUTTER}px;">'
            f'<table border="0" cellpadding="0" cellspacing="0" role="presentation"'
            f' class="az-module-shell" width="100%" style="max-width:{CARD}px;'
            f'background-color:{surface};border:1px solid {HAIRLINE[surface]};'
            f'border-radius:{r}px;border-collapse:separate;">{inner}</table></td></tr></table>')


def eyebrow(text, color=CORAL, align="center"):
    return (f'<div style="font-family:{MONO};font-size:11px;font-weight:700;letter-spacing:2px;'
            f'text-transform:uppercase;color:{color};padding-bottom:16px;text-align:{align};">'
            f'<span style="letter-spacing:0;padding-right:8px;">&mdash;</span>{text}</div>')


def title(text, on_dark, align="center"):
    track = "0.2px" if on_dark else "-0.3px"
    return (f'<div style="font-family:{SANS};font-size:26px;line-height:1.25;font-weight:700;'
            f'letter-spacing:{track};color:{BONE if on_dark else INK};'
            f'text-align:{align};">{text}</div>')


def body(text, on_dark, top=14, align="center", measure=None):
    """`measure` = max line length in px, fitted per paragraph by scripts/measure_lines.py.

    Email has no `text-wrap: balance` and every client greedy-wraps, so the last line's length is
    an accident unless the measure is fitted. Band is 380-440px (53-61 chars).
    """
    m = (f'max-width:{measure}px;margin-left:auto;margin-right:auto;' if measure else '')
    return (f'<div style="font-family:{SANS};font-size:15px;line-height:1.65;'
            f'color:{PAPER_DARK if on_dark else INK_MUTE};text-align:{align};'
            f'padding-top:{top}px;{m}">{text}</div>')


def meta(text, color=INK_MUTE, top=4, align="center"):
    return (f'<div style="font-family:{MONO};font-size:11px;line-height:1.5;color:{color};'
            f'text-align:{align};padding-top:{top}px;">{text}</div>')


def fine(text, color=PAPER_DARK):
    return (f'<div style="font-family:{SANS};font-size:12px;line-height:1.7;color:{color};'
            f'text-align:center;">{text}</div>')


def pill(label, href):
    """Coral fill, INK label. Bone on Coral fails contrast (PLATFORM_EMAIL.md §5 CTA)."""
    return (f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" align="center"'
            f' style="margin:26px auto 0;border-collapse:separate;"><tr>'
            f'<td align="center" style="background-color:{CORAL};border-radius:999px;">'
            f'<a href="{href}" target="_blank" rel="noopener noreferrer" style="display:inline-block;'
            f'padding:15px 30px;font-family:{SANS};font-size:15px;font-weight:700;color:{INK};'
            f'text-decoration:none;">{label}</a></td></tr></table>')


def rule_line(surface, margin="20px 0"):
    return (f'<div style="height:1px;background-color:{RULE[surface]};margin:{margin};'
            f'line-height:1px;font-size:0;">&nbsp;</div>')


def logo_img(surface):
    """Returns (src, width, height, cell_padding). The dark mark has ~24px baked margin, so its
    padding differs; both render a 114px-tall card."""
    if is_dark(surface):
        return LOGO_BONE, 259, 114, "0 26px"
    return LOGO_INK, 220, 66, "24px 26px"
