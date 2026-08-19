#!/usr/bin/env python3
"""Send a Hair Solutions Co. transactional service email through MailerSend.

Scope: TRANSACTIONAL / service mail only (order confirmation, shipping
confirmation). Marketing sending stays out of this repo entirely — see
AGENTS.md #2.

    python3 send_service_email.py --type order-confirmation \
        --order fixtures/sample-order.json --dry-run

    python3 send_service_email.py --type shipping-confirmation \
        --order fixtures/sample-order.json

Hard safety constraint
----------------------
`ALLOWED_RECIPIENTS` below is the complete set of addresses this script will
ever transmit to. It is a module constant, it is checked immediately before the
HTTP request is issued, and **no command-line flag, environment variable or
payload field can extend it**. Any other address aborts with exit code 2 before
a socket is opened. Vincent approved test sends to himself only.

Stdlib only (urllib.request), per AGENTS.md #6. Idempotent: every accepted send
is recorded in `.send-ledger.json` keyed by (type, order number, recipient,
content fingerprint); re-running the same send is a no-op unless --force.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# --------------------------------------------------------------------------
# Hard recipient allowlist. Not configurable. Do not parameterise this.
# --------------------------------------------------------------------------
ALLOWED_RECIPIENTS = frozenset({"vincent@hairsolutions.co"})

USER_AGENT = "hairsolutions-service-email/1.0 (+https://hairsolutions.co)"
API_BASE = "https://api.mailersend.com/v1"
SENDING_DOMAIN = "mail.hairsolutions.co"
DOMAIN_ID = "dnvo4dm6ynn45r86"

FROM_EMAIL = "orders@mail.hairsolutions.co"
FROM_NAME = "Hair Solutions Co."
REPLY_TO_EMAIL = "info@hairsolutions.co"
REPLY_TO_NAME = "Vincent at Hair Solutions Co."

HERE = Path(__file__).resolve().parent
TEMPLATE_DIR = HERE / "emails"
LEDGER_PATH = HERE / ".send-ledger.json"

EMAIL_TYPES = {
    "order-confirmation": {
        "template": "PP-1-order-confirmation.html",
        "subject": "Your order is confirmed, {{ name }}",
        "tag": "order-confirmation",
        "requires": ("order_number", "order_status_url", "estimated_ship_date",
                     "estimated_delivery_date", "items", "totals"),
    },
    "shipping-confirmation": {
        "template": "PP-4-shipped-tracking.html",
        "subject": "It's shipped — tracking inside",
        "tag": "shipping-confirmation",
        "requires": ("order_number", "estimated_delivery_date", "items",
                     "tracking_number", "carrier", "tracking_url"),
    },
}


# --------------------------------------------------------------------------
# Payload normalisation: raw order JSON -> MailerSend personalization data
# --------------------------------------------------------------------------
def build_personalization(order: dict, email_type: str) -> dict:
    """Turn the documented raw order shape into the MailerSend `data` object.

    A Cloudflare Worker replacing this script must reproduce this transform
    exactly; see README.md for the field-by-field contract. The only derived
    field is `item.has_spec`, because MailerSend's Twig subset has no reliable
    truthiness test for an absent key — the template compares `== true`.
    """
    customer = order.get("customer") or {}
    shipping = order.get("shipping") or {}

    items = []
    for raw in order.get("items") or []:
        spec = (raw.get("spec") or "").strip()
        items.append({
            "name": raw.get("name", ""),
            "spec": spec,
            "has_spec": bool(spec),
            "qty": raw.get("qty", 1),
            "price": raw.get("price", ""),
        })

    totals = order.get("totals") or {}
    data = {
        "name": customer.get("name", "there"),
        "order_number": order.get("order_number", ""),
        "order_status_url": order.get("order_status_url", ""),
        "estimated_ship_date": order.get("estimated_ship_date", ""),
        "estimated_delivery_date": order.get("estimated_delivery_date", ""),
        "items": items,
        "totals": {
            "rows": totals.get("rows") or [],
            "total_label": totals.get("total_label", "Total"),
            "total": totals.get("total", ""),
        },
    }
    if email_type == "shipping-confirmation":
        data["carrier"] = shipping.get("carrier", "")
        data["tracking_number"] = shipping.get("tracking_number", "")
        data["tracking_url"] = shipping.get("tracking_url", "")
    return data


def validate(order: dict, email_type: str, data: dict) -> list[str]:
    spec = EMAIL_TYPES[email_type]
    problems = []
    for key in spec["requires"]:
        value = data.get(key)
        if key in ("items",):
            if not value:
                problems.append("items: at least one line item is required")
            continue
        if key == "totals":
            if email_type == "order-confirmation" and not data["totals"]["total"]:
                problems.append("totals.total: required for order-confirmation")
            continue
        if not value:
            problems.append(f"{key}: missing or empty")
    for i, item in enumerate(data.get("items") or []):
        if not item["name"]:
            problems.append(f"items[{i}].name: missing")
        if email_type == "order-confirmation" and not item["price"]:
            problems.append(f"items[{i}].price: missing (must be a pre-formatted "
                            "display string — MailerSend's Twig subset cannot format numbers)")
    return problems


# --------------------------------------------------------------------------
# Minimal renderer for the MailerSend Twig subset actually used by the two
# templates: {{ a }}, {{ a.b }}, {% for x in y %}…{% endfor %},
# {% if x.y == true %}…{% endif %}. Preview/verification only — MailerSend
# renders server-side. Anything the templates use that this cannot parse is a
# construct worth re-checking against MailerSend's supported subset.
# --------------------------------------------------------------------------
_FOR = re.compile(r"\{%\s*for\s+(\w+)\s+in\s+([\w.]+)\s*%\}(.*?)\{%\s*endfor\s*%\}", re.S)
_IF = re.compile(r"\{%\s*if\s+([\w.]+)\s*==\s*true\s*%\}(.*?)\{%\s*endif\s*%\}", re.S)
_VAR = re.compile(r"\{\{\s*([\w.]+)\s*\}\}")


def _lookup(ctx: dict, path: str):
    cur = ctx
    for part in path.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
        if cur is None:
            return None
    return cur


def render(template: str, ctx: dict) -> str:
    def do_for(m):
        var, src, body = m.group(1), m.group(2), m.group(3)
        seq = _lookup(ctx, src) or []
        out = []
        for entry in seq:
            scoped = dict(ctx)
            scoped[var] = entry
            out.append(render(body, scoped))
        return "".join(out)

    text = _FOR.sub(do_for, template)
    text = _IF.sub(lambda m: render(m.group(2), ctx) if _lookup(ctx, m.group(1)) is True else "", text)

    def do_var(m):
        value = _lookup(ctx, m.group(1))
        if value is None:
            return ""
        return (str(value).replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))

    return _VAR.sub(do_var, text)


def to_text(html: str) -> str:
    """Crude HTML -> text, for the dry-run preview and the API `text` part."""
    text = re.sub(r"(?is)<(script|style).*?</\1>", "", html)
    text = re.sub(r"(?s)<!--.*?-->", "", text)          # mso conditional blocks
    text = re.sub(r"(?i)<div style=\"display:none.*?</div>", "", text, flags=re.S)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</(tr|p|h1|div|table)>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = (text.replace("&nbsp;", " ").replace("&times;", "x").replace("&rarr;", "->")
            .replace("&amp;", "&").replace("&#9632;", "*").replace("&#x27;", "'")
            .replace("&zwnj;", "").replace("&lt;", "<").replace("&gt;", ">")
            .replace("&quot;", '"'))
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return "\n".join(line.strip() for line in text.splitlines()).strip()


# --------------------------------------------------------------------------
# Safety
# --------------------------------------------------------------------------
class RecipientRefused(Exception):
    pass


def assert_allowed(email: str) -> str:
    """The single choke point. Called again immediately before the HTTP call."""
    normalised = (email or "").strip().lower()
    if normalised not in ALLOWED_RECIPIENTS:
        raise RecipientRefused(
            f"refusing to send to {email!r}. This script transmits only to "
            f"{sorted(ALLOWED_RECIPIENTS)}. The allowlist is a module constant "
            "and cannot be overridden by any flag, env var or payload field."
        )
    return normalised


# --------------------------------------------------------------------------
# Idempotency ledger
# --------------------------------------------------------------------------
def load_ledger() -> dict:
    if LEDGER_PATH.exists():
        try:
            return json.loads(LEDGER_PATH.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_ledger(ledger: dict) -> None:
    LEDGER_PATH.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n")


def idempotency_key(email_type: str, order_number: str, recipient: str, data: dict) -> str:
    fingerprint = hashlib.sha256(
        json.dumps(data, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()
    raw = f"{email_type}|{order_number}|{recipient}|{fingerprint}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


# --------------------------------------------------------------------------
# MailerSend API
# --------------------------------------------------------------------------
def api(method: str, path: str, token: str, body: dict | None = None):
    req = urllib.request.Request(
        f"{API_BASE}{path}",
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            # MailerSend sits behind Cloudflare, which returns 403 error 1010
            # ("browser_signature_banned") for the default Python-urllib
            # user-agent. Identify the client explicitly or every send fails.
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            payload = resp.read().decode() or ""
            return resp.status, dict(resp.headers), payload
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers), exc.read().decode() or ""


def confirm_accepted(token: str, message_id: str, attempts: int = 6) -> dict:
    """Poll GET /messages/{id} until MailerSend has the message on record."""
    last = {}
    for n in range(attempts):
        status, _, body = api("GET", f"/messages/{message_id}", token)
        try:
            parsed = json.loads(body) if body else {}
        except json.JSONDecodeError:
            parsed = {"raw": body}
        last = {"http_status": status, "body": parsed}
        if status == 200:
            return last
        time.sleep(2 + 3 * n)
    return last


# --------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--type", required=True, choices=sorted(EMAIL_TYPES),
                    help="which service email to send")
    ap.add_argument("--order", required=True, type=Path,
                    help="path to the order JSON payload")
    ap.add_argument("--dry-run", action="store_true",
                    help="render and validate locally; open no socket")
    ap.add_argument("--render-to", type=Path,
                    help="also write the rendered HTML to this path")
    ap.add_argument("--force", action="store_true",
                    help="ignore the idempotency ledger (does NOT affect the "
                         "recipient allowlist, which cannot be bypassed)")
    ap.add_argument("--no-verify", action="store_true",
                    help="skip the post-send GET /messages/{id} confirmation")
    args = ap.parse_args()

    spec = EMAIL_TYPES[args.type]
    order = json.loads(args.order.read_text())
    data = build_personalization(order, args.type)

    problems = validate(order, args.type, data)
    if problems:
        print("PAYLOAD INVALID:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    # Recipient resolution + allowlist gate, before anything else happens.
    raw_recipient = ((order.get("customer") or {}).get("email") or "")
    try:
        recipient = assert_allowed(raw_recipient)
    except RecipientRefused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    template = (TEMPLATE_DIR / spec["template"]).read_text()
    html = render(template, data)
    subject = render(spec["subject"], data)
    text = to_text(html)

    if args.render_to:
        args.render_to.parent.mkdir(parents=True, exist_ok=True)
        args.render_to.write_text(html)

    payload = {
        "from": {"email": FROM_EMAIL, "name": FROM_NAME},
        "to": [{"email": recipient, "name": data["name"]}],
        "reply_to": {"email": REPLY_TO_EMAIL, "name": REPLY_TO_NAME},
        "subject": subject,
        # `html` goes up as the RAW Twig template — MailerSend renders it against
        # `personalization`. `text` goes up already rendered (it contains no Twig),
        # so the plain-text part stays a faithful fallback of the HTML.
        "html": template,
        "text": text,
        "tags": ["transactional", spec["tag"]],
        "personalization": [{"email": recipient, "data": data}],
    }

    key = idempotency_key(args.type, data["order_number"], recipient, data)
    ledger = load_ledger()

    if args.dry_run:
        print("=" * 78)
        print(f"DRY RUN — {args.type} — nothing will be sent")
        print("=" * 78)
        print(f"POST {API_BASE}/email")
        print(f"from        : {FROM_NAME} <{FROM_EMAIL}>  (domain {SENDING_DOMAIN})")
        print(f"reply_to    : {REPLY_TO_NAME} <{REPLY_TO_EMAIL}>")
        print(f"to          : {recipient}   [ALLOWLISTED]")
        print(f"subject raw : {spec['subject']}")
        print(f"subject rndr: {subject}")
        print(f"tags        : {payload['tags']}")
        print(f"html        : {len(payload['html'])} bytes of Twig-templated HTML "
              f"(sha256 {hashlib.sha256(payload['html'].encode()).hexdigest()[:16]})")
        print(f"idempotency : {key}"
              + ("   [ALREADY SENT — would be skipped]" if key in ledger else "   [new]"))
        print()
        print("--- personalization[0].data (sent to MailerSend) " + "-" * 30)
        print(json.dumps(payload["personalization"][0], indent=2, ensure_ascii=False))
        print()
        print("--- rendered body, text view " + "-" * 49)
        print(text)
        print()
        print("--- rendered line-item table, HTML " + "-" * 43)
        table = re.search(r"(?s)(What(?:&#x27;|')?s? (?:you ordered|in the box).*?</table>)", html)
        print(table.group(1) if table else "(not found)")
        return 0

    if key in ledger and not args.force:
        prior = ledger[key]
        print(f"SKIP (idempotent): identical {args.type} for {data['order_number']} "
              f"already sent to {recipient} at {prior['sent_at']} "
              f"(message_id {prior['message_id']}). Use --force to resend.")
        return 0

    token = os.environ.get("MAILERSEND_API_TOKEN")
    if not token:
        print("MAILERSEND_API_TOKEN is not set. "
              "Run: set -a && source ~/.env && set +a", file=sys.stderr)
        return 1

    # Second gate, immediately before the socket opens.
    for entry in payload["to"]:
        assert_allowed(entry["email"])

    status, headers, body = api("POST", "/email", token, payload)
    message_id = headers.get("x-message-id") or headers.get("X-Message-Id")
    print(f"POST /email -> HTTP {status}")
    print(f"x-message-id: {message_id}")
    if body.strip():
        print(f"body: {body[:2000]}")
    if status != 202:
        print("NOT ACCEPTED — nothing recorded in the ledger.", file=sys.stderr)
        return 1

    ledger[key] = {
        "type": args.type,
        "order_number": data["order_number"],
        "to": recipient,
        "message_id": message_id,
        "sent_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    save_ledger(ledger)

    if not args.no_verify and message_id:
        result = confirm_accepted(token, message_id)
        print(f"GET /messages/{message_id} -> HTTP {result['http_status']}")
        print(json.dumps(result["body"], indent=2)[:3000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
