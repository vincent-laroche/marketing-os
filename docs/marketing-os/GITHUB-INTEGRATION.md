# GitHub Integration Contract

## Current mode

The Social Media OS integration is currently **source-and-artifact only**. Local tooling validates records, builds provenance, and emits a dry-run Issue plan. It does not create, update, close, schedule, or publish anything in GitHub or on a social platform.

The destination repository is `vincent-laroche/email-marketing-ops`. The existing Email Marketing Campaign OS and Project #4 remain authoritative for the Email domain. Social records use the independent `social-os-key` namespace and must not be added to the existing 69-record email invariant.

## Issue hierarchy

The intended Social Media OS hierarchy is:

```text
Social Campaign Issue
└── Content Concept Issue
    ├── Instagram Publication Issue
    ├── TikTok Publication Issue
    └── Facebook Publication Issue
```

Assets and experiments are independent Issues unless they are explicitly attached to a campaign or content concept. The source path and `social-os-key` are the stable upsert identity. Titles may change without creating a duplicate Issue.

`tools/social_os/build_issue_plan.py` emits `upsert-by-key` operations with parent keys, labels, source paths, source SHA-256 fingerprints, and preserved human-evidence sections. Any future writer must consume this plan and remain dry-run by default.

## Shared fields

These fields should be represented once in the eventual shared Marketing OS Project or reused from the existing Project where technically possible:

| Field | Values / type | Meaning |
|---|---|---|
| Stage | Idea, Brief, Creating, Editing, Review, Approved, Scheduled, Published, Measuring, Complete, Blocked | Operational state. |
| Work Type | Campaign, Content, Publication, Asset, Experiment, Bug/Fix | Record type. |
| Channel | Social, Cross-channel | Domain scope. |
| Platform | Cross-platform, Instagram, TikTok, Facebook | Execution surface. |
| Objective | Reach, Engagement, Traffic, Leads, Sales, Retention, Trust | Intended outcome. |
| Funnel | Awareness, Consideration, Conversion, Retention | Customer journey level. |
| Priority | P0, P1, P2, P3 | Work priority. |
| Primary KPI | Select/text | Success metric. |
| Review Due | Date | Decision deadline. |
| Publish Date | Date | Planned publication date, not proof of publication. |
| Preview URL | URL/text | Review artifact only. |
| Evidence Level | AUTHORITY, SOURCE, LOCAL_VALIDATED, PLATFORM_DRAFT_VERIFIED, LIVE_RELEASE_VERIFIED | Strongest evidence obtained. |

## Social-specific fields

| Field | Values / type | Meaning |
|---|---|---|
| Social Format | Short Video, Carousel, Static, Story, Text-Link, Live | Platform creative format. |
| Content Pillar | Education, Product & Solutions, Customer Stories / Social Proof, Questions & Objections, Brand & Founder, Lifestyle / Identity, Promotion, Trend / Entertainment | Content purpose, independent of format. |
| Feed Order | Integer or empty | Instagram feed position. |
| Reuse Potential | High, Medium, Low, No | Whether the concept should be repurposed. |
| Copy Readiness | Needs Work, Ready, N/A | Copy gate. |
| Creative Readiness | Needs Work, Ready, N/A | Creative gate. |
| Accessibility | Needs Work, Ready, N/A | Subtitles, readable text, alt text where applicable. |
| Tracking Readiness | Needs Work, Ready, N/A | Destination and attribution gate. |
| Claims Review | N/A, Required, Approved, Blocked | Claims safety gate. |
| Rights Review | N/A, Required, Approved, Blocked | Asset rights and consent gate. |
| Destination URL | Inert or approved URL | Publication destination. |
| Metrics Review Date | Date | Measurement checkpoint. |

## Proposed views

The eventual Social Media OS navigation should answer distinct questions rather than expose every record everywhere:

1. **Campaign Roadmap** — Campaign records only, grouped by production dates.
2. **Content Pipeline** — Content records only, grouped by Stage.
3. **Publishing Schedule** — Publication records grouped by Platform and Publish Date.
4. **Instagram Feed Planner** — Instagram non-Story publications ordered by Feed Order, paired with the generated feed-grid artifact.
5. **Content Mix & Pillars** — Content and Publication records grouped by Content Pillar.
6. **Cross-Platform Distribution** — Publications grouped by parent Content Concept.
7. **Creative Review & PRs** — Open pull requests linked to Social Issues.
8. **Publishing Readiness** — Publications in Review, Approved, or Scheduled with readiness gates visible.
9. **Performance & Learnings** — Published, Measuring, and Complete records with metrics and learnings.
10. **Evergreen & Repurpose** — Evergreen records and high-reuse Content Concepts.

Creating these views is a separate, approval-gated Project operation. The repository source and local validators do not assume that a Project or its fields already exist.

## External mutation rules

A future GitHub writer must satisfy all of the following before applying a plan:

- explicit approval for the exact repository and scope;
- a fresh source manifest and source fingerprints;
- a dry-run diff reviewed before mutation;
- upsert-by-key behavior with no duplicate creation;
- preservation of human-maintained Issue sections;
- no modification to Email Issues or the existing 69-record invariant;
- a read-back of every created or changed Issue and parent relationship;
- an evidence report linked to the relevant pull request.

Project creation, Project field changes, social platform accounts, scheduling, and publishing are not part of the local Social Media OS build. They require separate approval and separate platform evidence.
