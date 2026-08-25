#!/usr/bin/env python3
"""Select which HubSpot contacts may be uploaded to MailerLite, and tier them.

Standing decisions (Vincent, 2026-08-19):
  * Contacts NEVER come from Shopify. The HubSpot export is the only source.
  * `comm_marketing_status_manual` is worthless outside HubSpot — never read it.
  * Suppression is absolute: the X0 list below is excluded under every option.

Tiers (first match wins):
    X0  suppressed      never upload, for any reason
    X1  keep_non_marketing
    X2  hold_review     unvalidated leads, held pending Vincent's review
    A   promote_now
    B   promote_next_cycle
    C   customer        lifecyclestage == customer
    D   warm            intent_tier_static HOT/WARM/LUKEWARM/STALE_HIGH…
    E   cold            intent_tier_static COLD
    F   no signal

Writes tiered output to exports/ (gitignored — the rows carry PII).

    python3 mailerlite/select_audience.py
    python3 mailerlite/select_audience.py --tiers A,B,C,D,E
"""
import csv, json, os, re, sys, collections
from pathlib import Path

csv.field_size_limit(10 ** 7)
HERE = Path(__file__).resolve().parent.parent
SRC = HERE / "exports" / "hubspot-2026-08-18" / "contacts.csv"
OUT = HERE / "exports" / "mailerlite-audience"

WANTED = "A,B,C,D,E"
for a in sys.argv[1:]:
    if a.startswith("--tiers="):
        WANTED = a.split("=", 1)[1]
WANTED = {t.strip().upper() for t in WANTED.split(",") if t.strip()}

RISK = re.compile(r"crisis|chargeback|angry|lost|fraud", re.I)
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$", re.I)
WARM = {"HOT", "WARM", "LUKEWARM", "STALE_HIGH_HISTORICAL_INTENT"}

rows = list(csv.DictReader(open(SRC, newline="", encoding="utf-8")))
OPTOUTS = [h for h in rows[0] if h.startswith("hs_email_optout_")]


def suppressed(r):
    """Absolute exclusions. Returns the list of reasons (empty == not suppressed)."""
    out = []
    if not EMAIL.match((r.get("email") or "").strip().lower()):
        out.append("no/invalid email")
    if r.get("marketing_contact_intent") == "suppress_never_market":
        out.append("suppress_never_market")
    if RISK.search(r.get("customer_situation") or ""):
        out.append("situation:crisis/chargeback/angry/lost")
    if (r.get("hs_email_optout") or "").lower() == "true":
        out.append("hs_email_optout")
    if any((r.get(c) or "").lower() == "true" for c in OPTOUTS):
        out.append("subscription opt-out")
    if (r.get("hs_email_hard_bounce_reason_enum") or "").strip():
        out.append("hard bounce")
    if (r.get("contact_type") or "") in ("internal", "supplier"):
        out.append("internal/supplier")
    return out


def tier(r):
    if suppressed(r):
        return "X0"
    i = (r.get("marketing_contact_intent") or "").strip()
    if i == "keep_non_marketing":
        return "X1"
    if i == "hold_review":
        return "X2"
    if i == "promote_now":
        return "A"
    if i == "promote_next_cycle":
        return "B"
    if (r.get("lifecyclestage") or "") == "customer":
        return "C"
    it = (r.get("intent_tier_static") or "").strip().upper()
    if it in WARM:
        return "D"
    if it == "COLD":
        return "E"
    return "F"


# --- professional segmentation -------------------------------------------
# Hairdressers / hair professionals receive different content (Vincent,
# 2026-08-19). contact_type is the only trustworthy signal: a keyword sweep of
# free-text produced ~29% false positives, because consumers routinely write
# "looking for a stylist near me". Self-identified pros go to a REVIEW file
# instead of straight into the segment.
SEEK = re.compile(r"(looking|search\w*|need|want|find|is there|any)\b[^.!?]{0,40}"
                  r"\b(stylist|salon|barber|professional|someone)"
                  r"|\bi[' ]?m a runner\b|\bi run and\b", re.I)
