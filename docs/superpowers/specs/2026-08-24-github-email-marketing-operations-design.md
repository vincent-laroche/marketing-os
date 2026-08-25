# Email Marketing — Campaign OS — GitHub Design

**Date:** 2026-08-24

**Status:** Campaign OS approved; Email Preview Gallery architecture approved and written extension awaiting Vincent's review

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
Linked Pull Requests, and Reviewers fields. Use the built-in Status field plus 20 custom fields.

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

### 9.5 Preview publication

| Field | Type | Contract |
|---|---|---|
| Preview URL | Text | Public GitHub Pages URL after verified publication; blank for private, failed, unpublished, or expired review output |

The Operations Snapshot in every Email Issue includes Preview URL. The Project synchronizer may
populate it only from the verified public-publication ledger after read-back succeeds. A pull
request artifact URL, workflow run URL, intended URL, or failed deployment URL is never written to
this field.

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

### Insights after real performance data exists

Project Insights may later chart Emails by Stage, Campaigns by Status, revenue by Campaign Type or
Objective, campaigns shipped by month, Emails by Platform, and Issues by work area. Insights are an
analytical layer behind the five views, not a sixth primary view. Do not create performance charts
from blank or invented metrics during initial migration.

## 12. Email Preview Gallery extension

The Email Preview Gallery is a sixth Campaign OS interface surface hosted by GitHub Pages at
`email-preview.hairsolutions.co`. It is not a sixth native Project view: the five saved Project
views remain exactly as defined above. The Project description, repository README, Email Issues,
and the Preview URL field link to the gallery.

The default GitHub Pages URL is a deployment fallback only. The custom domain is the intended
public address, but Pages enablement, custom-domain configuration, and Cloudflare DNS remain
separately approval-gated external changes.

### 12.1 Chosen architecture

Use a static fixture compiler and GitHub Actions:

```text
Shopify email source at an exact commit
        ↓
Strict Liquid parser + fictional fixture registry
        ↓
Safety validation and unresolved-Liquid gate
        ↓
Rendered HTML + desktop PNG + mobile PNG + provenance manifest
        ↓
┌───────────────────────────┬────────────────────────────────┐
│ Draft or review revision  │ Explicit public publication    │
│ Private Actions artifact  │ GitHub Pages deployment        │
└───────────────────────────┴────────────────────────────────┘
```

The isolated preview tool may use a locked TypeScript/Node toolchain under
`tools/email-preview/` because strict Shopify-Liquid parsing and deterministic browser screenshots
require capabilities beyond the repository's normal standard-library Python scripts. Pin direct
dependencies and the browser version in the lockfile. Generated output, browser binaries, and
dependency trees remain untracked.

### 12.2 Fail-closed rendering contract

The compiler parses Shopify Liquid; it never performs regex-only substitution. It maintains an
explicit allowlist of supported variables, filters, tags, comparisons, loops, and limits. Initial
repository evidence requires support for `if`, `for`, `limit`, comparisons, `blank`, nested object
access, and the `default` filter.

For each requested email, rendering fails before output promotion when any of these is true:

- an unknown Liquid variable, filter, tag, comparison, or object path is encountered;
- a Liquid output or tag delimiter remains after rendering;
- a content-authority placeholder written inside Liquid-shaped delimiters remains unresolved;
- an expected fixture value has the wrong type or violates its schema;
- a customer-specific URL, checkout URL, unsubscribe token, tracking token, contact identifier, or
  contact-level PII survives sanitization;
- an active form, remote script, tracking pixel, unsafe protocol, or non-allowlisted network host
  remains;
- HTML validation, output-count validation, screenshot generation, or provenance validation fails.

The current 53 source emails all contain Liquid-shaped expressions, and many include
reality-dependent content instructions that are not executable Shopify Liquid. The renderer must
distinguish supported runtime Liquid from unresolved authority content and block both when a safe,
complete preview cannot be produced. It never publishes a partial email, silently drops an unknown
expression, substitutes an empty string for unsupported content, or reuses a stale successful
output for a failed revision.

