# GitHub Email Marketing Operations — Design

**Date:** 2026-08-24

**Status:** Approved by Vincent, including the connector-readable Issues and PRs architecture

**Target repository:** `vincent-laroche/email-marketing-ops`

**Target GitHub Project:** `Hair Solutions Co. — Email Marketing Operations`

## 1. Outcome

Move the current Hair Solutions Co. email marketing project into a clean, private GitHub
repository and a linked, private GitHub Project. The repository, GitHub Issues, and pull requests
are the durable operating system for the 53-email Shopify programme. The Project is a private,
derived planning and visualization layer over those connector-readable records.

The primary model is one GitHub Issue per email, following the event-marketing pattern. Technical
QA fields from HTML email-template workflows are added without creating a second competing
roadmap. No decision, status, requirement, blocker, or release result may exist only in a GitHub
Project field because Notion and ChatGPT connectors can read Issues and pull requests but cannot
reliably read GitHub Projects.

Shopify Messaging and Shopify Flow remain the sole marketing campaign and lifecycle platforms.
MailerLite remains legacy evidence only. Creating the repository and Project does not authorize an
email send, schedule, automation activation, subscriber change, or Shopify production change.

## 2. Existing repository continuity

`vincent-laroche/email-marketing-ops` is the existing private repository connected to this local
project and becomes the canonical repository. Its history is retained.

1. Preserve every existing commit and avoid force-pushes or orphan branches.
2. Reconcile the current working tree into small, verified, purpose-specific commits on the
   current project branch.
3. Open a pull request from the verified project branch into `main`; do not rewrite `main`
   history.
4. Merge through the pull request after checks pass, then verify the resulting `origin/main`.
5. Preserve unrelated remote branches unless they are reviewed and separately approved for
   deletion.
6. Verify that local `main`, `origin/main`, and the checked-out canonical revision agree.

The separate `vincent-laroche/email-marketing` repository is out of scope. Do not change its
visibility, branches, history, files, settings, or integrations.

## 3. Credential and privacy boundary

- Use `GITHUB_PAT_MASTER_TOKEN` from `/Users/vMac/.env` as an ephemeral `GH_TOKEN` value.
- Never print, persist, commit, or copy the token into the repository or Project.
- The target repository and GitHub Project are private.
- CRM exports, subscriber data, email addresses, browser state, cookies, credentials, and local
  agent/runtime data are excluded.
- Issue bodies contain audience logic and aggregate counts, never contact-level PII.

## 4. Sanitized repository structure

The canonical repository contains the current operational source, authority documents, and bounded
evidence:

```text
/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── email.yml
│   │   ├── journey.yml
│   │   ├── component.yml
│   │   └── operations.yml
│   └── pull_request_template.md
├── AGENTS.md
├── CLAUDE.md
├── PROJECT.md
├── README.md
├── CAMPAIGN-PLAN.md
├── Email Reference File/
├── shopify-messaging/
├── mailersend/
├── proof-bank/
├── tools/
├── scripts/
├── docs/
└── archive/
    └── mailerlite-legacy/
```

The MailerLite implementation, rendered legacy emails, API research, and MailerLite-specific block
library move under `archive/mailerlite-legacy/`. Archive banners make clear that these files must
not drive campaigns or automation.

The import excludes:

- `/Users/vMac/.env` and every credential-bearing file;
- `exports/` and all CRM/contact PII;
- `.git/`, `.claude/`, `.playwright-mcp/`, browser profiles, cookies, and worktrees;
- `node_modules/`, caches, build products, temporary files, and `.DS_Store`;
- obsolete MailerLite editor screenshots;
- local-only proof renders unless deliberately selected as durable QA evidence;
- ZIP bundles and other generated duplicates when source files are present.

The Figma plugin is included only as source and configuration if it is needed by the current email
workflow. Dependencies and generated output are excluded.

### 4.1 Approved pre-publication reconciliation

Before `main` is advanced:

- return CR-1 through CR-4 to the Email Reference File palette required by `AGENTS.md` while
  preserving their functional Shopify Liquid and content corrections;
- retain and verify the current Phase 4 Proof Bank and Phase 5 Shopify segment/tag work;
- archive `mailerlite/`, `mailerlite-blocks/`, and their build helpers under
  `archive/mailerlite-legacy/`;
- include the Figma email-block plugin as source only under `tools/`;
- retain only the final, durable email-rendering QA evidence under `docs/evidence/`;
- remove obsolete MailerLite editor screenshots from the active tree while preserving them in Git
  history;
- keep local CRM exports, browser state, agent worktrees, dependencies, generated plugin bundles,
  and intermediate proof renders out of Git.

## 5. GitHub Issues and pull requests architecture

GitHub Issues and pull requests are the canonical collaboration surface. This is the layer that
Notion, ChatGPT, Claude, Codex, and human reviewers must be able to read without GitHub Project
access.

### 5.1 Source-of-truth contract

- An Issue holds the durable work record: scope, current state, owner, requirements, blockers,
  decisions, evidence links, and acceptance criteria.