PRO_SELF = re.compile(r"""
  \b(i\s*(?:'m|\s+am)\s+(?:a|an)\s+|my\s+)[^.!?]{0,30}\b
     (salon\s*owner|master\s+stylist|stylist|barber|hairdress\w*|cosmetolog\w*|tricholog\w*)\b
| \b(salon|shop|studio)\s+owner\b
| \bi\s+(own|operate|manage)\s+(a|an|my|our)\b
| \b(my|our)\s+(salon|studio|shop|clients|business)\b
| \bin\s+the\s+(industry|business)\s+for\s+\d
| \bsupplier\s+to\s+purchase\b
""", re.I | re.X)
FREETEXT = ["message", "legacy_message_typeform", "jobtitle", "company"]


def is_pro(r):
    return "hair_professional" in (r.get("contact_type") or "")


def pro_candidate(r):
    """Self-identified professional not tagged as one. Needs human review."""
    if is_pro(r):
        return None
    for c in FREETEXT:
        v = r.get(c) or ""
        if PRO_SELF.search(v) and not SEEK.search(v):
            return (c, v[:300])
    return None


# MailerLite custom fields carried across. profile_hair_* deliberately omitted:
# only 1 of 3,967 rows populates them, so they would merge blank everywhere.
FIELDS = {
    "name": "firstname", "last_name": "lastname",
    "customer_status": "lifecycle_customer_status",
    "buyer_type": "contact_type",
    "intent_tier": "intent_tier_static",
    "value_band": "customer_lrv_amount",
    "lifecycle_stage": "lifecyclestage",
    "situation": "customer_situation",
}

buckets = collections.defaultdict(list)
supp_reasons = collections.Counter()
for r in rows:
    t = tier(r)
    if t == "X0":
        for x in suppressed(r):
            supp_reasons[x] += 1
    buckets[t].append(r)

print(f"source: {SRC.relative_to(HERE)}  rows={len(rows)}\n")
LABEL = {"A": "promote_now", "B": "promote_next_cycle", "C": "customer",
         "D": "warm intent", "E": "cold intent", "F": "no signal",
         "X0": "SUPPRESSED", "X1": "keep_non_marketing", "X2": "hold_review"}
for t in sorted(buckets):
    mark = "->" if t in WANTED else "  "
    print(f" {mark} {t:<3} {LABEL[t]:<22} {len(buckets[t]):>5}")
print("\n suppression reasons:")
for k, n in supp_reasons.most_common():
    print(f"      {n:>4}  {k}")

sel = [(t, r) for t in sorted(WANTED) for r in buckets.get(t, [])]
seen, dedup = set(), []
for t, r in sel:
    e = r["email"].strip().lower()
    if e in seen:
        continue
    seen.add(e)
    dedup.append((t, r))
print(f"\n SELECTED: {len(dedup)}   (tiers {','.join(sorted(WANTED))})")

OUT.mkdir(parents=True, exist_ok=True)
for t in sorted(WANTED):
    part = [r for tt, r in dedup if tt == t]
    if not part:
        continue
    p = OUT / f"tier-{t}-{LABEL[t].replace(' ', '-')}.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["email"] + list(FIELDS))
        for r in part:
            w.writerow([r["email"].strip().lower()] +
                       [(r.get(src) or "").strip() for src in FIELDS.values()])
    print(f"   wrote {p.relative_to(HERE)}  ({len(part)})")

pros = [r for t, r in dedup if is_pro(r)]
p = OUT / "segment-hair-professionals.csv"
with open(p, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["email", "tier"] + list(FIELDS))
    for t, r in dedup:
        if is_pro(r):
            w.writerow([r["email"].strip().lower(), t] +
                       [(r.get(src) or "").strip() for src in FIELDS.values()])
print(f"   wrote {p.relative_to(HERE)}  ({len(pros)})  <- different content")

cands = [(t, r, pro_candidate(r)) for t, r in dedup]
cands = [(t, r, c) for t, r, c in cands if c]
p = OUT / "pro-candidates-REVIEW.csv"
with open(p, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["email", "firstname", "lastname", "tier", "matched_column", "evidence"])
    for t, r, (col, ev) in cands:
        w.writerow([r["email"].strip().lower(), r.get("firstname", ""),
                    r.get("lastname", ""), t, col, ev])
print(f"   wrote {p.relative_to(HERE)}  ({len(cands)})  <- NOT auto-added; review first")

with open(OUT / "suppression-list.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["email", "reasons"])
    for r in buckets["X0"]:
        w.writerow([(r.get("email") or "").strip().lower(), "; ".join(suppressed(r))])
print(f"   wrote {(OUT / 'suppression-list.csv').relative_to(HERE)}  ({len(buckets['X0'])})")
