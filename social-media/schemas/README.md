# Social Media OS Source Schema

Social source files use Markdown with YAML front matter. The front matter is the machine-readable record; the Markdown body contains the human-readable brief, script, caption, creative direction, evidence, and learnings.

## Record types

| Type | Path | Parent | Key |
|---|---|---|---|
| `campaign` | `social-media/campaigns/<campaign>/campaign.md` | Optional shared initiative | `social:campaign:<slug>` |
| `content` | `social-media/campaigns/<campaign>/content/<concept>/concept.md` | Social campaign | `social:content:<slug>` |
| `publication` | `social-media/campaigns/<campaign>/content/<concept>/publications/<platform>.md` | Content concept | `social:publication:<platform>:<slug>` |
| `asset` | `social-media/assets/<slug>.md` | Optional content/publication | `asset:<provider>:<id>` |
| `experiment` | `social-media/campaigns/<campaign>/experiments/<slug>.md` | Campaign or concept | `experiment:<slug>` |
| `evergreen` | `social-media/evergreen/<slug>.md` | Content concept | `evergreen:<slug>` |

## Shared fields

Every record must include:

```yaml
type: campaign | content | publication | asset | experiment | evergreen
key: namespaced-unique-key
title: Human-readable title
stage: Idea | Brief | Creating | Editing | Review | Approved | Scheduled | Published | Measuring | Complete | Blocked
channel: Social | Cross-channel
objective: Reach | Engagement | Traffic | Leads | Sales | Retention | Trust
funnel: Awareness | Consideration | Conversion | Retention
priority: P0 | P1 | P2 | P3
primary_kpi: Human-readable metric
```

`Published`, `Measuring`, and `Complete` records require evidence fields in the body or front matter. A record may never be considered published merely because a pull request merged or a date exists.

## Campaign fields

```yaml
type: campaign
key: social:campaign:<slug>
title: ...
stage: ...
channel: Social | Cross-channel
objective: ...
funnel: ...
priority: ...
primary_kpi: ...
content_pillars: Education, Product & Solutions, Customer Stories / Social Proof, Questions & Objections, Brand & Founder, Lifestyle / Identity, Promotion, Trend / Entertainment
production_start: YYYY-MM-DD
campaign_end: YYYY-MM-DD
initiative_key: marketing:initiative:<slug> | null
```

## Content concept fields

```yaml
type: content
key: social:content:<slug>
title: ...
stage: ...
channel: Social | Cross-channel
objective: ...
funnel: ...
priority: ...
primary_kpi: ...
campaign_key: social:campaign:<slug>
content_pillar: Education | Product & Solutions | Customer Stories / Social Proof | Questions & Objections | Brand & Founder | Lifestyle / Identity | Promotion | Trend / Entertainment
format: Short Video | Carousel | Static | Story | Text-Link | Live
reuse_potential: High | Medium | Low | No
```

The concept is the master creative idea. Platform-specific hooks, durations, captions, covers, on-screen text, and destination behavior belong on publication records.

## Publication fields

```yaml
type: publication
key: social:publication:<platform>:<slug>
title: ...
stage: ...
channel: Social
platform: Instagram | TikTok | Facebook
objective: ...
funnel: ...
priority: ...
primary_kpi: ...
content_key: social:content:<slug>
format: Short Video | Carousel | Static | Story | Text-Link | Live
publish_date: YYYY-MM-DD | null
feed_order: integer | null
copy_readiness: Needs Work | Ready | N/A
creative_readiness: Needs Work | Ready | N/A
accessibility: Needs Work | Ready | N/A
tracking_readiness: Needs Work | Ready | N/A
claims_review: N/A | Required | Approved | Blocked
rights_review: N/A | Required | Approved | Blocked
destination_url: inert or approved URL
preview_template: template id from social-media/templates/manifest.json
asset_keys: comma-separated asset keys | none
```

A publication is ready to schedule only when its copy, creative, accessibility, tracking, claims, and rights states are all acceptable for that publication. A `Published` publication also requires a platform identifier and live read-back evidence.

## Asset fields

```yaml
type: asset
key: asset:<provider>:<id>
title: ...
stage: Review | Approved | Blocked
channel: Social | Cross-channel
provider: Cloudinary | Other approved provider
provider_id: ...
approved_url: https://...
thumbnail_url: https://... | null
sha256: 64-character hexadecimal digest
rights_status: Required | Approved | Blocked | N/A
consent_status: Required | Approved | Blocked | N/A
permitted_uses: social,organic,instagram,tiktok,facebook
expires_on: YYYY-MM-DD | null
```

Large media files do not belong in this repository. The asset record is the provenance and approval registry.

## Labels and review flags

Use labels for overlapping characteristics rather than adding more single-value fields:

- `area:copy`, `area:video`, `area:design`, `area:editing`, `area:motion`, `area:photography`, `area:audio`
- `flag:needs-decision`, `flag:needs-asset`, `flag:needs-approval`, `flag:trend-sensitive`, `flag:evergreen`, `flag:sponsored`, `flag:customer-facing`
- `risk:claim`, `risk:copyright`, `risk:consent`, `risk:offer`, `risk:platform-policy`, `risk:tracking`

The validator treats unknown labels as errors when they are supplied in front matter. This keeps filtering deterministic.
