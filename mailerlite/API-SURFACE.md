# MailerLite email-creation surface — verified 2026-08-18

Empirically probed against the live account (`2582372`) with `MAILERLITE_API_TOKEN`,
plus a visual pass through the dashboard. Supersedes the README's claim that
"automation email steps can't be created via API".

## Account reality check

| Fact | Value |
|---|---|
| Working account | **2582372**, login `info@ascensio.dev`, created 2026-08-18 10:16 |
| Claude MCP connector account | **2534132**, `vincent.laroche.br@gmail.com` — **wrong account, effectively empty** |
| Plan | **Free**, cap **250 subscribers**, trial (Advanced features) ends **2026-09-02** |
| Authenticated sending domains | **none** (`intercom_tags: "No Authenticated domain"`) |
| Subscribers synced | 248 of **3,958** Shopify customers — ceilinged by the 250 cap |

## The five ways to create email content

### 1. `POST /api/campaigns` with inline HTML — **works**
```
POST /api/campaigns
{ "name","language_id","type":"regular",
  "emails":[{"subject","from_name","from","content":"<html>…"}] }
```
Verified: returned **201**, `missing_data: []`, email `type: builder_html`.
Docs note `content` requires the **Advanced plan** — available now on trial, **lost 2026-09-02**.
`PUT /api/campaigns/{id}` updates draft campaigns with the same shape.

### 2. `POST /api/automations/{id}/steps` — **works, and is undocumented**
Returned **201** creating a real `type: email` step. The public docs claim no such
endpoint exists; it does. `GET` on it is 405 (POST-only), `PUT` and `DELETE` are supported.

### 3. `PUT /api/automations/{id}/steps/{step_id}` — **blocked only by sender auth**
Payload must be `{"data": {name, subject, from, from_name, reply_to, content, builder_type, preheader}}`.
Rejected with **422 "Sender email must be authenticated before you can send from this address."**
— *not* a capability limit. The identical message appears in the dashboard's own email-step
panel, so this gates the UI too. **Authenticate the domain and this unblocks.**

### 4. Dashboard editors (3 kinds, per campaign or automation email)
- **Drag & drop editor** — block-based, brand styles
- **Simple editor** (new) — inline editing
- **Custom HTML editor** — three entry points: *Generate email* (AI), *Import HTML code*
  (ZIP upload), *Code from scratch*. Has a `{ }` merge-tag rail and an "Agent (Beta)" tab.
  Note: "CSS (except media queries) will be applied as inline styles before sending."

Editor choice is made at creation. **`Actions` on an existing email offers only
*Save as template* / *Remove content blocks* — there is no convert-to-HTML.** An email
built in drag & drop cannot be switched to Custom HTML afterwards.

### 5. Templates — read-only via API
`GET /api/templates` works (128 gallery + 2 custom). **`POST /api/templates` is 405.**
Templates can only be created from the UI via *Actions → Save as template*.

## Automation step vocabulary (from the builder UI)

**Triggers** — Completes a form · Joins group(s) · Joins a segment · Clicks a link ·
Updates field · Event anniversary · Exact date · **Abandoned cart · Abandoned checkout ·
Buys specific product · Buys any product · Purchase frequency · Buys from category**

**Rules** — Delay · Condition · A/B test
**Actions** — Send email · Webhook · Send internal notification · Move to step ·
Update custom field · Copy to groups · Move to groups · **Remove from groups** · Unsubscribe

Everything `AUTOMATION-ASSEMBLY.md` needs exists natively, including *Remove from groups*
for the WB-4 sunset and *Condition* for the PP-7 click branch.

## What this means for the 22 emails

The manual "paste each email into the UI" plan is **not** the only option. Once
`mail.hairsolutions.co` is authenticated, the whole journey set can be pushed
programmatically: create step → PUT content. Sequence matters:

1. Authenticate the sending domain (unblocks both API and UI).
2. Push the 22 emails via steps + PUT while the trial's Advanced features are live.
3. Upgrade before **2026-09-02** or lose both the HTML `content` field and the
   subscriber headroom (250 cap vs 3,958 customers).

## Claude MailerLite connector (re-authenticated to 2582372, 2026-08-18)

Now on the correct account and sees all four journey shells. But for pushing the 22 emails
it is **not** the right tool:

- `update_automation_email` takes only `subject` + `plain_text` — **there is no HTML field.**
  It cannot carry the built `emails/*.html`.
- Tested live: it returns the *same* **422 "Sender email must be authenticated"**, confirming
  it wraps `PUT /automations/{id}/steps/{step_id}`.
- `build_custom_automation` supports only triggers
  `subscriber_joins_group | form_completed | abandoned_cart | subscriber_joins_segment`
  and step types `email | delay` — **no condition/branch, no purchase trigger.** Too limited
  for J1 (PP-7 click branch), J3 (sunset via remove-from-groups) and J4 (consumable/system branches).

Useful connector tools: `dry_run_automation`, `send_test_automation`, `validate_email_content`,
`validate_subject_lines`, `update_automation_delay`.

**Conclusion: one gate blocks everything.** Raw API, connector, and dashboard UI all fail on
the identical sender-authentication error. Authenticate the domain and all three unlock at once.

## DNS records needed for mail.hairsolutions.co

MailerLite requires three records (per its Cloudflare/authentication docs):

| Type | Name | Value |
|---|---|---|
| CNAME | `litesrv._domainkey` | `litesrv._domainkey.mlsend.com` |
| TXT | (SPF) | account-specific — read from Domains page |
| TXT | (domain verification) | account-specific — read from Domains page |

**HubSpot coexistence is fine.** MailerLite's DKIM selector is `litesrv`; HubSpot uses its own
(`hs1-`/`hs2-`), so the CNAMEs don't collide. SPF merges into one record with two includes:

