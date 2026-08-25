#!/usr/bin/env python3
"""Persistent Playwright browser agent for driving the MailerLite UI.

Standalone tooling only -- runs from ~/.venv-playwright (NOT a project
dependency; project scripts remain stdlib-only).

Launch:
    ~/.venv-playwright/bin/python tools/browser_agent.py &

Then drive it over HTTP on localhost:8420:
    /status /goto?url=... /new?url=... /click?selector=... /type?selector=...&text=...
    /press?key=... /screenshot?path=... /snapshot /eval?js=... /html

Login sessions persist in the profile dir across restarts.
"""

import json
import queue
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

PORT = 8420
PROFILE_DIR = str(Path.home() / ".ml-browser-profile")
MAX_HTML = 200_000

_commands = queue.Queue()


def _snapshot(page):
    js = """() => {
        const seen = new Set(); const out = [];
        const els = document.querySelectorAll('a, button, input, select, textarea, [role="button"], [role="link"], [role="tab"], [role="menuitem"]');
        for (const el of els) {
            const r = el.getBoundingClientRect();
            if (r.width === 0 || r.height === 0) continue;
            const tag = el.tagName.toLowerCase();
            const text = (el.innerText || el.value || el.getAttribute('aria-label') || el.placeholder || '').trim().slice(0, 120);
            const href = el.href || '';
            const key = tag + '|' + text + '|' + href + '|' + Math.round(r.x) + '|' + Math.round(r.y);
            if (seen.has(key)) continue;
            seen.add(key);
            out.push({tag, text, href, type: el.type || '', role: el.getAttribute('role') || '', x: Math.round(r.x), y: Math.round(r.y), id: el.id || ''});
            if (out.length >= 400) break;
        }
        return out;
    }"""
    return page.evaluate(js)


def _handle(page_holder, params):
    """Executed in the Playwright main thread. Returns JSON-able dict."""
    action = params.pop("action", ["status"])[0]
    page = page_holder["page"]

    if action == "status":
        return {"ok": True, "url": page.url, "title": page.title()}

    if action == "goto":
        page.goto(params["url"][0], wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(800)
        return {"ok": True, "url": page.url, "title": page.title()}

    if action == "new":
        page = page_holder["ctx"].new_page()
        page_holder["page"] = page
        page.goto(params["url"][0], wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(800)
        return {"ok": True, "url": page.url, "title": page.title()}

    if action == "click":
        sel = params["selector"][0]
        page.locator(sel).first.click(timeout=8000)
        page.wait_for_timeout(800)
        return {"ok": True, "url": page.url, "title": page.title()}

    if action == "type":
        page.locator(params["selector"][0]).first.fill(params["text"][0], timeout=8000)
        return {"ok": True}

    if action == "press":
        page.keyboard.press(params["key"][0])
        page.wait_for_timeout(400)
        return {"ok": True}

    if action == "screenshot":
        path = params.get("path", ["/tmp/ml-shot.png"])[0]
        page.screenshot(path=path, full_page=params.get("full", ["0"])[0] == "1")
        return {"ok": True, "path": path}

    if action == "snapshot":
        return {"ok": True, "url": page.url, "title": page.title(), "elements": _snapshot(page)}

    if action == "eval":
        return {"ok": True, "result": page.evaluate(params["js"][0])}

    if action == "evalfile":
        result = page.evaluate(params["js"][0])
        path = params["path"][0]
        text = result if isinstance(result, str) else json.dumps(result)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return {"ok": True, "path": path, "len": len(text)}

    if action == "setfile":
        path = params["path"][0]
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        js = """(text) => {
            const el = document.querySelector('.cm-content');
            if (!el || !el.cmView) return 'no-cm';
            const view = el.cmView.view;
            view.dispatch({changes: {from: 0, to: view.state.doc.length, insert: text}});
            return String(view.state.doc.length);
        }"""
        return {"ok": True, "result": page.evaluate(js, content)}

    if action == "html":
        html = page.content()
        return {"ok": True, "html": html[:MAX_HTML], "truncated": len(html) > MAX_HTML}

    return {"ok": False, "error": f"unknown action: {action}"}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        params["action"] = [parsed.path.lstrip("/") or "status"]
        holder = {}
        _commands.put((self.server.page_holder, params, holder))
        deadline = time.time() + 45
        while "result" not in holder and time.time() < deadline:
            time.sleep(0.05)
        body = json.dumps(holder.get("result", {"ok": False, "error": "timeout"})).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # quiet
        pass


def main():
    pw = sync_playwright().start()
    ctx = pw.chromium.launch_persistent_context(
        PROFILE_DIR,
        headless=False,
        viewport={"width": 1440, "height": 900},
        args=["--auto-open-devtools-for-tabs"],
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page_holder = {"ctx": ctx, "page": page}

    server = HTTPServer(("127.0.0.1", PORT), Handler)
    server.page_holder = page_holder
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"browser agent listening on http://127.0.0.1:{PORT}", flush=True)
    print(f"profile: {PROFILE_DIR}", flush=True)

    try:
        while True:
            try:
                ph, params, holder = _commands.get(timeout=0.25)
            except queue.Empty:
                continue
            try:
                holder["result"] = _handle(ph, params)
            except Exception as e:
                holder["result"] = {"ok": False, "error": f"{type(e).__name__}: {e}"}
    except KeyboardInterrupt:
        pass
    finally:
        ctx.close()
        pw.stop()


if __name__ == "__main__":
    main()
