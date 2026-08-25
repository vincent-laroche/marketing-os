#!/usr/bin/env python3
"""Delete every subscriber MailerLite created from the Shopify integration.

Standing decision (Vincent, 2026-08-19): contacts never come from Shopify. The
audience is built from the HubSpot export instead. The Shopify sync ignored
Shopify's own marketing-consent state and imported 95 non-consenting people
into the marketing group, so its output is not trustworthy as an audience.

Targets `source == "ecommerce"` and nothing else. HubSpot imports
(source="import") and manually added records (source="manual") are never
touched. Idempotent: already-deleted ids 404 and are counted as done.

    python3 mailerlite/purge_shopify_subscribers.py --dry-run
    python3 mailerlite/purge_shopify_subscribers.py

Nothing is sent or scheduled. This only removes subscriber records.
"""
import json, os, sys, time, urllib.error, urllib.parse, urllib.request

BASE = "https://connect.mailerlite.com/api"
TOKEN = os.environ["MAILERLITE_API_TOKEN"]
DRY = "--dry-run" in sys.argv
KEEP_SOURCES = {"import", "manual", "api", "form"}
THROTTLE = 0.55          # MailerLite allows 120 req/min


def call(method, path, **params):
    if params:
        path += ("&" if "?" in path else "?") + urllib.parse.urlencode(params)
    req = urllib.request.Request(BASE + path, method=method,
        headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req) as r:
                body = r.read()
                return r.status, (json.loads(body) if body else None)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2 ** attempt)
                continue
            return e.code, None
    return 429, None


def all_subscribers():
    out, cursor, seen = [], None, set()
    while True:
        kw = {"limit": 500, "cursor": cursor} if cursor else {"limit": 500}
        _, d = call("GET", "/subscribers", **kw)
        rows = [r for r in ((d or {}).get("data") or []) if r["id"] not in seen]
        if not rows:
            return out
        seen.update(r["id"] for r in rows)
        out += rows
        cursor = (d.get("meta") or {}).get("next_cursor")
        if not cursor:
            return out


subs = all_subscribers()
targets = [s for s in subs if s.get("source") == "ecommerce"]
kept = [s for s in subs if s.get("source") in KEEP_SOURCES]
other = [s for s in subs if s.get("source") not in KEEP_SOURCES | {"ecommerce"}]

print(f"account total ....... {len(subs)}")
print(f"delete (ecommerce) .. {len(targets)}")
print(f"keep ................ {len(kept)}  ({', '.join(sorted({s['source'] for s in kept}))})")
if other:
    print(f"unclassified ........ {len(other)} — NOT touched: "
          f"{sorted({str(s.get('source')) for s in other})}")

if DRY:
    print("\n--dry-run: nothing deleted.")
    sys.exit(0)
if not targets:
    print("\nnothing to do.")
    sys.exit(0)

deleted = gone = failed = 0
for i, s in enumerate(targets, 1):
    code, _ = call("DELETE", f"/subscribers/{s['id']}")
    if code in (200, 204):
        deleted += 1
    elif code == 404:
        gone += 1
    else:
        failed += 1
        print(f"  ! {s['id']} -> HTTP {code}")
    if i % 50 == 0 or i == len(targets):
        print(f"  {i}/{len(targets)}  deleted={deleted} already-gone={gone} failed={failed}")
    time.sleep(THROTTLE)

after = all_subscribers()
remaining = [s for s in after if s.get("source") == "ecommerce"]
print(f"\ndeleted={deleted} already-gone={gone} failed={failed}")
print(f"verify: account total {len(after)}, ecommerce-sourced remaining {len(remaining)}")
sys.exit(1 if (failed or remaining) else 0)
