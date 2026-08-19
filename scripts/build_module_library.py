#!/usr/bin/env python3
"""Reusable Atelier Zero module library — copy-agnostic shells, 3 surfaces each.

WHY SHELLS, NOT BAKED COPY (Vincent, 2026-08-19)
  `Text - Opening` is used by 31 different emails and `Button - Primary CTA` by 32; a saved block
  cannot hold any one email's words. So each module is saved ONCE per surface carrying neutral
  placeholder copy and correct geometry/type/palette. Real copy is injected per email at assembly.
  WB-1's modules are the exception - they were built before this decision and carry its copy.

  Placeholder copy is deliberately obvious ("Masthead headline", "Issue 00") so a shell can never
  be mistaken for finished copy and shipped by accident.

All geometry, palette and type come from scripts/az_primitives.py - never redefine them here.

  python3 scripts/build_module_library.py            # build all
  python3 scripts/build_module_library.py masthead   # build one
"""
import json
import pathlib
import sys

from az_primitives import (
    PAPER, INK, BONE, PAPER_DARK, INK_SOFT, INK_MUTE, CORAL, SURFACES, CARD, RADIUS,
    SANS, MONO, SERIF, ADDRESS,
    shell, eyebrow, title, body, meta, fine, pill, rule_line, logo_img, is_dark,
)

OUT = pathlib.Path(__file__).resolve().parent.parent / "mailerlite-blocks" / "library"
OUT.mkdir(parents=True, exist_ok=True)

# Placeholder link: the verified storefront root (200, no redirect). Never a HubSpot host -
# meetings.hubspot.com and the HubSpot CDN are dead/suspect and preflight flags them.
PLACEHOLDER_HREF = "https://hairsolutions.co/"
SITE_HREF = "https://hairsolutions.co/"
FACEBOOK_HREF = "https://www.facebook.com/hairsolutions.company"
INSTAGRAM_HREF = "https://www.instagram.com/hairsolutions.co"
YOUTUBE_HREF = "https://www.youtube.com/@hairsolutions_co"
DOT = "&nbsp;&middot;&nbsp;"

# Multi-column modules need a real media query to stack on a phone; the class names alone do
# nothing. MailerLite Code blocks accept a <style> block (it is not in FORBIDDEN_TAGS), and the
# Atelier Zero originals carried one for exactly this reason. Only emitted by modules that
# actually have columns - a single-column card must not carry dead CSS.
RESPONSIVE_CSS = (
    '<style>'
    '@media only screen and (max-width:480px){'
    '.az-stack{display:block!important;width:100%!important;box-sizing:border-box!important;}'
    '.az-mobile-pad{padding-left:24px!important;padding-right:24px!important;}'
    '.az-module-shell img{max-width:100%!important;height:auto!important;}'
    '}'
    '</style>'
)


def _link(href, label, color, external=True):
    """Footer links are inlined INSIDE fine()/meta() so the type stack is never re-declared."""
    rel = ' target="_blank" rel="noopener noreferrer"' if external else ''
    return (f'<a href="{href}"{rel} style="color:{color};'
            f'text-decoration:underline;">{label}</a>')


# ---------------------------------------------------------------- text ----
def text_masthead(surface):
    """Newsletter masthead: section label, headline, issue/date line.

    Role = Title -> radius/2xl 20px (DESIGN.md A3). The Atelier Zero original used a 34px headline
    and a 16px meta line; neither is in our five-size scale (11/12/15/22/26), so the headline maps
    to 26px and the meta line to the 11px Courier metadata role.
    """
    d = is_dark(surface)
    return shell(surface, (
        f'<tr><td align="center" style="padding:34px 34px 30px;">'
        f'{eyebrow("Section label", CORAL)}'
        f'{title("Masthead headline", d)}'
        f'{rule_line(surface, margin="20px auto 0")}'
        f'{meta("Issue 00 &middot; Month Year", PAPER_DARK if d else INK_MUTE, top=16)}'
        f'</td></tr>'), role="title")


