# Marketing OS Operating Contract

## Purpose

This repository is the durable source for Hair Solutions Co. marketing strategy, production source, review evidence, and channel-specific release preparation. It contains a shared Marketing OS control plane and specialized Email OS and Social Media OS domains.

The shared layer coordinates initiatives, objectives, audiences, offers, claims, assets, experiments, calendar milestones, approvals, results, and learnings. It does not replace the specialized production or release rules of either channel.

## Authority order

1. Vincent’s current explicit decision.
2. The relevant approved source authority for the channel and record type.
3. Root `AGENTS.md` and the applicable channel contract.
4. The canonical GitHub Issue and committed repository source.
5. Re-fetched external platform state, where a draft or publication exists.
6. `PROJECT.md` for chronology and handoff only.
7. Historical platforms, exports, screenshots, and superseded builds as evidence only.

A chat summary, local claim, or undocumented decision is not operational authority. A finding that is not recorded in a canonical Issue or pull request does not operationally exist.

## Shared identifiers

Shared records use `marketing-os-key`. Email records retain the existing `campaign-os-key` namespace, and Social Media OS records use `social-os-key`. Namespaces must not be silently converted or reused.

| Record | Key format | Example |
|---|---|---|
| Initiative | `marketing:initiative:<slug>` | `marketing:initiative:new-customer-education` |
| Audience | `marketing:audience:<slug>` | `marketing:audience:engaged-core` |
| Offer | `marketing:offer:<slug>` | `marketing:offer:consultation` |
| Claim | `marketing:claim:<slug>` | `marketing:claim:custom-fit` |
| Asset | `asset:<provider>:<id>` | `asset:cloudinary:hs_abc123` |
| Experiment | `experiment:<slug>` | `experiment:education-vs-product-hook` |
| Social campaign | `social:campaign:<slug>` | `social:campaign:new-customer-education` |
| Content concept | `social:content:<slug>` | `social:content:why-systems-look-natural` |
| Publication | `social:publication:<platform>:<slug>` | `social:publication:instagram:why-systems-look-natural` |

## State distinctions

Repository state, review state, platform draft state, schedule state, publication state, and measurement state are separate facts.

> A merged pull request means that the reviewed source was integrated. It does not mean that an email was sent, a journey was activated, a social post was scheduled, or a social post was published.

Preview URLs are review artifacts. They are not evidence of a live customer-facing or public resource unless the corresponding live read-back is recorded with `LIVE_RELEASE_VERIFIED` evidence.

## Permission classes

### Read-only

Read-only agents may inspect source, Issues, pull requests, project state, platform read-backs, and evidence. They may recommend work and identify blockers, but they may not change repository source, platform state, audiences, schedules, or publication state.

### Local write

Local-write agents may modify explicitly scoped repository source and generated local artifacts. They may not send, schedule, publish, activate, change audience membership, or change customer data. They must work from a named Issue or pull request and return exact files, tests, source fingerprints, and blockers.

### Approval-gated operator

An approval-gated operator may perform a narrow external platform operation only after explicit approval for the exact record and action. It must use idempotency where available, re-fetch the resulting external state, and record the external identifier, timestamp, source revision, and evidence level. No operator may infer approval from a merge or a passing CI run.

## Content and customer safety

Do not invent product facts, offers, testimonials, customer outcomes, metrics, customer questions, consent, claims, or platform mappings. Customer proof, customer imagery, creator material, music, and stock material require exact-use rights or consent evidence where applicable.

Customer exports and PII remain gitignored. Large production media belongs in the approved asset system, not in Git. Repository records store provider identity, approved URL, thumbnail, technical metadata, checksum or equivalent fingerprint, rights status, and permitted usage.

The existing Email OS rule remains absolute: there is no marketing send path in this repository. Shopify Messaging and Shopify Flow remain the marketing execution platforms, and activation or sending remains a separate deliberate decision. MailerLite remains legacy/reference only, and MailerSend remains transactional-only.

Social publishing is likewise disabled by default. Building, reviewing, merging, previewing, or scheduling preparation must not publish to Instagram, TikTok, Facebook, or another social platform.

## Evidence levels

Every operational report must distinguish the strongest evidence actually obtained:

1. `AUTHORITY` — governing source inspected.
2. `SOURCE` — committed source representation inspected.
3. `LOCAL_VALIDATED` — local tests, build, or render passed.
4. `PLATFORM_DRAFT_VERIFIED` — exact external draft or disabled graph re-fetched and verified.
5. `LIVE_RELEASE_VERIFIED` — actual customer-facing or public resource independently read back.

## Issue and pull-request discipline

Every change begins with a named Issue, a scoped pull request, or a documented implementation task created before work starts. Generated sections may be regenerated, but human-maintained sections such as `Blockers`, `Evidence`, `Decisions`, `Results`, and `Learnings` must be preserved.

Open work may not exist only in `PROJECT.md`. The project log records what changed and what is next; it is not a hidden backlog.

## Failure behavior

Validators fail closed on malformed keys, missing relationships, missing required evidence, unapproved assets, unsupported claims, unresolved placeholders, unsafe destinations, and ambiguous platform state. A blocked result is preferable to a plausible-looking artifact that cannot be trusted.

All operations must be idempotent or dry-run by default. Retries must not create duplicate Issues, assets, drafts, schedules, or publications.
