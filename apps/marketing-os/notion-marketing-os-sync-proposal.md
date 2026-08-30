# Marketing OS ↔ Notion Synchronization Proposal

**Status:** design only. This proposal does not authorize database creation, schema changes, worker deployment, Notion writes, Shopify writes, audience changes, publication, scheduling, or messaging activation.

## 1. Operating model

The Marketing OS should use **source-specific, one-way projections by default**. Notion remains authoritative for canonical email content, planning records, approved evidence, and the social working layer. Shopify remains authoritative for live customer consent, audience eligibility, campaign/automation runtime state, and observed commerce metrics. The Social repository remains authoritative for versioned production templates and campaign snapshots. Marketing OS is the authenticated read model, QA surface, and manual-release control plane.

> A worker must never promote a planning record into a live marketing action. It may observe and record evidence; it must not send, schedule, publish, activate, mutate an audience, or amend customer consent.

| System | Authority | Worker behavior | Prohibited behavior |
| --- | --- | --- | --- |
| Notion | Canonical email content, planning, evidence, approvals, social working records | Read into Marketing OS; later write only to explicitly worker-managed projection fields after approval | Overwrite canonical copy, body, source evidence, manual approvals, or historical decisions |
| Shopify | Native marketing consent, live segments, campaign/automation runtime state, commerce facts | Read-only observation projected to evidence fields | Customer edits, consent changes, segment changes, send/schedule/activate/publish actions |
| Social repository | Versioned template library and campaign snapshots | Read artifact revision/digest and import source-backed records | Rewrite repository content or infer missing creative/approval data |
| Marketing OS | Read models, QA packages, handoff/evidence state, audit trail | Read-only display and safe state calculation | Treat a UI state as marketing-operation permission |

## 2. Reuse first: existing Notion databases

| Existing source | Use in Marketing OS | Direction | Key boundary |
| --- | --- | --- | --- |
| `emails_master` | Canonical 53-email portfolio, copy/source readiness, series and module composition | Notion → Marketing OS | Source-only; no reverse sync of canonical copy or body. |
| `modules_master` | Module catalog and email relationship | Notion → Marketing OS | Source-only; preserve existing Notion relation. |
| Proof Bank | Permission-gated proof/reference lookup | Notion → Marketing OS | Permission must remain a release gate; no generated testimonials. |
| Shopify Email Automation Build Tracker | Journey/automation planning, trigger, exit, suppression, approval and build state | Notion → Marketing OS | Informational; no Flow/Messaging activation. |
| Shopify Campaign Calendar | Brief, claims, exclusions, approval, UTM and observed campaign outcome context | Notion → Marketing OS | Informational; no scheduled/send behavior. |
| Shopify Audience & Segment Registry | Audience planning and review metadata | Notion → Marketing OS | Shopify native status stays the only live eligibility authority. |
| Shopify Email KPI Scorecard / Marketing KPI Dashboard | Curated and aggregate performance history | Notion/Shopify → Marketing OS | No inferred or fabricated performance. |
| Campaigns | Cross-channel campaign grouping | Notion → Marketing OS | Extend relations only after explicit approval; avoid duplicate campaign registries. |
| Media & Asset Library | Approved asset, source, alt-text, and status context | Notion/Cloudinary → Marketing OS | Asset use remains blocked without approval and accessibility evidence. |
| Social Template Catalog | Template and hard-gate reference | Notion/repository → Marketing OS | It is not a social campaign, concept, publication, or approval registry. |

## 3. New records required before a full Social and cross-channel sync

No new database should be created automatically. These are the minimal **proposed** records required to turn the present inventory into a durable sync model.

| Proposed record | Purpose | Required fields / relations | Ownership |
| --- | --- | --- | --- |
| **Social Campaigns** | One working record per social campaign, linked to shared Campaigns | `social_campaign_key`, shared Campaign relation, repo snapshot path, source revision/digest, working status, source link, fixture flag | Notion working layer; repository is authoritative for production-library revision/snapshot facts. |
| **Social Content Concepts** | One approved-or-pending concept per campaign | `concept_key`, Social Campaign relation, Template relation, source copy reference, asset relation, claim review, rights review, accessibility review, fixture flag | Notion working layer; no generated copy/claims/assets. |
| **Social Publications** | One platform-format delivery candidate per concept | `publication_key`, Concept relation, platform, format, manual-operation status, operation evidence URL, external post ID, verified-live timestamp, fixture flag | Notion for plans/evidence; platform for live state. |
| **Marketing Governance & Release Evidence** | Channel-neutral approval and evidence record | entity relation, channel, decision, claim/rights/consent/QA gate states, reviewer, decision timestamp, evidence links, release package fingerprint | Notion owner-reviewed record; no automation authority. |
| **Marketing Performance Observations** | Evidence-backed campaign/publication performance snapshots | entity relation, source system, capture window, metric values, source URL/ID, captured timestamp, freshness, reliability note | External source is authoritative; Notion retains observation history. |
| **Worker Sync State** | Idempotency, freshness, and failure preservation | stable external key, source family, source URL, revision/fingerprint, captured/source-updated timestamps, sync-run ID, freshness, relation keys, error state | Worker-owned internal store, not a manual planning database. |

