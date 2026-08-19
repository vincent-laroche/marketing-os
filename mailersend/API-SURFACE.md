# MailerSend — API surface notes

Account domain `mail.hairsolutions.co` (id `dnvo4dm6ynn45r86`), verified, DKIM+SPF.

## 1. Cloudflare bans the default Python user-agent — HTTP 403, error 1010

`POST /v1/email` from stdlib `urllib.request` fails with:

    403  error_code 1010  browser_signature_banned
    "The site owner has blocked access based on your browser's signature."
    "**Do not retry.** Your user-agent has been banned by the site owner."

This is **not** an auth, token, quota or payload problem — the same token works
fine from `curl`. MailerSend sits behind Cloudflare, which bans the default
`Python-urllib/3.x` UA. Fix: send an explicit `User-Agent`. See `USER_AGENT`
in `send_service_email.py`. Any future stdlib caller must do the same.

Note the message says "do not retry" — that is Cloudflare boilerplate about
retrying *with the same UA*. Retrying with a real UA succeeds immediately.

## 2. Templates cannot be created via API

List/get/delete only — there is no create endpoint. Service emails are therefore
sent as **inline HTML** in the send payload, not as stored templates.

## 3. Nested personalization works — this is why service email lives here

Unlike MailerLite (flat subscriber fields only, no arrays, no loops), MailerSend
accepts arbitrary nested objects and arrays per recipient under
`personalization[].data`, rendered with Twig-style `{{ }}` / `{% for %}`.
This is what makes a real itemised order confirmation possible.

## 4. `GET /v1/messages/{id}` does not return the recipient address

`.emails[0].recipients[0].email` reads back as null even on a delivered message.
Verify recipients from the send-side ledger, not from this endpoint.
