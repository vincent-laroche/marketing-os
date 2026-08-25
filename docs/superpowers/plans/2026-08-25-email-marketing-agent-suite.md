# Email Marketing Project-Agent Suite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Install twelve detailed project-local Email Marketing agents with one shared operating contract, deterministic routing, and automated safety validation.

**Architecture:** Runnable Markdown definitions live in `.codex/agents/`; a non-runnable shared contract and routing guide keep cross-role rules consistent without duplicating volatile programme state. A Python stdlib validator treats the suite as configuration and rejects missing roles, unsafe tools, weak approval gates, obsolete platform assumptions, or incomplete handoff contracts.

**Tech Stack:** Markdown with YAML-style frontmatter, Python 3 stdlib, `unittest`, existing repository governance and Campaign OS artifacts.

**Spec:** `docs/superpowers/specs/2026-08-25-email-marketing-agent-suite-design.md`

## Global Constraints

- `Email Reference File/` remains authoritative for campaign structure, copy, and module presence.
- Shopify Messaging and Shopify Flow are the sole marketing campaign/lifecycle platforms.
- MailerLite is legacy/reference only; MailerSend is transactional only.
- No agent may send marketing email.
- Scheduling, activation, public preview publication, DNS, audiences, and customer data remain separately approval-gated.
- Findings must resolve to a canonical or filed GitHub Issue; filed Issues never receive `campaign-os-key`.
- Agents must distinguish authority, source, local validation, platform-draft verification, and live-release verification.
- Preserve unrelated dirty work; implementation remains isolated on `codex/email-agent-suite`.
- Python additions use the standard library only.
- Specialist agents never delegate or spawn child agents.

---

### Task 1: Agent-Suite Validator Contract

**Files:**
- Create: `tests/email_operations/test_project_agents.py`
- Create: `tools/validate_project_agents.py`

**Interfaces:**
- Consumes: `.codex/agents/*.md` runnable definitions and the expected role inventory.
- Produces: `validate(root: Path) -> list[str]` and CLI exit code `0` only when the complete suite is safe.

- [ ] **Step 1: Write failing inventory and safety tests**

Create tests that assert the exact twelve names, the shared-contract reference, required prompt
sections, permission-specific tool boundaries, approval-gated draft safeguards, no delegation, and
no active MailerLite marketing instructions.

```python
class ProjectAgentSuiteTest(unittest.TestCase):
    def test_complete_suite_passes_validator(self):
        self.assertEqual([], validate(ROOT))

    def test_expected_inventory_is_exact(self):
        self.assertEqual(EXPECTED_NAMES, discovered_names(ROOT))

    def test_validator_rejects_read_only_write_tool(self):
        with temporary_suite(ROOT) as suite:
            path = suite / "email-project-manager.md"
            path.write_text(path.read_text().replace('"Bash"', '"Bash", "Write"'))
            self.assertTrue(any("read-only" in error for error in validate(suite.parent.parent)))
```

- [ ] **Step 2: Run the focused test and verify failure**

Run: `python3 -m unittest tests.email_operations.test_project_agents -v`  
Expected: FAIL because the validator and twelve definitions do not exist.

- [ ] **Step 3: Implement the stdlib parser and validator**

Implement frontmatter extraction, JSON-style tool-list parsing, role inventory, required headings,
shared-reference, permission-class, prohibition, stopping-condition, and operator-read-back checks.
The CLI prints one error per line and exits nonzero on any failure.

```python
def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    definitions = load_definitions(root / ".codex" / "agents")
    errors.extend(validate_inventory(definitions))
    for definition in definitions.values():
        errors.extend(validate_definition(definition))
    return errors
```

- [ ] **Step 4: Run the test and verify it now fails only on missing definitions**

Run: `python3 -m unittest tests.email_operations.test_project_agents -v`  
Expected: FAIL with exact missing-role and shared-file errors, proving validator behavior is active.

- [ ] **Step 5: Commit the validator contract**

