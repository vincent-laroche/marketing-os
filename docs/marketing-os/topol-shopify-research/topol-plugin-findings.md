# Topol Plugin findings

Research date: 2026-08-25.

## Sources reviewed

1. https://docs.topol.io/
2. https://docs.topol.io/guide/new-topol-plugin-loader-url.html
3. https://docs.topol.io/guide/callbacks.html
4. https://www.npmjs.com/package/@topol.io/editor

## Verified findings

Topol is an embeddable white-label email editor with a script-loader integration and official packages for React, Vue, Angular, Svelte, and plain JavaScript. Its documented integration is based on a `TOPOL_OPTIONS` configuration containing an editor mount ID, an `authorize` object (`apiKey`, `userId`), and callbacks. The editor can return both a JSON document model and generated HTML through `onSave`.

The current loader URL is `https://v3.email-assets.topol.io/loader/build.js`. Topol's migration documentation says package version `0.3.0` uses this loader domain and that custom API endpoint CORS rules must allow requests from `https://v3.email-assets.topol.io`. The previous loader domain is scheduled to stop serving on 2026-09-15, so new implementation work should use the current domain and current package.

The current callback surface is materially broader than the user-provided minimal snippet. Verified callbacks include `onSave(json, html, mutations, syncedSections)`, `onSaveAndClose`, `onTestSend(email, json, html)`, `onOpenFileManager`, `onImageDelete(items)`, `onInit`, `onLoaded`, `onTemplateUpdated`, saved-block callbacks, `onClose`, unsaved-change state, rename, test-address persistence, undo/redo, preview, alerts, errors, and multilingual-language state callbacks.

Topol's `onSave` documentation states that `json` is the template document and `html` is the rendered output. The email subject is available in `json.attributes["mj-subject"].text`. `mutations` is relevant for multilingual templates, and `syncedSections` contains synced section IDs that must be resolved through the `api.SAVED_SECTIONS` storage when server-side rendering is needed.

The NPM package exposes programmatic actions including `init`, `save`, `load`, preview toggles, undo/redo, saved-block management, notifications, editor teardown, file selection, template naming, API-authorization refresh, custom-block content updates, and merge-tag replacement. It exports TypeScript types such as `ITopolOptions`, `INotification`, and `ISavedBlock`.

Topol's official documentation describes custom blocks, flexible image storage, white-labeling, merge tags, comments, autosaves, conditional content, and multilingual templates. These are the primary product surfaces to evaluate for a Shopify-specific block library and personalization layer.

## Initial integration implication

Topol should be treated as the presentation/editor layer only. The Shopify app must own tenant isolation, template persistence/versioning, subject/preheader metadata, merge-tag policy, asset storage, test-send delivery, publish state, and the bridge from a saved template to Shopify's marketing/automation surfaces. The Topol API key must not be exposed as a tenant secret; server-side authorization and domain restrictions should be used where supported.

## Additional verified findings

Topol custom blocks are configured in `TOPOL_OPTIONS.customBlocks`. They can be based on core block types such as text, button, image, and video; combine multiple blocks via `type: "mix"`; restrict or disable attributes; and, for full control, omit `type`, set `dialog: true`, and use `onOpenCustomBlockDialog` plus `TopolPlugin.updateCustomBlockContent()` to drive a host-owned dialog. Custom blocks are a direct fit for a curated Shopify block library, but the app must validate any dynamic HTML and URL content before publication.

Topol distinguishes ordinary Saved Blocks (independent copies) from Synced Sections (live reusable sections). API-backed mode uses `savedBlocks: true`, `syncedSectionsEnabled: true`, and an `api.SAVED_SECTIONS` endpoint. The endpoint supports list, create, detail, patch, delete, folders, search, pagination, sorting, and preview-image URLs. Requests contain `entity_id` corresponding to Topol's `userId`, `hostname`, and `key`; the app must map these to a securely authenticated shop and tenant, not blindly trust client-supplied identity fields.

