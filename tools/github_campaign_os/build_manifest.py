import argparse
import csv
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, Iterable, List, Optional

from .model import Record, fingerprint
from .preview_publications import ISSUE_REPORT_PATH, load_preview_urls


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "github-campaign-os"
CSV_PATH = next((ROOT / "Email Reference File").glob("emails_master*_all.csv"))
LEDGER_PATH = ROOT / "shopify-messaging" / "build-ledger.json"

CAMPAIGNS = {
    "J1": ("Post-Purchase", "Post-Purchase", "Retain"),
    "J2": ("Cart Recovery and Browse Abandonment", "Abandoned Cart", "Convert"),
    "J3": ("Win-Back to Sunset", "Win-Back", "Reactivate"),
    "J4": ("Reorder", "Reorder", "Retain"),
    "J5": ("Consultation", "Consultation", "Convert"),
    "W": ("Newsletter Welcome", "Welcome", "Build Trust"),
    "N": ("Newsletter Programme", "Newsletter", "Educate"),
}
SERIES_TO_CAMPAIGN = {
    "J1 · Post-Purchase · Master": "J1",
    "J2 · Cart Recovery · Master": "J2",
    "J3 · Win-Back → Sunset": "J3",
    "J4 · Reorder · Master": "J4",
    "J5 · Consultation · Master": "J5",
    "W · Newsletter Welcome": "W",
    "N · Newsletter Programme": "N",
}
FAMILY = {
    "PP": ("Shopify Flow", "Automated / Lifecycle", "Yes", "Post-Purchase"),
    "CR": ("Shopify Messaging", "Automated / Lifecycle", "No", "Abandoned Cart"),
    "BR": ("Shopify Messaging", "Automated / Lifecycle", "No", "Browse Abandonment"),
    "WB": ("Shopify Flow", "Automated / Lifecycle", "Yes", "Win-Back"),
    "RO": ("Shopify Flow", "Automated / Lifecycle", "Yes", "Reorder"),
    "C": ("Shopify Flow", "Automated / Lifecycle", "Yes", "Consultation"),
    "W": ("Shopify Messaging", "Automated / Lifecycle", "No", "Welcome"),
    "NL": ("Shopify Messaging", "One-time Campaign", "No", "Newsletter"),
}
TASKS = (
    ("text-customer-snapshot", "Resolve RO-4 Text Customer Snapshot source gap", "J4", "P0", "flag:launch-blocker"),
    ("comparison", "Resolve NL-16 Comparison source gap", "N", "P0", "flag:launch-blocker"),
    ("consent-audience", "Verify Shopify consent and audience", None, "P0", "risk:consent"),
    ("flow-rules", "Define Flow enrollment, collision, and exit rules", None, "P1", "area:automation"),
    ("dynamic-data", "Verify reality-dependent dynamic data", None, "P1", "area:data"),
    ("measurement", "Define measurement and baseline reporting", None, "P1", "area:analytics"),
    ("campaign-os-migration", "Migrate email operations to GitHub Campaign OS", None, "P1", "area:operations"),
    ("launch-governance", "Define launch approval and rollback governance", None, "P0", "risk:activation"),
)

