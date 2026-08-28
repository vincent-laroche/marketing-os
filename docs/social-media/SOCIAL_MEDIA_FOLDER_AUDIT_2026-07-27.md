# Social Media Marketing folder audit

**Date:** 2026-07-27
**Scope:** `/Users/vMac/01_projects/social_media_marketing`
**Mode:** Read-only audit and cleanup plan. No files were moved, deleted, published, or deployed.

## Recommendation

Keep one repository, but separate its three real concerns:

1. the live internal Social Marketing Studio app;
2. the current 2026 launch campaign;
3. a rebuilt, canonical Atelier Zero template library.

Do not delete the app source during the folder cleanup. The deployed app is still actively reading
Notion. It should either be repaired and protected, or explicitly decommissioned as a separate
production decision.

The active repository should not retain copied brand guides, mood-board screenshot dumps, generic ad
examples, old campaign sources, generated browser output, dependency folders, or hand-maintained
duplicates of the same campaign data.

## Current state

| Area | Finding |
| --- | --- |
| Total local size | Approximately 748 MB, including 666 MB of `node_modules`, 12 MB of browser screenshots, 5.6 MB of browser-run residue, 1.5 MB of stale build output, 27 MB of reference images, and 34 MB of Git history. |
| Git | `main` and `origin/main` both point to `0d25683`. The remote is synchronized, but the working tree contains 52 untracked files plus modified and deleted tracked files. |
| Valuable untracked work | The complete `FINAL Launch Campaign/`, `PROJECT.md`, template component sources, and reference material are not in Git. |
| Build | `npm run lint` does not type-check because `tsconfig.json` is deleted. `npm run build` fails on the unresolved `@/app/components` alias. |
| Live app | The live app is active and reports a successful Notion refresh. It is therefore not dead code. |
| Privacy | Unauthenticated `/daily` returns HTTP 200. Cloudflare Access is not protecting the internal app, despite the project contract. |
| Secrets | No obvious committed private keys or common token patterns were found. The code contains only environment-variable names and non-secret database identifiers. |
| HTML health | All five HTML artifacts parse, and all embedded JavaScript passes syntax checks. The newest creative gallery still has five broken local image/logo references. |
| Brand authority | The canonical Atelier Zero source check passes. The project-local template system and campaign gallery use older palettes and component rules. |

## Critical findings

### 1. The internal app is public

`https://social-marketing-studio.hairsolutions.co/daily` returns an unauthenticated HTTP 200 and
renders live Notion campaign data plus direct HubSpot Social shortcuts.

This is the highest-priority issue. Cleanup must not be mistaken for a security fix. The production
choice is:

- restore Cloudflare Access for Vincent only; or
- intentionally decommission the Worker and hostname.

Either option requires separate approval because it changes production infrastructure.

### 2. The active app cannot be rebuilt from the current worktree

The tracked files `tsconfig.json`, `next.config.ts`, and `public/robots.txt` are deleted locally.
The missing TypeScript path mapping causes the Vinext build to fail on `@/app/components`.

The existing `dist/` directory is not a reliable recovery source. Most of it dates from July 3 while
some metadata dates from July 26, so it is mixed generated residue rather than a clean release
artifact.

### 3. The template library exists, but it is legacy and not reproducible

The project has:

- seven square-post functions in `components/SocialBlocks.jsx`;
- three Story functions in the same file;
- shared primitives in `components/Primitives.jsx`;
- a compiled standalone viewer in `Hair Solutions Co - Social System.html`.

However:

- the JSX files have no imports or exports and depend on globals;
- the repository has no template build command, even though the HTML says to rerun one;
- the template system uses retired Core Palette V1 values, glass effects, full-serif headings,
  copied/typewritten wordmarks, and noncanonical fonts;
- the quote template contains unverified testimonial copy;
- the sale templates hardcode a 30% offer and urgency language;
- the Story sale template says “Swipe up,” an obsolete interaction;
- the canonical four carousel patterns are documented but are not implemented as reusable modules;
- there are no individual HTML files for each post or Story archetype.

These files should be preserved only until their useful structure is migrated to a real v7 template
source. They should not remain labeled as the current social design system.

### 4. The current campaign is valuable, but its presentation layer has drifted

`FINAL Launch Campaign/` is the current campaign bundle:

- `01 — Master Campaign Strategy.html`
- `02 — Launch Wireframes — Day by Day.html`
- `03 - Content Calendar.xlsx`
- `04 — Social Media Playbook.html`
- `05 — 30-Day Social Creative — First Draft.html`

The bundle is current in campaign timing and content intent. It starts August 3, 2026 and carries the
Days 1–30 creative work that should be preserved.

The presentation is not fully current:

