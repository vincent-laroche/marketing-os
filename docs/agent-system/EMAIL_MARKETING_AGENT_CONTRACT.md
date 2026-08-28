# Email Marketing agent operating contract

This contract applies to every project-local agent in `.codex/agents/`.
It complements, and never overrides, `AGENTS.md` and `PROJECT.md`.

## Required input and identity

Before work, read `AGENTS.md`, `PROJECT.md`, the canonical GitHub Issue or
`campaign-os-key`, and only the authority material needed for the named scope.
`Email Reference File/` is authoritative for campaign structure, copy, and
module composition. Record the Issue/key, branch, base and resulting SHA,
owned files, and evidence timestamp. Prose does not create hidden backlog.

## Evidence ladder

State the highest evidence level reached, never a higher one:

1. Authority inspected
2. Source inspected
3. Locally validated
4. Platform draft verified
5. Live or release verified

## Shared safety boundaries

- Preserve unrelated dirty work. Writers operate only on their explicit file
  allowlist and never claim another writer's surface.
- Stop on an authority conflict, account mismatch, stale evidence, unsupported
  Liquid, missing consent proof, or scope expansion.
- Never invent copy, claims, offers, customer data, metrics, dynamic variables,
  consent, or platform facts.
- Shopify Messaging and Shopify Flow are the marketing/lifecycle platforms.
  Never create or restore MailerLite campaigns or automations. MailerSend is
  transactional-only.
- Sending, scheduling, activation, Pages publication, DNS, audience mutation,
  customer-data changes, and platform configuration remain separate approval
  gates. A local check, Issue status, merged pull request, or Project field is
  not approval.
- Specialists do not spawn subagents. The root agent orchestrates handoffs.

## Standard evidence packet

Every result returns:

```text
Issue / campaign-os-key
Scope and owned files
Authority sources
Base and resulting SHA
Changes or findings
Checks performed
Evidence level reached
Blockers and decisions
External state changed: yes/no
Recommended next agent
Stopping condition
```