FIELD_NAMES = [
    "Stage", "Priority", "Work Type", "Platform", "Campaign Type", "Objective", "Audience", "Offer",
    "Execution Mode", "Messaging State", "Shopify Messaging URL", "Flow Required", "Flow State",
    "Shopify Flow URL", "Automation Trigger", "Automation / Flow Name", "Production Start", "Send Date",
    "Results Review", "Recipients", "Open Rate %", "Click Rate %", "Conversion Rate %", "Revenue",
    "Unsubscribe Rate %", "Primary KPI", "Target KPI", "Preview URL",
]
SELECT_OPTIONS = {
    "Stage": ["Brief", "Copy", "Design", "Build", "QA", "Approval", "Scheduled", "Sent", "Measuring", "Complete"],
    "Priority": ["P0", "P1", "P2", "P3"],
    "Work Type": ["Campaign", "Email", "Task", "Experiment", "Bug"],
    "Platform": ["Shopify Messaging", "Shopify Flow", "Shopify Notifications", "Repository Only", "Needs Decision"],
    "Campaign Type": ["Promotion", "Product Launch", "Welcome", "Lifecycle", "Abandoned Cart", "Browse Abandonment", "Post-Purchase", "Upsell or Cross-sell", "Win-Back", "Reorder", "Consultation", "Re-Engagement", "Newsletter", "Educational", "Transactional", "Announcement"],
    "Objective": ["Acquire", "Convert", "Increase AOV", "Retain", "Reactivate", "Educate", "Build Trust", "Drive Traffic", "Collect Feedback"],
    "Execution Mode": ["One-time Campaign", "Automated / Lifecycle", "Transactional / System", "TBD"],
    "Messaging State": ["Not Started", "Draft", "Configured", "Test Ready", "Verified", "Scheduled", "Active", "Sent", "Blocked", "N/A"],
    "Flow Required": ["Yes", "No", "TBD"],
    "Flow State": ["Not Required", "Not Started", "Draft", "Configured", "Testing", "Verified", "Active", "Paused", "Blocked"],
    "Primary KPI": ["Revenue", "Conversion Rate", "CTR", "Open Rate", "Orders", "Traffic", "Engagement"],
}
DATE_FIELDS = {"Production Start", "Send Date", "Results Review"}
NUMBER_FIELDS = {"Recipients", "Open Rate %", "Click Rate %", "Conversion Rate %", "Revenue", "Unsubscribe Rate %", "Target KPI"}


def load_rows() -> List[Dict[str, str]]:
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_ledger() -> Dict[str, Dict[str, Any]]:
    return {item["email"]: item for item in json.loads(LEDGER_PATH.read_text(encoding="utf-8"))}


def code_from_name(name: str) -> str:
    return name.split(" · ", 1)[0]


def html_for(code: str) -> Path:
    normalized = code.lower().replace("-", "-")
    matches = list((ROOT / "shopify-messaging" / "emails").glob(f"*-{normalized}.html"))
    if len(matches) != 1:
        raise ValueError(f"expected one HTML source for {code}, found {len(matches)}")
    return matches[0]


def snapshot(values: Dict[str, Any]) -> str:
    lines = ["<!-- campaign-os-snapshot:start -->", "## Operations Snapshot", ""]
    for name in FIELD_NAMES:
        value = values.get(name)
        lines.append(f"- **{name}:** {value if value not in (None, '') else 'Not set'}")
    lines.append("<!-- campaign-os-snapshot:end -->")
    return "\n".join(lines)


def issue_body(key: str, values: Dict[str, Any], purpose: str, sources: Iterable[str], authority: str = "") -> str:
    safe_authority = authority.replace("@hairsolutions.co", "[company email omitted]")
    source_lines = "\n".join(f"- `{path}`" for path in sources)
    return f"""<!-- campaign-os-key: {key} -->
{snapshot(values)}

## Purpose

{purpose}

## Authority sources

{source_lines}

<!-- campaign-os-authority:start -->
## Authority content

{safe_authority or 'See the repository-relative authority sources above.'}
<!-- campaign-os-authority:end -->

## Acceptance and QA

- [ ] Creative acceptance criteria are satisfied.
- [ ] Shopify Messaging state is evidenced in this Issue.
- [ ] Shopify Flow evidence is attached when Flow Required is Yes.
- [ ] Consent, audience, links, mobile, accessibility, and rollback checks are complete.
- [ ] No schedule, activation, or send is implied by approval or merge.

## Decisions

## Blockers

## Evidence

## Results

## Learnings
"""


def values_for(**overrides: Any) -> Dict[str, Any]:
    base = {name: None for name in FIELD_NAMES}
    base.update({
        "Stage": "QA", "Priority": "P2", "Work Type": "Email", "Platform": "Repository Only",
        "Campaign Type": "Lifecycle", "Objective": "Retain", "Audience": "Shopify consent-eligible audience; exact criteria require verification",
        "Offer": "None", "Execution Mode": "Automated / Lifecycle", "Messaging State": "Not Started",
        "Flow Required": "No", "Flow State": "Not Required", "Primary KPI": "Revenue",
    })
    base.update(overrides)
    return base


