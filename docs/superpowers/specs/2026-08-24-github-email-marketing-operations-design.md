# Email Marketing — Campaign OS — GitHub Design

**Date:** 2026-08-24

**Status:** Approved by Vincent

**Target repository:** `vincent-laroche/email-marketing-ops`

**Target GitHub Project:** `Email Marketing — Campaign OS`

## 1. Outcome

Build one private GitHub Project that governs the Hair Solutions Co. email programme from campaign
brief through production, review, scheduling, measurement, and learning.

The operating principle is:

**Issues describe work. Pull requests contain changes. Project fields describe state. Labels
describe overlapping characteristics.**

GitHub Issues and pull requests are the durable, connector-readable source of truth. The Project is
a synchronized navigation, planning, and reporting layer. No decision, state, blocker, approval, or
result may exist only in a Project field because Notion and ChatGPT can read repository Issues and
pull requests but cannot reliably read GitHub Projects.

Shopify Messaging and Shopify Flow are the sole marketing execution platforms. MailerLite is legacy
evidence only. Building Campaign OS does not authorize a send, schedule, automation activation,
subscriber change, or Shopify production change.

## 2. Repository continuity

`vincent-laroche/email-marketing-ops` is the existing private canonical repository. Preserve its
complete history.

1. Keep every existing commit reachable.
2. Reconcile the current working tree into small, verified commits on the current branch.
3. Open a pull request from the verified branch into `main`.
4. Merge normally through the pull request after checks pass.
5. Never create an orphan branch, force-push, rewrite `main`, or delete unrelated branches.
6. Verify the merged `origin/main` and local `main` resolve to the same revision.

The separate `vincent-laroche/email-marketing` repository is out of scope and remains unchanged.

## 3. Credential and privacy boundary

- Use `GITHUB_PAT_MASTER_TOKEN` from `/Users/vMac/.env` only as an ephemeral `GH_TOKEN`.
- Never print, persist, commit, or copy the token into an Issue, pull request, report, or Project.
- Keep the repository and Project private.
- Exclude CRM exports, subscriber records, email addresses, browser state, cookies, credentials,
  local agent data, and dependencies.
- Issue bodies, pull requests, and Project fields may contain audience logic and aggregate counts,
  never contact-level PII.

## 4. Hierarchy

Use native parent Issues and sub-issues:

```text
Campaign Issue
├── Email Issue
│   ├── independent Task or Bug when justified
│   └── linked pull request
├── Email Issue
│   └── linked pull request
└── Experiment Issue when a real test exists
```

Initial campaign parents are:

- J1 Post-Purchase;
- J2 Cart Recovery and Browse Abandonment;
- J3 Win-Back;
- J4 Reorder;
- J5 Consultation;
- W Welcome;
- N Newsletter.

All 53 current emails are native sub-issues of one of these seven Campaign Issues.

## 5. Work types

The Project lives under Vincent's personal GitHub account, so use a custom **Work Type** field
rather than organization-only custom Issue Types.

| Work Type | Contract |
|---|---|
| Campaign | Parent initiative containing objective, audience, strategy, sequence, schedule, KPIs, approvals, results, and learnings |
| Email | One actual outbound email with complete operational context and a parent Campaign |
| Task | Independently owned supporting work that deserves tracking beyond a checklist |
| Experiment | A hypothesis, control, variant, metrics, result, conclusion, and decision |
| Bug | A confirmed defect requiring correction |

Do not create an Issue for every small checkbox. Small production steps stay inside the Email Issue.
Do not invent an Experiment until a real hypothesis and measurement plan exist.

The initial manifest contains 69 Issues:

- 7 Campaign Issues;
- 53 Email Issues;
- 8 Task Issues for the two source gaps plus consent, Flow rules, dynamic data, measurement,
  Campaign OS migration, and launch governance;
- 1 Bug Issue for the duplicate abandoned-checkout automation;
- 0 invented Experiment Issues.

Pull requests are additional Project items and do not change the Issue count.

## 6. Naming conventions

Use predictable titles:

