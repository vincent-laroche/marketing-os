# Email Marketing Campaign OS Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconcile the existing email-marketing repository, make GitHub Issues and pull requests the connector-readable operating system, and create the private `Email Marketing — Campaign OS` Project with the approved hierarchy, 28 custom fields, automations, and six native views.

**Architecture:** The Email Reference File remains upstream campaign and copy authority. Standard-library Python compilers produce a versioned manifest and complete Issue bodies. Issues hold scope, Shopify implementation evidence, decisions, results, and learnings; pull requests hold proposed changes and review history; Project fields mirror the bounded Operations Snapshot in each Issue. The existing `vincent-laroche/email-marketing-ops` history reaches `main` through a normal migration pull request.

**Tech Stack:** Python 3 standard library, `unittest`, Git, GitHub CLI, GitHub REST and GraphQL APIs, GitHub Issues, GitHub pull requests, GitHub Projects v2, Shopify Messaging HTML/Liquid, TypeScript for the existing Figma plugin.

**Spec:** `docs/superpowers/specs/2026-08-24-github-email-marketing-operations-design.md`

**Companion plans:**

- `docs/superpowers/plans/2026-08-24-email-preview-gallery.md`

## Global constraints

- Work only in `vincent-laroche/email-marketing-ops`; never change `vincent-laroche/email-marketing`.
- Preserve existing history. Do not create an orphan branch, force-push, rewrite `main`, or directly push the migration to `main`.
- Use `GITHUB_PAT_MASTER_TOKEN` from `/Users/vMac/.env` only as an ephemeral `GH_TOKEN`. Never print, persist, or commit it.
- Do not send, schedule, publish, or activate email. Do not write Shopify customer tags, audiences, segments, Flow automations, or Messaging campaigns.
- Do not commit CRM exports, contact data, browser state, cookies, worktrees, dependencies, caches, generated plugin bundles, or secrets.
- Use Email Reference File copy verbatim. Missing authority stays blocked.
- Treat Issues and pull requests as canonical. Project fields are mirrors and may never be the only record of state or approval.
- Keep creative Stage, Messaging State, and Flow State independent. No source, preview, approval, or merge event advances a Shopify implementation state automatically.
- Use exactly 28 custom fields and six native Project views. Evidence remains in Issues and linked pull requests, not a redundant Project field.
- Do not create Project draft items. Project items are repository Issues and pull requests.
- Run every state-changing GitHub operation as dry-run, then once with `--apply`, then dry-run again to prove idempotence.
- Create small, task-owned commits and preserve unrelated worktree changes.

---

## Task 1: Restore the J2 email authority palette

**Files:**

- Create: `tests/email_operations/__init__.py`
- Create: `tests/email_operations/test_j2_email_contract.py`
- Modify: `shopify-messaging/emails/01-cr-1.html`
- Modify: `shopify-messaging/emails/02-cr-2.html`
- Modify: `shopify-messaging/emails/03-cr-3.html`
- Modify: `shopify-messaging/emails/04-cr-4.html`
- Modify: `shopify-messaging/build-ledger.json`
- Modify: `shopify-messaging/BUILD-LEDGER.md`
- Modify: `shopify-messaging/J2-CART-RECOVERY-READY.md`
- Modify: `PROJECT.md`

- [ ] **Step 1: Add a failing table-driven contract test**

Test the four CR files for the approved colours `#F6EFD9`, `#151411`, `#25221D`, `#C7BFAC`, and `#EA6452`; permit `#EDE3CC` where the reference modules use it, and reject `#F7F1DE`, `#EFE7D2`, `#15140F`, `#2A2620`, `#DDD2B6`, and `#ED6F5C`. Also require transparent body and wrapper surfaces, unsubscribe and physical-address variables, HTTPS images, and Shopify abandoned-checkout Liquid.

- [ ] **Step 2: Confirm the palette test fails for the expected reason**

```bash
python3 -m unittest tests.email_operations.test_j2_email_contract -v
```

Stop if the failure exposes missing Liquid, unsubscribe, address, or transparency rather than the known colour drift.

- [ ] **Step 3: Retokenize without regenerating the hand-finished files**

Apply the exact mapping:

| Superseded | Approved |
|---|---|
| `#F7F1DE` | `#EDE3CC` |
| `#EFE7D2` | `#F6EFD9` |
| `#15140F` | `#151411` |
| `#2A2620` | `#25221D` |
| `#DDD2B6` | `#C7BFAC` |
| `#ED6F5C` | `#EA6452` |

Preserve Liquid loops, cart behavior, URLs, approved copy, unsubscribe handling, and address handling.

- [ ] **Step 4: Correct ledger and handoff claims**

Replace references to the superseded `PLATFORM_EMAIL.md` palette with Email Reference File authority. Record that visual tokens changed while Shopify functionality remained intact. Do not claim rendered QA, scheduling, or activation.

- [ ] **Step 5: Verify and commit only J2 reconciliation**

