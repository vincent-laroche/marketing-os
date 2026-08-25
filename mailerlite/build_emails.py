#!/usr/bin/env python3
"""Render + validate all 22 MailerLite journey emails into ./emails/."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ml_components import shell, add_utm
from ml_content_pp import PP_EMAILS
from ml_content_cr import CR_EMAILS
from ml_content_wb import WB_EMAILS
from ml_content_ro import RO_EMAILS
from ml_content_w import W_EMAILS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "emails")
os.makedirs(OUT, exist_ok=True)

ALL = PP_EMAILS + CR_EMAILS + WB_EMAILS + RO_EMAILS + W_EMAILS
errors, report = [], []
for fn in ALL:
    slug, title, subject, preview, body = fn()
    html = add_utm(shell(title, preview, body), slug)
    path = os.path.join(OUT, slug + ".html")
    with open(path, "w") as f:
        f.write(html)
    # validation
    tokens = sorted(set(re.findall(r"\{\$[a-z_]+\}", html)))
    hubspot_leftover = re.findall(r"\{\{[^}]+\}\}", html)
    if "{$unsubscribe}" not in html:
        errors.append(f"{slug}: missing unsubscribe")
    if hubspot_leftover:
        errors.append(f"{slug}: HubSpot-style tokens left: {hubspot_leftover}")
    if "<table" not in html or "</html>" not in html:
        errors.append(f"{slug}: structure broken")
    kb = len(html) // 1024
    flag = " ⚠️ >100KB (Gmail clips)" if kb > 100 else ""
    report.append((slug, kb, len(tokens), flag))

print(f"{'email':38} {'KB':>4} {'tokens':>6}")
for slug, kb, ntok, flag in report:
    print(f"{slug:38} {kb:>4} {ntok:>6}{flag}")
print(f"\nTotal: {len(report)} emails")
if errors:
    print("\nERRORS:")
    [print(" -", e) for e in errors]
    sys.exit(1)
print("Validation: all OK (unsubscribe present, no HubSpot tokens, structure intact)")
