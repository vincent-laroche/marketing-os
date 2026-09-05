# Shopify findings

Research date: 2026-08-25.

## Sources reviewed

1. https://shopify.dev/docs/apps/build/app-extensions
2. https://shopify.dev/docs/apps/build/marketing

## Verified findings

An app extension adds an app's functionality to defined Shopify user interfaces; it is not itself an app. Extensions use the same authentication requirements and API rate limits as the parent app. The App Home surface can render the app's main page in Shopify admin, including for extension-only apps, but extension-only apps are limited to custom distribution.

App extensions are created with Shopify CLI, configured in an extension-specific `shopify.extension.toml`, and versioned/deployed together with the app as one app version. Some extension types require review and approval. Shopify UI extensions have a strict 64 KB compressed bundle-size limit, so the Topol editor should not be bundled into a UI extension; it belongs in a hosted App Home/Admin page or another surface that can load the host application.

Shopify's marketing-app guide identifies four relevant concepts: web pixel app extensions for behavioral events, customer segments for targeting, GraphQL Admin API operations for connecting and managing marketing efforts, and marketing automation actions for executing app marketing activities from Shopify's automation tool. The guide explicitly says a marketing activities app extension is not required to connect a marketing app to Shopify, and it is not required to create a marketing automation action.

The marketing guide presents the Admin surface as the place where merchants build customer segments and run marketing automations. The requested Topol editor therefore naturally belongs in the app's Admin/App Home experience, while Shopify Flow/marketing automation actions provide trigger/action orchestration rather than the editor itself.

## Initial implication

The initial product should be a hosted embedded Shopify app with an App Home/Admin page containing Topol. Add only the app extensions that materially improve discovery or workflow access. Do not attempt to package the full Topol runtime inside a 64 KB UI extension. Use GraphQL Admin API and Shopify app webhooks for shop data and lifecycle, and use Shopify's marketing/automation extension points for the integration boundaries documented below.

## Marketing connection and customer-segment findings

Shopify states that the GraphQL Admin API can create and manage marketing efforts in the app or on an external platform, allowing Shopify to present a complete picture of marketing performance. Shopify explicitly notes that a marketing activities app extension is not required for this connection.

Shopify marketing automations are a workflow tool built into the Shopify admin. A developer can create a marketing automation action so merchants execute the app's marketing activities based on store conditions; when triggered, the app can send information about the marketing activity back to Shopify for display and reporting. Shopify also explicitly notes that a marketing activity app extension is not required to create a marketing automation action.

Customer segments are groups of members, commonly customers, defined by query criteria. The GraphQL Admin API lets apps filter customers for marketing, analytics, and reporting. A segment may be used to send targeted email, and a member can belong to multiple segments. Shopify says segmentation replaces the older `SavedSearch` model and apps must migrate to segments rather than relying on customer saved searches. Segments are single-shop resources and Shopify documents a maximum of 250 segments per query (`first`/`last` max 250).

## Initial implication

The app should store a reference to the selected Shopify segment ID and resolve segment membership server-side when a campaign or automation run is executed. It must not copy a segment into a permanently static recipient list without an explicit snapshot policy. A campaign should distinguish a live segment target, a snapshot audience, and a Flow-provided recipient/event context. Shopify segment IDs and query definitions should be treated as Shopify-owned data and revalidated when publishing or sending.

## Marketing activities and automations findings

Shopify's current documentation marks the creation of new marketing activity app extensions as deprecated; only existing extensions can still be managed. It specifically directs developers building marketing automations to use a marketing automation Flow action extension instead. This rules out making a new marketing-activity app extension the core of the product.

Shopify marketing automations expose custom triggers and actions. A trigger starts a workflow and must include the Customer Shopify property; custom triggers are also available in Shopify Flow. An action is a marketing activity executed when workflow conditions are met and must include the Marketing activity ID Shopify property; custom actions are also available in Shopify Flow. When an action runs, Shopify sends one or more POST requests to standardized endpoints hosted by the app; the app must verify requests and handle duplicate requests.

## Product implication

The recommended Shopify-native automation surface is a Flow action extension that takes a campaign/template identifier and runtime inputs, then calls the app's backend to enqueue a delivery job. Do not invest in a new marketing-activity app extension for a new app. A custom trigger may be added later if the product needs to start workflows from app-owned events, but the first release should prioritize a Flow action that sends a saved Topol campaign.

## GraphQL and Flow action contract findings

Shopify states that the REST Admin API is legacy as of October 1, 2024 and new apps/integrations should use the GraphQL Admin API. GraphQL requests use one endpoint per API version, require authentication and explicit access scopes, are rate-limited, and should select only the fields needed. The app should use Shopify's current stable API version at implementation time and maintain a version upgrade policy.

