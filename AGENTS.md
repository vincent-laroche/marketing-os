# 01_projects — Root Agent Instructions

> Read this before working inside any subfolder of `01_projects`. It explains the convention every
> project here follows, so Claude Code, Codex, Antigravity, or any other agent can pick up a project
> mid-stream without re-deriving context.

## The convention

`01_projects` is the single, unified home for every active AI-agent project for OneHead Hair
Solutions (hairsolutions.co). One project = one top-level folder here. Every active project folder
carries three files:

- **`AGENTS.md`** — the project's single source of truth. Stable context: what the project is, where
  things live, hard rules, conventions, connectors. Read this first in any new session. Update it when
  something *durable* changes (a new rule, a corrected path, a new hard-won mechanic) — not for routine
  status updates.
- **`CLAUDE.md`** — a thin pointer (`@AGENTS.md`) so Claude Code loads the same content automatically.
  Don't add duplicate instructions here; if a note is genuinely Claude-specific, add a short section,
  but default to keeping everything in `AGENTS.md` so the two files can't drift apart.
- **`PROJECT.md`** — the living status log. Update this at the **end of every session**: current
  status, what changed, what's next, and which AI/tool touched it. This is what makes a Claude → Codex
  (or any direction) handoff work — the next agent reads `PROJECT.md` first to see where things stand,
  then `AGENTS.md` for the durable rules.

**Rule of thumb:** if it'll still be true next month, it belongs in `AGENTS.md`. If it's "what happened
this session / what's next," it belongs in `PROJECT.md`.

## Starting a session in any project

1. Read `<project>/PROJECT.md` — current status, last touched by which AI, open items.
2. Read `<project>/AGENTS.md` — durable context and rules.
3. Do the work.
4. Before ending the session, update `PROJECT.md` (status + a dated session-log line). Only touch
   `AGENTS.md` if something durable changed.

## Current projects

| Folder | What it is |
|---|---|
| `Email Marketing` | Rebuild of all HubSpot marketing emails (117) to modular section design, via API. The most mature project doc in this system — see its `AGENTS.md` as the model to match. Deliberately kept as a sibling of `hubspot/`, not nested inside it — see that project's `PROJECT.md` for the reasoning. |
| `Notion` | Small script set that rebuilds/maps the Notion "OS" databases (email marketing, social media, web design). **Confirmed by Vincent (2026-07-08): a genuinely separate effort from `05_knowledge/notion/`, not a duplicate** — no merge needed. |
| `Photo Retouch` | Hair-systems client photo retouching batches. |
| `Room Staging and Decoration` | Room staging concepts — floorplans, renders, mood images. |
| `Shopify Theme Dev` | **Grew substantially 2026-07-08** — now the docs/planning/reference/scripts home for the whole storefront project, having absorbed most of `06_storefront`'s non-repo content. Distinct from `06_storefront/shopify_github_synched_theme_files` (the actual live theme repo, stays put). |
| `Social Media Marketing` | Social Marketing Studio — internal Next.js app for social content planning/ops. Deployed to Cloudflare, access-restricted. |
| `hubspot` | **Consolidated 2026-07-08** — merged `Hubspot Setup/` and `Hubspot - Brand, ICP, Tracking, Buyer Intent & AEO/` into this one folder (subfolders: `inventory/`, `setup/`, `brand-icp-aeo-strategy/`, `workspace-setup-efficiency-agent/`). Single home for HubSpot platform/admin/strategy work — distinct from `Email Marketing/`, which stays separate. |
| `instagram_saved_content_to_notion` | `instagram-saves-content-engine` — Python pipeline syncing saved Instagram posts into Notion and generating reviewed content ideas. |

**Deleted 2026-07-08** (per Vincent): `Hermes Setup` (stub, no real content), `Marketing Strategy 2026`
(single docx, superseded), `Brand Design Systems` (superseded — brand truth lives only in `08_brand` now),
`Project Last Mile` (obsolete, content folded into `Email Marketing/`, `Social Media Marketing/`, and
`Shopify Theme Dev/` first), `hsc-brand-curation` (confirmed orphaned/stale git worktree of the real
`03_agents/hairsolutionsco-ai-toolkit` repo), `Hubspot Setup` and `Hubspot - Brand, ICP, Tracking, Buyer
Intent & AEO` (merged into `hubspot/`), `Knowledge Final Sorting`/`Skills Cleanup`/`Domain Settings`
(empty placeholders), `Artifacts` (per Vincent: same effort as `Email Marketing/`'s Email Marketing
Studio, neither actually used day-to-day — archived into `Email Marketing/archive/artifacts-legacy-2026-07-08/`,
then folder deleted).

**Not covered by this system** (asset/export dumps, not agent-driven work — leave as-is):
`Canva Export`, `audio_files`, `davinci_resolve`. `Domain Settings` is also currently empty.

