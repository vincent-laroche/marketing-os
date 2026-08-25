Closes #67

## Campaign OS scope

Implements the connector-readable Email Marketing Campaign OS for Shopify Messaging and Shopify
Flow while preserving the repository's existing history.

## Included

- deterministic 69-Issue manifest and versioned 28-field Project schema;
- governed Campaign, Email, Task, Experiment, and Bug forms plus PR template;
- idempotent Issue and Project synchronizers with live read-back reports;
- 69 live canonical Issues with native Campaign-to-Email sub-issue relationships;
- private GitHub Project #4 with six native views;
- fail-closed fictional-fixture Liquid preview compiler;
- rendered HTML, full desktop PNG, full mobile PNG, and exact provenance output contract;
- temporary private PR artifacts and manual, fail-closed public publication workflow;
- CR-1 through CR-4 retokenized to Email Reference File authority.

## Verification

- Python contract suite: 11 tests passing;
- preview compiler suite: 5 tests passing;
- TypeScript strict build passing;
- local CR-1 proof generated all three required user-facing outputs plus provenance;
- Issue read-back: 69 Issues, zero drift, zero second-run actions;
- Project read-back: private, 69 items, 28 custom fields present, six exact views, no browser configuration remaining;
- generated manifest check and whitespace validation passing.

## Safety and impact

- Authority and approved copy remain governed by `Email Reference File/`.
- No CRM export, customer PII, token, signed checkout URL, or real unsubscribe URL is published.
- Fictional fixtures only; customer-specific links are inert.
- `preview_public` remains `false`.
- GitHub Pages, the custom domain, Cloudflare, Shopify Messaging, Shopify Flow, audience,
  scheduling, activation, and sending are unchanged.

## Risks and rollback

- GitHub Issues and Project #4 are additive. The synchronizers are idempotent and fail on duplicate
  stable keys or contradictory readiness states.
- Revert this PR to remove repository tooling. Live Issues/Project remain recoverable and should be
  archived only through a separately approved cleanup.

Merge does not configure Shopify, schedule, activate, or send email.