A public build is atomic. If any public-selected email fails, no new Pages artifact is deployed and
the previous verified public site remains unchanged. A private review build emits no preview for a
failed email and reports the exact safe error category in the workflow summary.

### 12.3 Fictional fixture registry

Fixtures are small, reusable, repository-tracked, schema-validated fictional records. They never
derive from Shopify, HubSpot, MailerLite, exports, screenshots, logs, or real customer events.

Model fixtures as composable base personas plus state overlays:

- `normal-customer`: fictional name and ordinary safe defaults;
- `missing-first-name`: absent first name to exercise fallback behavior;
- `product-heavy`: five fictional line items plus a remaining-item count;
- future bounded states such as empty optional values, consultation quote, shipped order, reorder,
  or win-back timing.

Each Email metadata record chooses one primary persona/state combination for the required three
outputs. The schema permits additional named combinations later without changing the primary URL
contract. Fixture identifiers, values, and expected branches are included in provenance. Product
names, order numbers, codes, dates, prices, tracking values, and URLs are visibly fictional and
cannot match real customer records.

Customer-specific destinations are replaced with inert preview URLs. General approved
Hair Solutions Co. content links may remain clickable only after allowlist validation. Unsubscribe,
preference, checkout, account, tracking, and personalized destinations never remain live.

### 12.4 Three required outputs per email

Every successful primary preview produces exactly:

1. rendered interactive HTML;
2. full-page desktop screenshot at a fixed 1440-pixel viewport width;
3. full-page mobile screenshot at a fixed 390-pixel viewport width.

These are the three user-facing preview outputs. `provenance.json` is mandatory machine-readable
metadata beside them, not a fourth preview representation.

The browser height is fixed for viewport setup and screenshots use full-page capture. Device scale,
browser revision, fonts, network policy, animation policy, and reduced-motion setting are pinned so
the same source revision is reproducible. The gallery does not claim that browser screenshots
replace Gmail, Outlook, Apple Mail, or Shopify test-send QA.

Generated output uses deterministic paths by Campaign, Email code, fixture identifier, and full
source commit SHA. A stable canonical Email URL resolves to the latest verified public publication;
revision paths and the publication ledger retain the exact source identity.

### 12.5 Provenance and reproducibility

Every output directory includes `provenance.json` with:

- full source commit SHA and repository;
- source HTML path and SHA-256 digest;
- Email code and Campaign key;
- related Email Issue number and URL;
- related pull request number and URL;
- workflow run ID, attempt, and workflow-file revision;
- compiler version and dependency-lock digest;
- fixture persona and state identifiers plus fixture digest;
- render timestamp and output SHA-256 digests;
- publication visibility and canonical public URL when applicable.

Rendered HTML embeds the same identifiers as non-visible document metadata. Screenshot filenames
include the full source SHA and are bound to their digests in `provenance.json`; screenshots are not
watermarked or visually altered. The gallery detail page, which is separate from the rendered Email
document and its screenshots, displays provenance and links to the exact commit, pull request, and
Email Issue.

Private GitHub Actions artifacts are temporary review transport, not permanent storage or project
history. Their URLs never populate Preview URL. A PR comment records the source SHA, safe render
summary, artifact expiry expectation, and the exact workflow-dispatch command needed to reproduce
the artifact from that source revision. Expiration is expected and never treated as data loss.

Maintain a repository-tracked, append-only public-publication ledger containing Email code, source
SHA, Issue, PR, fixture identifiers, output digests, publication time, and canonical URL. It contains
no HTML, screenshots, PII, token, or secret. Any published revision can be reproduced by checking
out its source SHA and rerunning the pinned compiler.

### 12.6 Private review workflow

