#!/usr/bin/env python3
"""Launch a persistent Chrome (CDP :9223) on the MailerLite dashboard.
Stays alive so follow-up scripts can attach via connect_over_cdp."""
import time
from playwright.sync_api import sync_playwright

PROFILE = "/Users/vMac/04_marketing/email/mailerlite/.browser-profile"
CDP = "http://localhost:9223"

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(
        PROFILE,
        channel="chrome",
        headless=False,
        args=["--remote-debugging-port=9223", "--window-size=1440,950"],
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://dashboard.mailerlite.com/", wait_until="domcontentloaded")
    print("READY — browser up, CDP on :9223", flush=True)
    while True:
        time.sleep(60)