def text_opening(surface):
    """Opening block: section label, headline, one or two paragraphs of body copy.

    Role = Content -> radius 20px. It is a reading block, not a masthead: eyebrow, title and body
    are left-aligned because a centred rag breaks the 52ch measure contract once real
    multi-sentence copy is injected. Shared by 31 emails, so copy is placeholder only.
    """
    d = is_dark(surface)
    return shell(surface, (
        f'<tr><td style="padding:32px 34px;">'
        f'{eyebrow("Section label", CORAL, align="left")}'
        f'{title("Opening headline", d, align="left")}'
        f'{body("Opening paragraph goes here.", d, top=16, align="left")}'
        f'{body("Second paragraph goes here &mdash; delete if unused.", d, top=12, align="left")}'
        f'</td></tr>'), role="content")


def button_primary_cta(surface):
    """Primary CTA block: headline, one supporting line, one pill button.

    Role = CTA -> 20px; the button is the 999px pill, Coral fill with an INK label on every
    surface (Bone on Coral fails contrast). Centred, unlike the text modules: a lone action needs
    the button optically centred under its headline. Exactly one CTA per module.
    """
    d = is_dark(surface)
    return shell(surface, (
        f'<tr><td align="center" style="padding:34px 34px 36px;">'
        f'{title("Call to action headline", d)}'
        f'{body("Supporting line goes here.", d, top=12)}'
        f'{pill("Primary action", PLACEHOLDER_HREF)}'
        f'</td></tr>'), role="cta")


def text_reassurance(surface):
    """Reassurance block: label, headline, intro, three hairline-split points.

    Point labels use the Courier metadata role - PLATFORM_EMAIL.md §3 assigns Courier to
    "metadata, eyebrow labels, order/spec details", which is what these row labels are, and it
    keeps the module inside the five-size scale without inventing a sixth style. Separators come
    from rule_line() so they take the surface's own hairline token; the original hardcoded
    #DDD2B6, which is right on Paper/Bone and wrong on Ink.
    """
    d = is_dark(surface)
    points = "".join(
        f'{rule_line(surface, margin="22px 0 0" if n == 1 else "20px 0 0")}'
        f'{meta(f"Point {n} label", BONE if d else INK, top=16, align="left")}'
        f'{body("Supporting sentence goes here.", d, top=6, align="left")}'
        for n in (1, 2, 3))
    return shell(surface, (
        f'<tr><td style="padding:32px 34px;">'
        f'{eyebrow("Section label", CORAL, align="left")}'
        f'{title("Reassurance headline", d, align="left")}'
        f'{body("Reassurance paragraph goes here.", d, top=16, align="left")}'
        f'{points}</td></tr>'), role="content")


# ------------------------------------------------------- hero / founder ----
def hero_text_led(surface):
    """Text-led hero: eyebrow, headline, supporting paragraph, CTA, fine print.

    Role = Hero -> radius/lg 12px: this card sits directly under the header, and the smaller
    radius is what separates the opening card from the 20px content cards below it. No Georgia -
    a hero headline is the Arial title role. No fitted `measure`: real copy arrives per email, and
    a measure fitted to placeholder text is a lie. The original's CTA pointed at
    meetings.hubspot.com, which is dead to us and flagged by preflight.
    """
    d = is_dark(surface)
    return shell(surface, (
        f'<tr><td align="center" style="padding:38px 34px 24px;">'
        f'{eyebrow("Hero eyebrow")}'
        f'{title("Hero headline goes here", d)}'
        f'{body("Placeholder supporting sentence for the hero &mdash; one or two lines that set up "
               "the single idea this email carries.", d, top=18)}'
        f'{pill("Primary action &rarr;", PLACEHOLDER_HREF)}'
        f'</td></tr>'
        f'<tr><td align="center" style="padding:0 34px 34px;">'
        f'{fine("Placeholder reassurance line.", PAPER_DARK if d else INK_MUTE)}'
        f'</td></tr>'), role="hero")


