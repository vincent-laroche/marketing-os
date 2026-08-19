#!/usr/bin/env python3
"""Pre-publish preflight for MailerLite email modules and assembled emails.

Usage:
  python3 scripts/preflight_email.py mailerlite-blocks/            # whole library
  python3 scripts/preflight_email.py mailerlite-blocks/wb1_hero.html
  python3 scripts/preflight_email.py <path> --no-net               # skip HTTP checks

Exit code 0 = publishable, 1 = at least one FAIL. WARNs never block.
"""
import re, sys, json, pathlib, argparse, urllib.request, urllib.error, collections

# ---- authority ------------------------------------------------------------
BRAND = {"#EFE7D2":"Paper","#15140F":"Ink","#F7F1DE":"Bone","#DDD2B6":"Paper Dark",
         "#2A2620":"Ink Soft","#5A5448":"Ink Mute","#ED6F5C":"Coral"}
CARD_SURFACES = {"#EFE7D2", "#F7F1DE", "#15140F", "#ED6F5C"}   # PLATFORM_EMAIL.md §1.1
# Bone #F7F1DE readmitted as a section surface 2026-08-19 (Vincent). Paper Dark and Ink Soft
# remain excluded - the 2026-08-11 rejection was a THREE-sand stack, not Bone alone.
FORBIDDEN_TAGS = ("script","embed","frame","iframe","form","input","object","textarea")

# Verified 2026-08-19 against the live storefront.
DEAD_URLS = {
  "https://hairsolutions.co/contact": "404 - use https://hairsolutions.co/pages/contact",
  "https://hairsolutions.co/reviews": "404 - no reviews page exists on the storefront",
}
SUSPECT_HOSTS = {
  "meetings.hubspot.com": "HubSpot booking link - brand has moved off HubSpot, confirm still intended",
  "customerportal.hairsolutions.co": "HubSpot-hosted membership portal, confirm still intended",
  "50966981.fs1.hubspotusercontent-na1.net": "dead HubSpot CDN - rehost in MailerLite File Manager",
}
BARE_SOCIAL = {  # generic domain instead of the brand account
  "https://facebook.com/":  "https://www.facebook.com/hairsolutions.company",
  "https://instagram.com/": "https://www.instagram.com/hairsolutions.co",
  "https://youtube.com/":   "https://www.youtube.com/@hairsolutions_co",
}
# Custom fields that exist in MailerLite account 2582639.
KNOWN_FIELDS = {"name","last_name","email","company","city","country","phone","state","z_i_p",
  "buyer_type","carrier","customer_status","days_since_supply_order","estimated_delivery_date",
  "estimated_ship_date","intent_tier","last_order_specification","last_viewed_product",
  "last_viewed_product_url","migration_cohort","months_since_delivery","months_since_last_order",
  "order_band","order_number","order_status_url","product_summary","production_lead_time",
  "recommended_interval","recommended_reorder_items","reorder_count","tracking_number",
  "tracking_url","value_band","warm_up_wave","unsubscribe"}

R = collections.Counter()
def emit(level, check, msg):
    R[level] += 1
    print(f"  {level:4s} [{check}] {msg}")

