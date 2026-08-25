#!/usr/bin/env python3
"""Upload the tiered HubSpot audience produced by select_audience.py.

Standing decisions (Vincent, 2026-08-19):
  * Contacts come from the HubSpot export only — never from Shopify.
  * Suppression is absolute: X0 contacts are never uploaded, AND any that are
    already in the account get deleted.
  * Hairdressers / hair professionals go to their own group; they get
    different content.

Each tier lands in its own group so sends can be staged and the domain warmed
gradually. Idempotent: MailerLite upserts on email, so re-running updates
rather than duplicates.

    python3 mailerlite/upload_audience.py --dry-run
    python3 mailerlite/upload_audience.py

Nothing is sent or scheduled. Groups are created empty and campaigns are
untouched.
"""
import csv, json, os, sys, time, urllib.error, urllib.request
from pathlib import Path

csv.field_size_limit(10 ** 7)
BASE = "https://connect.mailerlite.com/api"
TOKEN = os.environ["MAILERLITE_API_TOKEN"]
DRY = "--dry-run" in sys.argv
HERE = Path(__file__).resolve().parent.parent
SRC = HERE / "exports" / "mailerlite-audience"
COHORT = "hubspot-2026-08-19"

GROUPS = {
    "A": "HS · A · Promote now",
    "B": "HS · B · Promote next cycle",
    "C": "HS · C · Customers",
    "D": "HS · D · Warm intent",
    "E": "HS · E · Cold intent",
}
PRO_GROUP = "HS · Hair professionals"


def call(method, path, body=None, tries=6):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
        headers={"Authorization": f"Bearer {TOKEN}",
                 "Content-Type": "application/json", "Accept": "application/json"})
    for _ in range(tries):
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5)
                continue
            try:
                return e.code, json.loads(e.read() or b"{}")
            except Exception:
                return e.code, {}
    return 429, {}


def band(v, edges, labels):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return ""
    for edge, lab in zip(edges, labels):
        if x <= edge:
            return lab
    return labels[-1]


def ensure_group(name):
    _, d = call("GET", "/groups?limit=100")
    for g in d.get("data", []):
        if g["name"] == name:
            return g["id"], False
    if DRY:
        return None, True
    s, d = call("POST", "/groups", {"name": name})
    if s >= 300:
        sys.exit(f"could not create group {name!r}: {s} {json.dumps(d)[:200]}")
    return d["data"]["id"], True


def all_subscribers():
    out, cursor = [], None
    while True:
        s, d = call("GET", "/subscribers?limit=500" + (f"&cursor={cursor}" if cursor else ""))
        rows = d.get("data") or []
        if not rows:
            return out
        out += rows
        cursor = (d.get("meta") or {}).get("next_cursor")
        if not cursor:
            return out


# ---- 1. purge any suppressed contact already present ----------------------
supp = {r["email"].strip().lower()
        for r in csv.DictReader(open(SRC / "suppression-list.csv", newline="", encoding="utf-8"))}
present = all_subscribers()
by_email = {s["email"].strip().lower(): s for s in present}
to_remove = [by_email[e] for e in supp & set(by_email)]
print(f"account: {len(present)} subscribers")
print(f"suppressed AND already present: {len(to_remove)}")
if to_remove and not DRY:
    for s in to_remove:
        code, _ = call("DELETE", f"/subscribers/{s['id']}")
        print(f"   deleted {s['email'][:2]}***  HTTP {code}")
        time.sleep(0.4)

# ---- 2. ensure groups ------------------------------------------------------
gid = {}
for t, name in GROUPS.items():
    gid[t], made = ensure_group(name)
    print(f"group {name!r}: {'created' if made else 'exists'} {gid[t] or ''}")
pro_gid, made = ensure_group(PRO_GROUP)
print(f"group {PRO_GROUP!r}: {'created' if made else 'exists'} {pro_gid or ''}")

pros = {r["email"].strip().lower()
        for r in csv.DictReader(open(SRC / "segment-hair-professionals.csv", newline="", encoding="utf-8"))}
print(f"hair professionals: {len(pros)}")

# ---- 3. upsert each tier ---------------------------------------------------
payloads = []
for t, name in GROUPS.items():
    f = SRC / f"tier-{t}-{ {'A':'promote_now','B':'promote_next_cycle','C':'customer','D':'warm-intent','E':'cold-intent'}[t] }.csv"
    for r in csv.DictReader(open(f, newline="", encoding="utf-8")):
        e = r["email"].strip().lower()
        if e in supp:
            continue
        groups = [g for g in (gid[t], pro_gid if e in pros else None) if g]
        fields = {
            "name": r.get("name", ""),
            "last_name": r.get("last_name", ""),
            "buyer_type": "hair_professional" if e in pros else "consumer",
            "intent_tier": (r.get("intent_tier") or "").lower(),
            "customer_status": r.get("customer_status", ""),
            "migration_cohort": COHORT,
            "value_band": band(r.get("value_band"), [0, 500, 2000], ["none", "low", "mid", "high"]),
        }
        fields = {k: v for k, v in fields.items() if v not in ("", None)}
        payloads.append({"method": "POST", "path": "api/subscribers",
                         "body": {"email": e, "fields": fields,
                                  "groups": groups, "status": "active"}})

print(f"\nto upsert: {len(payloads)}")
if DRY:
    print("--dry-run: nothing written.")
    print("sample:", json.dumps(payloads[0], indent=1)[:400])
    sys.exit(0)

ok = err = 0
errors = []
for i in range(0, len(payloads), 50):
    chunk = payloads[i:i + 50]
    s, r = call("POST", "/batch", {"requests": chunk})
    if s >= 300:
        err += len(chunk)
        errors.append((i, s, json.dumps(r)[:200]))
        continue
    for j, resp in enumerate(r.get("responses", [])):
        if resp.get("code", 500) < 300:
            ok += 1
        else:
            err += 1
            if len(errors) < 10:
                errors.append((chunk[j]["body"]["email"], resp.get("code"),
                               json.dumps(resp.get("body"))[:160]))
    print(f"  batch {i//50+1:>3}/{(len(payloads)+49)//50}  ok={ok} err={err}", flush=True)
    time.sleep(0.6)

print(f"\nupserted: {ok}   errors: {err}")
for e in errors[:10]:
    print("  x", e)
after = all_subscribers()
print(f"account now: {len(after)} subscribers (cap 2500)")
