#!/usr/bin/env python3
"""Re-push content into EXISTING MailerLite draft campaigns.

Why this exists: `push_campaigns.py` is create-only — it skips any campaign whose name already
matches, so a fix made in the repo never reaches a draft that was pushed before the fix. On
2026-08-19 an API sweep found all 24 drafts still carrying `Forest Hills, New York 11209`, the
retracted postal address, while every repo source had long since been corrected to Tallinn.

Drafts only. Never sets recipients, never schedules, never sends.

API constraints (empirical, see API-SURFACE.md):
  * `PUT /campaigns/{id}` wants `emails` as an INDEX-KEYED OBJECT — {"emails": {"0": {...}}}.
    An array returns 422 "The emails.0 field must be an array." The POST path differs. Do not
    "fix" this to match POST.
  * Only subject / from_name / from / reply_to / content are accepted inside emails.0.

Usage:
  python3 repair_draft_content.py --dry-run
  python3 repair_draft_content.py
  python3 repair_draft_content.py --only WB-1-checking-in
"""
import os, sys, json, argparse, urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ml_components import shell, add_utm
from ml_content_pp import PP_EMAILS
from ml_content_cr import CR_EMAILS
from ml_content_wb import WB_EMAILS
from ml_content_ro import RO_EMAILS
from ml_content_w import W_EMAILS

BASE = "https://connect.mailerlite.com/api"
SENDER = "vincent@hairsolutions.co"
TOKEN = os.environ.get("MAILERLITE_API_TOKEN")

BAD = ("Forest Hills", "Honey Creek", "New York 11209")
GOOD = "Ehitajate tee 110"


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE + path, data=data, method=method,
        headers={"Authorization": f"Bearer {TOKEN}",
                 "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except Exception:
            return e.code, {}


def wb1_modular_html():
    """WB-1 ships as the six-card modular build, not the ml_content_wb single-column render.

    Copy is verbatim to emails_master (gate 1 verified); surfaces alternate Paper/Ink; radius is
    role-based. Built by scripts/build_wb1.py in the browser-tools worktree.
    """
    p = ("/Users/vMac/04_marketing/email_marketing/.claude/worktrees/"
         "browser-tools-fast-dev-f3b771/mailerlite-blocks/_wb1_payload.json")
    if not os.path.exists(p):
        return None
    blocks = json.load(open(p))
    order = ["header_slim_light", "wb1_hero", "wb1_question_list",
             "wb1_close_cta", "wb1_signoff", "footer_preference_centre_dark"]
    if not all(k in blocks for k in order):
        return None
    inner = "".join(blocks[k] for k in order)
    pre = "No offer attached. Just wondering how you got on."
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="x-apple-disable-message-reformatting">'
        '<meta name="color-scheme" content="light dark">'
        '<title>Checking in &mdash; Vincent here</title></head>'
        '<body style="margin:0;padding:0;background-color:#F7F1DE;">'
        f'<div style="display:none;max-height:0;overflow:hidden;opacity:0;">{pre}'
        '&#8204;&nbsp;&#8204;&nbsp;&#8204;&nbsp;&#8204;&nbsp;&#8204;</div>'
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"'
        ' style="background-color:#F7F1DE;"><tr><td align="center" style="padding:24px 0;">'
        '<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0"'
        ' style="width:600px;max-width:100%;"><tr><td>'
        f'{inner}'
        '</td></tr></table></td></tr></table></body></html>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only")
    a = ap.parse_args()
    if not TOKEN:
        sys.exit("MAILERLITE_API_TOKEN not set")

    _, r = call("GET", "/campaigns?limit=100")
    live = {x["name"]: x for x in r.get("data", [])}
    print(f"live campaigns: {len(live)}")

    fixed, skipped, failed, clean = [], [], [], []
    for fn in PP_EMAILS + CR_EMAILS + WB_EMAILS + RO_EMAILS + W_EMAILS:
        slug, title, subject, preview, body = fn()
        if a.only and a.only != slug:
            continue
        if slug not in live:
            skipped.append(slug)
            continue
        cid = live[slug]["id"]

        html = wb1_modular_html() if slug == "WB-1-checking-in" else None
        if html is None:
            html = add_utm(shell(title, preview, body), slug)

        # never ship a regenerated body that still carries the retracted address
        hit = [b for b in BAD if b in html]
        if hit:
            failed.append((slug, "SOURCE STILL BAD", hit))
            print(f"  x {slug}: regenerated HTML still contains {hit}")
            continue
        if GOOD not in html:
            failed.append((slug, "NO TALLINN ADDRESS", []))
            print(f"  x {slug}: regenerated HTML has no Tallinn address")
            continue

        _, cur = call("GET", f"/campaigns/{cid}")
        curbody = ((cur.get("data") or {}).get("emails") or [{}])[0].get("content") or ""
        was_bad = any(b in curbody for b in BAD)
        if not was_bad and curbody == html:
            clean.append(slug)
            print(f"  = {slug}: already correct")
            continue

        if a.dry_run:
            print(f"  ~ would update {slug} ({cid}) bad_address={was_bad} "
                  f"{len(curbody)} -> {len(html)} bytes")
            fixed.append(slug)
            continue

        code, resp = call("PUT", f"/campaigns/{cid}", {
            "name": slug,
            "emails": {"0": {"subject": subject, "from_name": "Hair Solutions Co",
                             "from": SENDER, "reply_to": SENDER, "content": html}}})
        if code >= 300:
            failed.append((slug, code, json.dumps(resp)[:160]))
            print(f"  x {code} {slug}: {json.dumps(resp)[:160]}")
            continue

        _, ver = call("GET", f"/campaigns/{cid}")
        vd = (ver.get("data") or {})
        vb = (vd.get("emails") or [{}])[0].get("content") or ""
        ok = (not any(b in vb for b in BAD)) and GOOD in vb
        status_ok = vd.get("status") == "draft" and not vd.get("scheduled_for")
        print(f"  {'v' if ok and status_ok else 'x'} {slug}: address_ok={ok} "
              f"draft={status_ok} bytes={len(vb)}")
        (fixed if ok and status_ok else failed).append(slug)

    print(f"\nupdated {len(fixed)} · already-clean {len(clean)} · "
          f"not-in-account {len(skipped)} · failed {len(failed)}")
    if skipped:
        print("  not in account:", skipped)
    if failed:
        print("  FAILED:", failed)
        sys.exit(1)


if __name__ == "__main__":
    main()
