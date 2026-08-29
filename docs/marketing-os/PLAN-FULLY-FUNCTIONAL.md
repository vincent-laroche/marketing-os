# Marketing OS — Get to Fully Functional

> Plan for the next implementation agent. Assume no memory of prior sessions.
> Repo: `~/04_marketing/marketing-os` → `github.com/vincent-laroche/marketing-os` (public).
> Read `AGENTS.md` first, then `PROJECT.md`. Its hard rules bind every phase below.
>
> **This document is a plan, not a tracker.** Per `AGENTS.md` §8, work lives on its Issue:
> Phase 1 → #116 · Phase 2 → #131 · Phase 3 → #118, #119 · Phase 4 → #132 ·
> Phase 6 → #120, #121, #122, #123, #129. Parent audit: #117.
> Anything tracked only here is by definition untracked.

## Context

The repository was consolidated on 2026-08-28: four local folders became one, two GitHub
repos became one, and everything load-bearing is now committed. That work is done and is
not revisited here.

What remains is that **the application itself was never in version control.** It was built
in a Manus sandbox, still runs there, and its source exists only as an unreliable flat dump.
Because nobody can change it, two known defects stay live — most visibly, the app tells you
36 of 53 emails are `source_blocked` when in fact none of them are.

This plan takes the system from "infrastructure healthy, app unowned" to fully functional
and fully off the sandbox.

### What already works — do not "fix" these

| Component | State | Evidence |
|---|---|---|
| **Notion sync** | **Healthy.** Do not rebuild it. | Worker `/status`: 192 records, 11 sources, `blocked_count: 0`, all `Synced`; cron `*/30 * * * *` |
| Worker runtime | Live, `operations: disabled` (correct safety default) | `/health` 200 |
| Repository | Clean: 1 worktree, 45 tests / 341 subtests, manifest reproducible, Social OS PASS | local run |
| App runtime | Serving (HTTP 200) but source is not in git | `haircampaign-k3lybt53.manus.space` |

### Definition of done

1. `apps/marketing-os/` exists in the repo, builds, and its test suite passes.
2. The app runs on Cloudflare at a `hairsolutions.co` domain; the Manus deployment is retired.
3. #118 fixed — no email is falsely `source_blocked`; regression tests prove it.
4. #119 fixed — remaining states read as their actual evidence class.
5. #116 merged; deployed Worker source matches `main`.
6. Notion still reports 192 records Synced, 0 blocked, **after** the app moves.
7. #120–#123 either resolved from supplied evidence or explicitly pending with a named owner ask.

---

## Phase 1 — Merge the Worker (small, independent, do first) — #116

The Worker is deployed and working, but its source lives only on unmerged draft PR #116.
That is the same untracked-code problem the consolidation just eliminated.

1. Check out `feature/marketing-os-notion-sync`; run `npm run check` and `npm test` in
   `workers/marketing-os-notion-sync/` (expect syntax clean, **10/10** pass).
2. Verify against `docs/marketing-os/OPERATING-CONTRACT.md`: metadata-only writes, the
   restricted webhook event set, no send path, no cross-channel inference.
3. Mark ready for review and merge. Record the test counts on #116.

Do **not** broaden webhook events, Notion sources, Shopify scopes, or Social operations.

## Phase 2 — Reconstruct the app source (the risky one — gate it) — #131

Source: `~/08_warehouse/marketing-os-cleanup-2026-08-28/manus-dump/Marketing OS Build/`
(245 files, flat, no directories).

**Treat the dump as untrusted.** Its `package.json` is from `beefree-sdk-demo`, a different
project. If one foreign file is in there, files may equally be missing.

1. Rebuild the tree from import paths. Known structure, inferred from the files themselves:
   `server/` (`canonical.ts`, `campaigns.ts`, `db.ts`, `routers.ts`, `trpc.ts`, `qa.ts`,
   `release.ts`, `storage.ts`, `notion.ts`, `marketingSync.ts`, `exportPackage.ts`),
   `server/_core/` (`env.ts`, `context.ts`, `notification.ts`), `drizzle/schema.ts` +
   six migrations, `src/` (React surfaces: `App.tsx`, `EmailOverview.tsx`,
   `SocialWorkspace.tsx`, `SyncHealth.tsx`, `ReleaseGate.tsx`, `AccessGate.tsx`, …),
   `shared/const.ts`, plus `vite.ts`, `vitest.config.ts`, `index.html`.