## 4. Identity and relation contract

Before any sync runs, define immutable IDs without modifying existing canonical content.

| Entity | Required stable key | Example source anchor | Relation target |
| --- | --- | --- | --- |
| Email | `email_key` | canonical code / Notion page URL | module, proof, automation, campaign |
| Shared campaign | `campaign_key` | Campaigns database page URL | email campaign, social campaign, assets, observations |
| Social campaign | `social_campaign_key` | repo snapshot path + revision | shared campaign, concepts |
| Social concept | `concept_key` | source record URL / digest | template, assets, governance, publications |
| Publication | `publication_key` | source record URL + platform/format | concept, operation evidence, performance |
| Asset | `asset_key` | asset-library page URL / approved source URL | email, social concept, proof |
| Governance record | `decision_key` | Notion page URL | any governed entity |

The worker stores the Notion URL and source fingerprint separately from business keys. A missing fingerprint or mismatched source must fail closed and preserve the last successful observation.

## 5. Worker design

The existing Shopify worker practice is the correct pattern to reuse: **idempotent, failure-preserving, read-first synchronization**. A Marketing worker should be introduced as a separate scope from the current application runtime, with its own credentials and a worker-owned mapping store.

1. **Discovery mode:** collect schemas and candidate records; emit a diff only.
2. **Binding mode:** save the approved source IDs, source owners, stable keys, and field maps in the worker mapping store. No business content moves yet.
3. **One-way source import:** pull Notion canonical/planning data and repository artifacts into Marketing OS read models; stamp revision, digest, source URL, and freshness.
4. **External observation projection:** read Shopify/Cloudinary/social platform evidence where authorized, then write only designated observed-state fields or a separate evidence record. Never overwrite Notion-owned planning fields.
5. **Parity QA:** compare record counts, stable keys, selected field fingerprints, source timestamps, and relation integrity. Any conflict or missing source blocks that record.
6. **Manual release remains external:** the worker may display a ready-for-review gate, but the human performs any Shopify or social platform action outside the worker.

## 6. Required safety controls

| Control | Requirement |
| --- | --- |
| Fail-closed records | Missing provenance, unknown key, stale source, unresolved relation, rights gap, claim gap, or consent ambiguity blocks the record. |
| Conflict handling | Never last-write-wins. Create an exception entry with both fingerprints and source links; retain the last complete observed state. |
| Worker-owned fields | Any write target must be explicit (for example, `Last synced at`, `Sync run`, `Freshness`, `Observed source revision`, `Sync error`). Canonical/business fields are not worker-owned. |
| Rate and replay safety | All runs are idempotent by stable key and source revision. Duplicate events and retries cannot create duplicate campaign, concept, or publication rows. |
| PII minimization | No customer-level data is replicated into Marketing OS or Notion for this sync. Shopify remains the consent/customer authority. |
| Human release | Approval fields are evidence, not operation commands. A record may never send, schedule, publish, activate, or mutate an audience. |
| Auditability | Retain source URL, external key, fingerprint, captured time, source-updated time, sync run, operation result, and error state for every projected record. |

## 7. Approval gates before implementation

Implementation should pause until the following decisions are made explicitly.

1. Confirm whether the six proposed records are created as new Notion databases, or whether a named existing governance/data-source structure should be extended instead.
2. Approve the exact stable-key vocabulary and relations, particularly `campaign_key` and the Social concept/publication IDs.
3. Designate the worker runtime and mapping-store location, credentials, schedule/event triggers, and which Notion properties are worker-managed.
4. Approve a one-way **dry run** over a small controlled sample: one canonical email, one module relation, one shared campaign, one asset, and the existing Social Phase 1 fixtures.
5. Approve the conflict policy and the first evidence-only external observations. No Shopify Marketing or social-platform write scope should be requested.

## 8. Recommended first implementation slice

Start with a one-way, zero-side-effect read model:

1. Bind the existing Notion data sources and Social Phase 1 artifact by stable source URL and fingerprint.
2. Import the 53 canonical email records, modules, Proof Bank permission state, campaign registry, asset approval state, and Social template catalog.
3. Surface sync freshness and blocking exceptions in Marketing OS.
4. Run parity QA and produce a diff report.
5. Only after the new Social operational/governance records exist and are populated with approved source evidence, add their read-only projections.

This sequence makes the system genuinely synchronized without creating a second email source of truth or falsely turning fixture social records into production content.
