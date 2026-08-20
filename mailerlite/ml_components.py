#!/usr/bin/env python3
"""Hair Solutions Co. — MailerLite email component library.
Design tokens from Figma Email Design System v3 (page 291:724 audit).
All components: table-based, inline CSS, 600px, Paper theme."""
import html as _html

INK      = "#15140F"
BODY_CLR = "#5A5448"
MUTED    = "#8B8676"
BONE_BG  = "#F7F1DE"
# No wallpaper behind an email. Body and outer wrapper are transparent so the
# client's own background shows through — hard rule, 2026-08-19 (AGENTS.md #5).
PAGE_BG  = "transparent"
CARD_BG  = "#EFE7D2"
FILL     = "#DDD2B6"
CORAL    = "#ED6F5C"
LOGO_DARK = "https://hairsolutions.co/cdn/shop/files/logo-dark-transparent.png?height=64&v=1785988775"
ADDR      = "Hair Solutions Co. · Ehitajate tee 110, Tallinn, Estonia"
F_DISPLAY = "'Inter Tight','Helvetica Neue',Helvetica,Arial,sans-serif"
F_BODY    = "'Inter','Helvetica Neue',Helvetica,Arial,sans-serif"
F_MONO    = "'JetBrains Mono','Courier New',monospace"
E = _html.escape

def preheader(text):
    return (f'<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;">{E(text)}'
            f'&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;</div>')

def header_logo():
    return f'''
  <tr><td align="center" style="padding:28px 32px 8px 32px;">
    <a href="https://hairsolutions.co" target="_blank">
      <img src="{LOGO_DARK}" alt="Hair Solutions Co." width="148"
           style="display:block;margin:0 auto;border:0;width:148px;max-width:60%;height:auto;">
    </a></td></tr>'''

def masthead(text="Hair Solutions Co. — the newsletter"):
    return f'''
  <tr><td style="padding:22px 32px 0 32px;">
    <table role="presentation" cellpadding="0" cellspacing="0"><tr>
      <td width="22" style="border-top:1px solid {CORAL};font-size:0;line-height:0;">&nbsp;</td>
      <td style="padding-left:10px;font-family:{F_MONO};font-size:11px;line-height:15px;letter-spacing:1.5px;text-transform:uppercase;color:{INK};">{E(text)}</td>
    </tr></table></td></tr>'''

def hero(text):
    return f'''
  <tr><td style="padding:28px 32px 8px 32px;">
    <h1 style="margin:0;font-family:{F_DISPLAY};font-weight:800;font-size:24px;line-height:30px;letter-spacing:-0.3px;color:{INK};">{text}</h1>
  </td></tr>'''

def p(text, pad_top=8):
    return f'''
  <tr><td style="padding:{pad_top}px 32px 0 32px;font-family:{F_BODY};font-size:15px;line-height:23px;color:{BODY_CLR};">{text}</td></tr>'''

def signature():
    return p(f'<span style="font-style:italic;color:{INK};">Vincent</span><br>'
             f'<span style="font-size:13px;color:{MUTED};">Founder, Hair Solutions Co.</span>', pad_top=12)

def numlist(items):
    rows = "".join(f'''
      <tr><td width="26" valign="top" style="padding:10px 0 0 0;font-family:{F_MONO};font-size:12px;color:{CORAL};">{i:02d}</td>
          <td style="padding:10px 0 0 8px;font-family:{F_BODY};font-size:15px;line-height:23px;color:{BODY_CLR};">{t}</td></tr>''' for i, t in enumerate(items, 1))
    return f'''
  <tr><td style="padding:10px 32px 0 32px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">{rows}</table></td></tr>'''

def dashlist(items):
    rows = "".join(f'''
      <tr><td width="18" valign="top" style="padding:6px 0 0 0;font-family:{F_BODY};font-size:15px;color:{CORAL};">—</td>
          <td style="padding:6px 0 0 6px;font-family:{F_BODY};font-size:15px;line-height:23px;color:{BODY_CLR};">{t}</td></tr>''' for t in items)
    return f'''
  <tr><td style="padding:6px 32px 0 32px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">{rows}</table></td></tr>'''

def qa(pairs):
    out = ""
    for q, a in pairs:
        out += f'''
      <tr><td style="padding:14px 32px 0 32px;font-family:{F_BODY};font-weight:600;font-size:13px;line-height:19px;color:{INK};">{E(q)}</td></tr>
      <tr><td style="padding:3px 32px 0 32px;font-family:{F_BODY};font-size:13px;line-height:21px;color:{BODY_CLR};">{E(a)}</td></tr>'''
    return out