2. Write a **real** `package.json` from the actual imports — do not use the dump's.
3. Cross-check against the live app's served bundle at `haircampaign-k3lybt53.manus.space`
   to catch modules the dump omitted.
4. **Gate — do not proceed to Phase 3 until all three hold:**
   - `npm run build` succeeds.
   - The test suite runs and passes (the handoff cites 35 tests).
   - The app boots locally against the **existing Manus database** and serves the email list.

   A reconstruction that cannot run is not a reconstruction. If the gate fails, stop and ask
   Vincent for a structured Manus export rather than guessing further.
5. Commit to `apps/marketing-os/`. **Audit before committing — the repo is public:** no
   `.env`, no secrets, no `node_modules`, no customer data. `notionSecret.test.ts` and the
   Cloudflare bindings are the ones to check.

## Phase 3 — Fix the two defects (do this before porting)

Fix them while the app still runs on its known-good platform, so failures are attributable
to the fix rather than to the migration.

**#118 — two bugs, both confirmed in `server/canonical.ts`:**

```ts
function toList(value: string) {
  return value.split(/\n|;|\|/)   // ← no comma; comma is the ONLY separator the data uses
```

So `"Text - Masthead, Quote - Centered"` is looked up as one module name that cannot exist.
Separately, `deriveStatus` marks any non-empty `Missing Modules` as `source_blocked` without
consulting any inventory.

Fix **both together** — fixing only the regex converts 36 blocked emails into 36 emails
blocked on 89 individual labels. Consume the committed manifest
`github-campaign-os/module-availability.json` (89 requirements: 74 exact declared labels,
11 documented aliases, 4 punctuation folds; fail-closed proven for absent artifacts).
Keep the existing dependency labels flowing to `needs_input` — they already map correctly
to the #120 evidence classes.

**#119** — use the state vocabulary already agreed on that Issue: *Module availability
verified*, *Source evidence required*, *Owner confirmation required*, *Protection active*,
*No verified Shopify observation*. Retain every safety gate; do not turn a protective state
into a ready one.

Add regression coverage for all 36 formerly-false blockers **and** for an unavailable module
staying fail-closed.

## Phase 4 — Port off Manus — #132

Only three Manus seams exist. Replace each; everything else is ordinary Node/React.

| Seam | File | Replacement |
|---|---|---|
| Object storage | `server/storage.ts` (Forge presigned → S3) | Cloudflare **R2** binding |
| Owner notification | `server/_core/notification.ts` (`notifyOwner` → Forge API) | MailerSend (already in repo, `mailersend/`) or a logged no-op |
| Login | Manus OAuth, `users.openId` in `drizzle/schema.ts` | **Cloudflare Access** — see below |
| Database | `DATABASE_URL`, MySQL via `drizzle-orm/mysql2` | Managed MySQL via **Hyperdrive** |

**Auth — recommendation, confirm before ripping anything out.** This is a single-owner
internal tool. Cloudflare Access (Zero Trust) puts identity in front of the Worker, so the
app needs no auth code at all and the `users` table plus `openId` can go. That is a schema
change, so get Vincent's explicit yes first. If he prefers in-app auth, keep the table and
swap only the identity provider.

**Database.** Provision managed MySQL (PlanetScale or Neon-compatible). The six existing
Drizzle migrations apply unchanged — do not convert to D1/SQLite, which would mean rewriting
all of them. Reach it from the Worker through Hyperdrive. Migrate data from the Manus
instance and verify row counts on both sides before cutover.

**Deployment — copy the pattern already in this repo:** `apps/social-studio/public-gallery/wrangler.jsonc`.
Match its conventions: `workers_dev: false`, `preview_urls: false`, assets binding, custom
domain on `hairsolutions.co`, `observability.enabled`. Mirror its npm script shape too —
a `verify` (lint + build) that must pass before any `deploy`.

**Update the Worker's receipt URL.** `workers/marketing-os-notion-sync/wrangler.jsonc` has
`MARKETING_OS_RECEIPT_URL` pointing at `haircampaign-k3lybt53.manus.space/api/sync/notion/receipt`.
It must move with the app, or sync receipts silently stop landing. This is the single most
likely thing to be missed.

Retire the Manus deployment only after the Cloudflare one is verified.

## Phase 5 — Prove Notion still works end to end

Notion is healthy today. The port is what could break it.