- files 02 and 05 use the pre-v7 Atelier Zero palette;
- file 05 includes mustard, olive, glass surfaces, and shadows that the current system prohibits;
- file 05 points to five local assets that no longer exist;
- file 05 points to a retired copied-logo location instead of the approved logo source;
- files 01 and 04 are intentionally sketch-styled internal documents, not production social
  templates;
- changing product prices and offers are embedded as static text and require a fresh live check before
  use.

Preserve the campaign data and layouts. Refresh the rendering layer before treating any output as a
current production template.

### 5. Campaign data is maintained in too many places

The same or overlapping content exists in:

- live Notion databases;
- `lib/data.ts`;
- `FINAL Launch Campaign/02 — Launch Wireframes — Day by Day.html`;
- `FINAL Launch Campaign/03 - Content Calendar.xlsx`;
- `FINAL Launch Campaign/05 — 30-Day Social Creative — First Draft.html`;
- older root-level Markdown, CSV, and XLSX files.

This already creates visible conflicts:

- the old 180-day spreadsheet starts in February;
- the retired 90-day strategy starts in May;
- the Week 1 batch uses July dates;
- the final campaign starts August 3;
- the app’s seed data and live Notion data use a different shape from the final HTML gallery.

Recommended precedence:

1. live Notion for operational status, dates, asset links, and approvals;
2. one versioned campaign snapshot in the repository;
3. generated HTML and XLSX outputs from that snapshot;
4. `/Users/vMac/08_brand/brand-design-system` for all visual and content rules.

### 6. The live app mishandles Week 1’s three-post days

Live Notion returns three posts for each of Days 1–7. The app uses `post.day` as the React key, anchor
ID, and day-jump value, so it renders duplicate keys, duplicate `id="day-1"` style anchors, and repeated
day-navigation entries.

This is not a folder-cleanup issue, but it is a current app defect and should be fixed if the app is
retained.

## Template inventory

### Existing reusable concepts

Square/feed concepts:

1. `hero-brand-post`
2. `single-product-post`
3. `collection-post`
4. `quote-testimonial-post`
5. `blog-article-post`
6. `sale-promo-post`
7. `announcement-post`

Story concepts:

1. `story-product`
2. `story-quote`
3. `story-sale`

The 30-day gallery also contains useful generator logic for:

- wordmark, typographic, quote, product, and media statics;
- carousel slides;
- 1080 x 1350 Reel covers;
- 1080 x 1920 Reel storyboard frames;
- 1080 x 1920 Story frames;
- safe-zone overlays and production holds.

### Missing from a durable template system

- individual HTML output for each post and Story archetype;
- the four canonical carousel modules: how-it-works, before-after, drop-reveal, and testimonial-set;
- reusable Reel cover and Reel storyboard modules;
- a canonical 1080 x 1350 feed portrait master;
- an actual source-to-HTML build command;
- exports/imports and tests for the component source;
- approved-logo and approved-font hash verification;
- a current v7 token layer;
- a source manifest that distinguishes template, campaign instance, and generated preview.

## Exact keep, merge, archive, and remove map

### Keep active

Keep and repair the app/runtime source:

- `.openai/hosting.json`
- `app/`
- `build/`
- `lib/`
- `worker/`
- `public/favicon.svg`
- `package.json`
- `package-lock.json`
- `vite.config.ts`
- the tracked `tsconfig.json`, `next.config.ts`, and `public/robots.txt` if the app remains active

Keep and correct the project handoff files:

- `AGENTS.md`
- `CLAUDE.md`
- `PROJECT.md`
- `README.md`

Keep the current campaign content, moved under a dated campaign folder:

- all five numbered final artifacts, including the XLSX calendar as a generated/export format rather
  than the editable source.

### Keep only until migrated

- `components/Primitives.jsx`
- `components/SocialBlocks.jsx`
- `components/SystemPageShell.jsx`
- `styles/tokens.css`
- `Hair Solutions Co - Social System.html`

Their archetype structure is worth saving. Their design values, claims, offers, and build mechanics are
not current.

### Merge

1. Merge `FINAL Launch Campaign/02`, `03`, and `05` around one campaign data snapshot instead of
   embedding separate copies of the same days.
2. Merge the template JSX and compiled HTML into one source-controlled template package with generated
   output.
3. Replace local brand copies with a short reference index that points to:
   - `/Users/vMac/08_brand/brand-design-system/brand-design-system.html`
   - `/Users/vMac/08_brand/brand-design-system/specs/PLATFORM_SOCIAL.md`
   - `/Users/vMac/08_brand/logos`
4. Keep Notion as the operational status owner; treat repository campaign data as a dated snapshot,
   not a second live database.

### Archive outside the active tree

These are superseded source/provenance files:

