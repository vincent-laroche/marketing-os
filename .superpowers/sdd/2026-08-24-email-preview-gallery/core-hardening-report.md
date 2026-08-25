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
