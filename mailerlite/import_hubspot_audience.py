#!/usr/bin/env python3
"""Import the HubSpot-exported audience into MailerLite and tag it for segmentation.

Selection is deterministic and capped: all customers first, then prospects by
HubSpot intent tier (newest first within a tier), stopping at BUDGET so the account
keeps a spare-seat buffer under the 2,500 plan cap.

Idempotent: re-running updates the same people (MailerLite upserts on email) and
never exceeds BUDGET. Excludes opt-outs, hard bounces and manual marketing=false.

Requires MAILERLITE_API_TOKEN (set -a && source ~/.env && set +a).
"""
import os, sys, csv, json, re, time, urllib.request, urllib.error

BASE   = "https://connect.mailerlite.com/api"
TOKEN  = os.environ.get("MAILERLITE_API_TOKEN")
CAP    = 2500
BUFFER = 100          # spare seats left for new signups
EXPORT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "exports", "hubspot-2026-08-18", "contacts.csv",
)

NEWS_OFFERS      = "196144424243168637"
SHOPIFY_CUSTOMERS= "196144426449373175"

TIER_ORDER = ["HOT", "WARM", "LUKEWARM", "LIGHT_NURTURE",
              "STALE_HIGH_HISTORICAL_INTENT", "COLD", "LOW_INFORMATION", "DEAD"]
TIER_SLUG  = {"HOT":"hot","WARM":"warm","LUKEWARM":"lukewarm","LIGHT_NURTURE":"light_nurture",
              "STALE_HIGH_HISTORICAL_INTENT":"stale_high","COLD":"cold",
              "LOW_INFORMATION":"low_info","DEAD":"dead"}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$", re.I)


def call(method, path, body=None, tries=6):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE + path, data=data, method=method,
        headers={"Authorization": f"Bearer {TOKEN}",
                 "Content-Type": "application/json", "Accept": "application/json"})
    for _ in range(tries):
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5); continue
            try:
                return e.code, json.loads(e.read() or b"{}")
            except Exception:
                return e.code, {}
    return 429, {}


def num(x, k):
    v = (x.get(k) or "").strip()
    try:
        return float(v)
    except ValueError:
        return None


def value_band(rev):
    if rev is None or rev <= 0: return "none"
    if rev < 1000:  return "low"
    if rev < 4500:  return "mid"
    return "high"


def order_band(deals):
    if deals is None or deals <= 0: return "none"
    if deals == 1:  return "single"
    if deals < 5:   return "repeat"
    return "loyal"


def existing_emails():
    out, cursor = set(), None
    while True:
        s, d = call("GET", "/subscribers?limit=1000" + (f"&cursor={cursor}" if cursor else ""))
        for x in d.get("data", []):
            out.add(x["email"].strip().lower())
        cursor = (d.get("meta") or {}).get("next_cursor")
        if not cursor or not d.get("data"):
            break
    return out


def main():
    if not TOKEN:
        sys.exit("MAILERLITE_API_TOKEN not set")
    ml = existing_emails()
    budget = CAP - BUFFER - len(ml)
    print(f"already in MailerLite: {len(ml)}   free seats (minus {BUFFER} buffer): {budget}")
    if budget <= 0:
        sys.exit("no seats available")

    csv.field_size_limit(10 ** 9)
    rows = list(csv.DictReader(open(EXPORT)))

    def eligible(x):
        e = (x.get("email") or "").strip().lower()
        return bool(EMAIL_RE.match(e)) and e not in ml \
            and (x.get("hs_email_optout") or "").lower() != "true" \
            and not (x.get("hs_email_hard_bounce_reason_enum") or "").strip() \
            and (x.get("comm_marketing_status_manual") or "").lower() != "false"

    pool     = [x for x in rows if eligible(x)]
    customers= [x for x in pool if (x.get("lifecyclestage") or "") == "customer"]
    prospects= [x for x in pool if (x.get("lifecyclestage") or "") != "customer"]

    selected = list(customers)
    for tier in TIER_ORDER:
        if len(selected) >= budget:
            break
        grp = sorted([x for x in prospects if (x.get("intent_tier_static") or "").strip() == tier],
                     key=lambda x: x.get("createdate") or "", reverse=True)
        selected += grp[:budget - len(selected)]
    selected = selected[:budget]
    print(f"eligible {len(pool)} -> selected {len(selected)} "
          f"({len(customers)} customers, {len(selected)-len(customers)} prospects), "
          f"excluded {len(pool)-len(selected)}")

    # warm-up waves: customers first, then by tier order — 4 roughly equal waves
    for i, x in enumerate(selected):
        x["_wave"] = f"wave_{min(4, i * 4 // max(1, len(selected)) + 1)}"

    payloads = []
    for x in selected:
        e   = (x.get("email") or "").strip().lower()
        is_c= (x.get("lifecyclestage") or "") == "customer"
        rev = num(x, "total_revenue")
        dl  = num(x, "num_associated_deals")
        tier= TIER_SLUG.get((x.get("intent_tier_static") or "").strip(), "unknown")
        fields = {
            "name":       (x.get("firstname") or "").strip(),
            "last_name":  (x.get("lastname") or "").strip(),
            "city":       (x.get("city") or "").strip(),
            "country":    (x.get("country") or "").strip(),
            "state":      (x.get("state") or "").strip(),
            "buyer_type": "customer" if is_c else "prospect",
            "intent_tier": tier,
            "order_band":  order_band(dl),
            "value_band":  value_band(rev),
            "warm_up_wave": x["_wave"],
            "migration_cohort": "hubspot-2026-08-18",
        }
        fields = {k: v for k, v in fields.items() if v not in ("", None)}
        groups = [NEWS_OFFERS] + ([SHOPIFY_CUSTOMERS] if is_c else [])
        payloads.append({"method": "POST", "path": "api/subscribers",
                         "body": {"email": e, "fields": fields, "groups": groups,
                                  "status": "active"}})

    ok = err = 0
    errors = []
    for i in range(0, len(payloads), 50):
        chunk = payloads[i:i + 50]
        s, r = call("POST", "/batch", {"requests": chunk})
        if s >= 300:
            err += len(chunk); errors.append((i, s, json.dumps(r)[:200])); continue
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

    print(f"\nimported/updated: {ok}   errors: {err}")
    for e in errors[:10]:
        print("  x", e)


if __name__ == "__main__":
    main()