def cta(label, url, pad_top=26):
    return f'''
  <tr><td align="center" style="padding:{pad_top}px 32px 8px 32px;">
    <a href="{url}" target="_blank"
       style="display:inline-block;background-color:{CORAL};color:{INK};font-family:{F_DISPLAY};font-weight:600;font-size:13px;letter-spacing:0.5px;text-decoration:none;padding:16px 30px;border-radius:999px;line-height:1;">{E(label)}</a>
  </td></tr>'''

def cta_dual(l1, u1, l2, u2):
    return f'''
  <tr><td align="center" style="padding:26px 32px 4px 32px;">
    <a href="{u1}" target="_blank" style="display:inline-block;background-color:{CORAL};color:{INK};font-family:{F_DISPLAY};font-weight:600;font-size:13px;letter-spacing:0.5px;text-decoration:none;padding:16px 26px;border-radius:999px;line-height:1;">{E(l1)}</a>
    <span style="display:inline-block;width:10px;">&nbsp;</span>
    <a href="{u2}" target="_blank" style="display:inline-block;background-color:transparent;color:{INK};font-family:{F_DISPLAY};font-weight:600;font-size:13px;letter-spacing:0.5px;text-decoration:none;padding:15px 24px;border-radius:999px;border:1px solid {INK};line-height:1;">{E(l2)}</a>
  </td></tr>'''

def kv_table(rows, title=None):
    t = f'<tr><td colspan="2" style="padding:0 0 10px 0;font-family:{F_MONO};font-size:11px;letter-spacing:1.2px;text-transform:uppercase;color:{INK};">{E(title)}</td></tr>' if title else ""
    body = "".join(f'''
      <tr><td width="140" style="padding:9px 0;border-top:1px solid {FILL};font-family:{F_BODY};font-size:13px;line-height:19px;color:{BODY_CLR};">{E(k)}</td>
          <td style="padding:9px 0;border-top:1px solid {FILL};font-family:{F_BODY};font-weight:600;font-size:13px;line-height:19px;color:{INK};">{v}</td></tr>''' for k, v in rows)
    return f'''
  <tr><td style="padding:18px 32px 4px 32px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-bottom:1px solid {FILL};">{t}{body}</table>
  </td></tr>'''

def promo(code, line1, validity):
    return f'''
  <tr><td style="padding:20px 32px 4px 32px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:{CORAL};border-radius:16px;">
      <tr><td align="center" style="padding:22px 24px 6px 24px;font-family:{F_BODY};font-size:14px;line-height:20px;color:{INK};">{E(line1)}</td></tr>
      <tr><td align="center" style="padding:2px 24px 2px 24px;font-family:{F_MONO};font-size:20px;letter-spacing:2px;color:{INK};"><strong>{E(code)}</strong></td></tr>
      <tr><td align="center" style="padding:2px 24px 18px 24px;font-family:{F_MONO};font-size:11px;letter-spacing:1.2px;text-transform:uppercase;color:{INK};">{E(validity)}</td></tr>
    </table></td></tr>'''

def photo_slot(caption, note):
    return f'''
  <!-- PHOTO NEEDED: {E(note)} — replace this placeholder block before send. -->
  <tr><td style="padding:20px 32px 4px 32px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      <tr><td align="center" style="background-color:{FILL};border-radius:16px;padding:64px 24px;font-family:{F_MONO};font-size:11px;letter-spacing:1px;text-transform:uppercase;color:{BODY_CLR};">[ Photo — {E(note)} ]</td></tr>
      <tr><td style="padding:8px 4px 0 4px;font-family:{F_BODY};font-size:12px;line-height:18px;color:{MUTED};">{E(caption)}</td></tr>
    </table></td></tr>'''

def product_grid(items, title=None):
    t = f'''<tr><td style="padding:22px 6px 0 6px;font-family:{F_MONO};font-size:11px;letter-spacing:1.2px;text-transform:uppercase;color:{INK};">{E(title)}</td></tr>''' if title else ""
    cells = ""
    for i in range(0, len(items), 2):
        row = items[i:i+2]
        cells += '<tr>'
        for it in row:
            if it.get("img"):
                visual = f'<img src="{it["img"]}" width="240" style="display:block;width:100%;border-radius:12px;border:0;" alt="{E(it["name"])}">'
            else:
                visual = (f'<table role="presentation" width="100%"><tr><td align="center" style="background-color:{FILL};border-radius:12px;padding:46px 10px;'
                          f'font-family:{F_MONO};font-size:10px;letter-spacing:1px;text-transform:uppercase;color:{BODY_CLR};">[ {E(it.get("note","Product"))} ]</td></tr></table>')
            cells += f'''<td width="50%" valign="top" style="padding:10px 6px 0 6px;">
              <a href="{it["url"]}" target="_blank" style="text-decoration:none;">{visual}
              <div style="padding:8px 2px 0 2px;font-family:{F_BODY};font-weight:600;font-size:13px;line-height:18px;color:{INK};">{E(it["name"])}</div>
              <div style="padding:2px 2px 0 2px;font-family:{F_BODY};font-size:13px;color:{BODY_CLR};">{E(it["price"])}</div></a></td>'''
        if len(row) == 1:
            cells += '<td width="50%">&nbsp;</td>'
        cells += '</tr>'
    return f'''
  <tr><td style="padding:4px 26px 0 26px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">{t}{cells}</table></td></tr>'''



