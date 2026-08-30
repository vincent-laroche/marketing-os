# Topol × Shopify — research archive

Research produced 2026-08-25 into building a Shopify marketing app with a Topol
email builder. Committed 2026-08-29 because it is decision-grade material that was
sitting untracked, the same failure mode that nearly lost `shopify-messaging/PHASE5-PLAN.md`
(#127).

**This is research, not an approved direction.** The decision it feeds is #135 —
whether `apps/marketing-os` is a single-owner internal tool or the seed of a public
Shopify app. Nothing here is committed to.

## Contents

| File | What it is |
|---|---|
| `topol-shopify-marketing-app.md` | The main report: architecture, Shopify surfaces, Topol integration design, data model, eight-phase roadmap, decision register |
| `shopify-findings.md` | Shopify platform research — extensions, Flow, marketing activities, segments, protected customer data |
| `topol-plugin-findings.md` | Topol Plugin capabilities — loader, callbacks, custom blocks, product feeds, server rendering |
| `architecture.png` | Rendered architecture diagram |
| `architecture.mmd` | Mermaid source for the diagram |

## Two findings worth reading even if #135 goes another way

**Shopify Messaging has no third-party transport API.** The reviewed public docs expose
no mutation to inject arbitrary app HTML/JSON into the Messaging editor, or to have
Messaging deliver an app-owned template. Any app-owned builder — Topol, Unlayer or
otherwise — needs an ESP adapter for delivery. This constrains `AGENTS.md` §3, which
names Shopify Messaging as the sole campaign platform.

**Marketing activity app extensions are deprecated.** New marketing automations should
use Flow triggers and actions. The report explicitly excludes the legacy extension.

## Provenance and what is missing

Original directory: `Creating a Shopify App with Topol Email Integration (branch)/`,
a Manus research branch. Files were renamed to ASCII kebab-case; content is unchanged
except for one edit noted below.

- The report's architecture diagram was an expiring `manuscdn.com` signed URL. It now
  points at the local `architecture.png`, which is the durable copy.
- Seven `CleanShot` screenshots were left in
  `~/08_warehouse/marketing-os-cleanup-2026-08-28/` rather than committed.
- **Three files did not survive the export.** `architecture_draft.md`, `roadmap_draft.md`
  and a saved copy of the Shopify action-endpoints documentation are each 111 bytes of
  `<Error><Code>AccessDenied</Code></Error>` — failed downloads, not content. Whatever
  the two drafts contained is not recoverable from this archive.

## Cost context gathered alongside this

Recorded here because no trial start date exists anywhere in the project:

- Topol has **no permanent free tier** — only a 14-day Plugin trial, no card advertised,
  with conversion to paid an explicit choice rather than an automatic charge.
- Topol Business is $300/month; Startup $70, Expansion $140, Enterprise $600+.
- Unlayer Free is $0 forever but excludes Custom Tools and Cloud API.

Fuller comparison, including Beefree, is in the warehouse dump at
`manus-dump/Marketing OS Build/Topol vs. Unlayer vs. Beefree.md` and
`vendor-pricing-comparison.csv`.