```bash
python3 -m unittest tests.email_operations.test_j2_email_contract -v
git diff --check -- shopify-messaging tests/email_operations PROJECT.md
git add tests/email_operations/__init__.py tests/email_operations/test_j2_email_contract.py shopify-messaging/emails/01-cr-1.html shopify-messaging/emails/02-cr-2.html shopify-messaging/emails/03-cr-3.html shopify-messaging/emails/04-cr-4.html shopify-messaging/build-ledger.json shopify-messaging/BUILD-LEDGER.md shopify-messaging/J2-CART-RECOVERY-READY.md PROJECT.md
git commit --only tests/email_operations/__init__.py tests/email_operations/test_j2_email_contract.py shopify-messaging/emails/01-cr-1.html shopify-messaging/emails/02-cr-2.html shopify-messaging/emails/03-cr-3.html shopify-messaging/emails/04-cr-4.html shopify-messaging/build-ledger.json shopify-messaging/BUILD-LEDGER.md shopify-messaging/J2-CART-RECOVERY-READY.md PROJECT.md -m "fix(shopify-email): restore J2 authority palette"
```

---

## Task 2: Validate and harden retained Phase 4 and Phase 5 work

**Files:**

- Create: `tests/email_operations/test_shopify_program_state.py`
- Modify: `shopify-messaging/fill_proof_bank_nl.py`
- Modify: `shopify-messaging/build_engagement_tags.py`
- Modify: `proof-bank/proof-bank.json`
- Modify: the sixteen currently changed `shopify-messaging/emails/*-nl-*.html` files
- Modify: `shopify-messaging/PHASE5-PLAN.md`
- Modify: `PROJECT.md`

- [ ] **Step 1: Add evidence-schema tests**

Assert:

- build ledger is a list of 53 records with 51 `GREEN` and 2 `BLOCKED`;
- the blocked records are RO-4 and NL-16 with current authority-copy gaps;
- the email directory contains 53 HTML files;
- proof bank is a list of 87 records with unique `review_id` values;
- every non-empty `used_in` is a relative filename that exists among the 53 emails;
- proof records contain no email-address field;
- the ledger records 125 loud-placeholder occurrences across 35 emails;
- no ledger entry claims Scheduled, Sent, Measuring, Complete, or activation approval.

- [ ] **Step 2: Confirm current evidence satisfies the assertions**

```bash
python3 -m unittest tests.email_operations.test_shopify_program_state -v
```

Reconcile evidence from HTML if counts drift; never weaken an assertion merely to pass.

- [ ] **Step 3: Make proof filling repository-relative and idempotent**

Replace absolute project paths with `Path(__file__).resolve()` paths. Keep `--dry-run` read-only. Add a test that hashes the proof bank and newsletters before and after dry-run and requires identical hashes.

- [ ] **Step 4: Make the Shopify tag helper fail closed**

Make dry-run the default, require explicit `--apply` for writes, make flags mutually exclusive, report aggregates only, never print customer emails, and fail before a request when the token is absent. Unit tests must not call Shopify or read the external cohort.

- [ ] **Step 5: Verify retained artifacts without touching Shopify**

```bash
python3 -m unittest tests.email_operations.test_shopify_program_state -v
python3 -m py_compile shopify-messaging/fill_proof_bank_nl.py shopify-messaging/build_engagement_tags.py
python3 shopify-messaging/fill_proof_bank_nl.py --dry-run
git diff --check -- proof-bank shopify-messaging tests/email_operations PROJECT.md
```

- [ ] **Step 6: Commit only the retained Phase 4 and Phase 5 work**

Stage the exact newsletter paths reported by `git diff --name-only -- shopify-messaging/emails`, then include the proof bank, two scripts, test, Phase 5 plan, and session log. Verify the staged list excludes MailerLite, plugin, screenshot, and archive paths.

```bash
git diff --cached --name-status
git commit -m "feat(shopify-email): retain proof and audience preparation"
```

---

## Task 3: Archive MailerLite and curate durable tools and evidence

**Files:**

- Move: `mailerlite/` to `archive/mailerlite-legacy/implementation/`
- Move: `mailerlite-blocks/` to `archive/mailerlite-legacy/blocks/`
- Move: `scripts/make_mailerlite_blocks.py` to `archive/mailerlite-legacy/tools/make_mailerlite_blocks.py`
- Move: `scripts/normalize_blocks.py` to `archive/mailerlite-legacy/tools/normalize_blocks.py`
- Create: `archive/mailerlite-legacy/README.md`
- Move selected source: `figma-plugin/` to `tools/figma-email-blocks-plugin/`
- Create: `docs/evidence/email-rendering/2026-08-21/README.md`
- Move selected evidence from: `proof-email/`
- Modify: `.gitignore`
- Modify: `AGENTS.md`
- Modify: `CAMPAIGN-PLAN.md`
- Modify: `README.md`
- Modify: `PROJECT.md`
- Delete from active tree: `Email Reference File/MalerLite Editors/*.png`

- [ ] **Step 1: Add repository-boundary tests**

Require active docs to name Shopify Messaging and Shopify Flow as the marketing platforms; require MailerLite implementation paths below `archive/mailerlite-legacy/`; reject tracked `node_modules`, `.DS_Store`, `__pycache__`, generated plugin bundles, browser profiles, CRM exports, and worktrees.

- [ ] **Step 2: Create the legacy archive with Git-aware moves**

Move the implementation, block library, and MailerLite-only helpers. The archive README must state that the contents are historical evidence and cannot drive campaigns or automation.

