# HubSpot Email Builder Review

Use this reference for HubSpot marketing email reviews, coded templates, drag-and-drop emails, and module libraries.

## HubSpot Review Surfaces

Audit the email in the surface where it will ship:

- drag-and-drop editor content and modules;
- Design Manager coded template/module when applicable;
- preview as a specific contact when personalization exists;
- test email to real inboxes;
- plain-text version;
- footer, unsubscribe, preferences, and sender address;
- mobile preview and dark-mode/client tests where available.

## HubSpot-Specific Risks

Check:

- required unsubscribe/preference links are present for marketing email;
- personalization tokens have safe fallback text;
- smart content or segment logic does not create empty modules;
- modules remain editable by the operator without breaking HTML;
- images use HubSpot/file/CDN URLs that will remain accessible;
- CTA tracking URLs and UTM expectations are correct;
- plain-text version is not missing or misleading;
- preheader is intentional and not duplicate/garbage text;
- email type, subscription type, sender, and list/segment match consent.

## Design Manager And Coded Email

For coded HubSpot templates/modules:

- keep critical styles inline or email-safe;
- avoid web-only layout patterns in email modules;
- ensure module fields cannot create invalid layouts;
- constrain image dimensions and alt text fields;
- preserve required HubSpot unsubscribe and address tokens;
- test module defaults and empty states;
- validate that repeated modules keep reading order and mobile stacking.

## Drag-And-Drop Email

For HubSpot builder emails:

- verify content blocks do not become image-only;
- keep section padding and background roles consistent;
- check mobile stacking and CTA spacing;
- preview with images off where possible;
- test personalization fallback;
- avoid operator-editable fields that allow unsupported claims or missing compliance elements.

## Source Anchors

- HubSpot marketing email knowledge base: https://knowledge.hubspot.com/marketing-email
- HubSpot design manager docs: https://developers.hubspot.com/docs/cms/building-blocks/design-manager
- HubSpot email template markup docs: https://developers.hubspot.com/docs/cms/building-blocks/templates/email-template-markup
- HubSpot personalization tokens: https://knowledge.hubspot.com/marketing-email/personalize-your-marketing-emails
- HubSpot test and preview email guidance: https://knowledge.hubspot.com/marketing-email/preview-and-test-a-marketing-email
