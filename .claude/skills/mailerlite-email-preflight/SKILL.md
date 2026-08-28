---
name: mailerlite-email-preflight
description: Use before any Hair Solutions Co. email is proposed for test send, scheduling, sending, or automation activation — the release gate. Verifies link destinations resolve, copy matches the approved source, merge tags are valid, palette and stacking are correct, and CAN-SPAM compliance is present. Run it whenever asked "is this ready to publish / send / go live", or after building or editing any MailerLite module.
---

# Email preflight — the publish gate

An email is publishable only when this passes. Build rules live in `mailerlite-html-blocks`;
this skill decides whether the result may leave the building.

## Run the validator first

```bash
python3 scripts/preflight_email.py mailerlite-blocks/            # whole library
python3 scripts/preflight_email.py mailerlite-blocks/wb1_hero.html
python3 scripts/preflight_email.py mailerlite-blocks/ --no-net   # skip HTTP checks
```

Exit 0 = publishable. Exit 1 = blocked. **FAIL blocks; WARN needs a judgement call, not a fix.**
It checks structure, palette, card surfaces, flush-stack geometry, merge-tag syntax and field
existence, image alt/dimensions/host, every link (including live HTTP status), and compliance.

The validator cannot judge meaning. Sections 3 and 4 below are yours.

## 1. Links — every click lands somewhere real

The validator resolves each URL. Known state of the storefront, verified 2026-08-19:

| URL | Status |
|---|---|
| `/`, `/cart`, `/policies/privacy-policy` | 200 |
| `/collections/{lace,mono,skin,hybrid,mens}-hair-systems` | 200 |
| `/blogs/hair-systems-for-men` | 200 |
| `/pages/contact`, `/pages/contact-us`, `/pages/help-center` | 200 |
| `/contact` | **404 — use `/pages/contact`** |
| `/reviews` | **404 — no reviews page exists** |
| `/account` | 406 to Shopify customer accounts — fine in a browser |
| `/checkout` | redirects home on an empty cart — expected |

Also enforced:
- **No `href="#"`.** The Atelier Zero library ships 18 of them.
- **Social links must be the brand accounts**, not bare domains:
  `facebook.com/hairsolutions.company` · `instagram.com/hairsolutions.co` ·
  `youtube.com/@hairsolutions_co` · `tiktok.com/@hairsolutionsco`
- **HubSpot leftovers are WARNs, not auto-fails** — `meetings.hubspot.com/...` and
  `customerportal.hairsolutions.co` still resolve but the brand has moved off HubSpot. Confirm
  intent per email. `50966981.fs1.hubspotusercontent-na1.net` images are a hard FAIL — dead CDN.
- Every CTA must point at the *specific* next step named in the copy, not the homepage.
  A "Return to your cart" button going to `/` is a FAIL a validator cannot see.

## 2. Compliance

- `{$unsubscribe}` present and reachable.
- Verified postal address: **Hair Solutions Co., Ehitajate tee 110, Tallinn, Estonia**
  (`dashboard.mailerlite.com/account/profile`).
  **Resolved 2026-08-19 — Vincent confirmed Estonia is correct.** Treat any *Forest Hills /
  65 E. Honey Creek Drive, New York 11209* address as wrong and replace it. It appears in no file
  in this repo — all 27 built emails and every footer carry Tallinn — but it does appear in older
  rendered email art from outside the repo, so check anything inherited before reuse.
- Sender identity and reply-to match the journey.
- Subscription type matches the audience and the trigger.

## 3. Copy — check against the source, not vibes

Authority is the `Body` column of
`Email Reference File/emails_master 831f4e0d84e0831992d481ae881cfede_all.csv`, matched on
`Email name`. Also read `Module Stack`, `Subject`, `Preview Text`, `CTA`, `Missing Modules`.

- Copy must be **verbatim** unless a change was approved. Re-splitting a sentence, expanding
  "The cost?" into "Was it the cost?", or tightening a line all count as edits.
- The rendered module stack must match `Module Stack`. If a module is missing, say so — do not
  substitute.
- `Missing Modules` non-empty means the email is **Blocked**, not buildable.
- Every claim about product, price, discount, shipping, returns, timing or support must trace to
  an authority. Never invent.
- Voice: plain, calm, educational; relief not rescue. Say **system**, never wig or toupee.
  No hype, scarcity, emoji or exclamation marks.
- Placeholders (`[PULL from Proof Bank…]`, `{{ image: … }}`) must be resolved or removed.
- **Does the email contradict itself?** An email promising "no pitch" should not carry a
  testimonial or a discount. Structural consistency is a copy check.

## 4. Render and behaviour

- 600px desktop and 320px mobile.
- Images blocked: is the first meaningful content still useful? Alt text on every image.
- Dark mode: Ink cards must not invert into mud.
- Personalization: check known, blank, and malformed values. `{$field|default(value)}` is the only
  valid fallback form. Tags never resolve in Preview — that is expected, not a pass.
- Plain-text equivalent exists and reads.
- Under Gmail's clipping threshold (~102KB).

## 5. Verdict

Report exactly:

1. **Verdict** — PUBLISHABLE or BLOCKED
2. **FAILs** — with file, line, and the fix
3. **WARNs** — with a recommendation
4. **Untested** — clients not checked, dynamic blocks not exercised
5. **The exact next action** and the approval class it needs

Preflight passing authorises **nothing**, and it does not mean the email is approved. It is
**gate 0 of seven** in `email-ship-approval` — copy-vs-database, module count, brand compliance,
three-surface library coverage, opened links, a copy in Vincent's inbox, and a screenshot filed in
Figma all still have to pass. Run that skill before calling anything ready.

Test sends, scheduling, sending, activation, imports and deletions each need fresh explicit approval
in the current conversation — a previous approval never carries. A test send is still a send.
