#!/usr/bin/env python3
"""WB-1 · Checking In — Day 0. Copy verbatim from emails_master CSV Body.

TYPE SYSTEM — PLATFORM_EMAIL.md §3. Three families, each ROLE-LOCKED. Never mix roles:
  Arial   -> headings, body, buttons, captions, footer   (bold echoes Inter Tight)
  Courier -> metadata + eyebrow labels only
  Georgia italic -> short emphasis, pull quote, founder note ONLY
Scale is 5 sizes / 2 weights / 1 letter-spacing. Tracked uppercase is for eyebrows, never body.
Surfaces: Paper #EFE7D2 or Ink #15140F only. Flush stack: zero vertical wrapper padding.
"""
import json, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "mailerlite-blocks"
PAPER, INK, BONE = "#EFE7D2", "#15140F", "#F7F1DE"
PAPER_DARK, INK_SOFT, INK_MUTE, CORAL = "#DDD2B6", "#2A2620", "#5A5448", "#ED6F5C"

SANS  = "Arial, Helvetica, sans-serif"
MONO  = "'Courier New', Courier, monospace"
SERIF = "Georgia, 'Times New Roman', Times, serif"
# scale: 11 eyebrow/meta · 12 fine print · 15 body/label · 22 quote · 26 title
LOGO_BONE = "https://storage.mlcdn.com/account_image/2582639/6YZqwFXIewpePuTHcJLQmFlttJt1y0sAAo1GkX5f.png"
LOGO_INK  = "https://storage.mlcdn.com/account_image/2582639/KFEEEOLO86h7tNAsKTXCNm7jzoBw1XZ4S3TXEZD9.png"
REPLY = "mailto:info@hairsolutions.co?subject=Re%3A%20Checking%20in"

# Radius is ROLE-BASED, not one value - measured from the Figma Email Design System
# (file 9Il504CQE8jLaUTBVzphqc). DESIGN.md names the tokens; the templates apply them:
#   radius/md  8px  -> Navigation / header      radius/lg  12px -> Hero
#   radius/xl  16px -> Footer, Divider, Blog    radius/2xl 20px -> Title, Content, Call-To-Action
RADIUS = {"nav": 8, "hero": 12, "footer": 16, "divider": 16, "content": 20, "cta": 20}

# Wrapper arithmetic: CARD + 2*GUTTER = 600 (PLATFORM_EMAIL.md S2 "Maximum wrapper: 600px").
# The gutter is also the mobile edge margin - the same padding applies at every width - so it
# cannot shrink far without crowding the phone bezel. 12px is spacing/md, and stays under the
# 20px content radius without reading as accidental. Figma is 600 full-bleed (gutter 0); we keep
# an inset because the inset IS what makes the rounded corners read as stacked cards.
GUTTER = 12
CARD   = 600 - GUTTER * 2
# Figma draws the card stroke as rgba(21,20,15,0.08) and the divider rule as rgba(21,20,15,0.16).
# Outlook's Word engine cannot parse rgba() and may fall back to black, so both ship as solid hex.
# Do NOT composite the alpha into a new value - that invents off-palette colours (#DED6C2 etc) and
# preflight rejects them. Use the named tokens the system already has for exactly this job:
# Paper Dark = "dividers on light / borders, horizontal rules", Ink Soft = "dividers on Ink".
HAIRLINE = {PAPER: PAPER_DARK, INK: INK_SOFT, BONE: PAPER_DARK}
RULE     = {PAPER: PAPER_DARK, INK: INK_SOFT, BONE: PAPER_DARK}

def shell(surface, inner, role="content"):
    r = RADIUS[role]
    return (f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%"'
            f' style="background-color:transparent;border-collapse:collapse;margin:0;">'
            f'<tr><td align="center" style="padding:0 {GUTTER}px;">'
            f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" class="az-module-shell"'
            f' width="100%" style="max-width:{CARD}px;background-color:{surface};'
            f'border:1px solid {HAIRLINE[surface]};'
            f'border-radius:{r}px;border-collapse:separate;">{inner}</table></td></tr></table>')

