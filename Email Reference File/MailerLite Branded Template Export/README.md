# MailerLite branded template export — 16976917

Saved page of `dashboard.mailerlite.com/preview/templates/16976917`, captured 2026-08-19.

**Preserve this file.** MailerLite's public API blocks reading a single template —
`GET /api/templates/16976917` returns *"The GET method is not supported for route.
Supported methods: DELETE."* The `/templates` list endpoint returns only MailerLite's
stock gallery, and `/campaigns` returns 0. So this saved page is the only programmatic
access to this template outside the editor UI.

## What it is

MailerLite's **native default block set, recoloured to brand** — `ml-block`,
`mlContentTable`, `ml-btn`, `container ml-N` markup, carrying placeholder copy
("Compelling headline", "Introduce your concept").

Palette in use: `#151411` ink (40 uses), `#EA6452` coral (3 uses) — the
**Email Reference File module palette** named in AGENTS.md §1.

## How it differs from the Atelier Zero module library

This is a *different generation* from `mailerlite-blocks/` (git tag
`approved-module-library-2026-08-19`), and the two use different palettes:

| | This template | Atelier Zero library |
|---|---|---|
| Markup | MailerLite-native `ml-*` blocks | custom `az-module-shell` tables |
| Ink | `#151411` | `#15140F` |
| Coral | `#EA6452` | `#ED6F5C` |
| Light surfaces | — | Bone `#F7F1DE` / Paper `#EFE7D2` |
| Rule | — | `#DDD2B6` |
| Width | MailerLite default | 576px |
| Radius | MailerLite default | role-based 8/12/16/20px |
| Copy | placeholder | real, per-module |

Which generation is authoritative is an open decision — do not assume.