- `90-Day Launch Strategy — Improvement Punch-List.md`
- `HSC-90Day-Rebrand-Launch-Strategy.md`
- `Week 1 Launch Batch — Hair Solutions Co Instagram.md`
- `Hair_Solutions_180Day_Instagram_Campaign.xlsx`
- `canva_social_production_matrix.csv`
- `social_design_analysis.md`
- `FINAL Launch Campaign/02 — Wireframe Build Spec (for Sonnet).md`

These are reference/provenance images, not current production assets:

- all 12 “Original Atelier Zero Design System with Photos” screenshots;
- both generated marble-head replacement images;
- all 18 generic “Social:Ads:Sories” examples;
- all eight `social-media-posts/` screenshots.

The generated marble-head images are especially unsuitable for the active system because the canonical
brand contract prohibits generated AI imagery and stock photography.

### Remove from the active tree after backup

Regenerable or operating residue:

- `node_modules/`
- `dist/`
- `output/`
- `.playwright-cli/`
- `.wrangler/`
- `tsconfig.tsbuildinfo`
- every `.DS_Store`
- the empty `scripts/` directory
- the empty `reference/Atelier Zero Design System Photos Background only/` directory

Exact duplicate:

- `reference/atelier-zero-design.md` is byte-identical to
  `/Users/vMac/08_brand/atelier-zero-design-system-from-theme.md`.

## Reference recommendation

Keep no copied reference images in the active repository.

Replace the current 27 MB reference folder with two small maintained files:

1. `reference/README.md` — canonical brand, logo, social-spec, and approved-media routing;
2. `reference/TEMPLATE_CATALOG.md` — the current feed, Story, carousel, and Reel template inventory.

This is safer than selecting two arbitrary screenshots and calling them current.

## Proposed active structure

```text
Social Media Marketing/
├── AGENTS.md
├── CLAUDE.md
├── PROJECT.md
├── README.md
├── package.json
├── package-lock.json
├── tsconfig.json
├── next.config.ts
├── vite.config.ts
├── app/
├── build/
├── lib/
├── public/
├── worker/
├── campaigns/
│   └── 2026-rebrand-launch/
│       ├── README.md
│       ├── campaign.snapshot.json
│       ├── 01-master-strategy.html
│       ├── 02-day-by-day-wireframes.html
│       ├── 03-content-calendar.xlsx
│       ├── 04-social-playbook.html
│       └── 05-30-day-creative-draft.html
├── templates/
│   ├── src/
│   │   ├── primitives/
│   │   ├── feed/
│   │   ├── stories/
│   │   ├── carousels/
│   │   └── reels/
│   ├── html/
│   │   ├── index.html
│   │   ├── feed/
│   │   ├── stories/
│   │   ├── carousels/
│   │   └── reels/
│   └── manifest.json
├── reference/
│   ├── README.md
│   └── TEMPLATE_CATALOG.md
└── docs/
    └── SOCIAL_MEDIA_FOLDER_AUDIT_2026-07-27.md
```

## Execution plan

### Phase 0 — production decision

Before deploying anything:

1. restore Cloudflare Access for Vincent only; or
2. approve decommissioning the live app.

No folder move should silently make this production decision.

### Phase 1 — protection

1. Create a dedicated cleanup branch.
2. Create a fresh Git bundle, working-tree patch, dependency-excluded source snapshot, and SHA-256
   manifest under `/Users/vMac/01_projects/_backups/`.
3. Verify the bundle and archive before any move.
4. Commit the valuable currently untracked campaign and handoff files unchanged as a preservation
   checkpoint.

The July 26 backup currently lives under Trash. Its Git bundle verifies and its source snapshot is
readable, but Trash is not durable protection and it predates the final cleanup decision.

### Phase 2 — restore a reproducible app

1. Restore or intentionally replace the deleted tracked configuration files.
2. Fix Week 1 keys and anchors.
3. Update the stale path in `README.md`.
4. Run type-check and build.
5. Do not deploy until Cloudflare Access is correct.

### Phase 3 — consolidate campaign data

1. Extract one normalized Days 1–90 campaign snapshot.
2. Generate the wireframe HTML, calendar XLSX, and creative gallery from it.
3. Keep live Notion fields separate from immutable campaign copy.
4. Move the final campaign into `campaigns/2026-rebrand-launch/`.

### Phase 4 — rebuild the template library

1. Port the useful feed and Story archetypes to Atelier Zero v7.
2. Add the missing carousel and Reel modules.
3. Remove hardcoded testimonials, discounts, prices, urgency, and obsolete Story actions.
4. Verify approved logo/font hashes at build time and embed approved assets in generated standalone
   HTML.
5. Generate individual HTML files plus one gallery index.
6. Browser-check square, portrait, Story, and Reel outputs at native dimensions and mobile preview.

