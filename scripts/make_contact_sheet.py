#!/usr/bin/env python3
"""Render every MailerLite Code-block fragment in one scrollable page.

MailerLite's drag-and-drop canvas never renders Code blocks (by design), so this is the
fast review loop: iterate here, then paste into MailerLite once the module looks right.
Each fragment is rendered in its own srcdoc iframe so their <style> blocks can't leak
into each other or into this page.
"""
import html as H, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC  = ROOT / "mailerlite-blocks"
OUT  = SRC / "_contact-sheet.html"

PAPER, INK = "#EFE7D2", "#15140F"

frags = sorted(p for p in SRC.glob("*.html") if not p.name.startswith("_"))

cards = []
for p in frags:
    frag = p.read_text(encoding="utf-8").strip()
    name = p.stem
    dark = "_dark" in name or name.endswith("dark")
    bg   = INK if dark else PAPER
    doc  = (f'<!doctype html><meta charset="utf-8">'
            f'<body style="margin:0;background:{bg};">{frag}</body>')
    cards.append(
        f'<figure class="card{" dark" if dark else ""}">'
        f'<figcaption>{H.escape(name)}'
        f'<span class="tag">{"Ink" if dark else "Paper"}</span></figcaption>'
        f'<iframe loading="lazy" srcdoc="{H.escape(doc, quote=True)}"></iframe>'
        f'</figure>'
    )

OUT.write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MailerLite block contact sheet</title>
<style>
 :root{{color-scheme:light dark}}
 body{{margin:0;padding:32px;background:#F4F1EA;color:#15140F;
   font:15px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
 h1{{font-size:22px;margin:0 0 4px}}
 p.sub{{margin:0 0 28px;color:#5A5448}}
 .grid{{display:grid;gap:24px}}
 .card{{margin:0;background:#fff;border:1px solid #DDD2B6;border-radius:12px;overflow:hidden}}
 figcaption{{display:flex;justify-content:space-between;align-items:center;gap:12px;
   padding:10px 14px;font-size:12px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
   background:#EFE7D2;border-bottom:1px solid #DDD2B6}}
 .tag{{font-size:10px;letter-spacing:.06em;text-transform:uppercase;
   padding:2px 8px;border-radius:99px;background:#15140F;color:#F7F1DE}}
 .card.dark .tag{{background:#ED6F5C;color:#15140F}}
 iframe{{display:block;width:100%;height:340px;border:0}}
 @media(min-width:1240px){{.grid{{grid-template-columns:1fr 1fr}}}}
</style></head><body>
<h1>MailerLite block contact sheet</h1>
<p class="sub">{len(frags)} fragments, each rendered at its real width on its brand surface.
Code blocks never render inside MailerLite's editor canvas &mdash; review here instead.</p>
<div class="grid">{''.join(cards)}</div>
</body></html>""", encoding="utf-8")

print(f"{len(frags)} fragments -> {OUT}")
