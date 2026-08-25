# Marketing OS Architecture

## Product boundary

`vincent-laroche/marketing-os` is the public repository for Hair Solutions Co.'s marketing operating system. It is a **source, review, provenance, and release-preparation platform**. It is not the email sender, social publisher, customer database, asset CDN, or credential store.

The build has one shared control plane and two specialized domains:

| Domain | Durable source in this repository | Execution system | External action allowed from repository automation |
|---|---|---|---|
| Shared Marketing OS | Initiatives, audiences, claims, offers, assets, experiments, calendar milestones, approvals, results, learnings | GitHub Issues, pull requests, and Project views | None by default |
| Email OS | `Email Reference File/`, `shopify-messaging/`, Campaign OS manifest, preview compiler | Shopify Messaging + Shopify Flow; GitHub Pages for fictional previews | Public preview publication only through the bounded manual workflow |
| Social Media OS | `social-media/` records, migrated studio source, strategy/data references, templates | GitHub Social Media OS Project; Notion remains an optional read-only upstream | None; scheduling and publishing remain disabled |

## Repository structure

```text
marketing-os/
├── Email Reference File/                 # Email authority: copy and composition
├── shopify-messaging/                    # 53-email Shopify build and readiness ledger
├── email-previews/                       # Append-only public publication ledger
├── github-campaign-os/                   # Generated Email Issue/Project manifests
├── social-media/                         # Social source records, templates, schemas, references
├── apps/social-studio/                   # Migrated read-only operator dashboard source
├── docs/marketing-os/                    # Shared architecture, contracts, integration rules
├── docs/social-media/                    # Migrated social strategy and design references
├── data/social-media/                    # Public-safe calendar and production matrix sources
├── templates/social/                     # Reusable Social OS record templates
├── tools/email-preview/                  # Fail-closed Email preview compiler and Pages release tools
├── tools/github_campaign_os/             # Email Issue/Project compilers and verifiers
├── tools/social_os/                      # Social validators, manifests, previews, and dry-run plans
└── .codex/agents/                        # Project-local Email specialists and safety contracts
```

`apps/social-studio/` is a presentation layer over seed data and optional read-only Notion refreshes. It is not the canonical Social OS database. The canonical source is the Markdown record hierarchy under `social-media/`; the app must not write to Notion, GitHub Issues, social platforms, or customer systems.

## Authority and record flow

The source-of-truth order is deliberately different for each domain:

1. Vincent's current explicit decision.
2. The approved channel authority: `Email Reference File/` for email, approved Social OS records and brand/reference authority for social.
3. Root `AGENTS.md` and the shared Marketing OS operating contract.
4. Committed repository source and generated manifests.
5. GitHub Issues and pull requests as connector-readable operational records.
6. GitHub Projects as navigation and reporting layers.
7. Read-only external platform refreshes, such as Notion or Shopify state.

A record moves through this flow:

```text
Approved source record
        ↓
Local validation and deterministic manifest
        ↓
Pull request with review evidence
        ↓
Merged repository state
        ↓
Optional Project synchronization
        ↓
Optional external draft/read-back
        ↓
Separate approved schedule or publication operation
        ↓
Measured result and learning record
```

A merge, approval, preview URL, platform draft, scheduled date, or CI success never implies a send or publication.

## Email OS and GitHub Pages

The Email OS continues to store the complete 53-email programme in the repository. The preview compiler is allowed to publish only a complete set of selections with `preview_public: true`, exact committed source SHA, fictional fixture data, canonical Issue/PR provenance, output digests, and HTTPS read-back.

The renamed public repository changes the default Pages origin to:

```text
https://vincent-laroche.github.io/marketing-os
```

The existing custom domain remains a separate future operation. The Pages workflow must never publish source files, customer data, Liquid, private artifact URLs, unresolved variables, or unsafe links. An Email that fails the renderer stays blocked; it is not replaced with invented data merely to make the gallery complete.