- [ ] **Step 3: Curate the Figma plugin as source only**

Retain source, README, manifest, package manifests, TypeScript configuration, UI source, and examples. Ignore dependencies, `dist`, caches, and ZIP bundles.

- [ ] **Step 4: Curate only final rendering evidence**

Retain under `docs/evidence/email-rendering/2026-08-21/`:

- `render-qa.md`;
- `renders/stacked-block-proof-desktop.png`;
- `renders/stacked-block-proof-mobile.png`;
- `figma-transparency/figma-transparency-demo-final-desktop.png`;
- `figma-transparency/figma-transparency-demo-final-mobile.png`;
- `figma-transparency/figma-transparency-demo-qa.md`;
- `validation.json`.

Document their date, purpose, and non-production status. Exclude intermediate renders and temporary HTML.

- [ ] **Step 5: Keep screenshot deletions and repair active documentation**

Obsolete MailerLite editor screenshots remain recoverable in Git history. Update active paths and platform statements; do not rewrite historical archive documents as Shopify-era artifacts.

- [ ] **Step 6: Verify and commit**

```bash
python3 -m unittest tests.email_operations.test_repository_boundaries -v
npm --prefix tools/figma-email-blocks-plugin ci
npm --prefix tools/figma-email-blocks-plugin run build
git status --short
git diff --check
git diff --cached --name-status
git commit -m "chore: archive MailerLite and curate email tooling"
```

Confirm dependencies and build output stay ignored and that the staged set contains no PII, secrets, browser state, cache, or worktree path.

---

## Task 4: Compile the deterministic Campaign OS manifest

**Files:**

- Create: `tools/github_campaign_os/__init__.py`
- Create: `tools/github_campaign_os/model.py`
- Create: `tools/github_campaign_os/build_manifest.py`
- Create: `github-campaign-os/project-schema.json`
- Create: `github-campaign-os/manifest.json`
- Create: `tests/email_operations/test_campaign_os_manifest.py`
- Modify: `README.md`

- [ ] **Step 1: Add failing manifest-contract tests**

Require exactly 69 unique Issue records:

- 7 Campaign;
- 53 Email;
- 8 Task;
- 0 invented Experiment;
- 1 Bug.

Use stable keys:

```text
campaign:J1
campaign:J2
campaign:J3
campaign:J4
campaign:J5
campaign:W
campaign:N
email:CR-1
task:text-customer-snapshot
task:comparison
task:consent-audience
task:flow-rules
task:dynamic-data
task:measurement
task:campaign-os-migration
task:launch-governance
bug:duplicate-cart-recovery
```

Assert every record has a predictable title, parent where applicable, complete Issue body, allowed labels, all 28 Operations Snapshot values, repository-relative source links, and SHA-256 fingerprint. Reject contact email addresses and absolute `/Users/` paths.

- [ ] **Step 2: Define the versioned Project schema**

`project-schema.json` must define:

- private Project title `Email Marketing — Campaign OS`;
- canonical owner and repository;
- built-in Status options `Inbox`, `Ready`, `In Progress`, `In Review`, `Blocked`, `Done`;
- exactly 28 custom fields from the approved spec;
- all single-select options;
- the six numbered views with layout, filter, visible fields, grouping, and sorting;
- the approved area, asset, flag, risk, and `email-marketing` labels;
- four approved housekeeping workflows;
- schema version `1`.

Do not define labels that duplicate Status, Stage, Priority, Work Type, or Platform.

- [ ] **Step 3: Implement strict manifest dataclasses**

The frozen data model validates enum values, dates, number fields, relative paths, unique keys, parent types, and label namespaces before serialization. Each record exposes:

```text
key
work_type
title
email_code
campaign
parent_key
status
stage
priority
platform
campaign_type
objective
audience
offer
execution_mode
messaging_state
shopify_messaging_url
flow_required
flow_state
shopify_flow_url
automation_trigger
automation_flow_name
production_start
send_date
results_review
recipients
open_rate
click_rate
conversion_rate
revenue
unsubscribe_rate
primary_kpi
target_kpi
preview_url
labels
source_paths
source_fingerprint
issue_body
```

Allow null only for inapplicable or unproven dates, metrics, targets, email code, and parent.

- [ ] **Step 4: Compile seven Campaign and 53 Email records from authority**

Read the email master CSV, `shopify-messaging/build-ledger.json`, and the matching HTML artifacts. Map families:

```text
PP -> J1 -> Shopify Flow -> Automated / Lifecycle -> Flow Yes -> Post-Purchase
CR -> J2 -> Shopify Messaging -> Automated / Lifecycle -> Flow No -> Abandoned Cart
BR -> J2 -> Shopify Messaging -> Automated / Lifecycle -> Flow No -> Browse Abandonment
WB -> J3 -> Shopify Flow -> Automated / Lifecycle -> Flow Yes -> Win-Back
RO -> J4 -> Shopify Flow -> Automated / Lifecycle -> Flow Yes -> Reorder
C  -> J5 -> Shopify Flow -> Automated / Lifecycle -> Flow Yes -> Consultation
W  -> W  -> Shopify Messaging -> Automated / Lifecycle -> Flow No -> Welcome
NL -> N  -> Shopify Messaging -> One-time Campaign -> Flow No -> Newsletter
```

