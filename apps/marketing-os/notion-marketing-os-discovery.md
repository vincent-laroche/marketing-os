# Notion Marketing OS Discovery Notes

Discovery date: 2026-08-26. This is a read-only inventory snapshot; it does not authorize a sync or any Notion change.

## Connected workspace

- Workspace: Hair Solutions Co. (`f1a9f1df-1126-8124-9c1a-00035eb31f01`)
- Connected user: Hair Solutions Co. (`info@hairsolutions.co`)
- Notion discovery, query, and data-source capabilities are available.

## Confirmed operating databases

| Domain | Data source | Current role | Source |
| --- | --- | --- | --- |
| Shared campaign registry | `collection://4186d9fe-d6ab-4460-9622-cb7de438821e` | One cross-channel campaign record; fields are Name, Channels, Window, Status, Links & Notes. | https://app.notion.com/p/5024ef72e7ec4a6b8499b2234fd44219 |
| Canonical email source | `collection://fbc9f1df-1126-83a3-a049-87874c8d1a99` | `emails_master`; 53 rows; body, subject, module relation, series, source and build fields. | https://app.notion.com/p/8c69f1df11268320b806811ebcdb6029 |
| Email modules | `collection://f309f1df-1126-821e-8d1b-8714c8bd2bb3` | `modules_master`; reciprocal relation to email blueprints. | https://app.notion.com/p/a759f1df112682d7a66281acc1378f89 |
| Proof/permissions | `collection://d519f1df-1126-8203-ba7a-87a2e56b384d` | Proof Bank with Permission, source, type, date, and Email relation. | https://app.notion.com/p/bc29f1df1126827cb73f01f6521eca87 |
| Email automation readiness | `collection://c789ba58-02d5-45d4-b6b0-201de04febcc` | Shopify Email Automation Build Tracker with approval, status, trigger, exit, suppression, audience, and source fields. | https://app.notion.com/p/445db6a1bec94691bc23407f4536886c |
| Email campaign calendar | `collection://da751d10-2cf6-48af-9184-f8160bb5e3bd` | Shopify Campaign Calendar with claims review, approval, audience/exclusions, UTM, schedule, and outcome fields. | https://app.notion.com/p/dd889d06ffd2442cade741717c053f2e |
| Audience planning | `collection://bbc7227c-d718-4f82-b696-e7c7ed26a0be` | Segment Registry: planning and review metadata only; native Shopify status remains eligibility authority. | https://app.notion.com/p/74f277bd8d0241f2b08ed145bdff1452 |
| Email performance periods | `collection://52eda403-7c9c-49d7-8f6e-cdc804d77fcf` | Shopify Email KPI Scorecard: period-based revenue, delivery, click, order, deliverability, and risk summary. | https://app.notion.com/p/ef19fcbf99cc4588a5d43dba62b53e99 |
| Performance | `collection://3c19f1df-1126-8128-83c1-000bf78a0768` | Marketing KPI Dashboard: aggregate KPI definitions, cadence, current, target, and status. | https://app.notion.com/p/3c19f1df112681e290c7ec6d0751c703 |
| Social templates | `collection://e59a1965-1b0a-42ca-bfa2-86904b604e3e` | Social Template Catalog; 16 records; Template, Channel, Use, Hard Gate, Frames, and Repo File only. It is not a campaigns/concepts/publications model. | https://app.notion.com/p/f333ab53d64a4c4bb6b4adc01bb3de92 |
| Asset/DAM registry | `collection://bdd0ebbf-2f42-417c-b846-f12ff393beac` | Media & Asset Library with approval status, URL, source system, alt text, and usage notes. | https://app.notion.com/p/f07f4999f3324681890b26351aee90b4 |

## Confirmed source boundaries