def layout_founder_wrapper(surface):
    """Plain-text founder wrapper: greeting, letter body, one italic line, rule, signature.

    Role = Content -> 20px, because it is a body card in the stack, not the opening card; the
    hero's 12px would make a mid-stack card read as a second hero.

    GEORGIA IS LEGITIMATE HERE. §3 role-locks serif italic to a short emphasis phrase, a pull
    quote, or a founder note, and §5 allows exactly one short accented line. So this carries ONE
    short line at the 22px quote size - never a whole paragraph, which would change the voice.
    Left-aligned: a centred rag does not read as correspondence.
    """
    d = is_dark(surface)
    return shell(surface, (
        f'<tr><td style="padding:32px 34px 34px;">'
        f'<div style="font-family:{SANS};font-size:15px;line-height:1.65;font-weight:700;'
        f'color:{BONE if d else INK};text-align:left;">Greeting line,</div>'
        f'{body("First placeholder paragraph of the founder letter. Real copy is injected per "
               "email at assembly &mdash; this shell only carries the letter&rsquo;s geometry.",
               d, top=14, align="left")}'
        f'{body("Second placeholder paragraph, kept short so the wrapper stays a note rather "
               "than a page.", d, top=14, align="left")}'
        f'<div style="font-family:{SERIF};font-style:italic;font-size:22px;line-height:1.45;'
        f'color:{BONE if d else INK};padding-top:18px;text-align:left;">'
        f'One short emphasis line.</div>'
        f'{rule_line(surface, margin="22px 0 0")}'
        f'<div style="font-family:{SANS};font-size:15px;line-height:1.65;font-weight:700;'
        f'color:{BONE if d else INK};text-align:left;padding-top:16px;">Founder name</div>'
        f'{meta("Role &middot; Hair Solutions&nbsp;Co.", PAPER_DARK if d else INK_MUTE, top=4, align="left")}'
        f'</td></tr>'), role="content")


# ------------------------------------------------------------- proof -------
def testimonial(surface):
    """Customer testimonial card: eyebrow, headline, one quoted line, one attribution.

    DO NOT SHIP AS-IS. The quote and attribution are placeholders. An unsourced testimonial is a
    BLOCKER (§7: testimonials require channel-specific consent) and the Proof Bank is currently
    EMPTY, so no real customer words may be embedded in a shell. Replace both lines with a real,
    consented, on-file quote before this block goes into any email.

    Geometry follows quote_accent_bar: same Coral 4px rule, 20px indent, Georgia italic 22px.
    The difference is a section headline above the quote, because this is a proof section rather
    than an aside.
    """
    d = is_dark(surface)
    muted = PAPER_DARK if d else INK_MUTE
    attribution = "&mdash; Attribution placeholder &middot; consent not yet on file"
    return shell(surface, (
        f'<tr><td style="padding:34px 34px 32px;">'
        f'{eyebrow("Section label", muted, align="left")}'
        f'{title("Testimonial headline", d, align="left")}'
        # the quote needs air under the 26px title or the two run together as one block
        f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%"'
        f' style="border-collapse:collapse;margin-top:18px;"><tr>'
        f'<td width="4" style="width:4px;background-color:{CORAL};line-height:1;font-size:0;">'
        f'&nbsp;</td>'
        f'<td valign="top" style="padding-left:20px;">'
        f'<div style="font-family:{SERIF};font-style:italic;font-size:22px;line-height:1.45;'
        f'font-weight:700;color:{BONE if d else INK};margin:0 0 14px;">'
        f'Placeholder quote line &mdash; replace with a real, consented customer'
        f'&nbsp;testimonial.</div>'
        f'{meta(attribution, muted, top=0, align="left")}'
        f'</td></tr></table>'
        f'</td></tr>'), role="content")


def quote_centered(surface):
    """A single centred pull quote with attribution. No headline, no eyebrow, no CTA.

    Georgia italic is correct here - the pull quote is one of the three roles the serif is locked
    to. Size, weight and line-height match quote_accent_bar so the two quote variants read as one
    family; the accent bar is dropped because a centred quote is already set apart by its axis,
    and a left rule on centred text has nothing to align to.

    If the quote is ever attributed to a customer rather than to Vincent, the same consent gate
    that governs `testimonial` applies.
    """
    d = is_dark(surface)
    return shell(surface, (
        f'<tr><td align="center" style="padding:36px 34px 34px;">'
        f'<div style="font-family:{SERIF};font-style:italic;font-size:22px;line-height:1.45;'
        f'font-weight:700;color:{BONE if d else INK};text-align:center;">'
        f'&ldquo;Placeholder pull quote &mdash; one sentence, replaced per&nbsp;email.&rdquo;</div>'
        f'{meta("Attribution placeholder", PAPER_DARK if d else INK_MUTE, top=18)}'
        f'</td></tr>'), role="content")