The detailed marketing automation action tutorial requires a web server and a Flow/Actions extension. The action payload schema must include the Marketing activity ID Shopify property to be available to Shopify marketing automations. It can also include Customer, Order, Product, Company, and Company Contact reference properties when the corresponding scopes are requested. Merchant-configurable fields can hold a template/campaign selector or configuration values. A custom configuration page can be embedded in the automation editor; it requires a preview endpoint and, when enabled, a custom validation endpoint.

For each action run, Shopify sends a signed POST to the runtime URL. The payload includes `shop_id`, `shopify_domain`, `action_run_id`, `handle`, optional `step_reference`, `action_definition_id`, and `properties`. The endpoint must verify the HMAC before processing and identify the action by `handle`, using `action_definition_id` only as a fallback for legacy workflows. The runtime should respond within 10 seconds; `202` means accepted and causes Shopify to retry with increasing intervals for up to 36 hours, while 5xx responses are retried and 429 responses are retried with backoff. `action_run_id` should be stored as an idempotency key to prevent duplicate email sends.

Shopify's marketing automation action lifecycle includes marketing-activity create and delete endpoints. The create payload provides `marketing_activity_id`, `automation_step_type`, locale, shop, and workflow step identity; the app must return tactic, channel, and unique UTM values. After acknowledging creation, the app should asynchronously call `marketingActivityUpdate` with a user-recognizable title and status. After runs, it should call `marketingEngagementCreate` with delivery/engagement aggregates; abandoned-checkout workflows additionally require `abandonmentUpdateActivitiesDeliveryStatuses` to report SENT/NOT_SENT. The app can optionally create analytics annotations in API version 2026-10 or later with the relevant scope.

The Flow action configuration can use a relative runtime URL resolved against the app URL or an absolute HTTPS URL. Flow custom action extensions are created with Shopify CLI and deployed/versioned with the app. Shopify's docs state custom Flow actions/triggers for custom apps are available on Plus and dev stores during development; distribution and production availability must be validated during review for the target app type.

The current `MarketingActivity` GraphQL object requires `read_marketing_events` to read and exposes title, status, tactic, marketing channel type, UTM parameters, app, event, and reporting fields. The latest object documents `marketingActivityUpdate`, `marketingEngagementCreate` in the automation guide, and external marketing activity upsert/update resources. The GraphQL reference also marks the older marketing-activity app-extension creation mutations as deprecated, reinforcing the Flow action route.

## Initial implementation implication

Model a Flow action as an asynchronous command: validate the shop and selected template, render/compile the Topol design, resolve the customer/order context, enqueue a delivery job, immediately return `202`, and make the worker idempotent on `action_run_id`. On success/failure, update Shopify's marketing activity status and engagement/delivery metrics. A custom configuration page should let the merchant select an app-owned campaign/template and optionally configure subject, sender, or suppression behavior without embedding the full Topol editor in a small Flow UI extension.

## Shopify Messaging delivery findings

Shopify's official Messaging help documentation describes a native Shopify Messaging editor with predefined section types, custom-coded HTML, templates, campaigns, and marketing automations. Merchants can send to all email subscribers or a customer segment, personalize customer fields, edit UTM parameters, test, schedule, and cancel sends. Shopify Messaging's custom-coded message path accepts imported `.html` files, and Shopify documents a 50 KB limit for Custom Liquid code in a section.

The Shopify Messaging help docs describe how merchants use its own editor and templates, but the developer documentation reviewed here does not expose a public third-party API for injecting an arbitrary Topol JSON/HTML design into the Shopify Messaging editor or for asking Shopify Messaging to deliver a custom app-owned template. The docs instead direct third-party developers to GraphQL marketing resources and Flow action extensions. Therefore, the product must not assume that a Topol design can be programmatically imported into or sent by the Shopify Messaging app unless Shopify confirms a private/partner API in writing.

The viable public architecture is to integrate with Shopify's marketing and Flow surfaces while owning the actual email delivery through an email service provider, or to use Shopify Messaging only as a merchant-facing conceptual/automation surface if a supported action/API path is confirmed. The app can still use Shopify segments, Shopify customer consent, UTM tracking, and Shopify marketing activity reporting, but the delivery worker must have a defined sender, unsubscribe system, bounce/complaint handling, and provider integration.

The native Messaging product's documented personalization is limited to selected customer values in its own editor, whereas Topol merge tags can be app-defined. The app must therefore define and document its own merge-tag resolution and consent semantics rather than claiming native Messaging compatibility by default.

## App Home and Admin surface findings

Shopify documents two App Home models. App Home UI extensions are Shopify-hosted Preact/Remote DOM extensions with a 64 KB compressed bundle limit, no backend hosting, and custom-distribution-only availability. Shopify recommends the iframe-based App Home model for most apps that need server-side logic, webhooks, background jobs, browser APIs, or an App Store-public distribution.

