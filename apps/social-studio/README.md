# Social Studio

This is the migrated Hair Solutions Co. Social Studio operator dashboard inside the public `marketing-os` repository. It is a presentation layer for Social Media OS planning and review; it is not the canonical database and it is not a customer-facing site.

## Run locally

```bash
npm install
npm run dev
```

For a production-style local build:

```bash
npm run verify
npm run build
npm run start
```

## Data boundary

The app uses the committed seed snapshot in `lib/data.ts` and can optionally refresh read-only Notion databases through `NOTION_DEV_TOKEN` or `NOTION_TOKEN`. Runtime tokens are never committed. If the Notion request fails, the app falls back to the committed seed snapshot and identifies that state in the UI.

The canonical Social Media OS source remains the Markdown hierarchy under `../../social-media/`. The app must not write to Notion, GitHub Issues, GitHub Projects, Shopify, HubSpot, Cloudinary, Canva, or a social platform.

## Hosting boundary

The application source is public because it lives in the public Marketing OS repository. The operator dashboard must remain `noindex` and, if deployed, must be placed behind authentication. This migration does not enable or repoint the old Cloudflare Worker deployment.

Social publishing, scheduling, DMs, comments, replies, account changes, audience changes, and billing changes remain outside this application and require separate explicit approval.