- A pull request holds the durable implementation record: changed files, linked Issues, validation
  evidence, risks, screenshots where relevant, and the merge result.
- Issue comments record dated decisions or verification events that should remain readable to
  connectors.
- Labels carry the machine-readable subset needed for cross-tool discovery: item type, journey,
  workflow state, priority, and blocked state.
- Milestones may group delivery phases, but never replace Issue content.
- Project fields mirror Issue content for sorting and visualization. If a Project field and its
  Issue disagree, the Issue wins and the synchronization check fails.
- Project-only draft items are prohibited.

Every Issue body contains a generated **Operations Snapshot** table with the values also mirrored
into Project fields. The table includes Item Type, Journey, Workflow Status, Shopify Surface,
Audience Segment, Relative Send Timing, Target Send Date, UTM Campaign, Content Readiness, Design
Readiness, QA Status, Client Compatibility, Dark Mode, Consent Gate, Activation Gate, and Priority.
The manifest compiler updates this bounded table without overwriting human-written decisions,
blockers, or comments.

### 5.2 Pull request contract

- Every implementation branch is linked to at least one Issue.
- Pull request titles start with the primary email, journey, component, or operations code.
- The body uses closing keywords only when the pull request fully satisfies the linked Issue;
  partial work uses non-closing references.
- The body lists authority sources, changed files, tests, rendered evidence, consent and activation
  impact, and rollback notes.
- Email changes include the affected email codes and explicitly state whether approved copy changed.
- No pull request may claim an email is Scheduled, Active, or activation-approved without a dated
  Issue decision from Vincent.
- Merges use normal GitHub pull request history. No force-push to `main` and no direct migration
  push to `main` are used.

## 6. GitHub Project architecture

Create a private user-owned GitHub Project named:

**Hair Solutions Co. — Email Marketing Operations**

Link it to `vincent-laroche/email-marketing-ops`. Every tracked item is a repository Issue; draft-only
Project items are not used for durable work. The Project is rebuilt and verified from Issues, not
treated as an independent database.

### 6.1 Item model

- **53 Email issues:** one issue for every J1–J5, W, and N email.
- **7 Journey issues:** J1 Post-Purchase, J2 Cart Recovery, J3 Win-Back, J4 Reorder,
  J5 Consultation, W Welcome, and N Newsletter.
- **Component issues:** only shared components with real work or blockers. Do not create 104
  inventory-only component issues.
- **Operations issues:** cross-email consent, automation, activation, data, and measurement work.

Email issues are linked to their Journey issue through native GitHub sub-issue relationships.

Initial shared work includes:

- RO-4 `Text - Customer snapshot` source gap;
- NL-16 `Comparison` source gap;
- remaining dynamic and reality-dependent placeholders;
- Shopify consent and audience activation gates;
- journey enrollment, collision, and exit rules;
- duplicate abandoned-checkout automation resolution;
- Phase 6 measurement and baseline reporting.

### 6.2 Email issue contract

Every email issue contains:

- email code and canonical name;
- journey and parent issue;
- subject and preheader;
- approved copy in a collapsible section, copied verbatim from the authority export;
- source file links and a source fingerprint so drift is detectable;
- Shopify surface and automation trigger;
- audience segment and consent basis;
- relative send timing or target send date;
- dynamic-data and personalization requirements;
- UTM campaign code and destination links;
- content, design, compatibility, accessibility, consent, and activation checklists;
- blockers, decisions, and release evidence.
- the generated Operations Snapshot that mirrors every Project field;
- connector-readable labels for item type, journey, workflow state, priority, and blockers;
- linked pull requests and their validation results.

The Email Reference File remains upstream authority. Issue copy is a synchronized review surface,
not an independent copy source.

## 7. Project fields

Use GitHub's built-in Title, Assignees, Repository, Labels, Milestone, and Status fields. Add these
custom fields:

| Field | Type | Values or contract |
|---|---|---|
| Item Type | Single select | Journey, Email, Component, Operations |
| Journey | Single select | J1, J2, J3, J4, J5, W, N, Shared |
| Shopify Surface | Single select | Shopify Messaging, Shopify Flow, Shopify Notifications, Repository only |
| Audience Segment | Single select | Consented Cohort 2026, Engaged Core, Purchasers, Never Purchased, Abandoned Checkout 30d, Lapsed 60d, Consultation Interest, Newsletter Subscribers, Not Applicable, Needs Decision |
| Relative Send Timing | Text | Lifecycle timing such as `+4 hours` or `Delivery +110d` |
| Target Send Date | Date | Calendar date for broadcasts or explicitly dated work |
| UTM Campaign | Text | Canonical analytics campaign code |
| Content Readiness | Single select | Not Started, Draft, Needs Real Data, Approved, Blocked |
| Design Readiness | Single select | Not Started, Building, Review, Approved, Blocked |
| QA Status | Single select | Not Tested, Structural Pass, Rendered Pass, Approved, Blocked |
| Client Compatibility | Single select | Not Tested, Core Clients Pass, Outlook Issue, Gmail Clip Risk, Blocked |
| Dark Mode | Single select | Not Tested, Pass, Needs Work, Not Applicable |
| Consent Gate | Single select | Unverified, Verified, Not Applicable, Blocked |
| Activation Gate | Single select | Not Approved, Ready for Approval, Approved, Scheduled, Active, Retired |
| Priority | Single select | P0, P1, P2, P3 |

