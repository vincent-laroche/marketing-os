"""Render the 20 journey emails from the LIVE module HTML + the Notion copy.

Each email is a stack of real modules on a Paper body, exactly as it will render in
HubSpot. Field values not supplied by emails.py fall back to the module's own
fields.json default — the same resolution HubSpot performs.
"""
import json, os, re, sys
from render_proof import render
from emails import EMAILS

LIVE = "final-verify"
BODY_BG = "#EFE7D2"          # the email body background — Paper, per the brand spec


def defaults(folder):
    ctx = {}
    for f in json.load(open(f"{LIVE}/{folder}.module/fields.json")):
        fid, t, d = f["id"], f.get("type"), f.get("default")
        if t == "url" and isinstance(d, dict):
            ctx[fid] = {"href": d.get("href", "#")}
        elif t == "image" and isinstance(d, dict):
            ctx[fid] = dict(d)
        else:
            ctx[fid] = d
    return ctx


# The preference-centre footer's opt-down ask is optional: only WB-4 has real copy
# for it. Everywhere else it must render as a pure compliance footer, so blank the
# ask rather than inheriting the module's demo defaults.
OPT_DOWN_ASK = ("eyebrow", "heading", "body_text", "button_label")


def block_html(folder, surface, values):
    html = open(f"{LIVE}/{folder}.module/module.html").read()
    ctx = defaults(folder)
    if folder == "preference_opt_down":
        for k in OPT_DOWN_ASK:
            ctx[k] = ""
    ctx.update(values)
    offered = [c[0] for c in
               json.load(open(f"{LIVE}/{folder}.module/fields.json"))[0]["choices"]]
    if surface not in offered:
        raise SystemExit(f"{folder} does not offer surface '{surface}' (has {offered})")
    return render(html, surface, ctx)


def email_html(e):
    parts = []
    for folder, surface, values in e["blocks"]:
        parts.append(f"<tr><td style='padding:0 0 12px;'>{block_html(folder, surface, values)}</td></tr>")
    return ("<table role='presentation' width='100%' cellpadding='0' cellspacing='0' border='0' "
            f"style='width:100%;background:{BODY_BG};'><tr><td align='center' style='padding:28px 12px;'>"
            "<table role='presentation' width='600' cellpadding='0' cellspacing='0' border='0' "
            "style='width:600px;max-width:100%;'>" + "".join(parts) + "</table></td></tr></table>")


CSS = """<style>
 body{margin:0;background:#DDD2B6;font-family:-apple-system,Segoe UI,Arial,sans-serif}
 .wrap{max-width:1360px;margin:0 auto;padding:32px 16px 80px}
 h1{font-size:26px;margin:0 0 4px;color:#15140F;letter-spacing:-.4px}
 .lede{color:#5A5448;font-size:14px;margin:0 0 28px;line-height:1.6;max-width:820px}
 .row{display:flex;flex-wrap:wrap;gap:26px}
 .card{background:#EFE7D2;border-radius:14px;overflow:hidden;width:640px;max-width:100%}
 .hd{padding:16px 20px;border-bottom:1px solid #DDD2B6}
 .code{font-family:'Courier New',monospace;font-size:11px;letter-spacing:1.6px;
   text-transform:uppercase;color:#ED6F5C;margin:0 0 6px;font-weight:700}
 .subj{font-size:17px;font-weight:700;color:#15140F;margin:0 0 4px;line-height:1.3}
 .prev{font-size:13px;color:#5A5448;margin:0}
 .surf{font-family:'Courier New',monospace;font-size:10px;color:#5A5448;margin:8px 0 0;
   letter-spacing:.6px}
 .jrn{font-family:'Courier New',monospace;font-size:12px;letter-spacing:2px;text-transform:uppercase;
   color:#15140F;margin:44px 0 12px;border-top:1px solid #C9BC9C;padding-top:16px;font-weight:700}
</style>"""

if __name__ == "__main__":
    only = sys.argv[1:] or None
    out = [f"<meta charset='utf-8'><title>Journey emails — second pass</title>{CSS}<div class='wrap'>",
           "<h1>Journey emails — second pass</h1>",
           "<p class='lede'>Twenty emails composed from the Notion <code>emails_master</code> blueprint: "
           "header, plain-text founder letter, the commerce/promo block each one calls for, and a footer. "
           "Copy is verbatim from Notion. Surfaces follow the per-journey tonal plan — Post-Purchase warm, "
           "Cart Recovery escalating light&rarr;dark, Win-Back all ink, Reorder mid-tone paper — with Coral "
           "used exactly four times across the twenty.</p>"]
    seen = None
    os.makedirs("emails_out", exist_ok=True)
    for e in EMAILS:
        if only and e["code"] not in only:
            continue
        if e["journey"] != seen:
            seen = e["journey"]
            out.append(f"<p class='jrn'>{seen}</p><div class='row'>" if seen else "")
        surfaces = " → ".join(f"{b[0].replace('_',' ')}:{b[1]}" for b in e["blocks"])
        body = email_html(e)
        open(f"emails_out/{e['code']}.html", "w").write(
            f"<meta charset='utf-8'><title>{e['code']} — {e['subject']}</title>{body}")
        out.append(
            f"<div class='card'><div class='hd'><p class='code'>{e['code']} · {e['pos']}</p>"
            f"<p class='subj'>{e['subject']}</p><p class='prev'>{e['preview']}</p>"
            f"<p class='surf'>{surfaces}</p></div>{body}</div>")
    out.append("</div></div>")
    open("journey_emails.html", "w").write("\n".join(out))

    txt = open("journey_emails.html").read()
    left = sorted(set(re.findall(r"\{%[^%]*%\}", txt)))
    print(f"rendered {len([e for e in EMAILS if not only or e['code'] in only])} emails")
    print("unresolved HubL blocks:", left or "none")
    coral = sum(1 for e in EMAILS for b in e["blocks"] if b[1] == "coral")
    print(f"coral panels across the set: {coral}")
