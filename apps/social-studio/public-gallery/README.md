# Public Social Display Gallery

This directory is an isolated, no-login public display build for Hair Solutions Co. Social Media OS. It is intentionally separate from the internal `app/` operator dashboard and does not import the committed historical seed module or call Notion at runtime.

The public build contains a sanitized structural fixture only: 30 day rows, three square grid slots per day, five Story slots per day, and a separate 3 × 3 feed assembly. Dates, times, and images are unset by default. Do not add customer data, testimonials, prices, claims, private links, or platform controls here.

## Local verification

From `apps/social-studio/`:

```bash
npm run verify:public-gallery
```

## Cloudflare deployment

The Worker is `social-marketing-studio` and uses the approved custom domain `social-marketing-studio.hairsolutions.co`. The public build disables workers.dev and preview URLs. Deploy with the Cloudflare Production token supplied through the shell environment; never commit it:

```bash
CLOUDFLARE_API_TOKEN="$CLOUDFLARE_MASTER_API_TOKEN" npm run deploy:public-gallery
```

The Worker adds `X-Robots-Tag: noindex, nofollow`, a restrictive Content Security Policy, `X-Content-Type-Options: nosniff`, and `Referrer-Policy: no-referrer`. This site is a read-only visual assembly surface. It does not publish, schedule, send, write to Notion, or mutate GitHub, Shopify, HubSpot, Cloudinary, Canva, or a social platform.