# ---- the only five type roles ---------------------------------------------
def eyebrow(text, color=CORAL, align="center"):
    return (f'<div style="font-family:{MONO};font-size:11px;font-weight:700;letter-spacing:2px;'
            f'text-transform:uppercase;color:{color};padding-bottom:16px;text-align:{align};">'
            f'<span style="letter-spacing:0;padding-right:8px;">&mdash;</span>{text}</div>')

def title(text, on_dark):
    """Optical compensation. Identical CSS renders unequal: light-on-dark irradiates, so it
    reads heavier and tighter than dark-on-light. Arial has no weight above 700, so the lever
    is tracking - open the Ink title slightly, tighten the Paper one, and they meet."""
    track = "0.2px" if on_dark else "-0.3px"
    return (f'<div style="font-family:{SANS};font-size:26px;line-height:1.25;font-weight:700;'
            f'letter-spacing:{track};color:{BONE if on_dark else INK};text-align:center;">{text}</div>')

def body(text, on_dark, top=14, align="center", measure=None):
    """`measure` = max line length in px, FITTED per paragraph by scripts/measure_lines.py.

    Email clients have no `text-wrap: balance`, and greedy wrapping makes the last line
    arbitrary, so balance cannot be had by picking one global width - 380 balances this
    email's `close` but wrecks `pref`, and 410 does the reverse. The measure is therefore
    fitted per paragraph inside the readable band 380-440px (53-61 characters, comfortably
    inside the 45-75 rule). Mobile content is ~220px, narrower than the whole band, so this
    is a desktop-only correction that costs mobile nothing.
    Outlook desktop ignores max-width on a div and falls back to the full 500px - the same
    rag we have today, so the degradation is no worse than the status quo."""
    m = (f'max-width:{measure}px;margin-left:auto;margin-right:auto;' if measure else '')
    return (f'<div style="font-family:{SANS};font-size:15px;line-height:1.65;'
            f'color:{PAPER_DARK if on_dark else INK_MUTE};text-align:{align};padding-top:{top}px;{m}">{text}</div>')

def meta(text, color=INK_MUTE, top=4, align="center"):
    return (f'<div style="font-family:{MONO};font-size:11px;line-height:1.5;color:{color};'
            f'text-align:{align};padding-top:{top}px;">{text}</div>')

def fine(text, color=PAPER_DARK):
    return (f'<div style="font-family:{SANS};font-size:12px;line-height:1.7;color:{color};'
            f'text-align:center;">{text}</div>')

def pill(label, href):
    return (f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" align="center"'
            f' style="margin:26px auto 0;border-collapse:separate;"><tr>'
            f'<td align="center" style="background-color:{CORAL};border-radius:999px;">'
            f'<a href="{href}" target="_blank" rel="noopener noreferrer" style="display:inline-block;'
            f'padding:15px 30px;font-family:{SANS};font-size:15px;font-weight:700;color:{INK};'
            f'text-decoration:none;">{label}</a></td></tr></table>')

# ---- modules --------------------------------------------------------------
def header(surface, logo, w, h, pad):
    return shell(surface, (
        f'<tr><td align="center" style="padding:{pad};">'
        f'<a href="https://hairsolutions.co/" target="_blank" rel="noopener noreferrer"'
        f' style="text-decoration:none;border:none;display:inline-block;background-color:transparent;padding:0;">'
        f'<img src="{logo}" alt="Hair Solutions Co." width="{w}" height="{h}"'
        f' style="display:block;border:0;outline:none;width:{w}px;max-width:80%;height:auto;margin:0 auto;"/>'
        f'</a></td></tr>'), role="nav")

