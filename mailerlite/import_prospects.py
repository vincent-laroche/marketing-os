#!/usr/bin/env python3
"""Import the approved 1,000-prospect cohort into MailerLite.

Source : ~/02_dev/mkt-resend/data/current/free-prospect-import/import.csv
         (override with PROSPECT_IMPORT_DIR)
         (manifest approvalStatus "applied", csvSha256 verified before every run)
Target : group "News & Offers" — the Subscription Type declared by the W-series masters.

Idempotent: MailerLite's POST /api/subscribers upserts on email, so re-running updates
rather than duplicating. Importing does NOT send anything.

Run:  set -a && source ~/.env && set +a && python3 import_prospects.py [--dry-run]
"""
import csv
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = "https://connect.mailerlite.com/api"
TOKEN = os.environ.get("MAILERLITE_API_TOKEN")
GROUP_NEWS_OFFERS = "196144424243168637"

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get(
    "PROSPECT_IMPORT_DIR",
    os.path.expanduser("~/02_dev/mkt-resend/data/current/free-prospect-import"),
)
CSV_PATH = os.path.join(SRC, "import.csv")
MANIFEST = os.path.join(SRC, "manifest.json")

DRY = "--dry-run" in sys.argv


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

    manifest = json.load(open(MANIFEST))
    digest = hashlib.sha256(open(CSV_PATH, "rb").read()).hexdigest()
    if digest != manifest["csvSha256"]:
        sys.exit(f"ABORT: CSV hash mismatch.\n  expected {manifest['csvSha256']}\n  actual   {digest}")
    print(f"manifest    : {manifest['id']}")
    print(f"approval    : {manifest['approvalStatus']}")
    print(f"csv sha256  : verified")

    rows = list(csv.DictReader(open(CSV_PATH)))
    if len(rows) != manifest["audienceCount"]:
        sys.exit(f"ABORT: row count {len(rows)} != manifest audienceCount {manifest['audienceCount']}")
    print(f"rows        : {len(rows)} (matches manifest)")

    if DRY:
        print("\n--dry-run: nothing sent. Sample payload shape (email redacted):")
        r = rows[0]
        print(json.dumps({"email": "<redacted>",
                          "fields": {"name": r["first_name"], "last_name": r["last_name"],
                                     "customer_status": r["customer_status"],
                                     "migration_cohort": r["migration_cohort"]},
                          "groups": [GROUP_NEWS_OFFERS], "status": "active"}, indent=1))
        return

    ok = failed = 0
    errors = []
    BATCH = 50
    for i in range(0, len(rows), BATCH):
        chunk = rows[i:i + BATCH]
        reqs = [{"method": "POST", "path": "api/subscribers",
                 "body": {"email": r["email"],
                          "fields": {"name": r["first_name"], "last_name": r["last_name"],
                                     "customer_status": r["customer_status"],
                                     "migration_cohort": r["migration_cohort"]},
                          "groups": [GROUP_NEWS_OFFERS],
                          "status": "active"}} for r in chunk]
        code, resp = call("POST", "/batch", {"requests": reqs})
        if code >= 300:
            failed += len(chunk)
            errors.append((i, code, json.dumps(resp)[:200]))
        else:
            for res in resp.get("responses", []):
                if res.get("code", 500) < 300:
                    ok += 1
                else:
                    failed += 1
                    if len(errors) < 10:
                        errors.append((i, res.get("code"), json.dumps(res.get("body"))[:160]))
        print(f"  batch {i//BATCH + 1:2}/{(len(rows)+BATCH-1)//BATCH}  ok={ok} failed={failed}")
        time.sleep(0.6)

    print(f"\nimported ok : {ok}")
    print(f"failed      : {failed}")
    for e in errors[:10]:
        print("   err:", e)


if __name__ == "__main__":
    main()