- The Emails hub identifies `emails_master` as the canonical 53-email source and `modules_master` as the linked module library: https://app.notion.com/p/e7f9f1df112683ad93508191c021acac
- The Growth & Marketing hub says Notion is an operational source of truth but not a sending platform; Shopify owns native customer marketing eligibility: https://app.notion.com/p/3c19f1df1126816aa831d7346e4239ec
- The Social hub says Notion holds the catalog/campaign working layer, while `social-media-marketing` owns the versioned production library and campaign snapshot: https://app.notion.com/p/e2ee71689ea3417eb54fcb6924fa5b0e
- The Social Rebrand Launch page is a package of working artifacts and warns that it is not production-ready: https://app.notion.com/p/b7440c52378d4dc4a0221a93cdb9db16
- The Shopify OS worker design is a read-only projection with idempotent, failure-preserving refreshes; a failed refresh must not overwrite the last complete observation: https://app.notion.com/p/ac2e603e383b4498a1a8bf812d35dcd2
- Master Shopify OS preserves the same desired-state/evidence boundary and makes all writes a separate guarded action: https://app.notion.com/p/1b49e6f2b7614768b5ed9ec4f75c681d
- Existing worker design references provide the required sync metadata pattern: external identity, revision/fingerprint, Notion deep link, captured/source-updated timestamps, freshness state, sync-run ID, relations, and error state. The Marketing OS does not yet have a dedicated implementation of that mapping contract: https://app.notion.com/p/664fc6ad221a470a97e57832b7150cef

## Field ownership and permitted sync direction

| Domain | Properties or property group | Authoritative owner | Permitted worker direction | Marketing OS behavior |
| --- | --- | --- | --- | --- |
| Canonical emails | Email name, Body, Subject, Preview Text, CTA, Series, Position, Series Total, Module Stack, Modules Used | Notion `emails_master` / exported Email Reference File | Notion to Marketing OS only | Read-only import keyed by Notion page URL and canonical identifier; never write, generate, or overwrite canonical copy. |
| Email build metadata | Build Status, Missing Modules, HubSpot fields, Workflow IDs | Notion source records | Notion to Marketing OS only | Read-only readiness context; no implicit provider activation, publication, or workflow change. |
| Email automation planning | Automation, Journey, Trigger, Exit Condition, Suppression, Audience, Timing, Priority, Build Status, Approval Required, Approved, Source of Truth | Notion Automation Build Tracker | Notion to Marketing OS only | Display and QA context only. `Approved` and `Live` never create a send, schedule, Flow activation, or messaging action. |
| Email campaign planning | Brief, target/exclusions, claim review, offer, UTM, proposed date, status, approval | Notion Shopify Campaign Calendar | Notion to Marketing OS only | Read-only calendar and gate view. Actual recipient eligibility stays in Shopify; actual release remains manual. |
| Consent and segments | Segment code, eligibility/exclusion, ShopifyQL draft, review status | Notion Segment Registry for planning; Shopify native marketing status for live eligibility | Notion to Marketing OS planning projection; Shopify to Marketing OS read-only eligibility observation | Never update customer consent, segments, or audiences from Marketing OS or Notion. |
| Email KPI snapshots | Period, revenue, delivered, clicks, orders, complaints, bounces, performance notes | Shopify for live metrics; Notion scorecard for curated history | Shopify/Notion to Marketing OS only | Read-only observations only; no fabricated or inferred performance. |
| Shared campaigns | Name, Channels, Window, Status, Links & Notes | Notion Campaigns registry | Notion to Marketing OS only | Shared grouping/links only until explicit relations are added by the user. |
| Asset records | Asset, URL, type, source system, approval status, alt text, usage notes | Media & Asset Library / Cloudinary or Shopify source system | Notion/external source to Marketing OS only | Gate asset use on current approval and alt-text evidence; never invent assets, rights, or accessibility fields. |
| Proof records | Quote/Asset, customer, source, permission, type, date, Used In | Notion Proof Bank | Notion to Marketing OS only | Treat permission as a release gate; no automatic reuse or customer-story generation. |
| Social templates | Template, Channel, Use, Hard Gate, Frames, Repo File | Notion catalog plus `social-media-marketing` repo for the versioned production library | Notion/repo to Marketing OS only | Read-only template and hard-gate reference; catalog cannot model social campaign, concept, approval, or publication state. |
| Social Phase 1 fixtures | Campaign, concepts, publications, provenance, gate state | Current Social read model / upstream repo fixture source | Repo artifact to Marketing OS only | Remain visibly fixture-only. No promotion to approved, scheduled, published, or verified-live without separately approved source records. |