The built-in Status field uses:

`Backlog → Copywriting → Code & Design → QA → Ready for Shopify → Scheduled → Active`

`Blocked` and `Retired` are separate terminal/exception states.

Structural or rendered QA never implies activation approval. `Activation Gate` is separate from
workflow Status for that reason.

## 8. Project views

Create these views:

1. **Pipeline** — board grouped by Status; the primary daily operating view.
2. **Email Inventory** — table filtered to Item Type = Email with journey, timing, audience,
   readiness, QA, consent, and activation columns.
3. **Journeys** — board grouped by Journey with Journey and Email items.
4. **QA & Compatibility** — table focused on QA Status, Client Compatibility, Dark Mode, and
   blockers.
5. **Activation Calendar** — roadmap/calendar using Target Send Date; lifecycle emails without a
   calendar date remain visible in Pipeline rather than receiving invented dates.
6. **Blockers** — table filtered to Status = Blocked or any gate = Blocked.
7. **Components** — table filtered to Item Type = Component.

## 9. Initial-state mapping

Populate the board from current repository evidence rather than treating every email as new:

- All 53 email artifacts exist locally.
- 51 are structurally green; RO-4 and NL-16 are blocked by source gaps.
- Structural green maps to QA Status = Structural Pass, not Approved.
- Emails with unresolved placeholders map to Content Readiness = Needs Real Data.
- J2, W, and N map to Shopify Messaging; J1, J3, J4, and J5 map to Shopify Flow.
- Nothing starts as Scheduled, Active, or activation-approved.
- Shopify sender authentication is complete, but broad-audience consent remains gated.

## 10. Migration mechanics

Implementation is performed with idempotent, inspectable scripts where repetition is involved:

1. Classify the current staged, unstaged, untracked, and deleted files by ownership and purpose.
2. Exclude secrets, PII, ignored runtime state, oversized generated files, and accidental local
   artifacts.
3. Reconcile approved active work into small, verified commits while preserving existing history.
4. Generate and validate connector-readable Issue bodies, labels, and pull request templates.
5. Create Journey, Email, Component, and Operations Issues from deterministic manifests.
6. Open the migration pull request into `main`, attach the verification evidence, and merge only
   after checks pass.
7. Create the Project and custom fields from the same manifest used for Issues.
8. Add every Issue to the Project and mirror the Operations Snapshot values into Project fields.
9. Link the Project to the repository and link email sub-issues to journey parents.
10. Create the seven views and confirm their filters/grouping.
11. Re-fetch repository, Issue, pull request, and Project state and compare it with the manifests.

Retries must resolve resources by exact repository, Issue key, pull request, field, and option
identifiers. They must not create duplicate Issues, fields, or Project items. Synchronization is
Issue-first: it updates the bounded Operations Snapshot and then mirrors the same values to the
Project.

## 11. Acceptance criteria

The migration is complete only when:

- the target repository and Project are private;
- the complete existing `email-marketing-ops` commit history remains reachable;
- the migration is reviewed and merged through a pull request, and local `main` and `origin/main`
  resolve to the same verified revision without a force-push;
- the sanitized repository contains no secrets, contact-level PII, browser state, caches, or local
  agent worktrees;
- the separate `vincent-laroche/email-marketing` repository remains unchanged;
- the Project is linked to `vincent-laroche/email-marketing-ops`;
- all 53 email issues and 7 journey issues exist exactly once;
- shared component/operations issues exist exactly once;
- every Issue exposes its complete current Operations Snapshot and connector-readable labels;
- every implementation commit reaching `main` is represented by a linked pull request;
- all issues are Project items with required custom fields populated;
- Issue snapshots and mirrored Project fields agree exactly;
- all seven views exist with the approved layout intent;
- no item is incorrectly marked Scheduled, Active, or activation-approved;
- repository documentation names Shopify Messaging + Shopify Flow as the sole campaign/lifecycle
  platform;
- a final read-back audit records repository, Issue, pull request, Project, field, option, and view
  counts.

## 12. Non-goals

This migration does not:

- activate, schedule, send, or publish email;
- modify Shopify audiences, segments, automations, products, customers, or configuration;
- write to MailerLite, MailerSend, HubSpot, DNS, or Cloudflare;
- invent missing copy, dates, consent, proof, metrics, or QA results;
- delete or rewrite history in `vincent-laroche/email-marketing-ops`;
- modify the separate `vincent-laroche/email-marketing` repository;
- turn every historical module or proof artifact into a Project issue.