Build Campaign titles from the exact campaign code and canonical campaign name, and Email titles from the exact parent campaign, email code, and canonical short name. For example: `Campaign — J2 — Cart Recovery and Browse Abandonment` and `Email — J2 — CR-1 — Your Cart's Still Here`. Copy CSV Body, Subject, Preview Text, and CTA verbatim into the generated authority section. Fingerprint normalized authority fields, ledger data, and HTML digest.

- [ ] **Step 5: Compile eight Tasks and one Bug without inventing work**

Create independent Issues only for:

- RO-4 Text Customer Snapshot source gap;
- NL-16 Comparison source gap;
- Shopify consent and audience verification;
- Flow enrollment, collision, and exit rules;
- reality-dependent dynamic data;
- measurement and baseline reporting;
- Campaign OS repository and Project migration;
- launch approval and rollback governance;
- duplicate abandoned-checkout automation as the sole Bug.

Attach campaign-specific items to the appropriate parent Campaign and leave cross-campaign Tasks unparented with explicit related-Campaign links.

- [ ] **Step 6: Apply conservative initial field values**

- 51 structurally green Emails: Status `In Review`, Stage `QA`, Priority `P2`;
- RO-4 and NL-16: Status `Blocked`, Stage `Copy`, Priority `P0`, label `flag:launch-blocker`;
- Campaign parents: Status `In Progress`, evidence-backed Stage, Priority `P2`;
- missing decisions: `flag:needs-decision` only when a real Vincent decision is required;
- all 53 Emails: Messaging State `Not Started` and Shopify Messaging URL null unless an exact
  current Shopify record is matched to the approved Email;
- J1, J3, J4, and J5: Flow State `Not Started`; J2, W, and N: Flow State `Not Required`;
- automation names, triggers, URLs, and implementation evidence: null/empty unless current source
  or Shopify evidence proves the value;
- dates and all performance fields: null unless currently proven;
- no email: Scheduled, Sent, Measuring, Complete, or activation-approved.

- [ ] **Step 7: Generate connector-readable Issue bodies**

Each body contains:

1. a stable marker such as `<!-- campaign-os-key: email:CR-1 -->`, rendered from the record key;
2. Operations Snapshot bounded by `<!-- campaign-os-snapshot:start -->` and `<!-- campaign-os-snapshot:end -->`;
3. purpose, parent Campaign, and authority links;
4. authority content bounded by `<!-- campaign-os-authority:start -->` and `<!-- campaign-os-authority:end -->`;
5. the approved Campaign, Email, Task, Experiment, or Bug template sections;
6. mode-specific creative, Shopify Messaging, and Flow/automation acceptance and QA checklists;
7. human-maintained Decisions, Blockers, Evidence, Results, and Learnings sections.

The snapshot must show all Project values, including null values as `Not set`, so a connector can reconstruct Project state from the Issue alone.

The model validator must reject `Execution Mode = TBD` as complete, `Flow Required = No` with a
Flow State other than `Not Required`, `Flow Required = Yes` with `Flow State = Not Required`, and
any automated/lifecycle Email at Stage `Complete` without the implementation/results/learning
evidence required by the spec.

- [ ] **Step 8: Generate, test, and commit**

```bash
python3 -m tools.github_campaign_os.build_manifest --check
python3 -m tools.github_campaign_os.build_manifest --write
python3 -m tools.github_campaign_os.build_manifest --check
python3 -m unittest tests.email_operations.test_campaign_os_manifest -v
git diff --check -- tools/github_campaign_os github-campaign-os tests/email_operations README.md
git add tools/github_campaign_os github-campaign-os/project-schema.json github-campaign-os/manifest.json tests/email_operations/test_campaign_os_manifest.py README.md
git commit --only tools/github_campaign_os github-campaign-os/project-schema.json github-campaign-os/manifest.json tests/email_operations/test_campaign_os_manifest.py README.md -m "feat(github): compile email Campaign OS manifest"
```

---

## Task 5: Add Campaign OS Issue forms and pull request governance

**Files:**

- Create: `.github/ISSUE_TEMPLATE/campaign.yml`
- Create: `.github/ISSUE_TEMPLATE/email.yml`
- Create: `.github/ISSUE_TEMPLATE/task.yml`
- Create: `.github/ISSUE_TEMPLATE/experiment.yml`
- Create: `.github/ISSUE_TEMPLATE/bug.yml`
- Create: `.github/ISSUE_TEMPLATE/config.yml`
- Create: `.github/pull_request_template.md`
- Create: `tests/email_operations/test_github_templates.py`
- Modify: `README.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: Add failing form and template tests**

Without adding a YAML dependency, verify every form captures its approved contract, warns against contact PII, applies only `email-marketing` plus relevant characteristic labels, and never implies sending or approval. The Email form must capture Execution Mode, Messaging State, Flow Required, Flow State, safe Shopify URLs, automation name, trigger, and conditional implementation QA. Verify the PR template requires Issue and Campaign links, deliverable type, preview, changes, creative QA, Messaging impact, Flow impact, authority, approved-copy impact, consent impact, activation impact, risks, rollback, and approval checks.

- [ ] **Step 2: Implement the five forms**

Use exact Work Type names. Forms gather human-authored work that can later be normalized by the synchronizer. Disable blank Issues and route users to the Campaign OS README.

- [ ] **Step 3: Implement the PR template and durable rules**

The template distinguishes a closing reference such as `Closes #123` for fully satisfied acceptance criteria from a non-closing reference such as `Relates to #123` for partial work. It states that merge accepts a deliverable but does not configure Messaging, verify Flow, schedule, activate, or send. Add the connector-readable source-of-truth rule, Shopify readiness semantics, and future branch naming convention to README and AGENTS.

