# Email Marketing Project-Agent Suite — Design

**Date:** 2026-08-25  
**Owner:** Vincent Laroche  
**Tracking:** [#80](https://github.com/vincent-laroche/email-marketing-ops/issues/80)  
**Status:** Approved in chat; awaiting written-spec review before implementation

## 1. Objective

Build a project-local suite of twelve bounded agents that helps operate the Hair Solutions Co.
Email Marketing programme without losing authority, evidence, or approval boundaries between
specialists.

The suite must match the current programme:

- `Email Reference File/` is authoritative for campaigns, journeys, copy, structure, and module
  presence;
- Shopify Messaging and Shopify Flow are the sole marketing execution platforms;
- GitHub Issues and pull requests are the Campaign OS record, with Project #4 as the synchronized
  planning surface;
- MailerLite is legacy/reference only and must not be restored as a marketing platform;
- MailerSend is transactional only;
- local builds, private preview artifacts, public previews, platform drafts, activation, scheduling,
  and sends are separate evidence and approval states;
- customer data, consent, and real operational values may never be invented.

The suite is an operating layer, not a new source of business truth. Agents load current authority
at run time and return bounded evidence. They do not retain mutable programme facts inside their
prompts.

## 2. Why twelve agents

Four broad agents would accumulate too many permissions and would repeatedly reload unrelated
context. Eight agents cover the historical MailerLite role set but omit three current systems:
Campaign OS engineering, preview/publication engineering, and Shopify notification templates.

Twelve agents provide one owner per materially different workflow while retaining simple routing:

1. four upgraded project agents;
2. five recovered historical capabilities translated to Shopify;
3. three project-native specialists for Campaign OS, previews, and notifications.

The root Codex agent remains the orchestrator. Specialist agents do not spawn other agents.

## 3. Permission classes

Every role belongs to exactly one permission class.

### R — Read-only

May inspect repository files and read authorized external evidence. May not modify repository files,
GitHub, Shopify, customer data, audiences, DNS, or another platform.

### L — Local writer

May modify only explicitly owned repository files and run local validation. May not modify GitHub
planning state or any marketing platform. Commits and integration remain with the parent unless the
task explicitly delegates them.

### D — Approval-gated draft operator

Defaults to read-only. With explicit current-task approval, may create or update exactly one named
Shopify draft or disabled automation and must re-fetch it completely. May never schedule, activate,
send, publish, delete, broaden the named audience, or modify customer data.

No project agent may send marketing email. No permission class weakens `AGENTS.md`.

## 4. Agent inventory

### 4.1 `email-project-manager` — R

**Owns:** Campaign OS health, dependency order, priority recommendations, blocked-state quality, and
specialist routing.

**Must do:**

- reconcile the live Project, canonical Issues, pull requests, manifests, ledgers, and current
  repository state;
- distinguish planning fields from platform-evidence fields;
- rank the next three safe tasks by consent/deliverability, revenue protection, dependency value,
  customer impact, evidence readiness, and scope size;
- provide an exact proposed Project change set when drift exists.

**Must not do:** mutate GitHub while labeled read-only, infer Shopify state, create work merely to
fill the board, or operate a marketing platform.

### 4.2 `email-lifecycle-architect` — R

**Owns:** one named journey's implementation contract.

**Output:** trigger, channel eligibility, consent premise, exclusions, message sequence, delays,
collision precedence, exits, re-enrolment, dynamic-data contract, platform mapping, test matrix,
rollback, KPIs, unresolved decisions, and activation approval gate.

### 4.3 `email-producer` — L

**Owns:** one named Email Issue's complete local artifact.

**Must do:** use a file allowlist, trace copy and module composition to authority, preserve generated
source ownership, run applicable builders and validators, and report every unresolved data or
consent dependency.

**Must not do:** edit unrelated emails, invent content or data, modify platform drafts, or call a
local render release evidence.

### 4.4 `email-deliverability-release-reviewer` — R

**Owns:** final fail-closed release review before Vincent decides whether to schedule or activate.

**Verdict dimensions:** sender/domain, consent/audience, exclusions, content/claims, Liquid/dynamic
data, links/tracking, desktop/mobile evidence, timing/frequency, automation collisions/exits,
rollback, platform read-back, and exact approval evidence.

**Verdict:** `SHIP`, `FIX THEN REVIEW`, or `BLOCK`. `SHIP` is a recommendation and never a send or
activation authorization.

### 4.5 `email-audience-consent-steward` — R

**Owns:** Shopify audience and consent safety.

**Must inspect:** source and date of consent, channel eligibility, tags/segments, suppressions,
exclusions, audience overlap, customer-state assumptions, safe-start containment, counts, rollback,
and evidence freshness. It returns an exact audience brief; it never tags or modifies customers.

### 4.6 `email-design-module-specialist` — L

**Owns:** one reusable email module or bounded module-system change.

**Must preserve:** Email Reference File palette, transparent page background, approved copy,
responsive email-client compatibility, accessibility, editable/dynamic regions, and builder/source
ownership. It must not assemble an entire campaign unless the parent routes that work to
`email-producer`.

### 4.7 `email-preview-qa-engineer` — L

**Owns:** the fixture compiler and preview safety contract.

**Must verify:** fictional reusable personas, no PII/tokens/customer URLs, inert customer-specific
links, fail-closed Liquid, HTML plus desktop/mobile screenshots, exact SHA/PR/Issue provenance,
temporary private artifacts, public-approval filtering, append-only publication provenance,
atomic gallery generation, `noindex`, and `robots.txt`.

It may prepare and validate workflows but may not enable Pages, dispatch publication, set a custom
domain, or change Cloudflare without separately explicit approval.

### 4.8 `campaign-os-engineer` — L

**Owns:** repository code and validation behind Campaign OS Project #4.

**Must preserve:** 69 compiled-Issue invariant, filed-Issue distinction, generated-section
ownership, exact campaign key casing, reproducible manifests from committed bytes, Project schema,
idempotent sync, evidence-only platform fields, and GitHub workflow least privilege.

It may prepare Issue/Project mutations and dry runs. Live GitHub writes remain parent-owned unless
the current task explicitly delegates the exact mutation.

### 4.9 `shopify-messaging-campaign-operator` — D

**Owns:** one explicitly approved Shopify Messaging draft.

**Preconditions:** accepted Email artifact, approved audience brief, exact store/account, exact
campaign/Email Issue, sender evidence, and explicit current-task draft-write approval.

**After a write:** re-fetch name/ID, draft state, subject, preview text, sender, content, links,
tracking, audience/exclusions, schedule state, and recipient estimate. It must prove unscheduled and
unsent before returning.

### 4.10 `shopify-flow-automation-builder` — D

**Owns:** one accepted lifecycle architecture implemented as a disabled Shopify Flow automation.

**After a write:** re-fetch the complete graph and verify one intended entry path, conditions,
branches, waits, message actions, collision guards, exits, re-enrolment behavior, and disabled
state. It never activates or changes customers/tags outside the approved disabled graph.

### 4.11 `email-performance-analyst` — R

**Owns:** one named measurement question after verified sends exist.

**Must normalize:** account/store, timezone, date range, send cohort, exclusions, attribution
window, metric definitions, and data completeness. Opens are directional; clicks, conversions,
revenue, complaints, unsubscribes, and bounces take priority. Findings must separate observation,
inference, and causal confidence.

### 4.12 `shopify-notification-template-specialist` — D

**Owns:** one explicitly approved native Shopify notification template or named batch.

**Must treat notifications separately from marketing:** resolve the template-specific design
authority, preserve Shopify transactional Liquid, capture pre-write source, apply only the approved
change, re-fetch byte-equivalent content, and record rendered/browser evidence. It never sends a
notification, edits gift-card delivery, changes unrelated templates, or expands the approved batch.

## 5. Shared run-time contract

All twelve definitions must require `.codex/agents/EMAIL-AGENT-CONTRACT.md` and obey the following
run sequence.

### 5.1 Intake

1. Resolve repository root and current branch/worktree.
2. Read `PROJECT.md`, then `AGENTS.md`, then the shared agent contract.
3. Resolve the canonical Issue or filed Task Issue. If the surface has no Issue, stop and return the
   proposed Issue payload to the parent.
4. Identify exact scope, permission class, owned files/resources, acceptance criteria, and stopping
   condition.
5. Read only the authority sources needed for that scope.

### 5.2 Evidence freshness

Record:

- Issue number and `campaign-os-key` where applicable;
- local branch, base SHA, and inspected SHA;
- authority files used;
- external account/store/resource identifiers without secrets;
- evidence capture time and timezone;
- known stale, missing, or conflicting evidence.

Never embed volatile programme counts or live-state claims in an agent definition. Re-read them from
current authority.

### 5.3 Evidence levels

Agents use these exact levels:

1. `AUTHORITY` — governing source was inspected;
2. `SOURCE` — current implementation/source was inspected;
3. `LOCAL_VALIDATED` — applicable local tests/build/render passed;
4. `PLATFORM_DRAFT_VERIFIED` — exact external draft or disabled automation was re-fetched;
5. `LIVE_RELEASE_VERIFIED` — customer-facing/live state was independently read back.

An agent may only claim the highest level it actually reached. A source sync, green CI run, local
render, merge, or approval does not imply a live release.

### 5.4 Concurrency

- Treat every unrelated change as another person's work.
- Own only named files/resources.
- Never reset, clean, discard, or broadly format a shared worktree.
- Re-read an owned file immediately before editing and again before handing off.
- Stop when another writer has changed the same owned surface and the changes cannot be safely
  combined.
- The parent owns cross-agent integration and conflicting writes.

### 5.5 Findings and GitHub

Findings belong to the current Issue's human-maintained `Blockers`, `Evidence`, `Decisions`,
`Results`, or `Learnings` sections. Agents without GitHub write authority return an exact bounded
comment/Issue payload to the parent; they do not leave a prose-only backlog.

Compiled Issues retain their hidden `campaign-os-key`; filed Issues never receive one.

### 5.6 Standard evidence packet

Every agent returns:

```text
Agent:
Issue / campaign-os-key:
Scope:
Permission class:
Owned files or external resources:
Authority sources:
Base and inspected/result SHA:
Work performed or findings:
Checks and read-back:
Highest evidence level:
External state changed: yes/no; exact resource if yes
Blockers and decisions:
Canonical GitHub update required:
Recommended next agent:
Stopping condition reached:
```

## 6. Routing matrix

| Work trigger | Primary agent | Required next gate |
|---|---|---|
| Board drift, prioritization, dependency choice | project manager | parent-approved Project update |
| Journey trigger/branch/collision design | lifecycle architect | audience steward, then Flow builder |
| Consent, tag, segment, suppression question | audience/consent steward | lifecycle or release reviewer |
| Complete local email build/revision | email producer | preview QA |
| Reusable module or design-system change | design/module specialist | producer or preview QA |
| Liquid fixture, screenshot, gallery, Pages workflow | preview QA engineer | Campaign OS engineer or release reviewer |
| Manifest, Issue sync, Project sync, Actions governance | Campaign OS engineer | tests and parent integration |
| Shopify Messaging draft configuration | Messaging campaign operator | release reviewer |
| Shopify Flow disabled graph build | Flow automation builder | release reviewer |
| Final launch candidate | deliverability/release reviewer | Vincent decision |
| Post-send measurement | performance analyst | Project manager / Issue learning |
| Native Shopify transactional notification | notification specialist | rendered evidence and Vincent decision |

Agents report `not applicable` rather than manufacturing work outside their trigger.

## 7. Definition format and discovery

Definitions live under `.codex/agents/*.md` using the existing YAML-frontmatter format displayed by
Codex. Each definition contains:

- unique kebab-case `name`;
- precise description including permission class and invocation trigger;
- minimal tool allowlist;
- explicit disallowed write tools for read-only agents;
- calibrated `maxTurns`;
- mission, mandatory inputs, operating pass, stop conditions, hard boundaries, and output contract;
- a mandatory reference to the shared contract;
- a prohibition on child-agent delegation.

The shared contract and routing document have no agent frontmatter and therefore are not discovered
as runnable agents.

## 8. Validation

Add a Python stdlib validator and tests that fail when:

- the suite does not contain exactly twelve runnable definitions;
- a name or description is missing or duplicated;
- a read-only role exposes `Write`, `Edit`, or `NotebookEdit`;
- an agent omits the shared contract, evidence packet, stopping condition, GitHub Issue requirement,
  or no-delegation rule;
- an active marketing role proposes MailerLite as a campaign/lifecycle platform;
- an agent can send, schedule, activate, publish, change customer data, or bypass a required approval;
- a draft operator lacks full read-back and fail-closed preconditions;
- volatile counts, credentials, or obsolete absolute project paths are embedded in definitions.

Validation must run without external credentials and without touching GitHub or Shopify.

## 9. Delivery

Implementation is isolated from the dirty `journey-emails-v3-rebuild` worktree on branch
`codex/email-agent-suite`, based on current `origin/main`. Delivery contains only:

- twelve agent definitions;
- the shared contract and routing reference;
- the validator and tests;
- documentation and the `PROJECT.md` session record;
- Issue #80 evidence and a reviewable pull request.

Installing the suite makes no Shopify, MailerLite, MailerSend, audience, customer, campaign, Flow,
send, schedule, activation, GitHub Pages, DNS, or public-preview change.

## 10. Acceptance criteria

- Codex discovers all twelve project-local agents with accurate names and permission labels.
- The four existing roles retain their useful intent with stronger authority, evidence, and handoff
  contracts.
- All eight additional roles have non-overlapping ownership and explicit invocation triggers.
- Historical MailerLite role value is recovered without restoring MailerLite marketing operations.
- The shared contract prevents stale programme facts and cross-agent evidence loss.
- Static validation and tests pass from a clean checkout.
- Issue #80 and the pull request contain the canonical implementation evidence.
- No external marketing or publication state changes.
