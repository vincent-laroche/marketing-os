#!/usr/bin/env python3
"""Extract published Judge.me reviews from Shopify product metafields into a proof bank.

Read-only. These are reviews already published on the storefront, so publication
consent is inherent; names appear exactly as Judge.me displays them publicly.
Usage:  set -a && source ~/.env && set +a && python3 extract_proof_bank.py
"""
import json, os, re, csv, sys, urllib.request, html

SHOP = "one-head-hair.myshopify.com"
TOKEN = os.environ.get("SHOPIFY_APP_ADMIN_TOKEN")
API = "2026-07"
OUT = os.path.dirname(os.path.abspath(__file__))

def gql(query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        f"https://{SHOP}/admin/api/{API}/graphql.json", data=body,
        headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    if "errors" in d:
        raise SystemExit(f"GraphQL errors: {d['errors']}")
    return d["data"]

Q = """
query($cursor:String){
  products(first:50, after:$cursor){
    pageInfo{ hasNextPage endCursor }
    nodes{
      id title handle
      w: metafield(namespace:"judgeme", key:"widget"){ value }
    }
  }
}"""

def parse_reviews(widget_html, product):
    """Pull individual reviews out of the rendered Judge.me widget markup.

    Judge.me emits SINGLE-quoted attributes, so every pattern here is
    quote-agnostic ([\'"]). That detail is the whole reason a naive parser
    returns zero reviews against real markup.
    """
    out = []
    blocks = re.split(r'(?=<div[^>]*class=[\'"]jdgm-rev\s)', widget_html)
    for b in blocks[1:]:
        def attr(name):
            m = re.search(name + r'=[\'"]([^\'"]*)[\'"]', b)
            return m.group(1).strip() if m else ""

        def text(cls):
            m = re.search(
                r'class=[\'"][^\'"]*\b' + cls + r'\b[^\'"]*[\'"][^>]*>(.*?)</(?:div|span|b|a|h\d)>',
                b, re.S)
            if not m:
                return ""
            t = re.sub(r'<[^>]+>', ' ', m.group(1))
            return re.sub(r'\s+', ' ', html.unescape(t)).strip()

        body = text('jdgm-rev__body')
        title = text('jdgm-rev__title')
        if not (body or title):
            continue
        out.append({
            "review_id": attr('data-review-id'),
            "product": attr('data-product-title') or product["title"],
            "handle": product["handle"],
            "product_url": attr('data-product-url'),
            "author": text('jdgm-rev__author'),
            "rating": attr('data-score'),
            "title": title,
            "body": body,
            "date": (attr('data-content') or "")[:10],
            "verified_buyer": attr('data-verified-buyer'),
            "permission": "published-review",
            "used_in": "",
        })
    return out


def main():
    if not TOKEN:
        raise SystemExit("SHOPIFY_APP_ADMIN_TOKEN not set — source ~/.env first")
    reviews, cursor = [], None
    while True:
        data = gql(Q, {"cursor": cursor})
        page = data["products"]
        for p in page["nodes"]:
            w = (p.get("w") or {}).get("value") or ""
            if w:
                reviews.extend(parse_reviews(w, p))
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]

    # de-duplicate: the same review can render in more than one widget
    seen, uniq = set(), []
    for r in reviews:
        k = r["review_id"] or (r["author"], r["body"][:90])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(r)

    cols = ["review_id", "product", "handle", "product_url", "author", "rating",
            "title", "body", "date", "verified_buyer", "permission", "used_in"]
    with open(os.path.join(OUT, "proof-bank.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(uniq)
    with open(os.path.join(OUT, "proof-bank.json"), "w", encoding="utf-8") as f:
        json.dump(uniq, f, indent=2, ensure_ascii=False)

    print(f"products with reviews : {len({r['product'] for r in uniq})}")
    print(f"unique reviews         : {len(uniq)}")
    usable = [r for r in uniq if len(r["body"]) >= 120]
    print(f"substantial (>=120 ch) : {len(usable)}")
    from collections import Counter
    print("by rating:", dict(sorted(Counter(r["rating"] for r in uniq).items())))
    print(f"written to             : {OUT}/proof-bank.csv (+ .json)")

if __name__ == "__main__":
    main()