- [ ] **Step 4: Verify and commit**

```bash
python3 -m unittest tests.email_operations.test_github_templates -v
git diff --check -- .github tests/email_operations README.md AGENTS.md
git add .github tests/email_operations/test_github_templates.py README.md AGENTS.md
git commit --only .github tests/email_operations/test_github_templates.py README.md AGENTS.md -m "feat(github): govern Campaign OS issues and pull requests"
```

---

## Task 6: Implement the Issue-first GitHub synchronizer

**Files:**

- Create: `tools/github_campaign_os/gh_client.py`
- Create: `tools/github_campaign_os/sync_issues.py`
- Create: `tools/github_campaign_os/verify_issues.py`
- Create: `tests/email_operations/test_gh_client.py`
- Create: `tests/email_operations/test_issue_sync.py`
- Create: `github-campaign-os/issue-sync-report.json`
- Modify: `.gitignore`
- Modify: `README.md`

- [ ] **Step 1: Add failing client and reconciliation tests**

Use fake API responses only. Cover token redaction, private-repository validation, pagination, API errors, stable-key lookup, duplicate-key hard failure, creation and bounded update, preservation of human sections/comments, allowed-label reconciliation, 53 parent links, dry-run default, explicit `--apply`, and zero-action second dry-run.

- [ ] **Step 2: Implement a redacting GitHub client**

Read `GH_TOKEN` from the environment and call GitHub through JSON APIs. Typed errors may contain endpoint, status, and safe response text but never environment values, authorization headers, raw request headers, or contact data.

- [ ] **Step 3: Implement bounded Issue reconciliation**

Load `manifest.json`, resolve the exact private repository, read open and closed Issues, index by hidden stable key, and plan actions. `--apply` creates or updates 69 Issues and allowed labels. Updates replace only generated snapshot and authority sections; preserve decisions, blockers, evidence, results, learnings, comments, assignees, milestones, unrelated labels, and manual links.

Use native sub-issue GraphQL relationships for all 53 Email-to-Campaign links. Never close or reopen an Issue without an explicit lifecycle transition recorded in the manifest and approved in an Issue decision.

- [ ] **Step 4: Write connector-safe verification output**

The report records repository identity and privacy, counts by Work Type, duplicate or missing keys, snapshot drift, label drift, and parent-link drift. It includes Issue numbers but no token, PII, or body copy.

- [ ] **Step 5: Verify with local fakes and commit**

```bash
python3 -m unittest tests.email_operations.test_gh_client tests.email_operations.test_issue_sync -v
python3 -m tools.github_campaign_os.sync_issues --help
python3 -m tools.github_campaign_os.verify_issues --help
git diff --check -- tools/github_campaign_os tests/email_operations github-campaign-os README.md .gitignore
git add tools/github_campaign_os tests/email_operations/test_gh_client.py tests/email_operations/test_issue_sync.py github-campaign-os/issue-sync-report.json .gitignore README.md
git commit --only tools/github_campaign_os tests/email_operations/test_gh_client.py tests/email_operations/test_issue_sync.py github-campaign-os/issue-sync-report.json .gitignore README.md -m "feat(github): synchronize canonical Campaign OS issues"
```

The committed report is a pre-apply baseline and must not claim remote Issues already exist.

---

## Task 7: Implement Project synchronization and repository validation

**Files:**

- Create: `tools/github_campaign_os/sync_project.py`
- Create: `tools/github_campaign_os/verify_project.py`
- Create: `tools/github_campaign_os/validate_repository.py`
- Create: `tools/github_campaign_os/render_migration_pr.py`
- Create: `tests/email_operations/test_project_sync.py`
- Create: `tests/email_operations/test_repository_validator.py`
- Create: `github-campaign-os/project-sync-report.json`
- Create: `github-campaign-os/migration-pr.md`
- Modify: `.gitignore`
- Modify: `README.md`

- [ ] **Step 1: Add failing Project reconciliation tests**

Using fake GraphQL responses, cover:

- exact private user-owned Project resolution by owner and title;
- hard failure on duplicate titles;
- creation of built-in Status options and exactly 28 custom fields;
- single-select option reconciliation without duplicate options;
- addition of all canonical Issues and matching repository pull requests;
- field mirroring from Issue Operations Snapshots;
- Issue-versus-Project drift failure;
- creation of exactly six named views with approved layouts and filters;
- preservation of unrelated private Projects;
- dry-run default, explicit `--apply`, and zero-action second dry-run.

Project draft items must fail validation.

- [ ] **Step 2: Implement Project reconciliation**

