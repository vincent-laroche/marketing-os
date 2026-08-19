# Email Marketing

Hair Solutions Co. email marketing. Current sending platform: **MailerLite**
(HubSpot access was lost 2026-08; Resend is retained for transactional and now lives at
`~/02_dev/mkt-resend`).

## Layout

| Path | What it is |
|---|---|
| `Email Reference File/` | **Source of truth.** Notion export of the email system — see below. |
| `mailerlite/` | Active build + push pipeline for the MailerLite account (2582639). |
| `exports/` | HubSpot CRM exports. PII-bearing, **gitignored**. |
| `export_hubspot.py` | One-shot full HubSpot export (workflows, contacts, deals, orders). |
| `AGENTS.md` | Durable project context and rules. Read first. |
| `PROJECT.md` | Living status log. Read second. |

## `Email Reference File/` — the source of truth

Everything about campaigns, journeys, email structure, module composition, and copy comes
from here. Nothing else in this repo overrides it.

| Path | Contents |
|---|---|
| `emails_master …_all.csv` | The emails database — every email, its journey, timing, and metadata. |
| `modules_master …_all.csv` | The modules database — every module and which emails use it. |
| `emails_modules_hubspot versionr/` | 58 email copy decks (`.md`, incl. 5 `Journey · … Master` docs) **and** 102 complete HubSpot module trios (`module.html` + `fields.json` + `meta.json`), light and dark. |
| `modules_master/` | 80 per-module Notion pages. |
| `Atelier Zero — Resolved HTML Module Previews (102)/` | Rendered HTML preview of every module. |

Email families: `W-` welcome, `PP-` post-purchase, `CR-` cart recovery, `WB-` win-back,
`RO-` reorder, `C-` consultation, `BR-` browse, `NL-01…20` newsletter.

## `mailerlite/`

`ml_content_*.py` hold the per-journey copy (verbatim from the reference file);
`ml_components.py` renders it against the Figma Email Design System v3 tokens;
`build_emails.py` writes `emails/*.html`; `push_campaigns.py` and `configure_campaigns.py`
create and configure drafts via the API. **Nothing in this repo sends or schedules.**

Read `mailerlite/BUILD-LEDGER.md` for what has actually been built and pushed, and
`mailerlite/API-SURFACE.md` for the MailerLite API behaviours that cost time to discover.

## History

The HubSpot-era material — `modules/`, `emails/approved-html/`, `emails/atelier-zero/`,
`emails/second-pass/`, `legacy-csv-snapshots-2026-07-05/`, and the v3 build proofs — was
removed from the working tree on 2026-08-18. It remains in git history at commit `e892e64`
and earlier; recover with `git show e892e64:<path>` or `git checkout e892e64 -- <path>`.
