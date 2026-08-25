#!/usr/bin/env python3
"""Delete MailerLite campaigns. Dry-run by default; pass --yes to actually delete.

    python3 delete_campaigns.py                  # list what would go (no changes)
    python3 delete_campaigns.py --yes            # delete them, permanently
    python3 delete_campaigns.py --status all     # draft + ready + sent
    python3 delete_campaigns.py --status all --yes

Auth: reads MAILERLITE_API_TOKEN from the environment. Load your env first:

    set -a && source ~/.env && set +a

Deletion is permanent — MailerLite has no trash for campaigns.
"""
import os
import sys
import json
import time
import urllib.request
import urllib.error

API = "https://connect.mailerlite.com/api/campaigns"


def get_token():
    tok = os.environ.get("MAILERLITE_API_TOKEN")
    if not tok:
        sys.exit(
            "MAILERLITE_API_TOKEN is not set.\n"
            "Run:  set -a && source ~/.env && set +a"
        )
    return tok


def call(method, url, tok):
    req = urllib.request.Request(
        url,
        method=method,
        headers={"Authorization": "Bearer " + tok, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            body = r.read().decode(errors="ignore")
            return r.status, (json.loads(body) if body.strip() else {})
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:300].decode(errors="ignore")


def main():
    args = sys.argv[1:]
    go = "--yes" in args
    status = "draft"
    if "--status" in args:
        status = args[args.index("--status") + 1]

    tok = get_token()
    statuses = ["draft", "ready", "sent"] if status == "all" else [status]

    targets = []
    for st in statuses:
        code, d = call("GET", "%s?filter[status]=%s&limit=100" % (API, st), tok)
        if code != 200 or not isinstance(d, dict):
            print("  list %s: HTTP %s %s" % (st, code, d))
            continue
        for c in d.get("data", []):
            targets.append((c["id"], c.get("name", ""), st))

    if not targets:
        print("Nothing matches status=%s." % status)
        return

    print("%d campaign(s) matching status=%s:" % (len(targets), status))
    for cid, name, st in targets:
        print("  %s  [%s]  %s" % (cid, st, name))

    if not go:
        print("\nDRY RUN — nothing deleted. Re-run with --yes to delete permanently.")
        return

    print("\nDeleting...")
    ok = fail = 0
    for cid, name, _ in targets:
        code, resp = call("DELETE", "%s/%s" % (API, cid), tok)
        if code in (200, 201, 204):
            ok += 1
            print("  deleted %s  %s" % (cid, name))
        else:
            fail += 1
            print("  FAILED  %s  %s  -> HTTP %s %s" % (cid, name, code, resp))
        time.sleep(0.25)
    print("\nDone. deleted=%d failed=%d" % (ok, fail))


if __name__ == "__main__":
    main()
