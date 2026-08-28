# Tools, Deliverability, And Compliance

Use this reference when selecting tools or checking sender/compliance constraints.

## Testing Tools

- HubSpot preview/test send: first check for builder state, personalization fallback, plain text, footer, and basic mobile.
- Litmus: broad client rendering, dark mode, accessibility, spam checks, and previews.
- Email on Acid: client rendering, accessibility, previews, and QA checks.
- Can I Email: feature support for HTML/CSS email patterns.
- Mailgun Inspect: preview/spam/accessibility testing for email HTML.
- Mail Tester or GlockApps: supplemental deliverability diagnostics, not final truth.
- WebAIM/WCAG references: accessibility review logic.

## Local Checks

Use `scripts/audit_email_html.py` to catch:

- missing unsubscribe/address indicators;
- missing alt attributes;
- image-only risk;
- unsupported CSS/HTML patterns;
- width over 600px;
- subject/preheader placeholders;
- CTA target-size hints;
- color inventory and obvious contrast pair opportunities.

This helper is a triage tool, not a full rendering test.

## Deliverability-Sensitive Design

Flag:

- misleading subject/preheader;
- excessive image-to-text ratio;
- image-only CTAs or image-only critical content;
- spammy punctuation, all caps, fake urgency, or deceptive claims;
- missing unsubscribe/preferences;
- missing sender address;
- broken or excessive links;
- URL shorteners or suspicious domains;
- personalization that can expose missing/incorrect data.

## Sender Rules And Compliance

For current sender rules, verify against primary sources. As of current guidance:

- Gmail and Yahoo bulk sender rules emphasize authentication, low spam rates, and easy unsubscribe.
- One-click unsubscribe is associated with List-Unsubscribe and List-Unsubscribe-Post behavior for bulk senders.
- Marketing email needs clear sender identity and unsubscribe/preferences.
- CAN-SPAM, CASL, GDPR/ePrivacy, and local privacy laws affect consent and content, not just visual design.

Do not mark a campaign legally safe unless consent, sender identity, unsubscribe, address, and jurisdiction-specific requirements were checked.

## Source Anchors

- Gmail sender guidelines: https://support.google.com/a/answer/81126
- Yahoo Sender Hub: https://senders.yahooinc.com/
- RFC 8058 one-click unsubscribe: https://www.rfc-editor.org/rfc/rfc8058
- FTC CAN-SPAM compliance guide: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- Litmus: https://www.litmus.com/
- Email on Acid: https://www.emailonacid.com/
- Can I Email: https://www.caniemail.com/
- Mailgun Inspect: https://www.mailgun.com/products/inbox-placement/email-testing/