Synced sections are saved in template JSON as lightweight `syncedId` references. Before final HTML generation, the backend must resolve referenced synced sections and pass them to Topol's Convert JSON to HTML endpoint; otherwise the sections render as empty placeholders. When a synced section changes, any stored HTML for templates using it must be re-rendered, and open editor sessions may call `TopolPlugin.refreshSyncedSections()`.

Merge tags are host-defined placeholders replaced by the sending platform at delivery time. Topol supports grouped merge tags, nested groups, default preview values, smart merge tags, custom syntax, dynamic `setMergeTags()`, and loop merge tags with `childrenProperties`. Dynamic merge tags should be set inside `onInit`, because calls immediately after `init()` can be lost while the editor iframe is registering message listeners.

Topol does not store templates. The host system loads a template with `TopolPlugin.load(template)` and persists the JSON/HTML returned through `onSave`. The app should therefore persist the canonical JSON, a rendered HTML snapshot, version metadata, and the list of synced-section IDs; it should regenerate HTML at publish/send time rather than treating a stale saved HTML snapshot as canonical.

## Topol-specific design constraints

The requested Shopify block set should be implemented as a versioned configuration owned by the app. Global blocks such as header, product grid, offer, social row, and unsubscribe/footer can be Synced Sections if they must update everywhere; campaign-specific design fragments should be ordinary custom or Saved Blocks. Merge tags should be namespaced to the app's rendering/delivery system and translated to the eventual provider syntax only at the final send boundary if Shopify or the selected ESP uses a different variable format.

## Backend/API and security findings

Topol's `api` option points editor features such as autosaves, feeds, products, folders, image upload, AI text generation, premade templates, and saved sections at host-owned endpoints. Requests originate from `https://v3.email-assets.topol.io`, so CORS must permit that origin. Topol supports an `apiAuthorizationHeader` option, including a string or custom-header object, for token-based access to host endpoints; the app should use short-lived, shop-scoped authorization rather than a shared static bearer token in the browser.

Topol's Convert JSON to HTML API is `POST https://api.topol.io/email/v1/json2html`. It authenticates with `X-Secret-Key`, accepts a JSON-encoded `definition` plus rendering options (including merge tags, language, and variant evaluation), and returns HTML plus warnings. The secret key must never appear in client-side code. The Shopify app backend should proxy this call or perform it in a server-side render worker, with rate limits, audit logging, and retry handling.

Topol documents custom cloud storage options, including S3, but its example asks for broad bucket/object permissions and public access configuration. For a Shopify app, prefer an app-controlled object store or presigned upload service with tenant-scoped keys, private originals, CDN delivery, content-type/size validation, and revocation; do not copy the broad example policy without narrowing it to the product's threat model.

## Product and API-block findings

Topol's built-in Product block supports static product selection and dynamic product rendering. Static mode saves selected items into the template; dynamic mode binds the block to merge tags and relies on ESP-compatible loop syntax. Product availability is provided through host-owned feeds, products, and optional categories endpoints with pagination and filtering.

Topol Custom API Blocks provide a more general feed/items/categories contract. They can render categorized product, news, or other data blocks, map upstream API field names to block fields, and support static or dynamic modes. Dynamic mode synthesizes loop merge tags from the block structure.

For Shopify, the app should expose a controlled product-feed API backed by Shopify GraphQL product/collection queries and cached per shop. Static product blocks should store Shopify product/variant IDs plus a render snapshot and revalidate links/images at publish time. Dynamic product blocks should use the app's own loop/merge-tag namespace and render from the Flow/customer context through the delivery worker; they should not depend on Topol's documented SparkPost-only dynamic mode unless SparkPost is the chosen delivery provider.

The exact allowed blocks should be versioned in a server-owned configuration. The editor should receive only the curated `customBlocks`, `apiBlocks`, product-feed endpoints, merge tags, fonts, and saved/synced sections permitted by the merchant's plan and the app's current block schema.
