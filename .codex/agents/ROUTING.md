# Email Marketing Agent Routing

Use this guide to select the smallest specialist that owns the work. The root Codex agent is the
orchestrator. Specialists are leaves: they do not invoke one another.

## 1. Routing principles

1. Route by the system boundary being changed or judged, not by words in the request.
2. Use one writer per file or external resource.
3. Separate architecture, production, platform drafting, release review, and activation.
4. Use read-only specialists early; use external operators only after their prerequisites exist.
5. Do not invoke every reviewer automatically. Invoke only roles whose evidence can change the
   decision.
6. A role may return `not applicable` when its trigger is absent.
7. The parent integrates evidence packets and records GitHub updates.

## 2. Role triggers

### `email-project-manager`

Invoke for Project #4 health, priority, dependencies, blocked-state quality, next-task selection,
and specialist routing. Do not invoke for repository code changes, email production, or platform
configuration. It proposes board mutations but remains read-only.

### `email-lifecycle-architect`

Invoke when a named journey needs trigger, sequence, eligibility, collision, exit, re-enrolment,
data, test, rollback, or measurement design. Do not invoke for literal HTML changes or an already
accepted architecture unless implementation uncovers a material gap.

### `email-producer`

Invoke for a complete local Email artifact or a bounded revision to one Email Issue. Do not invoke
for reusable module-system work, platform draft configuration, consent analysis, or release signoff.

### `email-deliverability-release-reviewer`

Invoke after required source, preview, audience, and platform-draft evidence exists for one named
release candidate. Do not use it as an early design reviewer or to fill missing evidence itself.

### `email-audience-consent-steward`

Invoke for consent provenance, channel eligibility, segment/tag definitions, suppressions,
exclusions, overlap, safe-start containment, and audience-count evidence. Do not invoke to tag
customers or configure the campaign.

### `email-design-module-specialist`

Invoke for a reusable module, builder primitive, module token, responsive module behavior, or
module-level design fidelity. Do not invoke for whole-email assembly when modules already exist.

### `email-preview-qa-engineer`

Invoke for fixture rendering, Liquid support, preview safety, screenshots, provenance, Actions
artifacts, the public gallery, publication ledger, Pages workflow code, or preview-readiness
classification. Do not invoke merely because an email contains HTML; route source production first.

### `campaign-os-engineer`

Invoke for manifest generation, Issue synchronization, Project synchronization, repository
validators, schema, workflow permissions, publication-ledger integration, or GitHub drift. Do not
invoke to prioritize the portfolio or decide marketing strategy.

### `shopify-messaging-campaign-operator`

Invoke only for one explicitly approved Shopify Messaging draft after the local artifact, audience
brief, and sender prerequisites are ready. Do not invoke for Flow-orchestrated journeys or any
schedule/send action.

### `shopify-flow-automation-builder`

Invoke only for one accepted lifecycle architecture that must be implemented as a disabled Shopify
Flow graph. Do not invoke before consent/collision rules are accepted or for native Messaging-only
automations.

### `email-performance-analyst`

Invoke only after verified sends produce data or when defining exact metric semantics for a named
measurement question. Do not invent benchmarks or infer results from previews/drafts.

### `shopify-notification-template-specialist`

Invoke only for a named native Shopify transactional notification template or explicitly approved
batch. Do not mix notification design authority with campaign email authority and do not treat a
notification edit as a marketing campaign operation.

## 3. Standard workflows

### A. Local Email production

```text
email-project-manager (only if selection/prioritization is needed)
  → email-producer
  → email-preview-qa-engineer
  → email-deliverability-release-reviewer when release evidence is otherwise complete
```

Add `email-design-module-specialist` before the producer when a required reusable module is absent or
incorrect. Add `email-audience-consent-steward` before release when audience evidence is involved.

### B. Lifecycle journey through Shopify Flow

```text
email-lifecycle-architect
  → email-audience-consent-steward
  → email-producer for each scoped Email
  → email-preview-qa-engineer
  → shopify-flow-automation-builder with explicit draft-write approval
  → email-deliverability-release-reviewer
  → Vincent activation decision outside the agent suite
```

The Flow builder receives an accepted architecture; it does not redesign collision rules while
writing. Any material implementation conflict routes back through the parent to the architect.

### C. Shopify Messaging one-time or native automation draft

```text
email-producer
  → email-preview-qa-engineer
  → email-audience-consent-steward
  → shopify-messaging-campaign-operator with explicit draft-write approval
  → email-deliverability-release-reviewer
  → Vincent schedule/send decision outside the agent suite
```

### D. Campaign OS repository change

```text
email-project-manager for the operational requirement when needed
  → campaign-os-engineer
  → repository tests and drift verification
  → parent integration and GitHub recording
```

The project manager must not mutate the board while labeled read-only. The engineer may implement
local sync/validation code, but live GitHub mutations are parent-owned unless explicitly delegated.

### E. Preview and GitHub Pages work

```text
email-preview-qa-engineer
  → campaign-os-engineer for Issue/Project/workflow integration
  → email-deliverability-release-reviewer for a named public candidate
  → Vincent publication approval outside the agent suite
```

Pages enablement, manual workflow dispatch, custom domain, and Cloudflare DNS are separate gates.
Private artifacts do not become public because a pull request merges.

### F. Post-send measurement

```text
email-performance-analyst
  → email-project-manager for priority/learning implications
  → parent records Results/Learnings on the canonical Issue
```

### G. Native Shopify notifications

```text
shopify-notification-template-specialist with explicit template-write approval
  → rendered/browser evidence
  → email-deliverability-release-reviewer only when sender/deliverability release factors apply
  → Vincent decision for any customer-facing rollout
```

## 4. Safe parallel work

The parent may run these in parallel only after scope and evidence inputs are stable:

- lifecycle architecture and a read-only consent inventory, when neither depends on the other's
  undecided rule;
- preview QA for different Email files with no shared compiler change;
- release review dimensions that are genuinely independent, followed by parent synthesis;
- performance analysis for separate campaigns with fixed metric definitions.

Do not parallelize:

- two writers on the same email, module builder, manifest, workflow, or external draft;
- a platform operator with an upstream producer still changing the artifact;
- preview publication code and live publication;
- a Flow builder while collision/exit decisions remain open;
- a notification batch across multiple browser writers.

## 5. Handoff requirements

An upstream packet is acceptable only when it names the Issue, exact scope, authority, SHA,
evidence level, blockers, and stopping condition. The downstream agent re-verifies cheap,
drift-prone inputs; it does not blindly trust a previous agent's prose.

Minimum prerequisites by role:

| Downstream role | Required upstream evidence |
|---|---|
| producer | Issue, source deck/module map, file allowlist, data assumptions |
| preview QA | exact artifact SHA, Issue, supported fixture state, local source status |
| Messaging operator | accepted artifact, audience brief, sender proof, explicit write approval |
| Flow builder | accepted architecture, consent premise, collision/exit rules, explicit write approval |
| release reviewer | source/preview/platform evidence, audience proof, exact candidate |
| performance analyst | verified send identity, date/cohort/timezone, metric source |

## 6. Stop and reroute

The current agent stops and returns to the parent when:

- the request belongs to another role;
- an upstream evidence packet is incomplete;
- authority conflicts;
- the Issue is missing;
- scope expands materially;
- an external approval is absent or ambiguous;
- another writer changed the owned surface;
- the platform state differs from the approved target;
- a validator fails for a reason outside the role's ownership.

The agent names the correct next role but does not invoke it. The parent decides whether and when to
continue.