```bash
git add tools/validate_project_agents.py tests/email_operations/test_project_agents.py
git commit -m "test: define project agent safety contract"
```

### Task 2: Shared Contract and Routing Guide

**Files:**
- Create: `.codex/agents/EMAIL-AGENT-CONTRACT.md`
- Create: `.codex/agents/ROUTING.md`

**Interfaces:**
- Consumes: `AGENTS.md`, `PROJECT.md`, Issue #80, Campaign OS schema and current platform authority.
- Produces: mandatory run sequence, evidence levels, permission classes, standard evidence packet, and deterministic role routing used by every definition.

- [ ] **Step 1: Write the shared operating contract**

Include authority order, Issue resolution, scope lock, evidence freshness, five evidence levels,
concurrency, external-write gates, PII/secrets, platform boundaries, failure behavior, GitHub findings,
and the exact standard evidence packet.

- [ ] **Step 2: Write the routing guide**

Define each role's positive trigger, not-applicable condition, required inputs, downstream gate, safe
parallel groups, and prohibited overlapping writers. Include canonical sequences for local email
production, lifecycle/Flow implementation, one-time Messaging campaigns, preview publication,
Campaign OS maintenance, post-send analysis, and Shopify notifications.

- [ ] **Step 3: Run structural validation**

Run: `python3 tools/validate_project_agents.py`  
Expected: FAIL only because runnable definitions are still missing; shared-file errors are gone.

- [ ] **Step 4: Commit shared coordination**

```bash
git add .codex/agents/EMAIL-AGENT-CONTRACT.md .codex/agents/ROUTING.md
git commit -m "docs: add shared email agent contract"
```

### Task 3: Four Upgraded Core Agents

**Files:**
- Create: `.codex/agents/email-project-manager.md`
- Create: `.codex/agents/email-lifecycle-architect.md`
- Create: `.codex/agents/email-producer.md`
- Create: `.codex/agents/email-deliverability-release-reviewer.md`

**Interfaces:**
- Consumes: shared contract, routing guide, canonical Issue, role-specific authority.
- Produces: detailed evidence packets for Campaign OS prioritization, lifecycle contracts, local Email artifacts, and release verdicts.

- [ ] **Step 1: Write the read-only project-manager prompt**

Make GitHub reconciliation read-only and require exact proposed mutations rather than hidden `gh`
writes. Add board-health scoring, field-evidence rules, ranked routing, stop conditions, and Issue
payloads.

- [ ] **Step 2: Write the lifecycle-architect prompt**

Require a complete trigger/eligibility/consent/sequence/collision/exit/data/test/rollback/measurement
contract with Shopify Messaging versus Flow surface selection and no activation.

- [ ] **Step 3: Write the local email-producer prompt**

Require a file allowlist, source-deck/module traceability, builder ownership, token/data constraints,
email-client-safe implementation, local checks, preview handoff, and no external write.

- [ ] **Step 4: Write the release-reviewer prompt**

Require independent evidence for sender, consent, content, Liquid, links, render, timing, collisions,
rollback, draft read-back, and approval; return `SHIP`, `FIX THEN REVIEW`, or `BLOCK` without sending.

- [ ] **Step 5: Run focused tests**

Run: `python3 -m unittest tests.email_operations.test_project_agents -v`  
Expected: FAIL only for the eight not-yet-created roles.

- [ ] **Step 6: Commit the core roles**

```bash
git add .codex/agents/email-project-manager.md .codex/agents/email-lifecycle-architect.md .codex/agents/email-producer.md .codex/agents/email-deliverability-release-reviewer.md
git commit -m "feat: add core email marketing agents"
```

### Task 4: Eight Specialist Agents

**Files:**
- Create: `.codex/agents/email-audience-consent-steward.md`
- Create: `.codex/agents/email-design-module-specialist.md`
- Create: `.codex/agents/email-preview-qa-engineer.md`
- Create: `.codex/agents/campaign-os-engineer.md`
- Create: `.codex/agents/shopify-messaging-campaign-operator.md`
- Create: `.codex/agents/shopify-flow-automation-builder.md`
- Create: `.codex/agents/email-performance-analyst.md`
- Create: `.codex/agents/shopify-notification-template-specialist.md`

