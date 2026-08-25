# Task: rebuild 17 Shopify notification templates to Atelier Zero v7

## What this is

Hair Solutions Co. (hairsolutions.co) runs a Shopify store (`oneheadhair`). This task is
about Shopify's **native transactional/notification email system** — Admin →
Settings → Notifications → Customer notifications → [template] → Edit code. This is
**not** Shopify Messaging, **not** MailerLite, **not** HubSpot. Those are separate
products with separate rules; don't touch them and don't consult their docs for this.

Store admin: `https://admin.shopify.com/store/oneheadhair/email_templates/<slug>/edit`
You'll need to be signed in to Shopify admin as Hair Solutions Co in your browser tool.

## Ground truth — read this file first, trust nothing else

**`order_confirmation_VERIFIED_REFERENCE.liquid.html`, in this same directory, is the
only trustworthy reference.** It is a byte-exact copy of the *live, currently-saved*
`order_confirmation` template, pulled and verified directly from Shopify admin.

Do **not** trust any other file in this repo that claims to show "the correct" pattern —
specifically, `figma-review-renders/order_confirmation.html` (no `_VERIFIED_REFERENCE`
suffix) is a **stale, wrong-palette draft** from an earlier abandoned attempt. It uses a
bordered "floating card" look with a full-page background that was explicitly rejected.
Ignore it entirely.

Do not trust `brand-design-system/specs/PLATFORM_EMAIL.md` or any other doc's claimed
palette without cross-checking it against what's actually live in a currently-correct
template. A prior session's handoff notes claimed 4 templates were "done and verified
live" — 3 of the 4 turned out to have a real, live bug when actually checked. **Always
verify by reading the live saved source, never by trusting a written status claim,
including this one.**

## The architecture (verified correct, live, in the reference file)

Read the reference file's own `<style>` block — it's the literal spec, not a
paraphrase. The load-bearing structural rule, and the one that broke on 3 templates
last time, is:

- `.container` (the ~600px content column) carries the **Paper** background,
  `#EFE7D2`.
- `body`, `table.body`, and `table.body > tr > td` (the full-width outer wrapper)
  are **`background: transparent !important`** — no color at all.

**These must never be swapped.** The bug that shipped live on 3 templates was exactly
this inversion: Paper painted on the outer wrapper (bleeds across the recipient's whole
inbox pane in real email clients — invisible in a narrow screenshot, very visible in
production) while `.container` was left transparent. After you build each template,
explicitly check both rules before saving — don't just eyeball it.

Other fixed values, all present in the reference file:
- Coral `#ED6F5C` — the one CTA fill, text on it is Ink `#15140F`. Never white on Coral.
- `.header.row { margin: 16px 0 0 !important; }`
- `.content__cell { padding: 20px 0 36px !important; }` (asymmetric, extra room below CTA)
- `.section__cell { padding: 14px 0 !important; }`
- Footer is full-bleed Ink `#15140F` (deliberately NOT transparent — only the page
  background rule applies to `body`/`table.body`, not the footer band).
- Footer address, reuse verbatim: `{{ shop.name }} - Ehitajate tee 110, Tallinn, Estonia`
- CTA button: pill (`border-radius:999px`), `padding:13px 26px; font-size:15px` — not
  Shopify's oversized default padding.
- Eyebrow element (new, not in Shopify's stock markup): Courier New, 11px, tracked
  uppercase, `color:#5A5448`, **no background** — must stay fully transparent, it isn't
  a card.
- Do NOT use bordered/radius "floating card" sections. No box-shadow card stack. Body/
  outer wrapper/outer `<td>` stay transparent — full stop, this is a hard rule, not a
  style preference.
- Keep spacing tight — don't add extra vertical whitespace beyond the values above.

## The 17 templates

`pickup_receipt`, `local_out_for_delivery`, `local_delivered`, `local_missed_delivery`,
`gift_card_notification`, `gift_card_confirmation`, `store_credit_issued`,
`order_invoice`, `order_edited`, `order_cancelled`, `order_payment_receipt`,
`refund_notification`, `shipping_update`, `shipment_out_for_delivery`,
`shipment_delivered`, `customer_account_reset`, `customer_account_welcome`.

Do not touch any template outside this list — the other ~26 native templates are
deliberately out of scope (POS, B2B, low-frequency edge cases per an earlier audit) and
inherit only the master accent color/logo. Don't expand scope.

Each template needs its own footer identifier line, adapted per template — **check each
template's own existing Liquid source for what variable it already uses** before
inventing one:
- Order-lifecycle templates (`order_invoice`, `order_edited`, `order_cancelled`,
  `order_payment_receipt`, `refund_notification`, `shipping_update`,
  `shipment_out_for_delivery`, `shipment_delivered`, `pickup_receipt`,
  `local_out_for_delivery`, `local_delivered`, `local_missed_delivery`) likely use
  `order_name` like `order_confirmation` does — verify, don't assume.
- `gift_card_notification`, `gift_card_confirmation`, `store_credit_issued` use
  gift-card/store-credit variables, not an order at all. Read the template's existing
  body for what it already references and adapt the disclaimer sentence accordingly
  (same meaning, correct noun — "this gift card", not "order {{ order_name }}").
- `customer_account_reset`, `customer_account_welcome` have no order context. Write a
  generic account-appropriate service-email disclaimer instead of the order-based one —
  same intent ("this is a service email, not marketing, nothing to unsubscribe from"),
  adjusted wording.

Reference disclaimer sentence pattern (adapt the order-name clause per template):
> This is a service email about order {{ order_name }}, sent because you placed an
> order at {{ shop.name }}. It is not marketing, so there is nothing to unsubscribe
> from - your marketing preferences are separate and unaffected.

Use straight quotes/hyphens as shown — see the ASCII rule below.

## Per-template workflow

For each of the 17 templates, in order:

1. Navigate to `https://admin.shopify.com/store/oneheadhair/email_templates/<slug>/edit`,
   wait ~3s for the CodeMirror editor to mount.
2. Click into the editor. Verify you're actually in the plain code editor (not some
   other panel) before doing anything else.