```text
Campaign — J2 — Cart Recovery and Browse Abandonment
Email — J2 — CR-1 — Your Cart's Still Here
Task — RO-4 — Supply Text Customer Snapshot authority copy
Experiment — N — Subject line benefit versus product framing
Bug — J2 — Duplicate abandoned-checkout automation
```

Future email branches use:

```text
email/<campaign>/<email-code>-<short-name>
```

The existing migration branch keeps its current name so history is not rewritten.

## 7. Issue source-of-truth contract

An Issue holds durable scope, authority, state, requirements, blockers, decisions, acceptance
criteria, evidence, results, and learnings. Issue comments record dated decisions and verification
events that connectors must be able to read.

Every Issue body includes a generated **Operations Snapshot** bounded by explicit HTML comments.
The snapshot mirrors every Project field. Synchronization may replace only generated sections and
must preserve human-written decisions, blockers, evidence, results, learnings, and comments.

Every Email Issue contains:

- purpose and role in Campaign;
- audience and consent basis;
- trigger or intended Send Date;
- subject, preheader, primary CTA, secondary CTA, and offer;
- approved copy copied verbatim from the Email Reference File in a collapsible section;
- source links and SHA-256 source fingerprint;
- message hierarchy, content requirements, design requirements, assets, and personalization;
- tracking requirements and destination links;
- content, desktop, mobile, client, accessibility, links, offer, tracking, audience, sender,
  subject, preheader, and test-email acceptance checks;
- linked pull requests;
- post-send results and learnings.

The Email Reference File remains upstream copy and campaign authority. Issue copy is a synchronized
review surface, not an independent authoring source.

## 8. Pull request contract

A marketing pull request is a reviewable proposed version of a durable email deliverable. It may
contain copy, HTML, design specifications, screenshots, asset references, implementation notes,
platform links, and QA evidence.

Every implementation branch links at least one Issue. Pull request bodies contain:

- summary;
- closing Issue reference only when all acceptance criteria are satisfied;
- parent Campaign;
- deliverable type;
- preview or screenshot link;
- exact changes;
- desktop, mobile, Gmail, Apple Mail, link, tracking, personalization, offer, subject, and
  preheader QA;
- content, design, technical, and scheduling-approval checks;
- authority sources, approved-copy impact, consent impact, activation impact, risks, and rollback.

Merging accepts the deliverable into repository history. **Merge does not mean send.** Scheduling,
sending, measuring, and completion remain separate Issue Stage transitions.

## 9. Project fields

Enable native Title, Assignees, Labels, Repository, Milestone, Parent Issue, Sub-issue Progress,
Linked Pull Requests, and Reviewers fields. Use the built-in Status field plus 19 custom fields.

### 9.1 Workflow

| Field | Type | Values |
|---|---|---|
| Status | Built-in single select | Inbox, Ready, In Progress, In Review, Blocked, Done |
| Stage | Single select | Brief, Copy, Design, Build, QA, Approval, Scheduled, Sent, Measuring, Complete |
| Priority | Single select | P0, P1, P2, P3 |
| Work Type | Single select | Campaign, Email, Task, Experiment, Bug |

Status is the condition of work. Stage is its position in the email lifecycle. Do not combine them.
Most work starts at P2. P0 is reserved for send-blocking or serious customer/revenue risk.

### 9.2 Marketing classification

| Field | Type | Values or contract |
|---|---|---|
| Platform | Single select | Shopify Messaging, Shopify Flow, Shopify Notifications, Repository Only, Needs Decision |
| Campaign Type | Single select | Promotion, Product Launch, Welcome, Lifecycle, Abandoned Cart, Browse Abandonment, Post-Purchase, Upsell or Cross-sell, Win-Back, Reorder, Consultation, Re-Engagement, Newsletter, Educational, Transactional, Announcement |
| Objective | Single select | Acquire, Convert, Increase AOV, Retain, Reactivate, Educate, Build Trust, Drive Traffic, Collect Feedback |
| Audience | Text | Connector-readable audience description without contact PII |
| Offer | Text | Short offer description; full terms remain in the Issue |

MailerLite is intentionally absent from Platform because it is not an active execution platform.

### 9.3 Dates