def make_record(key: str, title: str, work_type: str, campaign: Optional[str], parent: Optional[str], values: Dict[str, Any], sources: List[str], authority: str = "", labels: Optional[List[str]] = None, email_code: Optional[str] = None) -> Record:
    source_digests = {}
    for source in sources:
        path = ROOT / source
        if path.is_file():
            source_digests[source] = fingerprint(path.read_bytes().hex())
    digest_inputs = {"key": key, "title": title, "values": values, "sources": source_digests, "authority": authority}
    body = issue_body(key, values, title, sources, authority)
    return Record(
        key, work_type, title, email_code, campaign, parent,
        values["Status"], values["Stage"], values["Priority"], values["Platform"], values["Campaign Type"],
        values["Objective"], values["Audience"], values["Offer"], values["Execution Mode"], values["Messaging State"],
        values["Shopify Messaging URL"], values["Flow Required"], values["Flow State"], values["Shopify Flow URL"],
        values["Automation Trigger"] or "", values["Automation / Flow Name"] or "", values["Production Start"], values["Send Date"],
        values["Results Review"], values["Recipients"], values["Open Rate %"], values["Click Rate %"], values["Conversion Rate %"],
        values["Revenue"], values["Unsubscribe Rate %"], values["Primary KPI"], values["Target KPI"], values["Preview URL"],
        labels or ["email-marketing"], sources, fingerprint(digest_inputs), body,
    )


def build_records() -> List[Record]:
    rows = load_rows()
    ledger = load_ledger()
    issue_numbers = json.loads(ISSUE_REPORT_PATH.read_text(encoding="utf-8"))["issues"]
    preview_authority: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        code = code_from_name(row["Email name"])
        campaign = SERIES_TO_CAMPAIGN[row["Series"]]
        preview_authority[code] = {
            "campaign_key": f"campaign:{campaign}",
            "source_path": str(html_for(code).relative_to(ROOT)),
            "canonical_issue": issue_numbers[f"email:{code}"],
        }
    preview_urls = load_preview_urls(preview_authority)
    records: List[Record] = []
    authority_path = str(CSV_PATH.relative_to(ROOT))
    for code, (name, kind, objective) in CAMPAIGNS.items():
        platform = "Shopify Messaging" if code in {"J2", "W", "N"} else "Shopify Flow"
        values = values_for(**{"Status": "In Progress", "Stage": "QA", "Work Type": "Campaign", "Platform": platform, "Campaign Type": kind, "Objective": objective, "Execution Mode": "Automated / Lifecycle" if code != "N" else "One-time Campaign", "Messaging State": "Not Started", "Flow Required": "No" if code in {"J2", "W", "N"} else "Yes", "Flow State": "Not Required" if code in {"J2", "W", "N"} else "Not Started"})
        records.append(make_record(f"campaign:{code}", f"Campaign — {code} — {name}", "Campaign", code, None, values, [authority_path], labels=["email-marketing", "area:campaign"]))
    for row in rows:
        code = code_from_name(row["Email name"])
        family = re.match(r"[A-Z]+", code).group(0)
        campaign = SERIES_TO_CAMPAIGN[row["Series"]]
        platform, execution, flow_required, campaign_type = FAMILY[family]
        blocked = code in {"RO-4", "NL-16"}
        html = html_for(code)
        html_rel = str(html.relative_to(ROOT))
        values = values_for(**{
            "Status": "Blocked" if blocked else "In Review", "Stage": "Copy" if blocked else "QA", "Priority": "P0" if blocked else "P2",
            "Platform": platform, "Campaign Type": campaign_type, "Objective": CAMPAIGNS[campaign][2], "Offer": row["CTA"] or "None",
            "Execution Mode": execution, "Messaging State": "Not Started", "Flow Required": flow_required,
            "Flow State": "Not Started" if flow_required == "Yes" else "Not Required",
            "Preview URL": preview_urls.get(code),
        })
        sources = [authority_path, html_rel, "shopify-messaging/build-ledger.json"]
        authority = f"**Email:** {row['Email name']}\n\n**Subject:** {row['Subject']}\n\n**Preview text:** {row['Preview Text']}\n\n**CTA:** {row['CTA']}\n\n{row['Body']}"
        short = row["Email name"].split(" · ", 1)[1]
        labels = ["email-marketing", "asset:email", f"area:{campaign.lower()}"] + (["flag:launch-blocker"] if blocked else [])
        records.append(make_record(f"email:{code}", f"Email — {campaign} — {code} — {short}", "Email", campaign, f"campaign:{campaign}", values, sources, authority, labels, code))
    for slug, title, campaign, priority, characteristic in TASKS:
        values = values_for(**{"Status": "Blocked" if priority == "P0" else "Ready", "Stage": "Brief", "Priority": priority, "Work Type": "Task", "Platform": "Repository Only", "Campaign Type": CAMPAIGNS[campaign][1] if campaign else "Lifecycle", "Objective": "Retain", "Execution Mode": "TBD", "Messaging State": "N/A", "Flow Required": "TBD", "Flow State": "Not Started"})
        parent = f"campaign:{campaign}" if campaign else None
        records.append(make_record(f"task:{slug}", f"Task — {title}", "Task", campaign, parent, values, ["CAMPAIGN-PLAN.md"], labels=["email-marketing", characteristic]))
    values = values_for(**{"Status": "Blocked", "Stage": "QA", "Priority": "P0", "Work Type": "Bug", "Platform": "Shopify Messaging", "Campaign Type": "Abandoned Cart", "Objective": "Convert", "Execution Mode": "Automated / Lifecycle", "Messaging State": "Blocked", "Flow Required": "No", "Flow State": "Not Required"})
    records.append(make_record("bug:duplicate-cart-recovery", "Bug — Resolve duplicate abandoned-checkout automation", "Bug", "J2", "campaign:J2", values, ["CAMPAIGN-PLAN.md"], labels=["email-marketing", "risk:automation", "flag:launch-blocker"]))
    if len(records) != 69 or len({record.key for record in records}) != 69:
        raise ValueError("Campaign OS inventory must contain 69 unique records")
    return records


