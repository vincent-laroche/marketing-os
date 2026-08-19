#!/usr/bin/env python3
"""Push the 22 built journey emails into MailerLite as draft campaigns.

Idempotent: a campaign whose name already matches a slug is skipped, never duplicated.
Creates drafts only — no recipients, no schedule, nothing sends.

Requires MAILERLITE_API_TOKEN in the environment (set -a && source ~/.env && set +a).
"""
import os, sys, json, urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ml_components import shell, add_utm
from ml_content_pp import PP_EMAILS
from ml_content_cr import CR_EMAILS
from ml_content_wb import WB_EMAILS
from ml_content_ro import RO_EMAILS
from ml_content_w import W_EMAILS

BASE = "https://connect.mailerlite.com/api"
SENDER = "vincent@hairsolutions.co"   # verified sender; campaigns need only verification
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

    pushed, failed = [], []
    for fn in PP_EMAILS + CR_EMAILS + WB_EMAILS + RO_EMAILS + W_EMAILS:
        slug, title, subject, preview, body = fn()
        if slug in existing:
            print(f"  = skip {slug}")
            pushed.append({"slug": slug, "campaign_id": existing[slug]})
            continue
        code, resp = call("POST", "/campaigns", {
            "name": slug, "language_id": 4, "type": "regular",
            "emails": [{"subject": subject, "from_name": "Hair Solutions Co",
                        "from": SENDER, "content": add_utm(shell(title, preview, body), slug)}]})
        if code >= 300:
            failed.append((slug, code, resp))
            print(f"  x {code} {slug}: {json.dumps(resp)[:120]}")
        else:
            d = resp["data"]
            pushed.append({"slug": slug, "campaign_id": d["id"],
                           "email_id": (d.get("emails") or [{}])[0].get("id")})
            print(f"  + {slug:38} {d['id']}")

    json.dump(pushed, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "pushed-campaigns.json"), "w"), indent=1)
    print(f"\npushed/ok: {len(pushed)}  failed: {len(failed)}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