Resolve resources by stable owner, repository, Project title, Issue key, pull request number, field name, and option name. Never assume Project number `4`, even if it is currently the next likely number. The synchronizer creates the Project as private, links the repository, adds Issues and PRs, mirrors fields, and creates the six views. It validates readiness pairs but never advances Messaging State, Flow State, Stage, scheduling, activation, or sending.

API-created views must use:

```text
01 · Campaign Portfolio -> TABLE_LAYOUT
02 · Email Production -> BOARD_LAYOUT
03 · Review & Pull Requests -> TABLE_LAYOUT
04 · Launch Calendar -> ROADMAP_LAYOUT
05 · Performance -> TABLE_LAYOUT
06 · Messaging & Automation Readiness -> TABLE_LAYOUT
```

Where the current API cannot set board column field, view ordering, roadmap date fields, grouping, sorting, or built-in workflows, emit an explicit `browser_configuration_required` checklist. Never report those settings complete from intent alone.

- [ ] **Step 3: Implement full read-back verification**

`verify_project.py` compares remote Project state with the schema and Issue snapshots. It reports privacy, repository link, Issue count, PR count, draft-item count, native Status options, 28 custom fields and options, six view names/layouts/filters, readiness-pair violations, field drift, and settings still requiring browser verification.

- [ ] **Step 4: Implement a repository release validator**

Reject:

- tracked `exports/`, `.claude/`, `.playwright-mcp/`, browser profiles, `node_modules/`, caches, `.env` files, and worktree internals;
- secret-looking assignments containing non-placeholder values;
- tracked files larger than 20 MiB unless explicitly allowlisted;
- invalid JSON;
- manifest counts other than 69 Issues, 7 Campaigns, and 53 Emails;
- active MailerLite execution paths;
- stale generated manifest or Issue snapshot drift;
- Project schema counts other than 28 custom fields and six native views;
- contradictory Execution Mode, Messaging State, Flow Required, or Flow State combinations;
- any active document naming MailerLite as the marketing platform.

The validator prints safe path and rule names only, never file contents from secret or PII candidates.

- [ ] **Step 5: Implement migration PR body rendering**

Read the Issue sync report to obtain the real Campaign OS migration Task number. Render a complete PR body with a closing reference, Campaign OS scope, authority sources, changed-file groups, test evidence, privacy validation, approved-copy impact, consent impact, Messaging impact, Flow impact, activation impact, risks, rollback, and the explicit statement `Merge does not configure Shopify, schedule, activate, or send email`.

- [ ] **Step 6: Verify locally and commit**

```bash
python3 -m unittest tests.email_operations.test_project_sync tests.email_operations.test_repository_validator -v
python3 -m tools.github_campaign_os.sync_project --help
python3 -m tools.github_campaign_os.verify_project --help
python3 -m tools.github_campaign_os.validate_repository
git diff --check -- tools/github_campaign_os tests/email_operations github-campaign-os README.md .gitignore
git add tools/github_campaign_os tests/email_operations/test_project_sync.py tests/email_operations/test_repository_validator.py github-campaign-os/project-sync-report.json github-campaign-os/migration-pr.md .gitignore README.md
git commit --only tools/github_campaign_os tests/email_operations/test_project_sync.py tests/email_operations/test_repository_validator.py github-campaign-os/project-sync-report.json github-campaign-os/migration-pr.md .gitignore README.md -m "feat(github): synchronize and verify Campaign OS Project"
```

The committed reports remain explicit pre-apply baselines until live synchronization occurs.

---

## Task 8: Create the 69 canonical Issues using the master PAT

**Files:**

- Modify: `github-campaign-os/issue-sync-report.json`
- Modify: `github-campaign-os/migration-pr.md`
- Modify: `PROJECT.md`

- [ ] **Step 1: Load the PAT without exposing it and verify scope**

Use a narrowly parsed value, never source or print the entire `.env`:

```bash
github_master_pat_value=$(awk -F= '$1=="GITHUB_PAT_MASTER_TOKEN"{print substr($0,index($0,"=")+1); exit}' /Users/vMac/.env)
test -n "$github_master_pat_value"
GH_TOKEN="$github_master_pat_value" gh api graphql -f query='{ viewer { login } }' --jq .data.viewer.login
GH_TOKEN="$github_master_pat_value" gh repo view vincent-laroche/email-marketing-ops --json nameWithOwner,isPrivate,defaultBranchRef
```

Expected result: viewer `vincent-laroche`, exact repository, private `true`, default branch `main`. Abort on any mismatch.

- [ ] **Step 2: Run Issue synchronization in dry-run mode**

```bash
GH_TOKEN="$github_master_pat_value" python3 -m tools.github_campaign_os.sync_issues
```

Expected plan on a clean first run: create 69 Issues, create only missing approved labels, add 53 sub-issue relationships, and perform no close/reopen action. If matching stable keys already exist, the action count may be lower but duplicate keys must be zero.

- [ ] **Step 3: Apply once and prove idempotence**

```bash
GH_TOKEN="$github_master_pat_value" python3 -m tools.github_campaign_os.sync_issues --apply
GH_TOKEN="$github_master_pat_value" python3 -m tools.github_campaign_os.sync_issues
GH_TOKEN="$github_master_pat_value" python3 -m tools.github_campaign_os.verify_issues --write
```