def faq(surface):
    """Enumerable question/answer pairs: eyebrow, headline, intro, three Q/A rows.

    Arial throughout, question and answer. Georgia is role-locked to pull quotes, short emphasis
    and the founder note; an FAQ answer is none of those.

    Table rows, not <ul>/<li>: a list is for genuinely enumerable things, which Q/A is, and a
    table row is the only list primitive Outlook's Word engine spaces predictably.
    """
    d = is_dark(surface)

    def pair(q, a):
        return (f'<tr><td>'
                f'<div style="font-family:{SANS};font-size:15px;line-height:1.5;font-weight:700;'
                f'color:{BONE if d else INK};">{q}</div>'
                f'{body(a, d, top=6, align="left")}'
                f'</td></tr>')

    return shell(surface, (
        f'<tr><td style="padding:34px 34px 32px;">'
        f'{eyebrow("Section label", CORAL, align="left")}'
        f'{title("FAQ headline", d, align="left")}'
        f'{body("Intro line for the answer set goes&nbsp;here.", d, top=16, align="left")}'
        f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%"'
        f' style="border-collapse:collapse;">'
        f'<tr><td>{rule_line(surface, margin="24px 0 20px")}</td></tr>'
        f'{pair("First question goes here?", "First answer goes here. Two plain sentences is the usual length.")}'
        f'<tr><td>{rule_line(surface)}</td></tr>'
        f'{pair("Second question goes here?", "Second answer goes here. Keep it to detail the reader can check.")}'
        f'<tr><td>{rule_line(surface)}</td></tr>'
        f'{pair("Third question goes here?", "Third answer goes here. Point to the next step without pressure.")}'
        f'</table>'
        f'</td></tr>'), role="content")


# ------------------------------------------------------ media / signal -----
def column_image_and_text(surface):
    """Two-column section: image slot beside a text block.

    NO <img>. We hold exactly two approved image assets on the MailerLite CDN - the two wordmarks
    behind logo_img(). There is no approved photographic placeholder, and the old HubSpot CDN is
    dead, so any src pointed there is a BLOCKER. A shell that ships a broken image teaches the
    assembler nothing, so the left column renders a labelled panel carrying the slot's own pixel
    dimensions. It reads correctly with images blocked because there is nothing to block, and it
    states the exact size the real asset must be cropped to. At assembly, swap the panel for a
    real <img> with meaningful alt plus explicit width and height.

    Table cells, never Grid or flex. `az-stack` + RESPONSIVE_CSS stacks the columns under 480px.
    Panel radius is the 12px hero/image role nested inside the 20px content shell; equal radii
    would flatten the nesting.
    """
    d = is_dark(surface)
    pad, gap = 30, 20
    col = (CARD - pad * 2 - gap) // 2
    img_h = col * 3 // 4
    fill = INK_SOFT if d else PAPER_DARK
    stamp = PAPER_DARK if d else INK_MUTE

    panel = (
        f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%"'
        f' style="border-collapse:separate;"><tr>'
        f'<td align="center" valign="middle" height="{img_h}" style="height:{img_h}px;'
        f'background-color:{fill};border-radius:{RADIUS["hero"]}px;padding:0 12px;">'
        f'{meta(f"IMAGE PLACEHOLDER<br/>{col}&times;{img_h}", stamp, top=0)}'
        f'</td></tr></table>')

    return RESPONSIVE_CSS + shell(surface, (
        f'<tr><td class="az-mobile-pad" style="padding:{pad}px;">'
        f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%"'
        f' style="border-collapse:collapse;"><tr>'
        f'<td class="az-stack" valign="top" width="{col}" style="width:{col}px;">{panel}</td>'
        f'<td class="az-stack" width="{gap}" style="width:{gap}px;height:{gap}px;'
        f'font-size:0;line-height:0;">&nbsp;</td>'
        f'<td class="az-stack" valign="top" width="{col}" style="width:{col}px;">'
        f'{eyebrow("Column label", CORAL, align="left")}'
        f'{title("Column headline", d, align="left")}'
        f'{body("Placeholder supporting copy for the text column &mdash; two short sentences at "
               "most. Swap the panel opposite for the real asset at assembly.", d, top=12,
               align="left")}'
        f'</td></tr></table></td></tr>'), role="content")


