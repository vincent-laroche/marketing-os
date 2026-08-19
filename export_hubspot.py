#!/usr/bin/env python3
"""Full HubSpot export: workflows, contacts, deals, orders (+ line items, companies).

Auth: HUBSPOT_SERVICE_KEY from ~/.env (the OAuth connector token is expired; the
service key is the working one as of 2026-08-18).

Output: exports/hubspot-<date>/  — JSON (full fidelity) + CSV (flat, for eyeballing).
PII-bearing: the exports/ directory is gitignored.

Run: set -a && source ~/.env && set +a && python3 export_hubspot.py
"""
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

TOKEN = os.environ.get("HUBSPOT_SERVICE_KEY")
API = "https://api.hubapi.com"
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "exports", "hubspot-2026-08-18")

OBJECTS = ["contacts", "deals", "orders", "line_items", "companies"]


def req(method, path, body=None, tries=5):
    for attempt in range(tries):
        data = json.dumps(body).encode() if body is not None else None
        r = urllib.request.Request(
            API + path, data=data, method=method,
            headers={"Authorization": f"Bearer {TOKEN}",
                     "Content-Type": "application/json", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(r) as x:
                return json.loads(x.read() or b"{}")
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < tries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            body_txt = e.read().decode("utf8", "replace")[:300]
            raise SystemExit(f"HTTP {e.code} on {path}: {body_txt}")
    raise SystemExit(f"gave up on {path}")


def properties_for(obj):
    d = req("GET", f"/crm/v3/properties/{obj}")
    return [p["name"] for p in d.get("results", [])]


def export_object(obj):
    props = properties_for(obj)
    print(f"  {obj}: {len(props)} properties")
    out, after = [], None
    while True:
        body = {"limit": 100, "properties": props}
        if after:
            body["after"] = after
        d = req("POST", f"/crm/v3/objects/{obj}/search", body)
        out.extend(d.get("results", []))
        after = ((d.get("paging") or {}).get("next") or {}).get("after")
        print(f"    fetched {len(out)}", end="\r")
        if not after:
            break
        time.sleep(0.25)
    print(f"    fetched {len(out)}   ")

    json.dump(out, open(os.path.join(OUTDIR, f"{obj}.json"), "w"), indent=1)
    # flat CSV: only properties that actually carry a value somewhere
    used = sorted({k for r in out for k, v in (r.get("properties") or {}).items() if v})
    with open(os.path.join(OUTDIR, f"{obj}.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id"] + used)
        for r in out:
            p = r.get("properties") or {}
            w.writerow([r.get("id")] + [p.get(k, "") for k in used])
    return len(out), len(used)


def export_workflows():
    v4 = req("GET", "/automation/v4/flows?limit=100")
    flows = v4.get("results", [])
    json.dump(flows, open(os.path.join(OUTDIR, "workflows_v4_flows.json"), "w"), indent=1)

    v3 = req("GET", "/automation/v3/workflows")
    wfs = v3.get("workflows", [])
    json.dump(wfs, open(os.path.join(OUTDIR, "workflows_v3_list.json"), "w"), indent=1)

    # full v3 definitions (the list endpoint omits actions)
    full = []
    for w in wfs:
        try:
            full.append(req("GET", f"/automation/v3/workflows/{w['id']}"))
        except SystemExit as e:
            full.append({"id": w["id"], "name": w.get("name"), "_error": str(e)[:120]})
        time.sleep(0.2)
    json.dump(full, open(os.path.join(OUTDIR, "workflows_v3_full.json"), "w"), indent=1)

    with open(os.path.join(OUTDIR, "workflows_index.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["api", "id", "name", "enabled", "type"])
        for x in flows:
            w.writerow(["v4", x.get("id"), x.get("name"), x.get("isEnabled"), x.get("type")])
        for x in wfs:
            w.writerow(["v3", x.get("id"), x.get("name"), x.get("enabled"), x.get("type")])
    return len(flows), len(wfs), len(full)


def main():
    if not TOKEN:
        sys.exit("HUBSPOT_SERVICE_KEY not set")
    os.makedirs(OUTDIR, exist_ok=True)
    print(f"output: {OUTDIR}\n")

    print("== workflows ==")
    a, b, c = export_workflows()
    print(f"  v4 flows: {a} | v3 workflows: {b} | v3 full definitions: {c}\n")

    print("== crm objects ==")
    summary = {}
    for obj in OBJECTS:
        n, cols = export_object(obj)
        summary[obj] = {"records": n, "populated_properties": cols}

    json.dump(summary, open(os.path.join(OUTDIR, "_summary.json"), "w"), indent=1)
    print("\n== summary ==")
    for k, v in summary.items():
        print(f"  {k:12} {v['records']:>6} records  {v['populated_properties']:>4} populated props")


if __name__ == "__main__":
    main()