def check_file(p, net=True, url_cache=None):
    s = p.read_text(encoding="utf-8")
    print(f"\n{p.name}")

    # A. structure
    if re.search(r"<!doctype|<html|<head\b|<body\b", s, re.I):
        emit("FAIL","structure","document scaffolding present - Code block takes a fragment only")
    for t in FORBIDDEN_TAGS:
        if re.search(rf"<\s*{t}\b", s, re.I):
            emit("FAIL","structure",f"<{t}> is rejected by MailerLite's Code block")

    # B. palette
    for hexv in sorted({h.upper() for h in re.findall(r"#[0-9A-Fa-f]{6}", s)}):
        if hexv not in BRAND:
            emit("FAIL","palette",f"{hexv} is not a brand token")
    for surf in {c.upper() for c in re.findall(r'az-module-shell[^>]*?background-color:(#[0-9A-Fa-f]{6})', s)}:
        if surf not in CARD_SURFACES:
            emit("FAIL","palette",f"card surface {surf} ({BRAND.get(surf,'?')}) - surfaces are Paper/Ink only")

    # C. geometry
    if re.search(r'padding:\s*[1-9]\d*px\s+\d+px?;?"?\s*>\s*<table[^>]*az-module-shell', s):
        emit("WARN","geometry","outer wrapper has vertical padding - cards will not stack flush")

    # D. merge tags
    for tag in re.findall(r"\{\$[^}]*\}", s):
        m = re.fullmatch(r"\{\$([a-z0-9_]+)(\|default\([^)]*\))?\}", tag)
        if not m:
            emit("FAIL","merge-tag",f"{tag} - MailerLite syntax is {{$field}} or {{$field|default(value)}}")
        elif m.group(1) not in KNOWN_FIELDS:
            emit("FAIL","merge-tag",f"{{${m.group(1)}}} is not a field in account 2582639")
    if 'default="' in s:
        emit("FAIL","merge-tag",'default="..." is invalid - use {$field|default(value)}')

    # E. images
    for img in re.findall(r"<img\b[^>]*>", s, re.I):
        if not re.search(r'alt="[^"]+"', img): emit("FAIL","image","<img> missing non-empty alt text")
        if not re.search(r'\bwidth="\d+"', img): emit("WARN","image","<img> missing width attribute")
        if re.search(r'src="http://', img):     emit("FAIL","image","<img> served over http, not https")

    # F. links
    hrefs = re.findall(r'href="([^"]*)"', s)
    for h in hrefs:
        if h.strip() in ("", "#"):
            emit("FAIL","link","dead placeholder href=\"#\"")
        elif h in DEAD_URLS:
            emit("FAIL","link",f"{h} -> {DEAD_URLS[h]}")
        elif h in BARE_SOCIAL:
            emit("FAIL","link",f"{h} is a generic domain - use {BARE_SOCIAL[h]}")
        else:
            for host, why in SUSPECT_HOSTS.items():
                if host in h: emit("WARN","link",f"{h} - {why}")
    for img in re.findall(r'src="(https?://[^"]+)"', s):
        for host, why in SUSPECT_HOSTS.items():
            if host in img: emit("FAIL","image",f"{img} - {why}")

    if net:
        for u in {h for h in hrefs if h.startswith("http")} | {i for i in re.findall(r'src="(https?://[^"]+)"', s)}:
            if url_cache is not None and u in url_cache:
                code = url_cache[u]
            else:
                req = urllib.request.Request(u, method="GET", headers={"User-Agent":"Mozilla/5.0 preflight"})
                try:
                    with urllib.request.urlopen(req, timeout=20) as r: code = r.status
                except urllib.error.HTTPError as e: code = e.code
                except Exception: code = 0
                if url_cache is not None: url_cache[u] = code
            if code == 0:        emit("FAIL","link",f"{u} unreachable")
            elif code >= 400 and code != 406:
                emit("FAIL","link",f"{u} returned HTTP {code}")

    return s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path"); ap.add_argument("--no-net", action="store_true")
    a = ap.parse_args()
    root = pathlib.Path(a.path)
    files = sorted(f for f in (root.glob("*.html") if root.is_dir() else [root])
                   if not f.name.startswith("_"))
    cache, joined = {}, []
    for f in files:
        joined.append(check_file(f, net=not a.no_net, url_cache=cache))

    # G. compliance - assessed across the whole email, not per module
    all_html = "\n".join(joined)
    print("\ncompliance (whole email)")
    if "{$unsubscribe}" not in all_html:
        emit("FAIL","compliance","no {$unsubscribe} link anywhere")
    if not re.search(r"Ehitajate tee 110", all_html):
        emit("WARN","compliance","verified postal address (Ehitajate tee 110, Tallinn, Estonia) not found")
    if re.search(r"Forest Hills|New York", all_html):
        emit("FAIL","compliance","Forest Hills / New York address contradicts MailerLite account settings")

    print(f"\n{'='*64}\n{len(files)} file(s)   FAIL {R['FAIL']}   WARN {R['WARN']}")
    print("VERDICT:", "PUBLISHABLE" if not R["FAIL"] else "BLOCKED - fix FAILs first")
    sys.exit(1 if R["FAIL"] else 0)

if __name__ == "__main__":
    main()