Pull requests that change an Email source, fixture, compiler, gallery code, or preview metadata run
the review workflow. It renders affected Emails with their primary fixture, performs fail-closed
validation, captures desktop and mobile screenshots, uploads the three outputs and provenance as a
private Actions artifact, and posts or updates one bounded PR comment.

Review artifacts may expire under GitHub retention policy. Issues and PRs retain only durable source
links, the source SHA, validation result, and reproduction instructions. Draft and review output is
never copied into Pages and never receives a public Preview URL.

### 12.7 Public publication workflow

Public publication requires all of these conditions:

- the selected Email metadata at the exact source SHA contains `preview_public: true`;
- a human deliberately starts the dedicated publication workflow with the exact source SHA and
  Email selection;
- the source revision is an ancestor of the canonical repository's `main` branch;
- Issue and pull request provenance resolve exactly once;
- all selected Emails pass the complete rendering, safety, screenshot, and provenance gates;
- the generated Pages artifact passes local link and gallery validation;
- Pages deployment and public URL read-back succeed.

Merge, approval, Status, Stage, scheduling, or a normal push never starts public publication. Setting
`preview_public: true` alone also does not deploy; it only makes an Email eligible for the deliberate
publication workflow. No failed or partial build updates the publication ledger or Project field.

After successful read-back, the workflow creates or updates a dedicated branch and normal pull
request for the append-only ledger update; it never commits directly to `main`. After that ledger PR
is merged, the Campaign OS synchronizer may mirror the canonical public URL into the Email Issue
Operations Snapshot and Project Preview URL field. Public withdrawal uses a reviewed manifest change
and deliberate deployment; it does not delete source history.

### 12.8 Gallery experience

The static gallery groups Emails by Campaign and shows code, canonical title, public state, desktop
thumbnail, and a link to the interactive HTML. Email detail pages provide desktop and mobile
screenshot views, the interactive preview, and provenance links. Search and Campaign filtering are
client-side over generated non-PII metadata. No fake performance metrics, customer records, sending
controls, scheduling controls, or editable production state appears.

The gallery is responsive, keyboard accessible, and built from the current brand authority resolved
at implementation time. Before frontend code is written, produce and obtain approval for a complete
desktop and mobile visual concept. Implementation must then be verified against that accepted
concept in the browser and with screenshot comparison.

### 12.9 Public-site safety and indexing

Every page carries `noindex, nofollow, noarchive` metadata and the site publishes a restrictive
`robots.txt`. These reduce discovery but are never described or tested as access control. Any content
on Pages is treated as public.

The public build excludes source maps, fixture source files, workflow logs, PR-only metadata,
unpublished Email records, contact data, secrets, and private repository content not required for
the selected preview. Content Security Policy is expressed through page metadata within GitHub
Pages' static-hosting limits. External asset hosts are explicitly allowlisted and every public
resource is checked for HTTPS.

### 12.10 GitHub platform constraints

GitHub Pages supports custom Actions workflows for private repositories on eligible paid plans, but
the resulting site is public by default outside qualifying Enterprise access control. The design
therefore treats every Pages byte as public regardless of repository visibility. The deployment job
uses the `github-pages` environment with minimum `contents: read`, `pages: write`, and
`id-token: write` permissions.

Private Actions artifacts require repository read access and expire. GitHub's current default is 90
days, with a configurable private-repository retention range; the review workflow records the actual
`expires_at` value returned by GitHub rather than assuming a duration.

Configure and verify the custom domain in GitHub before creating its Cloudflare DNS record to reduce
domain-takeover risk. Keep the GitHub domain-verification TXT record after verification. These steps
are included in the eventual implementation plan only behind Vincent's separate external-change
approval.

Platform references:

