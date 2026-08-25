# Core preview hardening report

## Status

Complete. The preview compiler is fail-closed across fixture/config validation, Liquid,
structural HTML/URL safety, browser capture, provenance, and atomic output promotion. No Pages,
workflow, Shopify, source-email, or publication state was changed.

## Commits

`Harden email preview compiler` — current task-owned commit.

## Exact files changed

- `tools/email-preview/fixtures/states/missing-first-name.json`
- `tools/email-preview/fixtures/states/product-heavy.json`
- `tools/email-preview/preview-config.json`
- `tools/email-preview/src/capture.ts`
- `tools/email-preview/src/cli.ts`
- `tools/email-preview/src/config.ts`
- `tools/email-preview/src/liquid.ts`
- `tools/email-preview/src/provenance.ts`
- `tools/email-preview/src/safety.ts`
- `tools/email-preview/src/types.ts`
- `tools/email-preview/test/preview.test.ts`
- `.superpowers/sdd/2026-08-24-email-preview-gallery/core-hardening-report.md`

## Red / green evidence

Red run (before implementation) failed for the intended regressions: product-heavy had 3 rather
than 5 products; `assign` rendered despite the allowlist; structural `script`/form/iframe/event
handler/protocol/host/pixel cases were accepted; and absent PR provenance was accepted. A later
red run proved incomplete capture could replace output because capture was not injectable or
checked before promotion. A final red run caught unhandled `@import` style content and bare email
identifiers.

Green coverage now proves all of those fail closed, including exact public
`mailto:info@hairsolutions.co`, canonical Email/source identity, required PR, request-interception
policy, the 53 manifest-backed selections, and incomplete-output preservation of a prior directory.

## Verification

```text
npm run build
Result: passed (TypeScript compiler)

npm test
Result: 19 passed, 0 failed

npm run preview -- --source shopify-messaging/emails/01-cr-1.html --email-code CR-1 \
  --commit-sha 00af96fb36e954ba23f887e93bdaad3fd79317b0 --issue 10 --pr 78 --out <temporary path>
Result: passed; exactly rendered.html, desktop.png, mobile.png, provenance.json; private visibility;
robots metadata present.
```

The readiness suite remains unchanged at 14 ready / 39 blocked, so hardening did not make a
previously blocked source appear renderable.

## Self-review

- Fixture files are schema-validated, fictional, composable, and deeply frozen. The missing-name
  state removes the property.
- The config rejects unknown keys and validates all 53 explicit selections against the canonical
  manifest; CLI validates canonical Issue identity and source bytes at the requested full SHA.
- LiquidJS parsing remains in use, while preflight makes its broader syntax fail closed.
- HTML safety operates on parse5's tree, sanitizes sensitive hrefs before capture, leaves only the
  approved support mailto, and requires `noindex,nofollow,noarchive`.
- Capture uses fixed desktop/mobile sizes, locale/timezone, motion suppression, closed request
  interception, and PNG validation.
- Outputs are generated in a sibling temporary directory and promoted only after all required
  artifacts and provenance are present; failure preserves the existing directory.

## Concern

No release blocker. The compiler correctly remains unable to render the 39 source-blocked emails;
that is existing source readiness, not a compiler bypass. The local smoke artifacts remain only in
an isolated temporary directory and were not published.

## Review round 1/5

Addressed all review findings. Fixture-aware Liquid validation now rejects unknown defaulted paths
and unknown nested loop paths; legitimate omitted `customer.first_name` remains known from the
fictional fixture schema. Structural validation now examines `srcset`, inline CSS `url()`, all
`data-*` values, and comments, rejects tokenized/non-allowlisted values, and identifies remote
one-pixel assets via HTML/CSS dimensions and tracking-shaped URLs.

PNG validation now requires signature, non-zero height, and the exact desktop/mobile widths.
The compiler independently validates those injected capture outputs before hashing/promoting.
The canonical output path is now an atomically switched symlink to immutable sibling versions;
it refuses an unsafe direct-directory replacement instead of allowing a missing-output window.

CLI input now requires `--campaign` and `--states`, rejects unknown options, validates the full
selected state set against its per-Email selection, and records states in provenance. The obsolete
global `preview_public` was removed; the per-Email boolean accepts future reviewed `true` values,
while the committed 53 selections remain `false`.

Embedded metadata now includes the complete identity before capture (source, campaign, Email,
persona/states, source/fixture/lock digests, Issue/PR URLs, workflow, timestamp, and visibility).
The final provenance sidecar is schema-validated and cross-checked against that embedded identity
before promotion.

### Round 1 red / green evidence

The focused red run failed on the previously open bypasses: `default` accepted an unknown object
path; loop-variable nesting accepted an unknown property; inline-style, `srcset`, `data-*`, and
comment URL surfaces passed; exact PNG width was not enforced; tokenized image requests were
permitted; and unknown CLI options were accepted. After implementation, the complete suite passed
with all regressions covered and the inventory remained 14 ready / 39 blocked.

```text
npm run build
Result: passed

npm test
Result: 21 passed, 0 failed

npm run preview -- --source shopify-messaging/emails/01-cr-1.html --email-code CR-1 \
  --campaign campaign:J2 --commit-sha b3ef91e4a19a676f99491f685a2cdaa8ccd77e77 \
  --issue 10 --pr 78 --states missing-first-name --out <temporary path>
Result: passed; canonical output is a symlink, exactly four artifacts are present, provenance
records the selected state set and private visibility, and no global visibility field exists.
```

## Review round 2/5

Liquid validation now processes tags and outputs in source order with a stack of lexical loop
scopes. A loop variable ceases to exist at its matching `endfor`; nested loops resolve their
iterable against the enclosing item, including a legitimate `item.variants` path.

URL validation rejects protocol-relative values before root-relative references are allowed, in
normal attributes and hidden data/comment values. CLI parsing now consumes strict option/value
pairs: every unknown flag, including a trailing flag, is rejected, and any missing value has a
deterministic `--name is required` error. Tracking-pixel detection now evaluates remote `src`,
`srcset`, and CSS `url()` sources for 1px/hidden dimensions and tracking-shaped URLs on every
element, including a background-image `div`.

### Round 2 red / green evidence

The new red tests demonstrated that a loop variable remained valid after `endfor`, nested loop
paths were not scope-resolved, protocol-relative URLs passed through both visible and hidden
surfaces, a trailing unknown option was ignored, and a CSS background pixel on a non-image element
was accepted. After the fixes:

```text
npm run build
Result: passed

npm test
Result: 22 passed, 0 failed

npm run inventory -- --check
Result: passed; 14 ready, 39 blocked
```
