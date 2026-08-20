#!/usr/bin/env python3
"""Phase 3 gate: every link in the 53 built emails resolves, or is a declared token.

Reads shopify-messaging/emails/*.html, collects every href and img src, and reports:
  OK        HTTP 200 (redirects followed)
  FAIL      any other status, or a network error
  TOKEN     a platform merge tag resolved at send time ({{ unsubscribe_url }} etc.)
  TODO      a deliberate loud '#TODO-' placeholder that must be resolved before send
Writes shopify-messaging/link-report.json. Read-only over the network.
"""
import glob, html, json, os, re, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EMAILS = os.path.join(ROOT, "shopify-messaging", "emails")
UA = "Mozilla/5.0 (compatible; hsc-email-linkcheck/1.0)"

def collect():
    urls = {}
    for f in sorted(glob.glob(os.path.join(EMAILS, "*.html"))):
        doc = open(f, encoding="utf-8").read()
        for u in re.findall(r'(?:href|src)="([^"]+)"', doc):
            u = html.unescape(u)  # hrefs are entity-encoded in HTML; probe the real URL
            urls.setdefault(u, set()).add(os.path.basename(f))
    return urls

def classify(u):
    if u.startswith("{{") or "{{" in u:
        return "TOKEN"
    if u.startswith("#TODO-"):
        return "TODO"
    if u.startswith("mailto:"):
        return "MAILTO"
    if u.startswith("http"):
        return None
    return "RELATIVE"

def probe(u):
    for method in ("HEAD", "GET"):
        try:
            r = urllib.request.Request(u, method=method, headers={"User-Agent": UA})
            with urllib.request.urlopen(r, timeout=25) as resp:
                return resp.status
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 501):
                continue
            return e.code
        except Exception as e:
            if method == "HEAD":
                continue
            return "ERR: %s" % type(e).__name__
    return "ERR"

def main():
    urls = collect()
    rows, live = [], []
    for u, files in sorted(urls.items()):
        c = classify(u)
        (rows if c else live).append((u, sorted(files), c))
    # the storefront rate-limits: probe serially, and retry a 429 after a pause
    results = []
    for u, _f, _c in live:
        st = probe(u)
        for delay in (3, 8, 20):
            if st != 429:
                break
            time.sleep(delay)
            st = probe(u)
        results.append(st)
        time.sleep(0.6)
    report, bad = [], 0
    for (u, files, _), status in zip(live, results):
        ok = status == 200
        bad += 0 if ok else 1
        report.append({"url": u, "status": "OK" if ok else "FAIL",
                       "http": status, "emails": files})
    for u, files, c in rows:
        report.append({"url": u, "status": c, "http": None, "emails": files})
    report.sort(key=lambda r: (r["status"] != "FAIL", r["status"], r["url"]))
    json.dump(report, open(os.path.join(ROOT, "shopify-messaging", "link-report.json"), "w"),
              indent=1, ensure_ascii=False)
    for r in report:
        print("%-7s %-5s %-72s %d email(s)" %
              (r["status"], r["http"] if r["http"] is not None else "", r["url"][:72], len(r["emails"])))
    n = {}
    for r in report:
        n[r["status"]] = n.get(r["status"], 0) + 1
    print("\n" + "  ".join("%s:%d" % kv for kv in sorted(n.items())))
    print("GATE:", "GREEN — every live URL 200" if bad == 0 else "RED — %d URL(s) not 200" % bad)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
