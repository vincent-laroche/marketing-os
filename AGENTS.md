# Email Marketing — Agent Instructions

> Durable context and hard rules for this project. Read this first, then `PROJECT.md` for
> current status. If something will still be true next month it belongs here; "what happened
> this session / what's next" belongs in `PROJECT.md`.

Location: `~/07_design/email_marketing`. Follows the standard project convention —
`AGENTS.md` (rules) + `CLAUDE.md` (`@AGENTS.md` pointer) + `PROJECT.md` (living status log).
Update `PROJECT.md` at the end of every session; only touch this file when a rule changes.

## 1. `Email Reference File/` is the source of truth

**Hard rule, set 2026-08-18 by Vincent.** `Email Reference File/` is the absolute source of
truth for email marketing campaigns, journeys, email structure and composition, copy, and
which modules appear in each email. It is a Notion export of the email system.

- Never author, "improve", or invent campaign structure or copy that contradicts it.
- Copy is used **verbatim** from `emails_modules_hubspot versionr/*.md`.
- Module composition comes from `modules_master …_all.csv` and the per-module pages.
- If it looks stale, ask Vincent to re-export from Notion — do not patch around it.
- Anything anywhere else in this repo that disagrees with it is obsolete by definition.

Contents:

| Path | Contents |
|---|---|
| `emails_master …_all.csv` | Emails database — every email, journey, timing, metadata. |
| `modules_master …_all.csv` | Modules database — every module and which emails use it. |
| `emails_modules_hubspot versionr/` | 58 email copy decks (`.md`, incl. 5 `Journey · … Master`) + 102 complete HubSpot module trios (`module.html` + `fields.json` + `meta.json`), light and dark. |
| `modules_master/` | 80 per-module Notion pages. |
| `Atelier Zero — Resolved HTML Module Previews (102)/` | Rendered HTML preview of every module. |

Email families: `W-` welcome, `PP-` post-purchase, `CR-` cart recovery, `WB-` win-back,
`RO-` reorder, `C-` consultation, `BR-` browse, `NL-01…20` newsletter.

## 2. Nothing here sends

No script in this repo sends or schedules email. Campaigns are created and configured as
**drafts** only. Sending and scheduling are manual, deliberate, out-of-band acts by Vincent.
This is a standing safety rule, not a current limitation — do not add a send path.

Related standing hazard: MailerLite treats a campaign with **no group/segment** as "all
active subscribers", not "no recipients". Every parked draft must be assigned to the
safeguard group `⛔ DO NOT SEND — Lifecycle Drafts (parked)` (id `196158361233786451`).

## 3. Platform roles (current)

**MailerLite — the sending platform.** Account 2582639. Live work lives in `mailerlite/`.
`ml_content_*.py` hold per-journey copy (verbatim from the reference file), `ml_components.py`
renders it against Figma Email Design System v3 tokens, `build_emails.py` writes
`mailerlite/emails/*.html`, `push_campaigns.py` / `configure_campaigns.py` create and
configure drafts. `BUILD-LEDGER.md` records what has actually been built and pushed;
`API-SURFACE.md` records API behaviours that cost real time to discover — read both before
touching the account.

**Resend — transactional only.** Lives at `~/02_dev/mkt-resend` (its own git repo, own
GitHub remote). Moved out of this project 2026-08-18. `mailerlite/import_prospects.py`
still reads its prospect CSV; override the location with `PROSPECT_IMPORT_DIR`.

**HubSpot — historical.** Account 50966981. **Access was lost in 2026-08** — the OAuth
connector token is expired and only `HUBSPOT_SERVICE_KEY` works, which is what
`export_hubspot.py` uses. Earlier notes in this file claiming a write-capable HubSpot
connector are obsolete. The entire HubSpot module/email build (`modules/`, `emails/`) was
removed from the working tree 2026-08-18; it remains in git history at `e892e64` and
earlier. The 102 module trios that survived that migration live in the reference file.

**Figma — review surface.** Where Vincent looks at a complete HTML email before it ships.
Not where email HTML is authored, stored, or sent from. The v3 design tokens originate here.

**Notion — the database layer.** Holds campaign metadata, copy drafts, and performance
stats. `Email Reference File/` is an export *of* Notion, which is why Notion wins upstream.

## 4. Brand

**Always resolve the brand authority at use time — never trust a palette hardcoded in a doc.**
`brand-design-system/` exists in two identical copies (`~/07_design` and `~/08_brand`); check
the real directory rather than any cached value. This has gone stale repeatedly.

## 5. PII

`exports/` holds HubSpot CRM exports (contacts, deals, orders, companies). It is
**gitignored and must stay that way.** Never commit it, never paste its contents into a
conversation, never publish it. Secrets come from `~/.env` via
`set -a && source ~/.env && set +a` — never hardcode a token.

## 6. Conventions

- Python 3, stdlib-only (`urllib.request`, `csv`, `json`) — no dependency stack here.
- Scripts are idempotent and support `--dry-run` where they touch a live account.
- `trash` over `rm`.
- Read before editing; minimal diffs; flag breaking changes before making them.