### Phase 5 — archive and clean

1. Move superseded planning sources and reference images to the verified external archive.
2. Remove the exact copied brand document.
3. Remove generated dependencies, stale build output, screenshots, local browser state, `.DS_Store`
   files, and empty directories.
4. Keep the active reference folder to two pointer/catalog files.

### Phase 6 — verification

Required completion evidence:

- clean Git status on the cleanup branch;
- current app type-check and build pass;
- template source regenerates every HTML output;
- all generated HTML parses and embedded JavaScript passes syntax checks;
- no broken local asset references;
- canonical brand source check passes;
- no copied brand binaries or unapproved reference imagery remain;
- no secrets or customer identifiers are committed;
- `main` and the intended GitHub branch are synchronized after approval;
- unauthenticated live access redirects to Cloudflare Access, or the app is intentionally offline.

## Expected result

Removing regenerated dependencies and audit residue reduces the local project from roughly 748 MB to
approximately 35–40 MB including Git history. The maintained working source itself should remain under
approximately 2 MB before approved campaign media.

More importantly, the cleanup establishes one current campaign source, one current template source,
one canonical brand authority, and one explicit production-app boundary.

## Cleanup execution record

Approved local cleanup was completed on `codex/social-marketing-cleanup` on 2026-07-27.

### Protection and reversibility

- Created and verified:
  `/Users/vMac/01_projects/_backups/2026-07-27-social-media-marketing-cleanup/`
- The recovery package contains a complete Git bundle, binary working-tree patch, dependency-excluded
  source snapshot, original-state inventories, archived superseded files, and SHA-256 manifests.
- Generated dependencies, build output, local browser artifacts, caches, and metadata residue were moved
  to Trash after verification. They are also reproducible from the retained source.

### Active structure after cleanup

- `campaigns/2026-rebrand-launch/` now owns the retained 2026 campaign.
- `campaign.snapshot.json` contains the full 90-day calendar (104 scheduled rows), the detailed 30-day
  creative plan (44 feed items and 98 Story frames), and the weekly Story rhythm.
- `templates/` now owns one v7 source layer, one manifest, one hash-verifying build command, one gallery
  index, and 16 individual HTML templates:
  - seven feed templates;
  - three Story templates;
  - four carousel templates;
  - two Reel templates.
- `reference/` contains only the source-routing note and template catalog.
- Retired planning, the legacy component sketch, the copied brand document, and screenshot libraries are
  outside the active repository in the verified archive.

### App repair

- Restored the tracked TypeScript, Next, and robots configuration.
- Replaced duplicate Week 1 React keys, duplicate day anchors, duplicate day navigation, and repeated
  Story lanes with one grouped row per launch day.
- Updated calendar and mockup card keys for multiple posts on the same day.
- Replaced the retired app palette with current Atelier Zero v7 roles and removed the prior glass and
  gradient treatments.
- Corrected the mobile navigation width after rendered 390px review.

### Verification evidence

- `npm run verify` passed before the regenerable dependency directory was removed.
- Canonical Atelier Zero source verification passed across 30 authority files.
- The canonical logo and font hashes passed during every template build.
- The app rendered at 1440px and 390px without browser warnings or errors.
- Representative feed, carousel, Story, and Reel templates rendered without browser warnings or errors.
- All 21 active HTML documents parsed; all inline JavaScript passed syntax checking.
- Every active local HTML/CSS asset reference resolves.
- The campaign workbook passed ZIP/container integrity checking.
- No high-confidence secret or private-key pattern was found in the active source.
- The active repository is approximately 36 MB, down from roughly 748 MB.

### Deliberately not changed

- No social post was published or scheduled.
- No Notion data was written.
- No Cloudflare setting was changed.
- No app deployment was performed.
- The live site's unauthenticated HTTP 200 remains a production security blocker. Cloudflare Access must
  be restored separately before any future deployment or release claim.

## Studio decommissioning addendum

On 2026-07-27, Vincent explicitly approved retirement of the obsolete Studio. A new verified Git bundle
and Studio-source snapshot were created before deleting the Cloudflare custom-domain binding and the
`social-marketing-studio` Worker. Cloudflare then returned no matching Worker or custom domain, and the
former URL returned HTTP 530 instead of serving the app. No matching Cloudflare Access application or DNS
record was present through the available account APIs.

The Vinext app, Notion read integration, Worker, deployment configuration, package lock, and build source
were moved to `/Users/vMac/01_projects/_backups/2026-07-27-social-media-studio-decommission/`. The active
repository now retains only the campaign, template library, reference routing, scripts, and audit record.
The GitHub repository was also renamed from `social-marketing-studio` to `social-media-marketing`.