1. `GET /health` and `/status` — expect `operations: disabled`, 192 records, `blocked_count: 0`.
2. Confirm the scheduled run still completes after cutover and that its receipt reaches the
   **new** app URL — check `mappings` still reports 192 `Synced`.
3. Confirm exactly one cron (`*/30 * * * *`) and the unchanged webhook event set.
4. Confirm canonical parity: 53 emails, 16 Social fixtures.

## Phase 6 — Close out the evidence Issues

Inspect for authoritative evidence supplied since 2026-08-28. If none, leave each explicitly
pending with a precise owner ask — **never fabricate a source value.**

- **#120** — consent/form evidence (W-1…W-5), offer values (PP-7b, C-3, W-1, W-4, NL-03/08/13/18),
  proof/rights (NL-07, NL-12, NL-17). Note `PHASE5-PLAN.md` is now committed and documents
  `hs-consented-2026` (986, owner-attested).
- **#121** — review/handoff/performance evidence. Performance needs a verified Shopify
  observation, which needs an owner-authorized external send. Do not create one.
- **#122** — least-privilege Shopify catalog credential. **Requires Vincent's approval before
  requesting any credential.** Read-only scopes only; never customer, consent, audience,
  order, Flow, Messaging or send scopes.
- **#123** — Social production evidence. Fixtures stay fixtures until approved material exists.
- **#129** — `proof-bank/extract_proof_bank.py` writes `used_in` empty and a re-run silently
  erases all 16 rights assignments. Safely fixable in code; do it.
- **PR #130** — NL proof insertions, open pending Vincent's rights decision under #120.
- **PR #84** — Claude agent suite, `MERGEABLE`, unblocked. Vincent's call.

## Phase 7 — Record and hand back

Per `AGENTS.md` §8, a finding not in an Issue or PR does not exist.

- Update #117 (parent), close #118/#119 when their fixes land with test counts cited.
- Update `PROJECT.md` — it is a chronological log, not a backlog; every open item names its Issue.
- Add any new Issues to Project #4 (Email) or #5 (Social). **Projects v2 writes work** with
  the `gh` keyring token — the old "browser required" note was wrong. Set `Status` and
  `Work Type` when adding; `item-add` leaves every field blank otherwise.
  Never touch Project #2.

---

## Verification

```bash
cd ~/04_marketing/marketing-os
python3 -m pytest tests/ -q                                   # 45 passed, 341 subtests
python3 -m tools.github_campaign_os.build_manifest --check     # reproducible
python3 -m tools.social_os.validate_social_os                  # PASS (5 source records)
cd apps/marketing-os && npm run build && npm test              # app builds and passes
cd ../../workers/marketing-os-notion-sync && npm run check && npm test   # 10/10
```

Then confirm, by reading back rather than asserting:

1. App answers on its `hairsolutions.co` domain; Manus URL retired.
2. **Zero** emails falsely `source_blocked`; the 36 resolve; an absent module still fails closed.
3. Worker `/status` — 192 records, `blocked_count: 0`, `operations: disabled`, one `*/30` cron.
4. A sync receipt lands at the **new** app URL after cutover.
5. `git status` clean but for gitignored `exports/`; `git worktree list` shows one entry.

## Guardrails — not negotiable by convenience

- **No marketing send path** (§2). Nothing may send, schedule, activate a Flow, mutate an
  audience or change consent state. The `mailersend` transactional allowlist is not widened.
- **`Email Reference File/` is source of truth** (§1) — read, never edited or worked around.
- **`exports/` stays gitignored** (§6). Never commit, paste, or publish it.
- **Merge is not activation** (§8). Creative Stage, Messaging State and Flow State stay independent.
- **The repo is public.** Audit every file before committing; secrets stay secret-managed.
- Social stays fixture-only and read-only; no platform write path.

## Risks worth naming up front

1. **Reconstructing an unreliable dump while also porting platforms** is the sharpest risk in
   this plan — two sources of failure at once. The Phase 2 gate and the Phase 3-before-4
   ordering exist specifically to separate them. Do not collapse them to save time.
2. **The Worker receipt URL** (Phase 4) is the most likely silent breakage: sync keeps
   reporting healthy while receipts go nowhere.
3. **Auth removal changes the schema.** Confirm with Vincent before dropping `users`/`openId`.
4. **A missing file may not surface until runtime.** If the Phase 2 gate fails, ask for a
   structured export instead of guessing.