def hero(surface=INK):
    """Original approved design, restored 2026-08-19 at Vincent's request after a verbatim-copy
    revert stripped the eyebrows and left the email visually inconsistent.

    APPROVED DEVIATION from emails_master (gate 1): the eyebrow label and the recast title are
    copy that does not appear in the master Body. Recorded in mailerlite/BUILD-LEDGER.md."""
    d = surface == INK
    return shell(surface, (
        f'<tr><td style="padding:38px 34px 40px;">'
        f'{eyebrow("A quick note")}'
        f'{title("It&rsquo;s been a while,<br/>{$name|default('there')}.", d)}'
        f'{body("Your last order with us was {$months_since_last_order|default('a few')} months ago.<br/>"
               "No pitch in this email &mdash; I&rsquo;m just curious how you got on.", d, top=18)}'
        f'{body("If you&rsquo;re still wearing a system and it&rsquo;s working, that&rsquo;s good to hear "
               "and you can ignore this.", d, measure=380)}'
        f'</td></tr>'), role="hero")

def question_list(surface=PAPER):
    """APPROVED DEVIATION: eyebrow + recast title, per above."""
    d = surface == INK
    return shell(surface, (
        f'<tr><td style="padding:38px 34px 40px;">'
        f'{eyebrow("If you stopped")}'
        f'{title("I&rsquo;d honestly like<br/>to know why.", d)}'
        f'{body("Was it the maintenance? The cost? Did the fit never come right? "
               "Did you go a different&nbsp;route&nbsp;entirely?", d, top=18, measure=380)}'
        f'</td></tr>'), role="content")

def close_cta(surface=INK):
    """APPROVED DEVIATION: eyebrow, recast title, and the coral reply pill. The master CTA column
    reads "No button - reply-only by design"; Vincent approved the pill and restored it 2026-08-19."""
    d = surface == INK
    return shell(surface, (
        f'<tr><td style="padding:38px 34px 40px;">'
        f'{eyebrow("Every reply gets read")}'
        f'{title("Your answer changes<br/>what we make.", d)}'
        f'{body("The most useful feedback I&rsquo;ve had all year came from people who stopped buying.",
               d, top=18, measure=380)}'
        f'{pill("Reply and tell me &rarr;", REPLY)}'
        f'</td></tr>'), role="cta")

def quote_accent_bar(surface=PAPER):
    """Georgia italic earns its place here: a pull quote is a different voice.

    APPROVED DEVIATION (Vincent, 2026-08-19). The quote is not in emails_master and is not
    sourced from the Proof Bank, and it sits in an email whose copy says "No pitch in this
    email". Both are recorded in mailerlite/BUILD-LEDGER.md as knowingly accepted."""
    d = surface == INK
    return shell(surface, (
        f'<tr><td style="padding:36px 34px 34px;">'
        f'{eyebrow("In their words", PAPER_DARK if d else INK_MUTE, align="left")}'
        f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%"'
        f' style="border-collapse:collapse;"><tr>'
        f'<td width="4" style="width:4px;background-color:{CORAL};line-height:1;font-size:0;">&nbsp;</td>'
        f'<td valign="top" style="padding-left:20px;">'
        f'<div style="font-family:{SERIF};font-style:italic;font-size:22px;line-height:1.45;'
        f'font-weight:700;color:{BONE if d else INK};margin:0 0 14px;max-width:476px;">'
        f'The fit consultation made the whole decision feel simple instead'
        f' of&nbsp;overwhelming.</div>'
        f'{meta("&mdash; Verified customer", PAPER_DARK if d else INK_MUTE, top=0, align="left")}'
        f'</td></tr></table></td></tr>'), role="content")

def divider(surface):
    """Figma `Email / Divider` - a short card whose only content is a 1px rule.

    Figma draws this card in pure white. We use Bone #F7F1DE instead: PLATFORM_EMAIL.md S1.1
    forbids a pure-white section surface outright, and Bone is the brand's near-white. Bone is
    also nominally excluded as a *surface* by that same rule - the divider is exempted because
    it is a spacer carrying no content, confirmed by Vincent 2026-08-19.
    padding 24px 40px, radius/xl 16px. It separates two cards of the SAME surface
    without breaking the flush stack."""
    return shell(surface, (
        f'<tr><td style="padding:24px 40px;">'
        f'<div style="height:1px;background-color:{RULE[surface]};line-height:1px;font-size:0;">'
        f'&nbsp;</div></td></tr>'), role="divider")