Expected second dry-run: zero actions. Verification must show 69 Issues, counts `7/53/8/0/1`, 53 parent links, zero duplicates, zero missing keys, zero snapshot drift, and zero managed-label drift.

- [ ] **Step 4: Render the real migration PR body and update handoff**

```bash
python3 -m tools.github_campaign_os.render_migration_pr --write
```

Confirm the body closes the real Campaign OS migration Task and contains no token, PII, absolute local path, or invented approval.

- [ ] **Step 5: Commit live read-back evidence and clear the shell value**

```bash
git add github-campaign-os/issue-sync-report.json github-campaign-os/migration-pr.md PROJECT.md
git commit --only github-campaign-os/issue-sync-report.json github-campaign-os/migration-pr.md PROJECT.md -m "docs(github): record canonical Campaign OS issues"
unset github_master_pat_value
```

---

## Task 9: Open the connector-readable migration pull request

**Files:**

- Read: `github-campaign-os/migration-pr.md`
- Read: all committed migration changes

- [ ] **Step 1: Run the complete local release preflight**

```bash
python3 -m unittest discover -s tests -v
python3 -m tools.github_campaign_os.build_manifest --check
python3 -m tools.github_campaign_os.validate_repository
python3 mailersend/build_service_emails.py --check
npm --prefix tools/figma-email-blocks-plugin ci
npm --prefix tools/figma-email-blocks-plugin run build
git diff --check
git status --short --branch
```

The worktree must be clean except for explicitly identified unrelated user work. If unrelated changes remain, stop before pushing and isolate the migration without discarding them.

- [ ] **Step 2: Verify ancestry and push the existing branch normally**

```bash
git fetch origin --prune
git merge-base --is-ancestor origin/main HEAD
git push origin journey-emails-v3-rebuild
```

Abort if `origin/main` is not an ancestor. Never force-push.

- [ ] **Step 3: Open a draft PR through the real Issue**

Load the PAT safely as in Task 8, then:

```bash
GH_TOKEN="$github_master_pat_value" gh pr create --repo vincent-laroche/email-marketing-ops --base main --head journey-emails-v3-rebuild --draft --title "Task — Build Email Marketing Campaign OS" --body-file github-campaign-os/migration-pr.md --label email-marketing
```

Read the PR back and verify base, head, draft state, label, closing Issue reference, complete body, and private repository. Do not merge yet.

- [ ] **Step 4: Record the PR number without creating a Project-only fact**

Run Issue verification so the linked PR is visible through the migration Task timeline. Add a dated migration-Task comment stating that the draft PR exists and that no sending, scheduling, or Shopify mutation occurred.

---

## Task 10: Create and configure the private Campaign OS Project

**Files:**

- Modify: `github-campaign-os/project-sync-report.json`
- Modify: `README.md`
- Modify: `PROJECT.md`

- [ ] **Step 1: Dry-run the complete Project build**

Load the PAT safely with the narrow `awk` command from Task 8, then:

```bash
GH_TOKEN="$github_master_pat_value" python3 -m tools.github_campaign_os.sync_project
```

Expected first-run plan:

- create one private `Email Marketing — Campaign OS` Project;
- link `vincent-laroche/email-marketing-ops`;
- configure built-in Status and 28 custom fields;
- add 69 Issues and the open migration PR;
- mirror Issue snapshots into Project fields;
- create six views;
- report browser-only configuration still outstanding.

No Project with the same owner and title may already exist twice.

- [ ] **Step 2: Apply once and prove API idempotence**

```bash
GH_TOKEN="$github_master_pat_value" python3 -m tools.github_campaign_os.sync_project --apply
GH_TOKEN="$github_master_pat_value" python3 -m tools.github_campaign_os.sync_project
```

Expected second dry-run: zero API actions, with browser-only settings listed separately rather than misreported as API drift.

- [ ] **Step 3: Configure the six views in GitHub's UI**

Use the browser because current Project APIs do not expose every ordering, board-column, roadmap-date, grouping, sorting, card-field, and workflow control.

Configure and save:

1. `01 · Campaign Portfolio`: Table; `Work Type:Campaign`; approved columns; Send Date ascending then Priority ascending.
2. `02 · Email Production`: Board; `Work Type:Email -Status:Done`; column field Stage; approved card fields; all ten Stage columns in lifecycle order.
3. `03 · Review & Pull Requests`: Table; `is:pr is:open`; approved columns.
4. `04 · Launch Calendar`: Roadmap; Production Start and Send Date; Month zoom; group by Campaign Type.
5. `05 · Performance`: Table; `Work Type:Email Stage:Sent,Measuring,Complete`; approved columns; Send Date descending.
6. `06 · Messaging & Automation Readiness`: Table; `Work Type:Email`; approved Shopify
   implementation columns; Status, Parent Issue, then Title sort. Verify the documented filter
   recipes for Missing Shopify implementation, Missing Flow, Ready for activation, Ready for
   scheduling, and Live automations without saving extra views.

Drag tabs into exact numerical order and delete any default extra view so exactly six remain.

- [ ] **Step 4: Configure approved built-in workflows**

In Project Workflows:

- enable auto-add for the canonical repository with `label:email-marketing`;
- set newly added items to Status `Inbox` when no synchronized state exists;
- keep or enable closed Issue to Done;
- keep or enable merged pull request to Done;
- leave auto-archive disabled;
- do not create any workflow from Approval to Scheduled, sending, Shopify activation, or metrics.
- do not create any workflow that advances Messaging State, Flow Required, or Flow State.

Auto-add affects new or updated matching items, so the synchronizer remains responsible for the initial 69 Issues and migration PR.

- [ ] **Step 5: Perform visual and GraphQL read-back**

Verify Project privacy, repository link, six tab names/order, layouts, filters, fields, board columns, roadmap dates, group/sort settings, and workflows. Confirm the draft PR appears in Review & Pull Requests and readiness states remain evidence-backed. Capture screenshots only if they contain no PII.

- [ ] **Step 6: Write verification, update docs, commit, and push to the open PR**

```bash
GH_TOKEN="$github_master_pat_value" python3 -m tools.github_campaign_os.verify_project --write
python3 -m tools.github_campaign_os.validate_repository
git add github-campaign-os/project-sync-report.json README.md PROJECT.md
git commit --only github-campaign-os/project-sync-report.json README.md PROJECT.md -m "docs(github): verify Email Marketing Campaign OS"
git push origin journey-emails-v3-rebuild
unset github_master_pat_value
```

The report must show 69 Issue items, at least one PR item, zero draft items, built-in Status plus 28 custom fields, exactly six native views, zero readiness-pair violations, zero Issue-field drift, and the verified Project URL.

---

## Task 11: Complete the PR, merge normally, and publish final read-back

**Files:**

- No new repository files after merge
- Update remotely: migration pull request and Campaign OS migration Task comment

- [ ] **Step 1: Re-run completion evidence immediately before ready-for-review**

```bash
python3 -m unittest discover -s tests -v
python3 -m tools.github_campaign_os.build_manifest --check
python3 -m tools.github_campaign_os.validate_repository
python3 mailersend/build_service_emails.py --check
npm --prefix tools/figma-email-blocks-plugin run build
git diff --check
git status --short --branch
```

Update the PR body with exact test results and Project verification. Do not reuse stale output.

- [ ] **Step 2: Mark ready and verify GitHub checks**

```bash
github_master_pat_value=$(awk -F= '$1=="GITHUB_PAT_MASTER_TOKEN"{print substr($0,index($0,"=")+1); exit}' /Users/vMac/.env)
test -n "$github_master_pat_value"
campaign_os_pr_number=$(GH_TOKEN="$github_master_pat_value" gh pr view journey-emails-v3-rebuild --repo vincent-laroche/email-marketing-ops --json number --jq .number)
test -n "$campaign_os_pr_number"
GH_TOKEN="$github_master_pat_value" gh pr ready --repo vincent-laroche/email-marketing-ops "$campaign_os_pr_number"
GH_TOKEN="$github_master_pat_value" gh pr checks --repo vincent-laroche/email-marketing-ops "$campaign_os_pr_number" --watch
```

All required checks must pass and no requested changes may remain.

- [ ] **Step 3: Merge through GitHub without squashing or rewriting history**

```bash
GH_TOKEN="$github_master_pat_value" gh pr merge --repo vincent-laroche/email-marketing-ops "$campaign_os_pr_number" --merge --delete-branch=false
```

Use a merge commit so all purpose-specific commits and prior repository history remain reachable.

- [ ] **Step 4: Verify `main` and the Project after merge**

```bash
git fetch origin --prune
git switch main
git pull --ff-only origin main
git rev-parse main
git rev-parse origin/main
```

Then run Issue and Project dry-runs with the PAT. Expected result: zero reconciliation actions after the merged PR and closed migration Task are reflected. The PR and Task may be Status Done through approved built-in automation; no Email Stage or send state may change.

- [ ] **Step 5: Publish the final audit in the connector-readable Task**

Add one dated comment to the Campaign OS migration Task containing:

- merged PR URL and revision;
- Project URL and private status;
- repository-link verification;
- counts for Issues, Work Types, parent links, PR items, 28 custom fields, six views, and draft items;
- zero drift and zero duplicate stable keys;
- confirmation that `vincent-laroche/email-marketing` was untouched;
- confirmation that no email was sent, scheduled, activated, or populated with invented metrics.
- confirmation that no source, preview, approval, or merge event was misreported as Shopify
  implementation evidence.

Unset `campaign_os_pr_number` and the PAT shell value. The final handoff must link the repository, Project, migration Issue, migration PR, design spec, implementation plan, and verification reports.

---

## Plan self-review checklist

- [ ] Every approved Campaign OS work type, all 28 custom fields, label family, hierarchy rule, automation, and all six native views are represented.
- [ ] Issues and pull requests remain sufficient for Notion and ChatGPT connectors without Project access.
- [ ] Project-specific Shopify platform truth overrides the generic MailerLite example.
- [ ] The existing canonical repository history is preserved and delivery occurs through a pull request.
- [ ] Every live write is dry-run first, explicit apply second, and idempotence check third.
- [ ] No step authorizes email sending, scheduling, activation, Shopify customer mutation, public preview publication, or invented metrics.
- [ ] No placeholder language or unresolved implementation decision remains in this plan.
