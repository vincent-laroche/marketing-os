#!/usr/bin/env python3
"""Tag Shopify customers with consent/engagement state, sourced from the mkt-resend
owner-attested-consent cohort (not from the raw, unattested HubSpot export).

Why this source, not the raw HubSpot export: CAMPAIGN-PLAN.md's "186 engaged, 3
documented consent" figure came from exports/hubspot-2026-08-18/contacts.csv, which
has no consent provenance for 99.9% of contacts. ~/02_dev/mkt-resend/data/current/
free-prospect-ranking/selected.json is a different, better-documented artifact: 1,000
contacts with a real owner attestation (Vincent Laroche, 2026-07-17T05:41:03Z, "all
current active HubSpot contacts in this scope have consciously opted into receiving
Hair Solutions Co. marketing emails") plus per-contact engagement (opens/clicks/
pageviews/sessions). This cohort was already approved and imported into MailerLite
(see mailerlite/import_prospects.py) — using it here for Shopify tagging is reusing
an existing decision, not making a new one.

Tags applied (additive only, via tagsAdd — never overwrites existing tags):
  hs-consented-2026   -> every matched contact (owner-attested consent basis)
  hs-engaged-core     -> matched contacts with engagement.opened > 0 or .clicked > 0

Matching: by email, case-insensitive, against every Shopify customer (paginated).
Idempotent: tagsAdd on an already-present tag is a no-op.

Run:  set -a && source ~/.env && set +a && python3 build_engagement_tags.py [--dry-run]
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

STORE = "one-head-hair.myshopify.com"
API_VERSION = "2026-01"
TOKEN = os.environ.get("SHOPIFY_APP_ADMIN_TOKEN")
GRAPHQL_URL = f"https://{STORE}/admin/api/{API_VERSION}/graphql.json"

COHORT_PATH = os.path.expanduser(
    "~/02_dev/mkt-resend/data/current/free-prospect-ranking/selected.json"
)

DRY = "--dry-run" in sys.argv


def gql(query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        GRAPHQL_URL, data=body, method="POST",
        headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"HTTP {e.code}: {e.read().decode()[:500]}")


def fetch_all_customers():
    """email(lowercased) -> {id, tags}"""
    out = {}
    cursor = None
    query = """
    query($cursor: String) {
      customers(first: 250, after: $cursor) {
        edges { cursor node { id email tags } }
        pageInfo { hasNextPage }
      }
    }"""
    while True:
        r = gql(query, {"cursor": cursor})
        edges = r["data"]["customers"]["edges"]
        for e in edges:
            node = e["node"]
            if node["email"]:
                out[node["email"].strip().lower()] = {"id": node["id"], "tags": node["tags"]}
        if not r["data"]["customers"]["pageInfo"]["hasNextPage"] or not edges:
            break
        cursor = edges[-1]["cursor"]
    return out


def main():
    if not TOKEN:
        sys.exit("SHOPIFY_APP_ADMIN_TOKEN not set")

    cohort = json.load(open(COHORT_PATH))
    print(f"cohort loaded: {len(cohort)} contacts from {COHORT_PATH}")

    print("fetching all Shopify customers (paginated)...")
    customers = fetch_all_customers()
    print(f"shopify customers fetched: {len(customers)}")

    matched = []
    for c in cohort:
        email = (c.get("email") or "").strip().lower()
        if not email or email not in customers:
            continue
        eng = c.get("engagement") or {}
        engaged = bool(eng.get("opened") or eng.get("clicked"))
        tags_to_add = ["hs-consented-2026"] + (["hs-engaged-core"] if engaged else [])
        matched.append({
            "email": email,
            "id": customers[email]["id"],
            "existing_tags": customers[email]["tags"],
            "tags_to_add": tags_to_add,
        })

    engaged_count = sum(1 for m in matched if "hs-engaged-core" in m["tags_to_add"])
    print(f"matched to Shopify customers: {len(matched)} of {len(cohort)}")
    print(f"  of which engaged (opens/clicks > 0): {engaged_count}")
    print(f"unmatched (in cohort, no Shopify customer record): {len(cohort) - len(matched)}")

    if DRY:
        print("\n--dry-run: no tags written. Sample of first 5 matches:")
        for m in matched[:5]:
            print(f"  {m['email']}: +{m['tags_to_add']} (existing: {m['existing_tags']})")
        return

    mutation = """
    mutation($id: ID!, $tags: [String!]!) {
      tagsAdd(id: $id, tags: $tags) { node { id } userErrors { message } }
    }"""
    ok, failed = 0, 0
    for m in matched:
        r = gql(mutation, {"id": m["id"], "tags": m["tags_to_add"]})
        errs = r.get("data", {}).get("tagsAdd", {}).get("userErrors", [])
        if errs or "errors" in r:
            failed += 1
            print(f"  FAILED {m['email']}: {errs or r.get('errors')}")
        else:
            ok += 1

    print(f"\ntagged: {ok} ok, {failed} failed, {len(matched)} total")


if __name__ == "__main__":
    main()