## Definitive gaps before a safe sync implementation

1. **Social operational records are absent.** No dedicated Social Campaigns, Content Concepts, Publications, or platform-operation/verification database was found. The Social Template Catalog cannot anchor these records because its only fields are Template, Channel, Use, Hard Gate, Frames, and Repo File.
2. **Marketing governance records are absent.** No Marketing OS–specific approval/decision ledger, claims registry, release package/evidence ledger, or approval-to-operation audit trail was found. Existing approval fields are local to the Email trackers and cannot safely govern Social or shared releases.
3. **Cross-channel relations are absent.** The shared Campaigns registry has no explicit relation to Email calendar rows, social records, assets, approval evidence, or KPI observations.
4. **Measurement granularity is incomplete.** The Marketing KPI Dashboard and Email KPI Scorecard are aggregate/periodic; neither provides a common campaign/publication performance relation. Social performance has no database source.
5. **Worker mapping state is absent for Marketing OS.** Existing Shopify worker practices establish the required metadata pattern, but no Marketing OS mapping contract currently holds a stable external ID, source revision/fingerprint, source/deep link, captured and source-updated timestamps, freshness, sync-run ID, relation keys, or error state.
6. **Canonical cross-source keys are absent.** Current source databases expose Notion page URLs and local auto-increment IDs, but no agreed canonical `campaign_key`, `email_key`, `concept_key`, `publication_key`, or `asset_key` ties Email, Social, and shared Campaigns together.

No database, schema, view, page, worker, or connector was changed during this discovery pass.

## Approved implementation updates — 2026-08-27

The owner approved an actual two-way sync, directed that existing Notion structures be extended rather than duplicated, approved the stable-key plan, and delegated runtime/mapping-store selection. The Notion credential was verified against the authenticated identity endpoint and the Social Template Catalog source.

### Existing structures extended

| Data source | Added worker-managed fields |
| --- | --- |
| Campaigns (`collection://4186d9fe-d6ab-4460-9622-cb7de438821e`) | Marketing OS Key, Sync State, Source Fingerprint, Last Synced, Sync Error, and Worker Managed Fields. |
| Social Template Catalog (`collection://e59a1965-1b0a-42ca-bfa2-86904b604e3e`) | Record Type, Key, Parent Key, Fixture Only, Source Revision/Fingerprint, Approval/Rights/Accessibility/Platform State, Operation Evidence, and the worker-managed sync fields. |

All existing planning/content fields were left unchanged. The Social catalog is the agreed existing structure to extend for the Social Campaign, Concept, and Publication hierarchy; parent relationships are recorded by stable parent key and resolved by the worker mapping state.

### Selected runtime and sync store

- **Runtime:** a dedicated `marketing-os-notion-sync` Cloudflare Worker, rather than the legacy Email control-plane Worker. This preserves separate Email, Social, and shared-record namespaces while still using the existing account controls.
- **Mapping store:** the existing `sync-state` Cloudflare D1 database (`45cbd382-a5bc-4804-8d97-ccf4bf61b638`) under a new `marketing_os` scope. It already implements mapping, idempotency, state, and error tables; no existing rows are modified by the Marketing OS worker.
- **Trigger model:** signed Notion webhooks notify the Worker of eligible source changes. The Worker re-fetches the latest source state after receiving an event because Notion webhooks carry a signal rather than the complete changed record. A low-frequency reconciliation schedule detects missed or out-of-order events. Notion retry behavior means processing must remain idempotent.

The existing `email-marketing-control-plane` Worker has a legacy daily schedule and no scoped binding topology, so it is not extended. The selected Worker receives no Shopify Marketing or social-platform write credentials.
