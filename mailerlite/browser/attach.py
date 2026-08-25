#!/usr/bin/env python3
"""Attach to the running Chrome (CDP :9223) and expose `page` for exploration.
Usage: python3 attach.py '<python one-liner using page>'  — or import from other scripts."""
import sys
from playwright.sync_api import sync_playwright

CDP = "http://localhost:9223"

def get_page(pw, url_hint="mailerlite"):
    browser = pw.chromium.connect_over_cdp(CDP)
    for ctx in browser.contexts:
        for p in ctx.pages:
            if url_hint in (p.url or ""):
                return browser, p
    # fallback: first page of first context
    ctx = browser.contexts[0]
    return browser, (ctx.pages[0] if ctx.pages else ctx.new_page())

if __name__ == "__main__":
    with sync_playwright() as pw:
        browser, page = get_page(pw)
        print("attached:", (page.url or "")[:110])
        code = sys.argv[1] if len(sys.argv) > 1 else "pass"
        exec(code)
        browser.close()