| Field | Type | Contract |
|---|---|---|
| Production Start | Date | Real date when work should begin; blank until approved |
| Send Date | Date | Intended calendar send date; blank for undated triggers |
| Results Review | Date | Real planned review date; blank until the send plan exists |

Relative lifecycle timing remains in the Issue and must not be converted into invented calendar
dates.

### 9.4 Performance

| Field | Type | Contract |
|---|---|---|
| Recipients | Number | Verified successfully targeted or sent count |
| Open Rate % | Number | Verified Shopify open rate |
| Click Rate % | Number | Verified Shopify click-through rate |
| Conversion Rate % | Number | Verified attributed conversion rate |
| Revenue | Number | Verified attributed revenue |
| Unsubscribe Rate % | Number | Verified unsubscribe rate |
| Primary KPI | Single select | Revenue, Conversion Rate, CTR, Open Rate, Orders, Traffic, Engagement |
| Target KPI | Number | Optional numeric target with its unit defined in the Issue |

Performance values start blank and are written only from verified Shopify evidence.

## 10. Labels

Do not duplicate Status, Stage, Priority, Work Type, or Platform with labels. Use labels only for
overlapping characteristics.

### Work area

`area:copy`, `area:design`, `area:html`, `area:automation`, `area:segmentation`, `area:qa`,
`area:analytics`, `area:deliverability`

### Assets

`asset:image`, `asset:product`, `asset:template`, `asset:component`

### Flags

`flag:launch-blocker`, `flag:needs-decision`, `flag:needs-approval`, `flag:reusable`,
`flag:customer-facing`

### Risks

`risk:claim`, `risk:offer`, `risk:deliverability`, `risk:tracking`, `risk:technical`

Use one repository routing label, `email-marketing`, for Project auto-add. The Operations Snapshot
inside each Issue makes Work Type and state connector-readable without duplicating them as labels.

## 11. Five Project views

Create exactly these views in this order:

### `01 · Campaign Portfolio`

- Layout: Table
- Filter: Work Type = Campaign
- Columns: Title, Status, Stage, Priority, Campaign Type, Objective, Platform, Production Start,
  Send Date, Assignees, Sub-issue Progress, Revenue
- Sort: Send Date ascending, then Priority ascending

### `02 · Email Production`

- Layout: Board
- Filter: Work Type = Email and Status is not Done
- Column field: Stage
- Columns: Brief, Copy, Design, Build, QA, Approval, Scheduled, Sent, Measuring, Complete
- Card fields: Priority, Assignees, Send Date, Platform, Parent Issue, Linked Pull Requests

### `03 · Review & Pull Requests`

- Layout: Table
- Filter: open pull requests
- Columns: Title, Status, Repository, Assignees, Reviewers, Labels, Updated

### `04 · Launch Calendar`

- Layout: Roadmap
- Start date: Production Start
- Target date: Send Date
- Default zoom: Month
- Group: Campaign Type
- Items without real dates remain blank

### `05 · Performance`

- Layout: Table
- Filter: Work Type = Email and Stage is Sent, Measuring, or Complete
- Columns: Title, Parent Issue, Send Date, Campaign Type, Objective, Audience, Recipients, Open Rate
  %, Click Rate %, Conversion Rate %, Revenue, Unsubscribe Rate %, Primary KPI
- Sort: Send Date descending

QA, consent, risks, and blockers remain fully readable in Issue bodies and labels; they do not
create extra saved views.

## 12. Initial-state mapping

Populate from current repository evidence:

- 53 Email artifacts exist.
- 51 are structurally green and start Status `In Review`, Stage `QA`.
- RO-4 and NL-16 start Status `Blocked`, Stage `Copy`, Priority `P0`, and
  `flag:launch-blocker` because required authority copy is missing.
- Other unresolved dynamic or reality-dependent placeholders remain explicit in Issue acceptance
  criteria and use `flag:needs-decision` only when a real Vincent decision is required.
- J2, W, and N use Shopify Messaging; J1, J3, J4, and J5 use Shopify Flow.
- Campaign parents start conservatively at Status `In Progress` and their evidence-backed Stage.
- Dates, recipients, performance, scheduling, sending, and completion fields start blank unless a
  current repository source proves a value.
