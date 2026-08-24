# GitHub Email Marketing Operations — Design

**Date:** 2026-08-24  
**Status:** Approved by Vincent  
**Target repository:** `vincent-laroche/email-marketing`  
**Target GitHub Project:** `Hair Solutions Co. — Email Marketing Operations`

## 1. Outcome

Move the current Hair Solutions Co. email marketing project into a clean, private GitHub
repository and a linked, private GitHub Project. The repository holds source and evidence. The
Project is the operating control plane for the 53-email Shopify programme.

The primary model is one GitHub Issue per email, following the event-marketing pattern. Technical
QA fields from HTML email-template workflows are added without creating a second competing
roadmap.

Shopify Messaging and Shopify Flow remain the sole marketing campaign and lifecycle platforms.
MailerLite remains legacy evidence only. Creating the repository and Project does not authorize an
email send, schedule, automation activation, subscriber change, or Shopify production change.

## 2. Destructive repository reset

The existing `vincent-laroche/email-marketing` repository is intentionally replaced:

1. Change the repository from public to private before importing any project material.
2. Build a sanitized snapshot of the current project in an isolated temporary directory.
3. Create a new orphan `main` root commit with no parent.
4. Force-push that root to `main`, replacing the repository's existing reachable history.
5. Delete every other remote branch, including `shopify-sync-on-demand-only`.
6. Verify that `main` is the only branch and that its root commit has no parent.
7. Leave `vincent-laroche/email-marketing-ops` unchanged as recovery evidence. It is not the
   operating repository after migration.

The reset removes old repository content from normal GitHub references. GitHub may retain
unreachable objects internally for an unspecified period; this operation cannot guarantee physical
erasure from GitHub infrastructure.

## 3. Credential and privacy boundary

- Use `GITHUB_PAT_MASTER_TOKEN` from `/Users/vMac/.env` as an ephemeral `GH_TOKEN` value.
- Never print, persist, commit, or copy the token into the repository or Project.
- The target repository and GitHub Project are private.
- CRM exports, subscriber data, email addresses, browser state, cookies, credentials, and local
  agent/runtime data are excluded.
- Issue bodies contain audience logic and aggregate counts, never contact-level PII.

## 4. Sanitized repository structure

The new repository contains the current operational source, authority documents, and bounded
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

## 5. GitHub Project architecture

Create a private user-owned GitHub Project named:

**Hair Solutions Co. — Email Marketing Operations**

Link it to `vincent-laroche/email-marketing`. Every tracked item is a repository Issue; draft-only
Project items are not used for durable work.

### 5.1 Item model

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

### 5.2 Email issue contract

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

The Email Reference File remains upstream authority. Issue copy is a synchronized review surface,
not an independent copy source.

## 6. Project fields

Use GitHub's built-in Title, Assignees, Repository, Labels, Milestone, and Status fields. Add these
custom fields:

| Field | Type | Values or contract |
|---|---|---|
| Item Type | Single select | Journey, Email, Component, Operations |
| Journey | Single select | J1, J2, J3, J4, J5, W, N, Shared |
| Shopify Surface | Single select | Shopify Messaging, Shopify Flow, Shopify Notifications, Repository only |
| Audience Segment | Single select | Consented Cohort 2026, Engaged Core, Purchasers, Abandoned Checkout 30d, Lapsed 60d, Consultation Interest, Newsletter Subscribers, Not Applicable, Needs Decision |
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

## 7. Project views

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

## 8. Initial-state mapping

Populate the board from current repository evidence rather than treating every email as new:

- All 53 email artifacts exist locally.
- 51 are structurally green; RO-4 and NL-16 are blocked by source gaps.
- Structural green maps to QA Status = Structural Pass, not Approved.
- Emails with unresolved placeholders map to Content Readiness = Needs Real Data.
- J2 and W map to Shopify Messaging; J1, J3, J4, and J5 map to Shopify Flow.
- Nothing starts as Scheduled, Active, or activation-approved.
- Shopify sender authentication is complete, but broad-audience consent remains gated.

## 9. Migration mechanics

Implementation is performed with idempotent, inspectable scripts where repetition is involved:

1. Generate and validate the sanitized repository snapshot.
2. Scan it for secrets, PII, ignored runtime state, oversized generated files, and broken paths.
3. Create and push the orphan `main` only after the scan passes.
4. Delete non-main branches and verify the remote branch list.
5. Create the Project and custom fields.
6. Create Journey, Email, Component, and Operations issues from deterministic manifests.
7. Add every issue to the Project and populate fields by exact issue number.
8. Link the Project to the repository and link email sub-issues to journey parents.
9. Create the seven views and confirm their filters/grouping.
10. Re-fetch repository and Project state and compare it with the manifests.

Retries must resolve resources by exact repository, issue, field, and option identifiers. They must
not create duplicate issues, fields, or Project items.

## 10. Acceptance criteria

The migration is complete only when:

- the target repository and Project are private;
- target `main` is a new root commit and the only remote branch;
- the sanitized repository contains no secrets, contact-level PII, browser state, caches, or local
  agent worktrees;
- `email-marketing-ops` remains unchanged;
- the Project is linked to `vincent-laroche/email-marketing`;
- all 53 email issues and 7 journey issues exist exactly once;
- shared component/operations issues exist exactly once;
- all issues are Project items with required custom fields populated;
- all seven views exist with the approved layout intent;
- no item is incorrectly marked Scheduled, Active, or activation-approved;
- repository documentation names Shopify Messaging + Shopify Flow as the sole campaign/lifecycle
  platform;
- a final read-back audit records repository, issue, Project, field, option, and view counts.

## 11. Non-goals

This migration does not:

- activate, schedule, send, or publish email;
- modify Shopify audiences, segments, automations, products, customers, or configuration;
- write to MailerLite, MailerSend, HubSpot, DNS, or Cloudflare;
- invent missing copy, dates, consent, proof, metrics, or QA results;
- delete or rewrite `vincent-laroche/email-marketing-ops`;
- turn every historical module or proof artifact into a Project issue.