The current 14 ready / 39 blocked split is a content-readiness fact, not a license to weaken the gate. The first public Pages run should publish the 14 structurally ready Emails as one atomic snapshot, or a smaller explicitly approved set if the release owner chooses that scope. The other 39 remain visible in the readiness inventory but do not receive public detail pages until their actual blockers are resolved.

## Social Media OS and GitHub Project

The Social Media OS Project is separate from Email Project #4. It should contain only Issues with the `social-os-key` marker and should use the following hierarchy:

```text
Social Campaign
└── Content Concept
    ├── Instagram Publication
    ├── TikTok Publication
    └── Facebook Publication
```

The Project is a reporting surface. Markdown source records remain canonical. The initial Project creation must be read-back verified for repository link, fields, views, and item count. Issue synchronization must be dry-run first, upsert by `social-os-key`, preserve human evidence sections, and never alter the Email 69-record invariant.

Recommended Social Project fields are:

| Field | Type | Purpose |
|---|---|---|
| Status | Built-in status | Inbox, Ready, In Progress, In Review, Blocked, Done |
| Stage | Single select | Idea, Brief, Creating, Editing, Review, Approved, Scheduled, Published, Measuring, Complete |
| Work Type | Single select | Campaign, Content, Publication, Asset, Experiment, Evergreen |
| Platform | Single select | Cross-platform, Instagram, TikTok, Facebook |
| Content Pillar | Single select | Education, Product, Proof, Brand, Product & Solutions, Questions & Objections, Promotion, Trend / Entertainment |
| Format | Single select | Short Video, Carousel, Static, Story, Text-Link, Live |
| Objective | Single select | Reach, Engagement, Traffic, Leads, Sales, Retention, Trust |
| Funnel | Single select | Awareness, Consideration, Conversion, Retention |
| Priority | Single select | P0, P1, P2, P3 |
| Review Due | Date | Review deadline |
| Publish Date | Date | Planned date, not proof of publication |
| Evidence Level | Single select | AUTHORITY, SOURCE, LOCAL_VALIDATED, PLATFORM_DRAFT_VERIFIED, LIVE_RELEASE_VERIFIED |
| Preview URL | Text | Inert review artifact URL only |
| Feed Order | Number | Instagram feed planning |
| Reuse Potential | Single select | High, Medium, Low, No |
| Claims Review | Single select | N/A, Required, Approved, Blocked |
| Rights Review | Single select | N/A, Required, Approved, Blocked |

Recommended views are Campaign Roadmap, Content Pipeline, Publishing Schedule, Instagram Feed Planner, Content Mix & Pillars, Cross-Platform Distribution, Creative Review, Publishing Readiness, Performance & Learnings, and Evergreen & Repurpose.

## Migrated Social Studio app

The migrated app is kept under `apps/social-studio/` so its package boundary is explicit. It is built and run independently from the Python/Email toolchain:

```bash
npm --prefix apps/social-studio install
npm --prefix apps/social-studio run verify
npm --prefix apps/social-studio run dev
```

The app's Notion integration is read-only and uses runtime environment variables only. No Notion token, Cloudflare token, Project ID, or deployment secret may be committed. The old Cloudflare Access deployment is not silently re-pointed or made public by this migration. If the dashboard is redeployed, it must retain authentication and receive a separate deployment approval.

## Public-repository safety

Because the repository is public:

- `exports/`, local environments, browser state, dependencies, generated screenshots, and temporary output remain ignored.
- Large media, customer proof, creator material, music, and stock imagery remain in the approved asset system. Git stores metadata and approved references, not the binaries.
- The repository may contain public-safe strategy and source material, but no PII, credentials, private customer URLs, unapproved testimonials, or unresolved secrets.
- Public email Pages output is an intentionally narrow fictional preview surface, not a dump of the Email Reference File.
- Social application code is public source, but the operator dashboard remains `noindex` and must be deployed behind authentication if hosted.

## Change management

Every change belongs to a canonical Issue or pull request. Local validation runs before a pull request. External writes are separate from source changes and must include exact scope, idempotency, re-fetch, and evidence. Any future platform operator must be disabled by default and must not infer authorization from a merged PR, Project status, or a date field.