- No email starts Scheduled, Sent, Measuring, Complete, or activation-approved.

## 13. Built-in automation

Configure only obvious housekeeping:

1. Auto-add Issues and pull requests from `vincent-laroche/email-marketing-ops` carrying the
   `email-marketing` label.
2. Set newly added items to Status `Inbox` when no explicit synchronized state exists.
3. Set closed Issues to Status `Done`.
4. Set merged pull requests to Status `Done`.

Do not automate Approval to Scheduled, scheduling, sending, Shopify activation, audience changes,
or performance values. Do not auto-archive during initial migration.

## 14. Sanitized repository structure

Keep current authority, Shopify source, transactional MailerSend source, proof bank, tools, scripts,
documentation, and bounded evidence. Move the MailerLite implementation, MailerLite-specific block
library, and helpers under `archive/mailerlite-legacy/` with warning banners.

Before the migration pull request:

- restore CR-1 through CR-4 to the Email Reference File palette while preserving Shopify Liquid
  and content fixes;
- retain and verify Phase 4 Proof Bank and Phase 5 segment/tag preparation;
- include the Figma email-block plugin as source only under `tools/`;
- retain only final durable rendering evidence under `docs/evidence/`;
- remove obsolete MailerLite editor screenshots from the active tree while preserving them in Git
  history;
- exclude CRM exports, browser state, agent worktrees, dependencies, generated plugin bundles,
  caches, ZIP duplicates, and intermediate proof renders.

## 15. Migration mechanics

Use deterministic, inspectable, idempotent scripts:

1. Classify and reconcile the dirty working tree into verified commits.
2. Compile a versioned manifest from the Email Reference File, build ledger, HTML, and approved
   schema.
3. Create or update 69 Issues by a hidden stable key; abort on duplicates.
4. Link 53 Email sub-issues to seven Campaign parents.
5. Push the current branch and open a draft migration pull request linked to the Campaign OS Task.
6. Create the private Project, its 19 custom fields, labels, automations, and five views.
7. Add all 69 Issues and the migration pull request to the Project.
8. Mirror Issue Operations Snapshot values into Project fields and fail on drift.
9. Complete verification, mark the pull request ready, obtain passing checks, and merge normally.
10. Re-fetch repository, Issue, pull request, parent/sub-issue, Project, field, automation, and view
   state and publish the final audit as a connector-readable Issue comment.

Every state-changing command runs first as dry-run, once with `--apply`, and again as dry-run to
prove zero-action idempotence.

## 16. Acceptance criteria

The migration is complete only when:

- repository and Project are private;
- complete existing history remains reachable and no force-push occurred;
- the migration reaches `main` through a linked, reviewed pull request;
- local `main` and `origin/main` resolve to the same revision;
- the separate `vincent-laroche/email-marketing` repository is unchanged;
- exactly 69 canonical Issues exist once each with complete Operations Snapshots;
- every Email is a native sub-issue of the correct Campaign;
- the migration pull request is a Project item and appears in the PR view while open;
- every Project field matches its Issue snapshot;
- the built-in Status field and exactly 19 custom fields exist with approved options;
- exactly five views exist with approved names, order, layouts, filters, fields, grouping, and sort;
- approved auto-add and housekeeping workflows are enabled without marketing-decision automation;
- no contact PII, secret, browser state, dependency tree, cache, or agent worktree is tracked;
- no email is incorrectly marked Scheduled, Sent, Measuring, Complete, or activation-approved;
- final read-back is recorded in Issues or pull requests, not only in a Project-only artifact.

## 17. Non-goals

This work does not:

- send, schedule, publish, or activate email;
- modify Shopify audiences, segments, automations, products, customers, or campaign configuration;
- write to MailerLite, MailerSend, HubSpot, DNS, or Cloudflare;
- invent missing copy, dates, consent, performance, proof, QA, experiments, or approvals;
- create an Issue for every small checklist item;
- delete or rewrite canonical repository history;
- change the separate `vincent-laroche/email-marketing` repository;
- make the Project a source of truth that connectors cannot read.
