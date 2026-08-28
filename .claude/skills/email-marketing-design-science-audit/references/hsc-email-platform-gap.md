# Hair Solutions Co. Email Platform Spec Gap Notes

Based on `/Users/vMac/Downloads/PLATFORM_EMAIL_FINAL.md`, last updated 2026-06.

## Already Covered Well

- Email-specific constraints: 600px layout, table structure, inline CSS, no JavaScript/forms/grid, image-blocked readability.
- Client target set: Gmail, Apple Mail, Outlook, iOS Mail, dark mode.
- Hex-first email palette and dark-mode-safe combinations.
- Email-safe typography and type scale.
- CTA hierarchy, subject/preheader rules, tone, claims, and transactional clarity.
- Detailed component contracts for wrapper, header, hero, body copy, CTA, product, testimonial, editorial, order summary, consultation reminder, footer, legal/unsubscribe, and dark-mode-safe blocks.
- Composition patterns for major lifecycle email types.
- Compliance reminders: unsubscribe/preferences, sender details, consent-sensitive claims, no fake urgency.

## Potential Gaps To Add Through This Skill

- A measured audit workflow that separates design judgment from proof.
- Deterministic HTML checks for alt text, 600px width risk, unsupported CSS, missing compliance indicators, and image-only risk.
- HubSpot-specific preview/test-send, plain-text, personalization fallback, module editability, smart content, and subscription-type review.
- Rendering-test matrix with proof requirements across Gmail, Apple Mail, Outlook, mobile, dark mode, and image-blocked state.
- Accessibility framing beyond checklist: reading order, link purpose, target size, contrast pair measurement, and cognitive load.
- Deliverability and inbox-placement risk checks connected to current Gmail/Yahoo sender rules.
- Lifecycle audit scoring: whether each email job is sell, educate, reassure, remind, confirm, recover, or retain.
- Integration with `color-science-palette-audit` for palette/contrast and `website-ux-science-audit` for hierarchy/composition where transferable.

## Important Existing TODOs

- Email-safe logo asset paths.
- Cloudinary / Shopify CDN folder URLs.
- HubSpot/Klaviyo/Shopify Email template locations.
- Unsubscribe, preferences, sender address, booking, reorder, and support merge tags/URLs.

## Skill Behavior For Hair Solutions Co.

When auditing Hair Solutions email:

- preserve calm, useful, private, premium, human tone;
- avoid hype, urgency, medical claims, pity, shame, emoji, and exclamation-heavy writing;
- treat realism, fit, base type, density, maintenance, privacy, and support as trust-building content;
- keep transactional emails accurate and light;
- use dark sections sparingly;
- keep champagne accents small and never as primary CTA fill;
- verify claims rather than polishing unsupported claims.
