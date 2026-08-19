#!/usr/bin/env python3
"""Assign every draft campaign to the DO NOT SEND safeguard group.

Two API quirks, both discovered the hard way:
  * PUT /campaigns/{id} requires `name` in the body even when only changing
    groups — omitting it returns 422 "The name field is required."
  * The assignment does NOT read back on `groups` (that stays null). It lands
    on `filter` as an in_any/groups rule. Verify via `filter` + the
    recipients_count dropping to 0, never via `groups`.

MailerLite treats a campaign with no group as "all active subscribers", not
"no recipients" (see AGENTS.md #2). Any unparked draft therefore reads as
1,000 recipients and one mis-click in the UI would send it for real.

Idempotent: campaigns already parked are skipped. Nothing is sent or scheduled.

    python3 mailerlite/park_drafts.py --dry-run
    python3 mailerlite/park_drafts.py
"""
import json, os, sys, urllib.request, urllib.error

PARKED = "196158361233786451"   # ⛔ DO NOT SEND — Lifecycle Drafts (parked)
BASE = "https://connect.mailerlite.com/api"
TOKEN = os.environ["MAILERLITE_API_TOKEN"]
DRY = "--dry-run" in sys.argv


def call(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or "{}")


def parked_group_ids(c):
    """Group ids a campaign targets. Lives in `filter`, not `groups`."""
    out = []
    for grp in (c.get("filter") or []):
        for rule in grp:
            args = rule.get("args") or []
            if len(args) == 2 and args[0] == "groups":
                out += list(args[1])
    return out


def main():
    status, body = call("GET", "/campaigns?filter[status]=draft&limit=100")
    if status != 200:
        sys.exit(f"list failed {status}: {body}")
    drafts = body.get("data", [])
    print(f"{len(drafts)} draft campaigns\n")

    parked = skipped = failed = 0
    for c in drafts:
        cid, name = c["id"], c["name"]
        current = parked_group_ids(c)
        if current == [PARKED]:
            print(f"  ok      {name} (already parked)")
            skipped += 1
            continue
        if DRY:
            print(f"  WOULD   {name}  {current or '[all subscribers]'} -> parked")
            parked += 1
            continue
        st, resp = call("PUT", f"/campaigns/{cid}", {"name": name, "groups": [PARKED]})
        if st == 200:
            d = resp.get("data", {})
            got = parked_group_ids(d)
            if got == [PARKED] and d.get("recipients_count") == 0:
                print(f"  PARKED  {name}")
                parked += 1
            else:
                print(f"  NO-OP   {name} -> accepted but filter={got}")
                failed += 1
        else:
            print(f"  FAIL    {name} [{st}] {str(resp)[:120]}")
            failed += 1

    print(f"\nparked={parked} already={skipped} failed={failed}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
