# Email Preview Gallery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fail-closed static Shopify-Liquid preview compiler that produces rendered HTML, full desktop and mobile screenshots, exact provenance, private pull-request artifacts, and an explicitly published GitHub Pages gallery.

**Architecture:** A locked Node/TypeScript tool parses Shopify Liquid with strict variables and filters, composes schema-validated fictional fixtures, validates rendered HTML and URLs, captures deterministic Playwright screenshots, and emits one atomic output tree. Pull requests upload temporary private artifacts; a separate manual workflow may publish only source revisions that carry `preview_public: true` and satisfy every provenance and safety gate.

**Tech Stack:** Node 24, TypeScript 7.0.2, LiquidJS 10.29.0, Zod 4.4.3, parse5 8.0.1, Playwright 1.62.1, tsx 4.23.12, Node test runner, GitHub Actions, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-08-24-github-email-marketing-operations-design.md`

## Global constraints

- Use fictional fixture data only. Never read CRM exports, Shopify customers, MailerLite, HubSpot, logs, screenshots, or browser profiles for fixture values.
- Every successful primary preview has exactly three user-facing outputs: rendered HTML, a 1440px full-page desktop PNG, and a 390px full-page mobile PNG. `provenance.json` is required metadata beside them.
- Fail closed on unsupported tags, filters, variables, object paths, unresolved Liquid delimiters, authority placeholders, unsafe HTML, unsafe protocols, non-allowlisted hosts, live personalized links, token-like values, or missing Issue/PR/SHA provenance.
- Draft and review outputs stay in private, expiring Actions artifacts. Their URLs never populate Project Preview URL.
- Public publication requires `preview_public: true`, manual `workflow_dispatch`, an exact source SHA that is an ancestor of `main`, unique Email Issue and PR provenance, successful deployment read-back, and a reviewed publication-ledger pull request.
- Merge, approval, Stage, schedule, normal push, and `preview_public: true` alone never trigger publication.
- Pages enablement, custom-domain configuration, Cloudflare DNS, and initial public deployment remain separately approval-gated.
- Resolve gallery brand values from `/Users/vMac/08_brand` at implementation time; do not copy a cached palette from project documentation.

---

## Task 1: Create the locked preview package and fictional fixture model

**Files:**

- Create: `tools/email-preview/package.json`
- Create: `tools/email-preview/package-lock.json`
- Create: `tools/email-preview/tsconfig.json`
- Create: `tools/email-preview/src/types.ts`
- Create: `tools/email-preview/src/config.ts`
- Create: `tools/email-preview/fixtures/personas/normal-customer.json`
- Create: `tools/email-preview/fixtures/states/missing-first-name.json`
- Create: `tools/email-preview/fixtures/states/product-heavy.json`
- Create: `tools/email-preview/preview-config.json`
- Create: `tools/email-preview/test/config.test.ts`
- Modify: `.gitignore`

**Interfaces:**

- Produces: `loadPreviewConfig(root: string): Promise<PreviewConfig>`
- Produces: `composeFixture(config: PreviewConfig, personaId: string, stateIds: string[]): FixtureData`
- Produces: `PreviewSelection { emailCode, sourcePath, campaignKey, personaId, stateIds, previewPublic }`
- Consumes later: Tasks 2–6 use `PreviewSelection` and `FixtureData` without reading fixture files directly.

- [ ] **Step 1: Write failing configuration and privacy tests**

```ts
import assert from 'node:assert/strict';
import test from 'node:test';
import { composeFixture, loadPreviewConfig } from '../src/config.js';

test('loads 53 unique repository-relative email selections with public preview off', async () => {
  const config = await loadPreviewConfig(process.cwd());
  assert.equal(config.emails.length, 53);
  assert.equal(new Set(config.emails.map((x) => x.emailCode)).size, 53);
  assert.ok(config.emails.every((x) => !x.previewPublic));
  assert.ok(config.emails.every((x) => x.sourcePath.startsWith('shopify-messaging/emails/')));
});