```
v=spf1 include:50966981.spf10.hubspotemail.net include:_spf.mlsend.com ~all
```

Current live state of `mail.hairsolutions.co`: SPF = HubSpot only, no MailerLite DKIM.
Apex DMARC is `p=quarantine`, so unauthenticated mail is quarantined, not merely flagged.

**Blocked on:** the two account-unique TXT values, which are only visible on the Domains page
of a logged-in dashboard session.

## Automation step API — working recipe (verified 2026-08-18, post domain-auth)

Once `mail.hairsolutions.co` authenticated (`active_spf` + `active_dkim` + `verified` all
true), pushing built HTML into automation email steps works end to end:

```
PUT /api/automations/{automation_id}/steps/{step_id}
{ "parent_id": "<preceding step id>",          # TOP LEVEL — inside data it is silently nulled
  "data": { "name", "subject", "from", "from_name", "reply_to",
            "content": "<full html>", "builder_type": "html" } }
```

Hard-won details:

- **`data.preheader` is prohibited** when `content` is supplied — 422. MailerLite derives the
  preheader from the HTML's own hidden preheader div, so ours is already carried.
- **`parent_id` must be top level.** Passing it inside `data` returns 200 but sets it to null.
- **Steps chain in reverse on creation.** A bare `POST /steps` makes the new step the head and
  re-parents the previous one under it.
- **`create_automation` (MCP connector) leaves steps UNLINKED.** It reports `steps_created: 9`
  and the right order, but every email comes back with `parent_id: null` — the flow is N
  disconnected fragments, not one sequence, and would not run. Fix by PUTting `parent_id` on
  each email to point at its preceding delay. Always verify: exactly one step should have no
  parent.
- `complete: false` on steps/automation is a soft advisory. The real health signals are
  `eligible_for_sending: true`, `broken: false`, and `dry_run_automation` reporting
  `emails_designed: N, emails_undesigned: 0`.
- Domain auth gates automation steps only. Campaigns need merely a *verified sender*.

## What this account cannot run (2582639, Comfort plan)

- **No e-commerce shop connected** → `abandoned_cart`, `abandoned_checkout`,
  `purchased_any_product`, `purchase_frequency` triggers all come back `broken: true`.
  This blocks J1 (Post-Purchase), J2 (Cart Recovery) and J4 (Reorder) structurally.
- **999 of 1,000 subscriber cap used** by the prospect cohort → no headroom to sync the
  3,958 Shopify customers those journeys would target.
- Template #7 "Advanced welcome" is plan-gated: "Cannot use this template on your current plan."

### 6. `PUT /api/campaigns/{id}` — group assignment reads back on `filter`, not `groups`

Two quirks, both cost real time (2026-08-19):

1. **`name` is required on every PUT**, even when the only change is the audience.
   Omitting it returns 422 *"The name field is required."*
2. **The assignment does not read back on `groups`** — that field stays `null`
   forever. It lands on `filter` as a rule:
   `"filter": [[{"operator":"in_any","args":["groups",["<group_id>"]]}]]`

   Verifying via `groups` therefore produces a **false negative** — the write looks
   like a silent no-op when it actually succeeded. Verify via `filter`, plus
   `recipients_count`.

3. **`recipients_count` is `null` on the list endpoint** and only computed on
   `GET /api/campaigns/{id}`. Do not assert `== 0` against list output.

This is distinct from the genuine no-ops (`groups: []` to *clear*, and the
`settings.use_google_analytics` UTM keys), which really are discarded.

### 7. `DELETE /api/subscribers/{id}` is a SOFT delete — an upsert resurrects it

Discovered 2026-08-19 while rebuilding the audience. After deleting all 631
Shopify-sourced subscribers (verified: zero `source=ecommerce` remained), a
later `POST api/subscribers` upsert of an overlapping email brought 186 of them
**back with their original `id`, `created_at` and `source`** — plus their old
group memberships. Only `updated_at`, `fields` and newly-assigned groups
reflected the upsert.

Consequences:

- `source` is **not** provenance for the current record. A subscriber can read
  `source: ecommerce` while having arrived via a HubSpot CSV upsert. Judge
  provenance by a field you control (here: `migration_cohort`), never by `source`.
- Deleting to "clean" an audience does not survive re-adding the same address.
  Prior group membership returns with it — which can silently re-arm an
  automation trigger keyed on that group.
- Counting `source=ecommerce` therefore **overstates** Shopify's contribution.
  Cross-check against the upload list before concluding the integration re-ran.

### 8. `name` is required on **every** PUT, not just campaigns

The §6 campaign quirk generalises. `PUT /api/automations/{id}` with only a `triggers` body
returns 422 *"The name field is required."* Resend the object's existing `name` on every PUT
or the write is rejected outright.

### 9. `PUT /api/ecommerce/shops/{id}` — the sync group cannot be cleared, only repointed

- `{"group_id": null}` → 422 *"The group id field must be an integer."*
- `{"group_id": ""}`   → 422, same message.
- `{"group": null}`    → **200 and silently does nothing** — another of this API's no-op
  writes. Reading back is mandatory.

There is therefore no API way to disconnect the Shopify subscriber sync from a group while
keeping the shop connected for catalog data. The workaround is to repoint it at an inert
quarantine group. `enable_resubscribe` and `enable_popups` *do* accept `false` and take
effect — turn both off: `enable_resubscribe: true` lets the integration resurrect people who
had unsubscribed.

The embedded Shopify app's UI matches (verified 2026-08-19): the Groups tab shows the current
sync group with an **Active** badge and offers only per-group **Select** buttons — repoint,
never unselect. Pop-ups and resubscribe are On/Off toggles on its Settings tab. The
**Disconnect** button there is the only full off, and it severs the catalog sync too.