def signal_promo_code(surface):
    """Discount-code signal: label, headline, the code, terms.

    CORAL DISCIPLINE. A promo code is a legitimate Coral moment, but a filled Coral card would
    spend the email's single accent block (§1.1) and force Ink label text to hold contrast. So the
    code sits in a Coral-BORDERED inset over the section surface: same signal, one hairline of
    Coral, and the module stays droppable into an email that already spends its Coral on a pill.

    The code is Courier - the metadata / order-detail role - at 22px. `CODEHERE` is deliberately
    fake: the live codes (FREESHIP, WELCOMEBACK20, RETURNING15) belong to specific campaigns and a
    shell must never carry one.
    """
    d = is_dark(surface)
    chip = (
        f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%"'
        f' style="border-collapse:separate;"><tr>'
        f'<td align="center" style="background-color:transparent;border:1px solid {CORAL};'
        f'border-radius:{RADIUS["nav"]}px;padding:20px 16px;">'
        f'<div style="font-family:{MONO};font-size:22px;line-height:1.3;font-weight:700;'
        f'letter-spacing:3px;color:{BONE if d else INK};">CODEHERE</div>'
        f'{meta("Offer terms &mdash; one line", PAPER_DARK if d else INK_MUTE, top=8)}'
        f'</td></tr></table>')

    return shell(surface, (
        f'<tr><td align="center" style="padding:34px 34px 32px;">'
        f'{eyebrow("Offer label")}'
        f'{title("Promo headline", d)}'
        f'{body("Placeholder line describing what the code applies to.", d, top=14)}'
        f'<div style="height:22px;line-height:22px;font-size:0;">&nbsp;</div>'
        f'{chip}'
        f'{body("Placeholder line on how to redeem it &mdash; one sentence.", d, top=16)}'
        f'</td></tr>'), role="content")


def list_trust_strip(surface):
    """Four short reassurance points in a 2x2 grid.

    The Atelier Zero original ran four columns across 568px, leaving each point ~130px and wrapping
    a two-word label onto three lines. Two cells per row keeps every point on the readable side of
    the measure and stacks to one column under 480px.
    """
    d = is_dark(surface)
    pad, gap = 30, 20
    col = (CARD - pad * 2 - gap) // 2
    points = [(f"Trust point 0{n}", "Placeholder supporting line, one short sentence.")
              for n in (1, 2, 3, 4)]

    def cell(label, text):
        return (f'<td class="az-stack" valign="top" width="{col}" style="width:{col}px;">'
                f'{rule_line(surface, margin="0 0 12px")}'
                f'{meta(label, BONE if d else INK, top=0, align="left")}'
                f'{body(text, d, top=6, align="left")}</td>')

    spacer_col = (f'<td class="az-stack" width="{gap}" style="width:{gap}px;height:{gap}px;'
                  f'font-size:0;line-height:0;">&nbsp;</td>')
    spacer_row = ('<tr><td colspan="3" height="24" style="height:24px;font-size:0;'
                  'line-height:0;">&nbsp;</td></tr>')

    return RESPONSIVE_CSS + shell(surface, (
        f'<tr><td class="az-mobile-pad" align="center" style="padding:32px {pad}px 12px;">'
        f'{eyebrow("Strip label")}'
        f'{title("Trust strip headline", d)}'
        f'</td></tr>'
        f'<tr><td class="az-mobile-pad" style="padding:16px {pad}px 32px;">'
        f'<table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%"'
        f' style="border-collapse:collapse;">'
        f'<tr>{cell(*points[0])}{spacer_col}{cell(*points[1])}</tr>'
        f'{spacer_row}'
        f'<tr>{cell(*points[2])}{spacer_col}{cell(*points[3])}</tr>'
        f'</table></td></tr>'), role="content")