test('missing-first-name removes the field instead of inserting real data', async () => {
  const config = await loadPreviewConfig(process.cwd());
  const fixture = composeFixture(config, 'normal-customer', ['missing-first-name']);
  assert.equal(fixture.customer.first_name, undefined);
  assert.doesNotMatch(JSON.stringify(fixture), /@|checkout\.shopify\.com|unsubscribe/i);
});
```

- [ ] **Step 2: Run the test and confirm it fails because the package does not exist**

```bash
cd tools/email-preview
npm test
```

Expected: non-zero exit because `package.json` or `src/config.ts` is absent.

- [ ] **Step 3: Add the exact locked package definition**

```json
{
  "name": "@hair-solutions/email-preview",
  "private": true,
  "type": "module",
  "engines": { "node": ">=24 <25" },
  "scripts": {
    "typecheck": "tsc --noEmit",
    "test": "tsx --test test/**/*.test.ts",
    "build": "tsx src/cli.ts build",
    "check": "tsx src/cli.ts check"
  },
  "dependencies": {
    "liquidjs": "10.29.0",
    "parse5": "8.0.1",
    "zod": "4.4.3"
  },
  "devDependencies": {
    "@types/node": "26.3.0",
    "playwright": "1.62.1",
    "tsx": "4.23.12",
    "typescript": "7.0.2"
  }
}
```

Run `npm install --package-lock-only` and require lockfile version 3. Add `node_modules/`, `.cache/`, `playwright-report/`, and generated preview output to `.gitignore`.

- [ ] **Step 4: Implement schema-validated composable fixtures**

Define `FixtureData` with only fictional customer, abandoned checkout, order, products, store, and inert-link values required by the current 53 emails. Deep-merge one base persona with named state overlays, validate the merged result with Zod, deep-freeze it, and reject unknown keys. Use visibly fictional values such as customer `Mara Example`, order `PREVIEW-1001`, and products prefixed `Preview`.

`preview-config.json` lists all 53 source paths, derives Campaign/email identity from `github-campaign-os/manifest.json`, selects one primary persona/state combination, and initializes every `preview_public` value to `false`.

- [ ] **Step 5: Verify determinism and commit**

```bash
npm --prefix tools/email-preview install --package-lock-only
npm --prefix tools/email-preview run typecheck
npm --prefix tools/email-preview test
git diff --check -- tools/email-preview .gitignore
git add tools/email-preview/package.json tools/email-preview/package-lock.json tools/email-preview/tsconfig.json tools/email-preview/src/types.ts tools/email-preview/src/config.ts tools/email-preview/fixtures tools/email-preview/preview-config.json tools/email-preview/test/config.test.ts .gitignore
git commit --only tools/email-preview/package.json tools/email-preview/package-lock.json tools/email-preview/tsconfig.json tools/email-preview/src/types.ts tools/email-preview/src/config.ts tools/email-preview/fixtures tools/email-preview/preview-config.json tools/email-preview/test/config.test.ts .gitignore -m "feat(preview): define fictional fixture registry"
```

---

## Task 2: Implement strict Liquid parsing and fail-closed HTML safety

**Files:**

- Create: `tools/email-preview/src/liquid.ts`
- Create: `tools/email-preview/src/safety.ts`
- Create: `tools/email-preview/src/render.ts`
- Create: `tools/email-preview/test/liquid.test.ts`
- Create: `tools/email-preview/test/safety.test.ts`
- Create: `tools/email-preview/test/fixtures/valid-liquid.html`
- Create: `tools/email-preview/test/fixtures/unsupported-liquid.html`
- Create: `tools/email-preview/test/fixtures/unsafe-links.html`

**Interfaces:**

- Consumes: `FixtureData`, `PreviewSelection` from Task 1.
- Produces: `renderStrict(source: string, fixture: FixtureData): Promise<string>`
- Produces: `validateRenderedHtml(html: string): SafetyReport`
- Produces: `SafetyError { code, sourcePath?, detail }`, where detail is safe and contains no HTML body or fixture value.

- [ ] **Step 1: Write failing parser tests**

```ts
test('renders the supported cart loop and fallback', async () => {
  const html = await renderStrict(SUPPORTED_SOURCE, PRODUCT_HEAVY_FIXTURE);
  assert.match(html, /Mara Example|there/);
  assert.doesNotMatch(html, /{{|}}|{%|%}/);
});

