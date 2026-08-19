# HubSpot DNS removal — 2026-08-19

Vincent: "HubSpot is completely out of the game. Remove traces of HubSpot in those
domains and subdomains." Zone `44c9e2d6eb71ce0de6bb40e563bbf351` (hairsolutions.co).

Full pre-change backup of all 10 matched records:
`hubspot-records-backup-2026-08-19.json` (type/name/content/ttl/proxied/id) — enough
to recreate any record exactly.

## Removed (9 changes)

| Record | Why safe |
|---|---|
| `hs1-50966981._domainkey.hairsolutions.co` | HubSpot DKIM, apex |
| `hs2-50966981._domainkey.hairsolutions.co` | HubSpot DKIM, apex |
| `hs1-50966981._domainkey.mail.hairsolutions.co` | HubSpot DKIM, mail subdomain |
| `hs2-50966981._domainkey.mail.hairsolutions.co` | HubSpot DKIM, mail subdomain |
| `cloud.hairsolutions.co` CNAME | HubSpot sites, returned **404** |
| `helpcenter.hairsolutions.co` CNAME | HubSpot sites, returned **404** |
| `help.hairsolutions.co` CNAME | HubSpot sites, returned **404** |
| `mail.hairsolutions.co` CNAME → `50966981.group31.sites.hubspot.net` | HubSpot sites, **404**. Also an RFC violation: a CNAME cannot coexist with the SPF/verification TXT records on that same name. Removing it is a net correctness win for email. |
| apex SPF TXT | dropped `include:50966981.spf10.hubspotemail.net` |

Apex SPF before → after:

    v=spf1 include:_spf.google.com include:50966981.spf10.hubspotemail.net a mx include:_spf.mlsend.com include:_spf.mailersend.net ~all
    v=spf1 include:_spf.google.com a mx include:_spf.mlsend.com include:_spf.mailersend.net ~all

Google Workspace (`_spf.google.com`), MailerLite and MailerSend includes all preserved.
This frees one of SPF's hard 10-lookup budget.

## Deliberately NOT removed

`customerportal.hairsolutions.co` → `50966981.group31.sites.hubspot.net` is **live**:
HTTP 200, 13.9 KB, a real HubSpot membership login page (`<title>Portal | Log in</title>`,
`<h1>Welcome back</h1>`). Unlike the others it is not a 404. Deleting it takes a
customer-facing login offline (NXDOMAIN), so it was held for an explicit decision.
Record id `8aacc882a08d17f3f3f0f9f6b0d48c74`.

## Verified after the change

- MailerLite DKIM `litesrv._domainkey.mail.hairsolutions.co` → intact
- `mail.hairsolutions.co` SPF + `mailerlite-domain-verification` TXT → intact
- MailerSend live re-verify (`POST /domains/{id}/verify`): `dkim=true spf=true`
- **End-to-end proof:** a real send returned `HTTP 202`, message
  `6a851c1c77ae976484a53a4b`, `status=sent`. Sending is unaffected.

## Note on the old apply script

`APPLY-MAILERLITE-DNS.sh` still contains a ROLLBACK block that would restore the
HubSpot SPF include. That rollback is **obsolete** — do not run it.
