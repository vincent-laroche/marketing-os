# HubSpot Marketing Email HTML Library

Initial baseline exported 2026-07-08 from the hairsolutions.co HubSpot portal via the Marketing Email v3 API (`GET /marketing/v3/emails`, paginated).

**Current coverage:** A read-only reconciliation on 2026-08-04 added the 12 HubSpot records that were missing from the original baseline. All **89 current, non-archived HubSpot email IDs** now have local HTML counterparts. The directory contains **116 files** in total because it intentionally retains 27 historical local records that are no longer in the current HubSpot catalogue.

The eight newly added abandonment records are `AUTOMATED_DRAFT` emails and must not be treated as release-approved merely because they are included here. This directory is a source/review library, not a publication or sending control.

The explicit `Supporting -- Do Not Reuse -- Test -- Test for Cursor` email was removed from this active
library and preserved under `archive/cleanup-2026-07-27/held-email/`.

## How these HTML files were built

HubSpot's v3 Marketing Email API does not expose a fully pre-rendered HTML endpoint on this portal (confirmed: `/marketing-emails/v1/...` legacy API returns 404, and there's no `/preview` or `/render` route). Each email's actual content lives as structured JSON (`content.flexAreas` + `content.widgets`) describing drag-and-drop modules.

Each `.html` file here was reconstructed by walking that JSON in section/column/widget order and rendering each module type (rich text, image, button, footer, social-follow, product block) into standalone HTML. Most emails on this portal already store a full hand-authored HTML table in their main rich-text widget, so reconstruction is close to exact for those; auxiliary modules (buttons, images, footer, social links) are rebuilt from their style/config fields.

**Known limitations:**
- Personalization tokens (`{{ contact.firstname }}`, `{{ unsubscribe_link }}`, etc.) are left unresolved as literal text — that's what HubSpot's own send-time renderer would substitute per-recipient, so there's no static value to bake in.
- The one `@hubspot/email_products` widget (dynamic product carousel) is stubbed with a comment noting the referenced product ID, since its content is generated at send time.
- Any widget type not explicitly handled is preserved as an HTML comment containing its raw JSON, so nothing is silently dropped.

`manifest.json` lists all 116 local-library emails (id, name, state, subject, filename). The reconciliation tool at `tools/sync_missing_hubspot_email_html.py` has an explicit 12-ID allowlist and refuses to overwrite or duplicate existing files.