**Interfaces:**
- Consumes: accepted upstream evidence packet and exact canonical Issue.
- Produces: non-overlapping specialist outputs defined by the design spec; D-class operators additionally produce full post-write read-back.

- [ ] **Step 1: Add the audience/consent and performance read-only prompts**

Cover Shopify channel consent, tags/segments, suppressions, overlap/count evidence, attribution,
metric normalization, confidence, and learning capture without customer writes.

- [ ] **Step 2: Add the module and preview local-writer prompts**

Cover module authority, transparent page surface, responsive email constraints, builder ownership,
fixture safety, fail-closed Liquid, desktop/mobile screenshots, provenance, Actions artifacts,
publication ledgers, and Pages/Cloudflare gates.

- [ ] **Step 3: Add the Campaign OS local-engineer prompt**

Cover manifest reproducibility, compiled/filed Issue distinction, generated/human Issue sections,
schema/Project drift, key casing, GitHub Actions permissions, dry-run/idempotency, and parent-owned live
mutations.

- [ ] **Step 4: Add Messaging and Flow approval-gated operator prompts**

Require current explicit draft-write approval, exact store/resource resolution, bounded write scope,
post-write full read-back, disabled/unscheduled proof, stop-on-drift, and irreversible-action bans.

- [ ] **Step 5: Add the notification-template specialist prompt**

Require an approved template or batch, notification-specific authority resolution, pre-write backup,
browser focus assertions, exact source read-back, rendered verification, and no notification send.

- [ ] **Step 6: Run the complete agent tests and validator**

Run: `python3 -m unittest tests.email_operations.test_project_agents -v`  
Expected: PASS.

Run: `python3 tools/validate_project_agents.py`  
Expected: `12 project agents validated` and exit code 0.

- [ ] **Step 7: Commit the specialist roles**

```bash
git add .codex/agents/*.md
git commit -m "feat: add specialist email marketing agents"
```

### Task 5: Integration, Documentation, and Delivery

**Files:**
- Modify: `README.md`
- Modify: `PROJECT.md`
- Modify: `docs/superpowers/specs/2026-08-25-email-marketing-agent-suite-design.md`
- Modify: `docs/superpowers/plans/2026-08-25-email-marketing-agent-suite.md`

**Interfaces:**
- Consumes: validated twelve-agent suite and Issue #80.
- Produces: operator-facing discovery/routing documentation, chronological handoff, canonical Issue/PR evidence, and clean reviewable branch.

- [ ] **Step 1: Document discovery and routing**

Add a concise README section linking the shared contract and routing guide, clarifying that the twelve
agents are specialists rather than durable state stores.

- [ ] **Step 2: Update the spec and plan status**

Mark the design implemented and check completed plan steps only after their commands pass.

- [ ] **Step 3: Run focused and full repository validation**

Run: `python3 tools/validate_project_agents.py`  
Expected: PASS with twelve agents.

Run: `python3 -m unittest discover -s tests -v`  
Expected: all tests pass.

Run: `git diff --check`  
Expected: no whitespace errors.

- [ ] **Step 4: Update `PROJECT.md`**

Add a dated session entry linked to #80 stating the exact roles installed, validation evidence, branch,
remaining integration step, and confirmation that no platform/publication/customer state changed.

- [ ] **Step 5: Commit documentation**

```bash
git add README.md PROJECT.md docs/superpowers/specs/2026-08-25-email-marketing-agent-suite-design.md docs/superpowers/plans/2026-08-25-email-marketing-agent-suite.md
git commit -m "docs: hand off email agent suite"
```

- [ ] **Step 6: Push, open the pull request, and update Issue #80**

Push `codex/email-agent-suite`, open one pull request against `main`, and post the validation and PR
link to #80. Do not merge without reviewing CI and the final diff.