# ------------------------------------------------------------ footers -----
def footer_social(surface):
    """Footer carrying the brand's social presence.

    Social accounts are TEXT links, never icons - there is no approved icon asset on the MailerLite
    CDN, and a broken image in a footer is worse than a word. Each link points at the real brand
    account; a bare domain (facebook.com/) is a preflight FAIL.

    Compliance carried: the literal {$unsubscribe} token, sender identity, and the verified
    Tallinn postal address from az_primitives.ADDRESS.
    """
    d = is_dark(surface)
    pri = BONE if d else INK
    sec = PAPER_DARK if d else INK_MUTE
    social = (_link(FACEBOOK_HREF, "Facebook", sec) + DOT
              + _link(INSTAGRAM_HREF, "Instagram", sec) + DOT
              + _link(YOUTUBE_HREF, "YouTube", sec))
    unsub = _link("{$unsubscribe}", "Unsubscribe or update how often you hear from us",
                  pri, external=False)
    identity = (f'<strong style="color:{pri};">Hair Solutions Co.</strong><br/>'
                f'{ADDRESS}<br/>{_link(SITE_HREF, "hairsolutions.co", sec)}')
    return shell(surface, (
        f'<tr><td align="center" style="padding:30px 34px 32px;">'
        f'{eyebrow("Follow along", sec)}'
        f'{fine(social, sec)}'
        f'{rule_line(surface, margin="20px 0")}'
        f'{fine(unsub, pri)}'
        f'{rule_line(surface, margin="20px 0")}'
        f'{fine(identity, sec)}'
        f'{meta("You are receiving this because you subscribed at hairsolutions.co.", sec, top=14)}'
        f'</td></tr>'), role="footer")


def footer_standard(surface):
    """Plain compliance footer - no social block. The quietest footer in the system.

    Geometry, padding and link colours are identical to footer_social and to WB-1's
    preference_centre(), so swapping one for another never changes the card's shape.

    Compliance carried: the literal {$unsubscribe} token, sender identity, and the verified
    Tallinn postal address.
    """
    d = is_dark(surface)
    pri = BONE if d else INK
    sec = PAPER_DARK if d else INK_MUTE
    identity = (f'<strong style="color:{pri};">Hair Solutions Co.</strong><br/>{ADDRESS}<br/>'
                f'{_link(SITE_HREF, "hairsolutions.co", sec)}')
    unsub = _link("{$unsubscribe}", "Unsubscribe or manage your preferences", pri, external=False)
    return shell(surface, (
        f'<tr><td align="center" style="padding:30px 34px 32px;">'
        f'{fine(identity, sec)}'
        f'{rule_line(surface, margin="20px 0")}'
        f'{fine(unsub, pri)}'
        f'{meta("Sent because you asked to hear from us &mdash; that&rsquo;s the only reason.", sec, top=14)}'
        f'</td></tr>'), role="footer")


MODULES = {
    "Text - Masthead": text_masthead,
    "Text - Opening": text_opening,
    "Button - Primary CTA": button_primary_cta,
    "Text - Reassurance": text_reassurance,
    "Hero - Text-led": hero_text_led,
    "Layout - Plain-text founder wrapper": layout_founder_wrapper,
    "Testimonial": testimonial,
    "Quote - Centered": quote_centered,
    "FAQ": faq,
    "Column - Image and text": column_image_and_text,
    "Signal - Promo code": signal_promo_code,
    "List - Trust strip": list_trust_strip,
    "Footer - Social": footer_social,
    "Footer - Standard": footer_standard,
}


def slug(name):
    return name.lower().replace(" - ", "__").replace(" ", "_")


def main():
    only = sys.argv[1].lower() if len(sys.argv) > 1 else None
    blocks = {}
    for name, fn in MODULES.items():
        if only and only not in slug(name):
            continue
        for sname, sf in SURFACES.items():
            blocks[f"{name} - {sname}"] = fn(sf)

    if not blocks:
        sys.exit(f"no module matched {only!r}. known: {list(MODULES)}")

    for n, h in blocks.items():
        (OUT / f"{slug(n)}.html").write_text(h + "\n", encoding="utf-8")
    (OUT / "_library.json").write_text(json.dumps(blocks, indent=1), encoding="utf-8")

    print(f"built {len(blocks)} shells ({len(blocks)//3} modules x 3 surfaces) -> {OUT}")


if __name__ == "__main__":
    main()