test('fails on an unsupported tag instead of dropping it', async () => {
  await assert.rejects(() => renderStrict('{% assign x = 1 %}{{ x }}', FIXTURE), {
    code: 'UNSUPPORTED_LIQUID_TAG'
  });
});
```

Cover `if`, `endif`, `for`, `endfor`, `limit`, `blank`, `default`, nested object access, `!=`, and `>`; reject every other tag/filter/operator until deliberately added with tests.

- [ ] **Step 2: Run focused tests and confirm the missing-module failure**

```bash
npm --prefix tools/email-preview test -- --test-name-pattern='Liquid|safety'
```

- [ ] **Step 3: Implement a strict LiquidJS boundary**

Instantiate LiquidJS with strict variables and filters. Parse before rendering. Walk/inspect the parsed template tokens and enforce the explicit tag/filter/operator allowlists; rendering is never regex substitution. Render against the frozen fixture only. Reject any remaining Liquid delimiter or Liquid-shaped authority instruction after rendering.

```ts
export const SUPPORTED_TAGS = new Set(['if', 'endif', 'for', 'endfor']);
export const SUPPORTED_FILTERS = new Set(['default']);

export async function renderStrict(source: string, fixture: FixtureData): Promise<string> {
  const templates = liquid.parse(source);
  assertSupportedTemplates(templates);
  const html = await liquid.render(templates, fixture);
  assertNoLiquidRemains(html);
  return html;
}
```

- [ ] **Step 4: Implement structural and URL validation with parse5**

Reject scripts, active forms, iframes, remote stylesheets, event-handler attributes, non-HTTPS remote resources, tracking pixels, data/javascript/vbscript protocols, token-looking query parameters, contact identifiers, real unsubscribe/checkout/account/tracking destinations, and hosts outside `hairsolutions.co` and `res.cloudinary.com`.

Rewrite personalized destinations to `href="#preview-inert"` with `aria-disabled="true"` and `data-preview-link-kind`; do not preserve original personalized URLs in comments or data attributes. General approved Hair Solutions links may remain after validation.

- [ ] **Step 5: Run the full package checks and commit**

```bash
npm --prefix tools/email-preview run typecheck
npm --prefix tools/email-preview test
git diff --check -- tools/email-preview
git add tools/email-preview/src/liquid.ts tools/email-preview/src/safety.ts tools/email-preview/src/render.ts tools/email-preview/test
git commit --only tools/email-preview/src/liquid.ts tools/email-preview/src/safety.ts tools/email-preview/src/render.ts tools/email-preview/test -m "feat(preview): fail closed on unsafe Liquid"
```

---

## Task 3: Generate the three outputs and exact provenance

**Files:**

- Create: `tools/email-preview/src/provenance.ts`
- Create: `tools/email-preview/src/capture.ts`
- Create: `tools/email-preview/src/output.ts`
- Create: `tools/email-preview/src/cli.ts`
- Create: `tools/email-preview/test/provenance.test.ts`
- Create: `tools/email-preview/test/output.test.ts`

**Interfaces:**

- Consumes: safe rendered HTML from Task 2.
- Produces: `buildEmailPreview(input: BuildInput): Promise<PreviewBuildResult>`
- Produces: deterministic directory `generated/<campaign>/<email>/<fixture>/<full-sha>/`.
- Produces: `email.html`, `<email>-desktop-<full-sha>.png`, `<email>-mobile-<full-sha>.png`, and `provenance.json`.

- [ ] **Step 1: Write failing output-count, SHA, and provenance tests**

Require the three user-facing outputs, a provenance sidecar, full 40-character SHA filenames, SHA-256 digests for all three outputs, exact Issue and PR URLs, source path/digest, fixture IDs/digest, compiler/lock digest, run/attempt, timestamp, visibility, and canonical URL rules. Missing or ambiguous Issue/PR provenance must fail.

- [ ] **Step 2: Implement deterministic provenance**

```ts
export interface ProvenanceInput {
  repository: string;
  sourceSha: string;
  sourcePath: string;
  emailCode: string;
  campaignKey: string;
  issueUrl: string;
  prUrl: string;
  workflowRunId: string;
  workflowAttempt: number;
  fixturePersonaId: string;
  fixtureStateIds: string[];
  visibility: 'private-review' | 'public';
  canonicalUrl?: string;
}
```

Embed non-visible provenance meta tags in `email.html`. Never watermark or modify the screenshots to carry provenance.

- [ ] **Step 3: Implement pinned Playwright capture**

Install the lockfile browser with `npx playwright install chromium`. Use Chromium from the locked Playwright package, `deviceScaleFactor: 1`, reduced motion, disabled animations/transitions, fixed locale/timezone, and `fullPage: true`. Capture widths 1440 and 390. Abort every request except the local document and explicitly allowlisted HTTPS image assets.

- [ ] **Step 4: Implement atomic output promotion**

Write one build to a temporary directory inside the generated-output parent. Validate HTML, both PNG signatures/dimensions, output count, and provenance digests. Rename the complete directory into place only after all checks pass. On any failure, delete only that task-owned temporary directory and preserve prior verified output.

- [ ] **Step 5: Verify reproducibility and commit**

Build the same fictional test email twice with the same fixed timestamp and inputs; require identical HTML and provenance content digests. Screenshot pixel digests must match in the pinned local environment.

```bash
npm --prefix tools/email-preview exec playwright install chromium
npm --prefix tools/email-preview run typecheck
npm --prefix tools/email-preview test
git diff --check -- tools/email-preview
git add tools/email-preview/src tools/email-preview/test
git commit --only tools/email-preview/src tools/email-preview/test -m "feat(preview): capture deterministic email outputs"
```

---

## Task 4: Produce and approve the gallery visual concept

**Files:**

- Create: `docs/design/email-preview-gallery/concept.html`
- Create: `docs/design/email-preview-gallery/desktop.png`
- Create: `docs/design/email-preview-gallery/mobile.png`
- Create: `docs/design/email-preview-gallery/decision.md`

**Interfaces:**

- Consumes: current `/Users/vMac/08_brand/brand-design-system` tokens and representative fictional preview metadata.
- Produces: approved desktop and mobile design evidence that Task 5 must implement exactly.

- [ ] **Step 1: Resolve current brand authority**

Read the current brand-design-system instructions, web tokens, typography, spacing, radius, and component contracts. Record source paths and revision in `decision.md`; do not hardcode email-card palette rules as gallery UI rules.

- [ ] **Step 2: Build one static visual concept**

The concept must show Campaign grouping, search, Campaign filter, Email cards, desktop/mobile screenshot access, interactive HTML access, public state, and a separate provenance panel. It must not show fake metrics, customer records, editable state, sending controls, or scheduling controls.

- [ ] **Step 3: Capture full desktop and mobile concept screenshots**

Use Playwright at 1440px and 390px. Verify keyboard focus, visible labels, sensible card hierarchy, and no horizontal overflow.

- [ ] **Step 4: Obtain Vincent's approval before Task 5**

Record the approval date and approved screenshot digests in `decision.md`. If approval is not present, stop this plan after committing the concept; do not implement the final gallery UI.

- [ ] **Step 5: Commit the approved concept evidence**

```bash
git add docs/design/email-preview-gallery
git commit --only docs/design/email-preview-gallery -m "design(preview): approve gallery concept"
```

---

## Task 5: Build the static gallery from verified preview metadata

**Files:**

- Create: `tools/email-preview/src/gallery.ts`
- Create: `tools/email-preview/assets/gallery.css`
- Create: `tools/email-preview/assets/gallery.js`
- Create: `tools/email-preview/assets/robots.txt`
- Create: `tools/email-preview/test/gallery.test.ts`

**Interfaces:**

- Consumes: `PreviewBuildResult[]` and the Task 4 approved concept.
- Produces: a complete static site directory with index, Campaign pages, Email detail pages, revision assets, `robots.txt`, and no unpublished Email.

- [ ] **Step 1: Write failing static-site tests**

Assert Campaign grouping, client-side search/filter metadata, keyboard landmarks, `noindex,nofollow,noarchive`, restrictive robots, interactive HTML link, two screenshot links, separate provenance links, no fake metrics, no private artifact URL, and exclusion of `preview_public: false` Emails from public mode.

- [ ] **Step 2: Implement deterministic static rendering**

Generate HTML strings from escaped metadata; do not introduce a runtime framework. Copy only the three verified outputs and public provenance needed for selected Emails. Exclude fixtures, source maps, logs, PR-only metadata, and repository source.

- [ ] **Step 3: Implement approved responsive styles and behavior**

Match the Task 4 concept. JavaScript may only filter/search already-public card metadata and enhance navigation; the gallery remains useful without JavaScript.

- [ ] **Step 4: Run accessibility, link, and screenshot comparison checks**

Use Playwright to tab through the page, check accessible names and overflow, validate all local links, and compare desktop/mobile renders with approved concept screenshots using a documented pixel-diff threshold. Any material mismatch blocks completion.

- [ ] **Step 5: Commit the gallery generator**

```bash
npm --prefix tools/email-preview run typecheck
npm --prefix tools/email-preview test
git diff --check -- tools/email-preview
git add tools/email-preview/src/gallery.ts tools/email-preview/assets tools/email-preview/test/gallery.test.ts
git commit --only tools/email-preview/src/gallery.ts tools/email-preview/assets tools/email-preview/test/gallery.test.ts -m "feat(preview): build static email gallery"
```

---

## Task 6: Add private review and deliberate public-publication workflows

**Files:**

- Create: `.github/workflows/email-preview-review.yml`
- Create: `.github/workflows/email-preview-publish.yml`
- Create: `tools/email-preview/src/github.ts`
- Create: `tools/email-preview/src/publication-ledger.ts`
- Create: `email-previews/publication-ledger.json`
- Create: `tools/email-preview/test/workflows.test.ts`
- Create: `tools/email-preview/test/publication-ledger.test.ts`

**Interfaces:**

- Review workflow produces one private artifact and one bounded, updated PR comment.
- Publish workflow consumes exact `source_sha` and Email selection inputs and never runs on push, merge, approval, schedule, or Stage.
- Successful public read-back produces a branch and pull request that appends to the publication ledger; it never commits to `main` directly.

- [ ] **Step 1: Write failing workflow-policy tests**

Parse the YAML as text/structured indentation without adding a YAML runtime dependency. Require review trigger `pull_request`, publish trigger only `workflow_dispatch`, SHA-pinned official Actions, temporary artifact retention, exact permissions per job, `github-pages` environment only on deploy, no secrets in command arguments, and no automatic public trigger.

- [ ] **Step 2: Implement the private review workflow**

Pin:

```text
actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09
actions/setup-node@a0853c24544627f65ddf259abe73b1d18a591444
actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02
actions/github-script@ed597411d8f924073f98dfc5c65a23a2325f34cd
```

Use `contents: read`, `pull-requests: write`, and no Pages permission. Install with `npm ci`, install the locked Chromium, render affected Emails, upload the three outputs plus provenance for 14 days, and update one marker-bounded PR comment with source SHA, safe results, expiry expectation, and reproduction command. Failed Emails receive no artifact output and report only safe error codes.

- [ ] **Step 3: Implement the manual public workflow**

Validate `preview_public: true` at the exact input SHA, prove the SHA is an ancestor of `origin/main`, resolve exactly one Email Issue and related PR, build all selected Emails atomically, validate the complete site, then deploy with SHA-pinned `configure-pages`, `upload-pages-artifact`, and `deploy-pages`. The deploy job has only `pages: write` and `id-token: write`; a later ledger job has narrowly scoped `contents: write` and `pull-requests: write`.

- [ ] **Step 4: Implement read-back and append-only ledger PR creation**

Fetch every canonical public URL after deployment, verify HTTP success, expected source SHA metadata, output digests, no Liquid, and no unsafe URL. Create/update branch `automation/email-preview-publication-ledger` and open one normal PR containing only the append-only ledger change. Do not update Project Preview URL until that PR merges and the core synchronizer reads the ledger from `main`.

- [ ] **Step 5: Verify workflows locally and commit**

```bash
npm --prefix tools/email-preview run typecheck
npm --prefix tools/email-preview test
python3 -m unittest tests.email_operations.test_github_templates -v
git diff --check -- .github/workflows tools/email-preview email-previews
git add .github/workflows/email-preview-review.yml .github/workflows/email-preview-publish.yml tools/email-preview/src/github.ts tools/email-preview/src/publication-ledger.ts tools/email-preview/test email-previews/publication-ledger.json
git commit --only .github/workflows/email-preview-review.yml .github/workflows/email-preview-publish.yml tools/email-preview/src/github.ts tools/email-preview/src/publication-ledger.ts tools/email-preview/test email-previews/publication-ledger.json -m "feat(preview): add governed review and publication workflows"
```

---

## Task 7: Integrate preview verification with Campaign OS

**Files:**

- Modify: `tools/github_campaign_os/build_manifest.py`
- Modify: `tools/github_campaign_os/sync_project.py`
- Modify: `tools/github_campaign_os/validate_repository.py`
- Modify: `tests/email_operations/test_campaign_os_manifest.py`
- Modify: `tests/email_operations/test_project_sync.py`
- Modify: `tests/email_operations/test_repository_validator.py`
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `PROJECT.md`

**Interfaces:**

- Consumes: `email-previews/publication-ledger.json` from merged `main` only.
- Produces: Preview URL in Issue Operations Snapshot and Project only for verified public ledger entries.

- [ ] **Step 1: Add failing ledger-to-Project tests**

Require blank Preview URL for private, expired, failed, intended, or unmerged output. Require a public URL only when Email code, source SHA, Issue, PR, output digests, and canonical URL match one append-only ledger entry.

- [ ] **Step 2: Implement bounded Preview URL synchronization**

Read the ledger during manifest compilation. Reject duplicate Email/SHA publication identities and any URL outside the configured Pages/custom-domain origin. The Project synchronizer mirrors the ledger-derived URL; it never reads Actions artifact URLs.

- [ ] **Step 3: Extend repository validation**

Require lockfile freshness, exact three-output contract tests, safe workflow triggers and permissions, no generated site or browser binary tracked, no fixtures in public output, and no unresolved Liquid in committed public evidence.

- [ ] **Step 4: Run the full local verification suite**

```bash
python3 -m unittest discover -s tests -v
npm --prefix tools/email-preview ci
npm --prefix tools/email-preview run typecheck
npm --prefix tools/email-preview test
python3 -m tools.github_campaign_os.build_manifest --check
python3 -m tools.github_campaign_os.validate_repository
git diff --check
```

- [ ] **Step 5: Update handoff and commit**

Document private review reproduction, manual publication requirements, artifact expiry, and the separate Pages/domain/Cloudflare gate. Commit only the integration files.

---

## Task 8: Separately approved Pages and custom-domain release

**Files:**

- Remote GitHub Pages settings
- Remote GitHub environment settings
- Remote domain verification
- Remote Cloudflare DNS
- Update after verified release: `email-previews/publication-ledger.json`, Issue/PR evidence, `PROJECT.md`

- [ ] **Step 1: Stop for explicit external-change approval**

Present the exact Pages visibility, selected first-public Emails, GitHub domain-verification record, proposed Cloudflare DNS record, rollback, and confirmation that every published byte is public. Do not continue from general build approval.

- [ ] **Step 2: Configure GitHub before DNS**

After approval, enable Pages with GitHub Actions, configure the `github-pages` environment, add and verify `email-preview.hairsolutions.co` in GitHub, and retain the verification TXT record.

- [ ] **Step 3: Apply the exact Cloudflare DNS change**

Apply only the approved record, verify DNS resolution and HTTPS, and preserve unrelated zones/settings.

- [ ] **Step 4: Manually publish selected eligible Emails**

Dispatch the public workflow with exact source SHA and Email selection. Verify Pages deployment, public read-back, noindex/robots, provenance, three outputs, and safety. Merge the generated ledger PR normally, then run Campaign OS synchronization so Preview URL appears.

- [ ] **Step 5: Record final external evidence**

Record GitHub run, deployment, ledger PR, public URLs, source SHA, Issue/PR provenance, DNS/HTTPS verification, and rollback. Do not claim this task complete from workflow intent alone.

---

## Plan self-review checklist

- [ ] Unsupported or unresolved Liquid always fails closed and cannot promote stale output.
- [ ] Every successful Email has exactly HTML, desktop PNG, and mobile PNG plus provenance metadata.
- [ ] Fixtures are fictional, composable, schema-validated, and independent of customer systems.
- [ ] Customer-specific links are inert and no PII, token, checkout, tracking, or real unsubscribe value survives.
- [ ] Private artifacts are temporary and reproducible from exact source SHA.
- [ ] Public publication requires the exact flag plus deliberate dispatch and never follows merge/schedule automatically.
- [ ] Every output resolves to one exact source SHA, Email Issue, PR, fixture, compiler lock, and digest.
- [ ] Preview URL derives only from a verified public ledger entry merged to main.
- [ ] Pages, custom domain, Cloudflare, and first publication remain behind a separate approval checkpoint.
