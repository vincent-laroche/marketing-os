# Public Social Content Audit

**Status:** Open audit; non-production quarantine applies

**Owning Issue:** [#102](https://github.com/vincent-laroche/marketing-os/issues/102)

**Scope:** Migrated `apps/social-studio/lib/data.ts`, `data/social-media/canva_social_production_matrix.csv`, `data/social-media/Hair_Solutions_180Day_Instagram_Campaign.xlsx`, `docs/social-media/**`, and `social-media/**`.

## Classification

The migrated Social Studio seed data, planning matrix, spreadsheet, and historical strategy documents are **public reference material only**. They are not an approved content library, current product catalogue, current pricing source, consent record, evidence register, or publication queue. A record appearing in these files does not authorise social posting, scheduling, paid promotion, or customer-facing reuse.

The canonical Social Media OS fixture under `social-media/campaigns/schema-fixture/` is separately labelled as non-production structural fixture content. Its Issue hierarchy is #90–#94. The migrated application data and planning files are broader historical/reference material and remain quarantined under this audit.

## Audit results

The first-pass scan found the following indicator counts. Counts are search indicators, not counts of unique claims or confirmed PII.

| Indicator category | Matches | Interpretation |
|---|---:|---|
| Claim or proof language | 203 | Requires source and claim review before reuse |
| Commercial or pricing language | 122 | Requires current Shopify/source verification before reuse |
| Customer, named-person, testimonial, or consent language | 148 | Requires identity, rights, and exact-use consent review |
| Platform or publishing language | 585 | Planning language only; not authorization to publish |

Representative high-risk material includes testimonial and customer-proof concepts, before/after and transformation references, a model placeholder described as a real person, numerical milestones such as `100 orders`, referral and discount language such as `$50 credit` and `10% off`, sale language such as `up to 20% off`, and a claim that care tips can make a system last `2x longer`. The app seed data also contains product-price statements and asset records whose consent is `Pending` or `Internal only`. These examples are retained only as historical/reference findings until an authoritative source, currentness check, and approval record exist.

## Required disposition before production reuse

| Content class | Public disposition | Production requirement |
|---|---|---|
| Structural Social fixture records | Allowed as clearly labelled fixtures | Preserve `social-os-key`; no customer-facing approval implied |
| Generic planning and educational concepts | Quarantined reference | Confirm current claims, product facts, and channel suitability |
| Prices, offers, discounts, and availability | Quarantined reference | Verify against current Shopify authority and record exact evidence |
| Testimonials, customer quotes, transformations, and before/after assets | Quarantined reference | Attach exact source, identity handling, rights, and exact-use consent |
| Named people, model or ambassador copy | Quarantined reference | Confirm identity, role, permission, and permitted channel/use |
| Platform captions, hashtags, CTAs, and dates | Planning reference | Pass Social review, claims/rights gates, and explicit publication approval |
| Notion-derived or fallback seed data | Read-only reference | Do not treat refresh or fallback display as approval |

No migrated Social item receives `Approved`, `Scheduled`, or `Published` status from this audit. Social platform operations remain disabled by default. No external Social account was accessed or changed as part of the audit.

## Evidence and next action

The audit was performed locally against the named repository files on 2026-08-25. The indicator scan is a triage aid; it does not establish that every match is unsafe or that every unflagged line is safe. Issue #102 owns the follow-up classification and any redaction/removal PR. Until that Issue is resolved, downstream tools must treat these files as non-production historical/reference input.
