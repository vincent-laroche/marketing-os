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

**Brand colours for email come from the modules in `Email Reference File/`, not from
`brand-design-system/`.** Set 2026-08-19 by Vincent. The rendered module previews in
`Atelier Zero — Resolved HTML Module Previews (102)/` ARE the correct brand colours:
`#F6EFD9` page · `#EDE3CC` card · `#151411` ink · `#25221D` body · `#C7BFAC` rule ·
`#EA6452` coral. Do **not** consult, cite, or reconcile against
`brand-design-system/specs/ATELIER_ZERO_RULEBOOK_V1.md` or `specs/PLATFORM_EMAIL.md` —
Vincent has explicitly ruled both out of scope. §4 below does not apply to email colour.

**Exception — the page background is transparent, decided 2026-08-19 by Vincent.** The
module palette above is correct for *cards and insets only*. `<body>` and the outer wrapper
table are `background-color:transparent` on every email; `#F6EFD9` is **not** painted as a
page background, and neither is any other value. The client's own background shows through
the gutter, and it will go dark in dark-mode clients — that is intended, not a bug to patch.
Reintroducing a page background in a new or rebuilt template is a regression.

Consequence, recorded so it is not rediscovered: `mailerlite/ml_components.py` renders a
*different* palette (`#F7F1DE / #EFE7D2 / #ED6F5C / #15140F / #DDD2B6`), so the 27 emails
built from it do not match the modules. Retokenising it to the module palette above is
open work, not a decision to revisit.

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

## 2. No marketing send path

No script in this repo sends or schedules **marketing** email. Campaigns are created and
configured as **drafts** only. Sending and scheduling marketing are manual, deliberate,
out-of-band acts by Vincent. This is a standing safety rule, not a current limitation — do
not add a marketing send path.

**Narrow, deliberate exception — transactional only.** `mailersend/send_service_email.py`
does send, because order confirmations and shipping notices are service mail a customer is
waiting on, not campaigns. It is bounded by `ALLOWED_RECIPIENTS`, a module constant checked
immediately before the request is issued; no flag, environment variable or payload field can
extend it, and any other address aborts before a socket opens. Widening that allowlist is a
deliberate decision, never a side effect. Everything else in this repo remains send-free.

Related standing hazard: MailerLite treats a campaign with **no group/segment** as "all
active subscribers", not "no recipients". Every parked draft must be assigned to the
safeguard group `⛔ DO NOT SEND — Lifecycle Drafts (parked)` (id `196158361233786451`).

## 3. Platform roles (current)

**Shopify Messaging — the sending platform for the 53-email programme.** Decided
2026-08-19 by Vincent, superseding the MailerLite-as-sender note below for this programme.
The 53 emails in `Email Reference File/` (J1–J5, W, N) build and send from Shopify Messaging
and Shopify Flow. This does **not** retract the consent lesson recorded under Shopify below —
it relocates it: consent state must be verified *inside Shopify*, per channel, before any
journey is activated. Hard blocker as of this date: no Shopify DKIM selector is published and
DMARC is `p=quarantine`, so Shopify mail from @hairsolutions.co is quarantined until the
store-specific sender-authentication CNAMEs are added. See `CAMPAIGN-PLAN.md` Phase 0.

**MailerLite — the sending platform.** Account 2582639. Live work lives in `mailerlite/`.
`ml_content_*.py` hold per-journey copy (verbatim from the reference file), `ml_components.py`
renders it against Figma Email Design System v3 tokens, `build_emails.py` writes
`mailerlite/emails/*.html`, `push_campaigns.py` / `configure_campaigns.py` create and
configure drafts. `BUILD-LEDGER.md` records what has actually been built and pushed;
`API-SURFACE.md` records API behaviours that cost real time to discover — read both before
touching the account.

**MailerSend — transactional only.** Replaced Resend 2026-08-19 (Vincent), consolidating
onto MailerLite's sibling platform. Lives in `mailersend/`: `send_service_email.py` plus six
templates. Uses `MAILERSEND_API_TOKEN`. Every accepted send is recorded in
`.send-ledger.json` keyed by (type, order number, recipient, content fingerprint), so
re-running is a no-op unless `--force`.

The three `SVC-*` templates (order confirmed, specification review, reorder received) are
**build output** of `build_service_emails.py`, drawn from the Figma Email Design System
canvas `225:357`. Edit the builder, never the HTML; `--check` fails when they have drifted.
`mailersend/DESIGN-NOTES.md` records every place those templates depart from the Figma
frames and why — read it before "correcting" one back. The older `PP-1` / `PP-4` pair is
hand-written and covers the same order-confirmation ground as `SVC-1`; which one is
canonical is Vincent's call, not a cleanup.

**Resend — decommissioned 2026-08-19.** Superseded by MailerSend. `~/02_dev/mkt-resend`
(its own git repo and remote) **stays on disk regardless**: `mailerlite/import_prospects.py`
reads its prospect CSV. Override that location with `PROSPECT_IMPORT_DIR`. Do not delete
that repo without first rehoming the CSV.