def signoff(surface=PAPER):
    d = surface == INK
    return shell(surface, (
        f'<tr><td align="center" style="padding:28px 34px 30px;">'
        f'<div style="font-family:{SANS};font-size:15px;font-weight:700;color:{BONE if d else INK};'
        f'text-align:center;">Vincent</div>'
        f'{meta("Founder, Hair Solutions Co.", PAPER_DARK if d else INK_MUTE)}</td></tr>'), role="content")

def preference_centre(surface=INK):
    d = surface == INK
    return shell(surface, (
        f'<tr><td align="center" style="padding:30px 34px 32px;">'
        f'{eyebrow("Your preferences", PAPER_DARK)}'
        f'{body("You can hear from us less often, or not at all. Either is completely fine, and it "
               "will not affect your order or your support.", True, top=0, measure=430)}'
        f'<div style="height:1px;background-color:{INK_SOFT};margin:20px 0;line-height:1px;font-size:0;">&nbsp;</div>'
        f'<div style="font-family:{SANS};font-size:15px;line-height:1.6;text-align:center;">'
        f'<a href="{{$unsubscribe}}" style="color:{BONE};font-weight:700;text-decoration:underline;">'
        f'Unsubscribe or update how often you hear from us</a></div>'
        f'<div style="height:1px;background-color:{INK_SOFT};margin:20px 0;line-height:1px;font-size:0;">&nbsp;</div>'
        f'{fine("<strong style=\'color:"+BONE+"\'>Hair Solutions Co.</strong><br/>"
               "Ehitajate tee 110, Tallinn, Estonia<br/>"
               "<a href=\'https://www.hairsolutions.co\' style=\'color:"+PAPER_DARK+";"
               "text-decoration:underline;\'>hairsolutions.co</a>")}'
        f'</td></tr>'), role="footer")

SURFACES = {"Bone": BONE, "Paper": PAPER, "Ink": INK}
LOGO = {BONE: LOGO_INK, PAPER: LOGO_INK, INK: LOGO_BONE}
LOGO_DIM = {BONE: (220, 66, "24px 26px"), PAPER: (220, 66, "24px 26px"),
            INK: (259, 114, "0 26px")}

MODULES = {
 "Header - Centered logo": lambda sf: header(sf, LOGO[sf], *LOGO_DIM[sf]),
 "Hero - Founder opening": hero,
 "Content - Question list": question_list,
 "Content - Close":         close_cta,
 "Quote - Accent bar":      quote_accent_bar,
 "Content - Sign-off":      signoff,
 "Footer - Preference centre": preference_centre,
 "Divider":                 divider,
}

blocks = {}
for mod, fn in MODULES.items():
    for sname, sf in SURFACES.items():
        blocks[f"{mod} - {sname}"] = fn(sf)

# the shipped WB-1 stack, by saved-block name
SHIPPED = [
 "Header - Centered logo - Paper",
 "Hero - Founder opening - Ink",
 "Content - Question list - Paper",
 "Content - Close - Ink",
 "Quote - Accent bar - Paper",
 "Content - Sign-off - Paper",
 "Footer - Preference centre - Ink",
]

def slug(n):
    return n.lower().replace(" - ", "__").replace(" ", "_")

for n, h in blocks.items():
    (OUT / f"{slug(n)}.html").write_text(h + "\n", encoding="utf-8")
(OUT / "_wb1_payload.json").write_text(json.dumps(blocks, indent=1), encoding="utf-8")
(OUT / "_wb1_shipped.json").write_text(json.dumps({k: blocks[k] for k in SHIPPED}, indent=1), encoding="utf-8")

(OUT / "_wb1-assembled.html").write_text(
 '<!doctype html><html><head><meta charset="utf-8"><title>WB-1 assembled</title></head>'
 '<body style="margin:0;padding:24px 0;background:#F7F1DE;">'
 '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td align="center">'
 '<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px;max-width:100%;">'
 f'<tr><td>{"".join(blocks[k] for k in SHIPPED)}</td></tr></table></td></tr></table></body></html>',
 encoding="utf-8")
print(f"built {len(blocks)} saved-block variants ({len(MODULES)} modules x {len(SURFACES)} surfaces)")
print("shipped stack:", len(SHIPPED), "cards")