- [Using custom workflows with GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Creating a GitHub Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
- [Downloading workflow artifacts](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts)
- [Managing a custom domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)

## 13. Initial-state mapping

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

## 14. Built-in automation

Configure only obvious housekeeping:

1. Auto-add Issues and pull requests from `vincent-laroche/email-marketing-ops` carrying the
   `email-marketing` label.
2. Set newly added items to Status `Inbox` when no explicit synchronized state exists.
3. Set closed Issues to Status `Done`.
4. Set merged pull requests to Status `Done`.

Do not automate Approval to Scheduled, scheduling, sending, Shopify activation, audience changes,
or performance values. Do not auto-archive during initial migration.

## 15. Sanitized repository structure

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

## 16. Migration mechanics

Use deterministic, inspectable, idempotent scripts:

1. Classify and reconcile the dirty working tree into verified commits.
2. Compile a versioned manifest from the Email Reference File, build ledger, HTML, and approved
   schema.
3. Create or update 69 Issues by a hidden stable key; abort on duplicates.
4. Link 53 Email sub-issues to seven Campaign parents.
5. Push the current branch and open a draft migration pull request linked to the Campaign OS Task.
6. Create the private Project, its 20 custom fields, labels, automations, and five views.
7. Add all 69 Issues and the migration pull request to the Project.
8. Mirror Issue Operations Snapshot values into Project fields and fail on drift.
9. Build and verify the strict fixture compiler, private review workflow, three-output renderer,
    provenance system, publication ledger, and responsive static gallery in the migration pull
    request.
10. Complete verification, mark the pull request ready, obtain passing checks, and merge normally.
11. Re-fetch repository, Issue, pull request, parent/sub-issue, Project, field, automation, and view
    state and publish the final audit as a connector-readable Issue comment.
12. After the separately approved external-change checkpoint, enable GitHub Pages, run the deliberate
    public-publication workflow for eligible Emails, verify the public site, configure and verify
    `email-preview.hairsolutions.co` in GitHub, add the exact Cloudflare DNS record, verify HTTPS, and
    only then synchronize public Preview URLs.

Every state-changing command runs first as dry-run, once with `--apply`, and again as dry-run to
prove zero-action idempotence.

## 17. Acceptance criteria

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
- the built-in Status field and exactly 20 custom fields exist with approved options;
- exactly five views exist with approved names, order, layouts, filters, fields, grouping, and sort;
- approved auto-add and housekeeping workflows are enabled without marketing-decision automation;
- no contact PII, secret, browser state, dependency tree, cache, or agent worktree is tracked;
- no email is incorrectly marked Scheduled, Sent, Measuring, Complete, or activation-approved;
- final read-back is recorded in Issues or pull requests, not only in a Project-only artifact.
- Preview URL is blank for every Email without a verified public publication;
- each successful preview has rendered HTML plus full desktop and mobile screenshots;
- unsupported or unresolved Liquid causes a closed failure and never a partial publication;
- every output resolves to one exact source SHA, pull request, Email Issue, fixture state, and digest;
- expired private review artifacts remain reproducible from their recorded source revision;
- public publication requires both `preview_public: true` and deliberate workflow dispatch;
- the public gallery exposes no PII, customer-specific URL, token, real unsubscribe link, draft,
  review artifact, or unpublished Email;
- Pages, custom-domain, and Cloudflare state change only under their separate approval gates.

## 18. Non-goals

This work does not:

- send, schedule, publish, or activate an Email campaign in Shopify;
- modify Shopify audiences, segments, automations, products, customers, or campaign configuration;
- write to MailerLite, MailerSend, HubSpot, DNS, or Cloudflare without a separately approved step;
- invent missing copy, dates, consent, performance, proof, QA, experiments, or approvals;
- create an Issue for every small checklist item;
- delete or rewrite canonical repository history;
- change the separate `vincent-laroche/email-marketing` repository;
- make the Project a source of truth that connectors cannot read.
- treat Actions artifacts as permanent storage;
- publish raw or partially rendered Shopify Liquid;
- expose draft or review Emails through security by obscurity;
- treat `noindex` or `robots.txt` as authentication;
- claim browser screenshots replace email-client rendering QA.