def trust_strip():
    return f'''
  <tr><td align="center" style="padding:20px 32px 4px 32px;font-family:{F_MONO};font-size:11px;letter-spacing:1px;text-transform:uppercase;color:{MUTED};">
    Handcrafted to your spec &nbsp;·&nbsp; 14-day inspection window &nbsp;·&nbsp; Direct line to the founder
  </td></tr>'''

def support(text):
    return f'''
  <tr><td align="center" style="padding:18px 32px 4px 32px;font-family:{F_BODY};font-size:13px;line-height:19px;color:{BODY_CLR};">
    <span style="color:{CORAL};">&#9632;</span>&nbsp; {text}
  </td></tr>'''

def cart_placeholder():
    return f'''
  <!-- DYNAMIC BLOCK — IN MAILERLITE: delete this static block and insert the native
       E-commerce -> "Abandoned cart" block so real cart line items render per recipient. -->
  <tr><td style="padding:18px 32px 4px 32px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px dashed {MUTED};border-radius:12px;">
      <tr><td align="center" style="padding:26px 20px;font-family:{F_MONO};font-size:11px;letter-spacing:1px;text-transform:uppercase;color:{BODY_CLR};">
        [ Abandoned-cart block — live items render at send time ]</td></tr>
    </table></td></tr>'''

def footer(variant="preference"):
    social = ""
    if variant == "social":
        social = f'''<div style="padding:0 0 10px 0;font-family:{F_MONO};font-size:11px;letter-spacing:1.2px;text-transform:uppercase;">
          <a href="https://www.instagram.com/hairsolutionsco" style="color:{BODY_CLR};text-decoration:underline;">Instagram</a> &nbsp;·&nbsp;
          <a href="https://hairsolutions.co" style="color:{BODY_CLR};text-decoration:underline;">Website</a> &nbsp;·&nbsp;
          <a href="https://hairsolutions.co/pages/help-center" style="color:{BODY_CLR};text-decoration:underline;">Help centre</a></div>'''
    tagline = f'<div style="padding:0 0 8px 0;font-family:{F_BODY};font-weight:600;font-size:12px;color:{INK};">Hair Solutions Co.</div>' if variant == "standard" else ""
    return f'''
  <tr><td align="center" style="padding:34px 32px 40px 32px;border-top:1px solid {FILL};">
    {tagline}{social}
    <div style="font-family:{F_BODY};font-size:12px;line-height:19px;color:{BODY_CLR};">{ADDR}</div>
    <div style="padding-top:8px;font-family:{F_BODY};font-size:12px;line-height:19px;color:{MUTED};">
      You're receiving this because you subscribed or ordered at hairsolutions.co.<br>
      <a href="{{$unsubscribe}}" style="color:{MUTED};text-decoration:underline;">Unsubscribe</a> &nbsp;·&nbsp;
      <a href="{{$url}}" style="color:{MUTED};text-decoration:underline;">View in browser</a>
    </div>
  </td></tr>'''

def shell(title, pre, body_rows):
    return f'''<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="IE=edge"><title>{E(title)}</title>
<!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript><![endif]-->
<style>@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Inter+Tight:wght@600;800&family=JetBrains+Mono:wght@400;600&display=swap');
@media only screen and (max-width:620px){{.ml-container{{width:100%!important;}}td{{padding-left:24px!important;padding-right:24px!important;}}}}</style>
</head>
<body style="margin:0;padding:0;background-color:{PAGE_BG};-webkit-text-size-adjust:100%;">
{preheader(pre)}
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:{PAGE_BG};"><tr><td align="center">
<table role="presentation" class="ml-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:{CARD_BG};">
{header_logo()}
{body_rows}
</table></td></tr></table>
</body></html>'''


def add_utm(html, slug):
    """Append campaign UTM params to hairsolutions.co links only.

    Skips MailerLite {$tokens}, mailto: and off-site links. MailerLite's native
    Google Analytics toggle is not writable through the connect API (the campaigns
    endpoint silently drops it), so tagging happens at the href level instead.
    """
    import re as _re
    qs = f"utm_source=mailerlite&amp;utm_medium=email&amp;utm_campaign={slug}"

    def _sub(m):
        url = m.group(1)
        if not url.startswith("https://hairsolutions.co"):
            return m.group(0)
        sep = "&amp;" if "?" in url else "?"
        return f'href="{url}{sep}{qs}"'

    return _re.sub(r'href="([^"]*)"', _sub, html)
