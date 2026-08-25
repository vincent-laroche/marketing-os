#!/usr/bin/env python3
"""Configure the 27 draft MailerLite campaigns: sender, subject, preheader, UTM, recipients.

Idempotent and safe to re-run. Matches campaigns by exact name (slug) — never creates,
duplicates, deletes, schedules or sends. Content is re-pushed from the builder so the
UTM-tagged hrefs land; copy still comes only from ml_content_*.py.

Requires MAILERLITE_API_TOKEN (set -a && source ~/.env && set +a).
"""
import os, sys, json, urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ml_components import shell, add_utm
from ml_content_pp import PP_EMAILS
from ml_content_cr import CR_EMAILS
from ml_content_wb import WB_EMAILS
from ml_content_ro import RO_EMAILS
from ml_content_w import W_EMAILS

BASE      = "https://connect.mailerlite.com/api"
SENDER    = "vincent@hairsolutions.co"       # only fully-verified from-address
FROM_NAME = "Hair Solutions Co"
NEWS_OFFERS = "196144424243168637"           # "News & Offers" — 999 prospects

# Broadcast audience. W-1..W-3 and W-5 are prospect nurture and get the group.
# W-4 is a known content shell (empty Proof Bank) -> deliberately NOT made send-ready.
# Every PP/CR/WB/RO email is per-subscriber lifecycle, fired by automations -> no group.
BROADCAST = {
    "W-1-welcome-expectations": NEWS_OFFERS,
    "W-2-how-systems-work":     NEWS_OFFERS,
    "W-3-style-inspiration":    NEWS_OFFERS,
    "W-5-soft-consult-invite":  NEWS_OFFERS,
}
TOKEN = os.environ.get("MAILERLITE_API_TOKEN")


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE + path, data=data, method=method,
        headers={"Authorization": f"Bearer {TOKEN}",
                 "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except Exception:
            return e.code, {}


def main():
    if not TOKEN:
        sys.exit("MAILERLITE_API_TOKEN not set")
    _, r = call("GET", "/campaigns?limit=100")
    existing = {x["name"]: x["id"] for x in r.get("data", [])}

    rows, failed = [], []
    for fn in PP_EMAILS + CR_EMAILS + WB_EMAILS + RO_EMAILS + W_EMAILS:
        slug, title, subject, preview, body = fn()
        cid = existing.get(slug)
        if not cid:
            failed.append((slug, "no such campaign", {}))
            print(f"  x {slug}: not found in account")
            continue

        # NOTE: MailerLite's PUT wants `emails` as an index-keyed object, and only
        # accepts subject / from_name / from / reply_to / content inside it.
        payload = {
            "name": slug,
            "language_id": 4,
            "emails": {"0": {
                "subject":   subject,
                "from_name": FROM_NAME,
                "from":      SENDER,
                "reply_to":  SENDER,
                "content":   add_utm(shell(title, preview, body), slug),
            }},
            "settings": {"track_opens": True, "ecommerce_tracking": False},
        }
        if slug in BROADCAST:
            payload["groups"] = [BROADCAST[slug]]

        code, resp = call("PUT", f"/campaigns/{cid}", payload)
        if code >= 300:
            failed.append((slug, code, resp))
            print(f"  x {code} {slug}: {json.dumps(resp)[:160]}")
            continue

        d = resp["data"]
        e = (d.get("emails") or [{}])[0]
        rows.append({
            "slug": slug, "campaign_id": cid, "status": d.get("status"),
            "subject": e.get("subject"), "from": e.get("from"),
            "from_name": e.get("from_name"), "reply_to": e.get("reply_to"),
            "preheader_field": e.get("preheader"),
            "preheader_in_html": preview in (e.get("content") or ""),
            "utm_in_html": f"utm_campaign={slug}" in (e.get("content") or ""),
            "track_opens": d.get("settings", {}).get("track_opens"),
            "groups": d.get("basic_filter_for_humans", {}).get("included_groups"),
            "all_active": d.get("basic_filter_for_humans", {}).get("all_active_subscribers"),
            "recipients_count": d.get("recipients_count"),
            "missing_data": d.get("missing_data"),
        })
        print(f"  + {slug:34} utm={rows[-1]['utm_in_html']} "
              f"pre={rows[-1]['preheader_in_html']} missing={d.get('missing_data')}")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "configured-campaigns.json")
    json.dump(rows, open(out, "w"), indent=1)
    print(f"\nconfigured: {len(rows)}  failed: {len(failed)}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