The Topol editor needs a hosted browser runtime, server APIs, tenant persistence, webhooks, background rendering/delivery, and likely a public App Store app. It should therefore use the iframe-based embedded App Home/App URL, not an App Home UI extension. A small App Home UI extension could be an optional launcher for a custom-distribution internal tool, but it is not the correct primary surface.

Shopify Admin UI extensions can add lightweight actions or blocks to Product, Customer, and Order pages. They use targets, target APIs, and Shopify web components; admin actions open modals from More actions or bulk menus, while admin blocks show contextual cards. These are useful later for contextual actions such as "Create campaign from this customer/order" or "Open email automation", but cannot host the full Topol editor due to their constrained runtime and bundle model.

The extension catalog lists Flow triggers/actions, App Home, Admin actions/blocks/links, web pixels, and customer-segment action extensions. For this product, the core surfaces should be iframe App Home plus Flow action; optional later surfaces include a customer-segment action extension and an Admin action/block. New marketing activity app extensions should be excluded because Shopify marks them deprecated.

## Customer-segment extension findings

Shopify provides a customer-segment action extension that appears in the **Use segment** modal on a segment details page. The extension receives the selected segment through the Admin UI extension API (`data.selected[0].id`) and can query Shopify directly with `fetch("shopify:admin/api/graphql.json", ...)`, including `customerSegmentMembers` when the app needs member IDs. It is rendered with Remote UI and Shopify components, not as a general hosted browser page.

A customer-segment template extension can add app-provided query templates to Shopify's segment editor, using a TOML target such as `admin.customers.segmentation-templates.data`. This could be a later growth feature for Hair Solutions Co.-specific audiences, but it is not required for the first release.

A segment action extension is a strong optional entry point: the merchant opens a segment, selects the app action, chooses a saved Topol campaign or is linked to the app's hosted campaign composer, and confirms a send/draft. The extension itself should remain a thin selector/launcher; the full editor and delivery workflow belong in the hosted app. The action must handle consent, audience snapshot/live-segment semantics, and asynchronous delivery outside the extension runtime.

## Security, data, and launch findings

A public app that reads customer email, name, address, phone, order, or related protected resources must request protected customer data/field access in the Partner Dashboard and pass Shopify's review. Shopify requires data minimization, transparency, purpose limitation, consent/opt-out handling where applicable, merchant data-protection agreements, retention limits, and encryption in transit and at rest. Level 2 requirements include encrypted backups, test/production separation, data-loss prevention, least-privilege staff access, access logging, and incident response.

Shopify's current app authentication guidance recommends Shopify CLI/templates for most apps. An embedded app uses token exchange, sends an access token in `X-Shopify-Access-Token`, and stores an offline token for background jobs/webhooks; online tokens can attribute staff actions. Access scopes should be minimal. The Topol app needs server-side authentication because it will have background rendering, Flow endpoints, webhooks, customer data, and delivery workers.

Shopify webhooks provide near-real-time events but delivery is not guaranteed and order is not guaranteed. The app should verify `X-Shopify-Hmac-Sha256`, deduplicate with `X-Shopify-Webhook-Id`, and run reconciliation jobs using `updated_at` filters. Required lifecycle topics include `app/uninstalled` plus Shopify privacy/compliance topics; additional customer/order/product topics should be added only when they directly support campaign personalization or trigger handling.

Public distribution requires App Store review and a complete listing, support process, protected-data compliance, and quality checks. Private/custom distribution can be used for an internal Hair Solutions Co. deployment, but a public product intended for other Shopify merchants should use a public App Store app with the appropriate protected-data review.

## External marketing activity API findings

Shopify's current GraphQL Admin API exposes `marketingActivityUpsertExternal`, which requires `write_marketing_events` and creates or updates an external marketing activity using a stable `remoteId`, title, remote management URL, status, UTM parameters, tactic, and marketing channel type. This is the most promising public API for representing standalone Topol campaigns in Shopify without relying on deprecated marketing-activity app extensions.

`marketingActivityUpdateExternal` can update by Shopify marketing activity ID, remote ID, or UTM parameters and can set title, management URL, preview image URL, and status. This supports a campaign dashboard link back to the hosted app and an email preview image. The app should store its own campaign ID as `remoteId` and use deterministic, unique UTM values per shop/campaign/send.

`marketingEngagementCreate` requires `write_marketing_events` and can submit activity-level or remote-ID engagement metrics such as sends, views, unique views, clicks, unique clicks, unsubscribes, complaints, failures, sessions, orders, sales, and customer counts. The app should use this to reconcile provider metrics into Shopify reporting, subject to field semantics and validation in the target API version.

`MarketingEvent` exposes manage/preview URLs, remote IDs, channel type, tactic/type, start/end time, and UTM values. A campaign should expose a stable preview/manage route that validates the shop and campaign token and should avoid putting customer PII in URLs or UTM values.