**Shopify — catalog only, never contacts.** Set 2026-08-19 by Vincent after the integration
synced 631 subscribers into the *marketing* group while ignoring Shopify's own consent
state (95 had none). **Contacts never come from Shopify.** The audience is built from the
HubSpot export by `select_audience.py`. The shop connection is retained only so product data
can populate e-commerce blocks; its subscriber sync is pointed at
`⛔ Shopify sync — quarantine` (id `196200001017218918`) with resubscribe and popups off, so
anything it imports lands somewhere inert. Never point it at a sending group.

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

## 5. No wallpaper behind an email

**Hard rule, set 2026-08-19 by Vincent.** An email paints no page background. `<body>` and
the outer wrapper table are `background-color:transparent`, so the client's own background
shows through the gutter between the card column and the window edge. Colour belongs to
cards and to insets inside cards — never to the surface behind them.

This is not a palette question and does not reopen one: no value is correct there, including
Bone `#F7F1DE`, Paper `#EFE7D2` and `#F6EFD9`. Those remain correct as *card* surfaces.

Applies to every email in this repo, both platforms. Enforced at the source, not per file:
`mailerlite/ml_components.py` (`PAGE_BG`) and `mailersend/build_service_emails.py` (`PAGE`).
The two hand-written MailerSend templates, `PP-1` and `PP-4`, carry it inline. A rebuilt or
new template that reintroduces a page background is a regression.

Consequence to expect: on a dark-mode client the gutter goes dark while the cards stay light.
That is the intended behaviour, not a bug to patch with a background.

## 6. PII

`exports/` holds HubSpot CRM exports (contacts, deals, orders, companies). It is
**gitignored and must stay that way.** Never commit it, never paste its contents into a
conversation, never publish it. Secrets come from `~/.env` via
`set -a && source ~/.env && set +a` — never hardcode a token.

## 7. Conventions

- Python 3, stdlib-only (`urllib.request`, `csv`, `json`) — no dependency stack here.
- Scripts are idempotent and support `--dry-run` where they touch a live account.
- `trash` over `rm`.
- Read before editing; minimal diffs; flag breaking changes before making them.

## 8. GitHub is the operating system — nothing is tracked in prose

**Hard rule, set 2026-08-24 by Vincent.** The Campaign OS is live: the private
`vincent-laroche/email-marketing-ops` repository and GitHub Project #4. Issues and pull
requests are **canonical**, because external connectors read them. Project #4 mirrors state.

**A finding that is not in an Issue or a pull request does not exist.** This is the whole
rule, and it binds every agent and every session:

- Never end a turn with "I found X" / "someone should do Y next" / "flagging Z for later"
  as prose. Open an Issue, or comment on the canonical Issue, or put it in the pull request
  that carries the change. Then cite the number.
- Every claim in a session report must carry its `#number`. A finding without one is
  incomplete work, not a finding.
- Discovered a defect while doing something else? File it before you report it. Out of scope
  is a reason to open an Issue, never a reason to leave it in chat.
- Work on an Email or Campaign belongs on that canonical Issue — use its `## Blockers`,
  `## Evidence`, `## Decisions`, `## Results` and `## Learnings` sections. The synchronizers
  preserve human-maintained sections; generated sections are rewritten, so never hand-edit
  those.
- A new surface with no Issue (as the native Shopify notification templates were) gets a Task
  Issue before work starts, not after.

`PROJECT.md` remains the chronological session log and it is **not a backlog**. Every open
item it lists must name the Issue that owns it. If an item has no Issue, the fix is to open
one, not to write a better paragraph. Anything tracked only in `PROJECT.md`, `README.md`, a
plan document, or a chat message is by definition untracked.

**Issue and Project mechanics.** Two kinds of Issue exist, and they must not be confused:

- **Compiled Issues** — the 69 canonical records (7 Campaigns, 53 Emails, 8 Tasks, 1 Bug) built by
  `tools/github_campaign_os/` from the Email Reference File and the build ledger. Each carries a
  hidden `<!-- campaign-os-key: … -->`. Never hand-create one and never hand-edit its generated
  snapshot or authority blocks; the synchronizers rewrite those and preserve everything else.
- **Filed Issues** — new Tasks, Bugs, and Experiments discovered while working. File these through
  `.github/ISSUE_TEMPLATE/`. They must **not** carry a `campaign-os-key`, because that marker is
  what makes `verify_issues` count an Issue as canonical; adding one to a hand-written Issue breaks
  the 69-record invariant.

Regenerate the manifest with `python3 -m tools.github_campaign_os.build_manifest --write` and never
hand-edit `github-campaign-os/*.json` — a stale generated file is a defect and the test suite fails
on it. Generate from a **clean** worktree: the manifest fingerprints source bytes, so generating
while another worktree is dirty produces fingerprints that match no commit.

Canonical email codes come from the manifest, never from a filename. `13-pp-7b.html` is `PP-7b`,
not `PP-7B`; uppercasing a filename silently breaks the Issue lookup for that one email.

Credentials are ephemeral. There is no GitHub token in `~/.env`; the working credential is the
`gh` CLI keyring (`gh auth token`). Never print, persist, or commit it.

**Merge is not activation.** Closing an Issue or merging a pull request accepts a repository
deliverable only. It never configures Shopify Messaging, creates or enables a Flow, changes an
audience or consent state, schedules, activates, or sends. Creative Stage, Messaging State, and
Flow State are deliberately independent and must never be inferred from one another.