**See `CLEANUP-STRATEGY-2026-07-08.md`** (this folder's root) for the full consolidation/cleanup history
and remaining open items.

## The four root "big project" folders

These are NOT part of the `01_projects` file convention — each is a large, live, git-tracked codebase or
content library with its own tooling, too big/heavy to fold in here. Attach whichever is relevant as a
second Claude Desktop folder when working in that domain; `01_projects` stays the lightweight "what's
going on" layer.

| Folder | Role |
|---|---|
| `/Users/vMac/04_marketing` | Content library — mostly superseded, per Vincent (2026-07-08): the real marketing content and knowledge has been moved to Notion. What's left is duplicate/needs-review material that conceptually belongs in `05_knowledge`, not here. **Not being triaged right now** — leave it sitting until Vincent is ready to treat it as a local knowledge base. Its obsolete persistent-agent runtime (`.agent/` — BOOTSTRAP/HEARTBEAT/SOUL/TOOLS/USER) was removed entirely 2026-07-08. |
| `/Users/vMac/05_knowledge` | Knowledge-base project — also mostly superseded by the Notion migration, per Vincent. Same as above: **not being triaged right now**, sits until Vincent is ready to work it as a local knowledge base. Contains sub-projects `the-hair-concierge/` and `Pricing Strategy 2026/`. Has a `_SENSITIVE_QUARANTINE/` folder — don't touch without confirming contents first. Its `.agents/` folder is just a `skills/` subfolder, not the same obsolete-runtime pattern as `04_marketing` — left untouched. |
| `/Users/vMac/06_storefront/shopify_github_synched_theme_files` | **This exact subfolder** (not `06_storefront/` itself) is the live, GitHub-synced hairsolutions.co Shopify theme repo — confirmed by Vincent 2026-07-08. Always attach this specific path for Shopify dev work. **Cleanup executed 2026-07-08:** everything else in `06_storefront/` (old duplicate theme copies, planning docs, audits, scripts, backups) has been moved into `Shopify Theme Dev/` or deleted where confirmed redundant — see that project's `PROJECT.md` for the full breakdown. `06_storefront-breadcrumbs` (a stray, fully-merged git worktree) was removed. `Hair Solutions Co. Design System/` (Figma export) deleted per Vincent. `shopify/` app folder investigated — confirmed scaffolding for the custom Shopify Admin API app created during the legacy-token-to-app-based-access migration; empty placeholder subfolders deleted, real app-config docs + secrets infrastructure kept (see `Shopify Theme Dev/AGENTS.md` for detail, including a flagged `.env` FIFO anomaly needing a fix). `06_storefront/` root now holds only the local theme-dev working copy, the live-repo subfolder, and the trimmed-down `shopify/` folder. |
| `/Users/vMac/08_brand` | **The one and only brand master, confirmed by Vincent 2026-07-08.** Every other brand reference anywhere in this system — the old "clay" palette, the "Crown Harbor" palette that superseded it, all of it — is now also superseded by a new palette living only in `08_brand`. Never trust a palette hardcoded into a project doc; always check `08_brand` directly. |

## Cross-cutting notes

- Business auth/secrets: `/Users/vMac/.env` (reachable via Desktop Commander when a project's own
  sandbox can't mount the home directory directly).
- **Brand: always check `/Users/vMac/08_brand` directly, never a cached palette in a doc** — see the
  table above. `Email Marketing/AGENTS.md` §4 has the fullest account of how many times this has already
  gone stale.
- If you create a new project folder here, copy this convention: add `AGENTS.md` + `CLAUDE.md`
  (`@AGENTS.md`) + `PROJECT.md`, and add a row to the table above.

## Imported Claude Cowork project instructions

### Project description

Email Marketing is Vincent's workspace for running Hair Solutions Co.'s email marketing across three
tools, each with its own job. The exact end-to-end flow isn't fixed yet — Vincent is still working it
out — so treat the roles below as current defaults, not a locked pipeline, and update this section once
a real pattern settles.

### HubSpot — campaign creation and production (account 50966981)

The HubSpot connector became write-capable on 2026-07-30 and is now powerful enough to create and edit
entire marketing emails and campaigns directly via the API — not just tweak existing ones. In scope:
subject line, from name, reply-to, preview text, recipients, subscription type, layout, A/B test setup,
campaign objects and their asset associations, and pulling email/campaign analytics and attribution.
Out of scope: sending and scheduling. Use the `hubspot-email-marketing` skill for this. Local Design
Manager module source (the reusable drag-and-drop building blocks) is a separate concern — use the
`hubspot-email-modules` skill for that.

### Figma — visualizing full HTML emails

Vincent has a one-month Figma Pro trial and considers it the best place to look at a complete HTML
email before it ships. Expect requests to lay out full HTML email campaigns in Figma purely so he can
review them visually — Figma is a rendering/review surface here, not where email HTML gets authored,
stored, or sent from.

### Notion — the database layer

Notion holds the structured, ongoing record: campaign metadata/info, copy and text drafts, and
performance stats/metrics. Treat it as where a campaign's data and results get logged, not where email
HTML lives.

### Standing note

None of the Figma, Notion, or HubSpot conventions above (folder structure, database schema, naming) are
settled yet. Ask Vincent before assuming a specific structure in any of the three, and tighten this
section once the actual flow emerges.