3. Extract the current source. The editor is CodeMirror 6; in the page's JS context:
   `document.querySelector('.cm-content').cmView.view.state.doc.toString()`.
4. **Never return large HTML/Liquid text directly as a raw tool/script result** — it can
   trip a content-safety classifier on some tool stacks (observed as a
   "[BLOCKED: Cookie/query string data]"-style rejection). Route it through the
   clipboard instead: in the page, `await navigator.clipboard.writeText(btoa(unescape(
   encodeURIComponent(doc))))`, then immediately read the OS clipboard and
   base64-decode it into a local scratch file. Do the decode step *immediately* —
   don't let time pass between copy and read, the clipboard can get silently
   overwritten by something else in some environments.
5. Build the new document in the scratch file: keep the `{% capture email_title %}` /
   `{% capture email_body %}` Liquid logic block at the top exactly as Shopify's
   original had it (that's the subject-line and conditional-copy logic — don't touch
   the conditional structure, only the HTML/CSS below it), then rebuild the HTML body
   below it using the reference file's structure and `<style>` block, adapted only for:
   this template's own subject/body copy (do not invent copy — if unsure what a
   template's copy should say, keep Shopify's own original wording and just re-skin
   it), the eyebrow text, and the footer identifier per the section above.
6. **Before pasting back, strip every non-ASCII character.** Run a check equivalent to
   `grep -n -P '[^\x00-\x7F]' file.html` and confirm it returns nothing. Curly
   apostrophes, em dashes, and middots get mangled somewhere in the clipboard
   round-trip. Replace with straight `'`, `-`, and `-` — including ones already present
   in Shopify's own original copy — since the whole document goes through the same
   pipe.
7. Push back: click into the editor, confirm focus, copy the finished file to the OS
   clipboard **immediately** before selecting all text in the editor and pasting (same
   overwrite risk as step 4 — copy right before pasting, not earlier). Immediately
   after paste, re-read the live doc via the same JS accessor and confirm its length
   matches the file's byte count exactly, and that it contains no non-ASCII characters.
8. Save: find the Save button (an "Unsaved changes" bar appears at the top of the page —
   it can be scrolled out of view, so scroll to top before deciding it's not there).
   Click Save, wait ~2s, check again. **It often needs a second click** — if the
   "Unsaved changes" bar is still showing, click Save again.
9. **Verify the save actually persisted, not just the in-memory editor state**: navigate
   fresh to the same edit URL (a real reload, not just checking the still-open tab) and
   re-read the live document. Confirm the `.container` / `body, table.body` /
   `table.body > tr > td` background rules are exactly right (Paper on `.container`,
   transparent on the wrapper) and that your footer/eyebrow edits are present. Do not
   move to the next template until this passes.
10. Optional but recommended for visual sanity: extract the rendered preview and eyeball
    it for the "floating card with big empty gaps" failure mode — if you see that, the
    wrapper transparency rule likely didn't apply, go back and check step 9 again.

Do this template-by-template, verifying persistence after each save before starting the
next one. Don't batch all 17 edits and save at the end — a mistake early compounds
across all 17 if you don't catch it immediately.

## Standing rules (binding, no exceptions)

- No exclamation marks, no emoji, no hype/urgency/scarcity language anywhere in copy you
  write or touch.
- Never invent product, pricing, shipping, return, or support claims. If a template's
  original copy makes a claim, keep it; don't add new ones.
- Mobile is not optional — this is table-based HTML email, so "mobile" mostly means:
  keep the `<meta name="viewport">` tag, keep the `.container` width sane (~600px with
  fluid `width:100%` fallback as the reference file already does), don't introduce fixed
  pixel widths wider than 600px anywhere.
- Do not touch any Shopify notification template outside the 17 named above.
- Do not touch the master "Customize email templates" settings page — out of scope,
  leave the (technically wrong) master accent color alone. Every per-template override
  must force the correct Coral `#ED6F5C` explicitly via `!important`, same as the
  reference file does — don't rely on inheriting the master setting.

## When you're done

Report a table: all 17 slugs, pass/fail per template, and for each one note whether the
footer identifier needed a non-default variable (gift card / store credit / account) or
any other structural judgment call. Do not report a template as done unless you
completed step 9 (fresh-reload persistence verification) for it.