def project_schema() -> Dict[str, Any]:
    fields = []
    for name in FIELD_NAMES:
        if name in SELECT_OPTIONS:
            fields.append({"name": name, "type": "single_select", "options": SELECT_OPTIONS[name]})
        elif name in DATE_FIELDS:
            fields.append({"name": name, "type": "date"})
        elif name in NUMBER_FIELDS:
            fields.append({"name": name, "type": "number"})
        else:
            fields.append({"name": name, "type": "text"})
    return {
        "schema_version": 1, "title": "Email Marketing — Campaign OS", "owner": "vincent-laroche",
        "repository": "vincent-laroche/email-marketing-ops", "private": True,
        "status": ["Inbox", "Ready", "In Progress", "In Review", "Blocked", "Done"], "fields": fields,
        "views": [
            {"name": "01 · Campaign Portfolio", "layout": "TABLE_LAYOUT", "filter": "work-type:Campaign"},
            {"name": "02 · Email Production", "layout": "BOARD_LAYOUT", "filter": "work-type:Email"},
            {"name": "03 · Review & Pull Requests", "layout": "TABLE_LAYOUT", "filter": "status:\"In Review\""},
            {"name": "04 · Launch Calendar", "layout": "ROADMAP_LAYOUT", "filter": "work-type:Campaign,Email"},
            {"name": "05 · Performance", "layout": "TABLE_LAYOUT", "filter": "stage:Sent,Measuring,Complete"},
            {"name": "06 · Messaging & Automation Readiness", "layout": "TABLE_LAYOUT", "filter": "work-type:Email"},
        ],
        "labels": ["email-marketing", "area:campaign", "area:automation", "area:data", "area:analytics", "area:operations", "asset:email", "flag:launch-blocker", "flag:needs-decision", "risk:consent", "risk:automation", "risk:activation"],
        "workflows": ["Auto-add repository items", "Set new items to Inbox", "Set pull requests to In Review", "Set merged pull requests to Done"],
    }


def serialized() -> Dict[Path, str]:
    manifest = {"schema_version": 1, "records": [record.to_dict() for record in build_records()]}
    return {
        OUT / "manifest.json": json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        OUT / "project-schema.json": json.dumps(project_schema(), ensure_ascii=False, indent=2) + "\n",
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build the deterministic Campaign OS manifest")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    outputs = serialized()
    if args.write:
        OUT.mkdir(parents=True, exist_ok=True)
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8")
        return 0
    stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
    if stale:
        print("stale generated files: " + ", ".join(stale), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
