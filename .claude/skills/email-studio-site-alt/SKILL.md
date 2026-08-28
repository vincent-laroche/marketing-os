---
name: email-studio-site
description: Use when working on the Hair Solutions Co. Email Studio Sites app, including its Studio, Emails, Modules, HubSpot Sync, Agent JSON pages, Notion sync, HubSpot read-only audit, local source layout, validation, and safe publish handoff.
---

# Email Studio Site

Use this skill for the Hair Solutions Co. Email Studio Sites app.

## Source of Truth

- Local repo: `/Users/vMac/04_marketing/email-studio-site`
- Production site: `https://hsc-email-studio.hair-solutio-6585.chatgpt-team.site`
- Sites project config: `/Users/vMac/04_marketing/email-studio-site/.openai/hosting.json`
- Sites project id: `appgprj_6a42d00f5bc88191907b8abb5137f2c4`
- Current app stack: Vinext / React / TypeScript, deployed through OpenAI Sites.

Do not create a new Sites project for this app. Reuse the project id in `.openai/hosting.json`.

## Current Role Split

- HubSpot is production source of truth: final sent email JSON, segmentation, analytics, and send engine.
- Notion is the structural planning library: email rows, module rows, approval state, relationships.
- Studio is the visual validator: preview, build, inspect, and export HTML.
- This app currently reads and audits. Do not write to HubSpot or Notion unless Vincent explicitly approves the exact write path.

## Important Routes

- `/studio` embeds the original Email Studio work surface.
- `/emails` shows the synced email queue and readable multi-tag system.
- `/modules` shows the reusable module library from Notion.
- `/hubspot` shows the HubSpot production drift panel.
- `/agent-json` documents machine-readable agent endpoints.
- `/api/sync` returns Studio seed data plus live Notion email/module rows when Notion runtime env is configured.
- `/api/hubspot/audit` returns the read-only HubSpot vs Notion drift audit.

The production site is workspace-gated. Agent HTTP reads need either an authenticated workspace session or a private bearer token sent as:

```text
OAI-Sites-Authorization: Bearer <token from secure env only>
```

Never paste or print that token.

## File Map

- `app/components.tsx`: shared shell, side navigation, sync panel, tables, tags, module cards.
- `app/styles.css`: global UI layout and component styling.
- `app/studio/page.tsx`: page that embeds the legacy studio iframe.
- `app/emails/page.tsx`: email queue page.
- `app/modules/page.tsx`: module library page.
- `app/hubspot/page.tsx`: production drift control panel.
- `app/agent-json/page.tsx`: endpoint documentation and sample payload page.
- `app/api/sync/route.ts`: read-only Notion/Studio JSON endpoint.
- `app/api/hubspot/audit/route.ts`: read-only HubSpot drift JSON endpoint.
- `lib/notion.ts`: Notion database querying, normalization, relation summaries, fallback seed data.
- `lib/hubspot.ts`: HubSpot OAuth refresh, marketing email fetch, JSON/module extraction, drift model.
- `lib/emailTags.ts`: readable multi-tag inference for emails.
- `lib/emailStudioSeed.ts`: embedded Studio seed email data.
- `public/studio/email-studio.html`: original standalone Email Studio UI embedded inside `/studio`.
- `public/studio/assets/`: Studio logo/media assets.

## Runtime Environment

Secrets are not committed. The production Sites runtime env has the live values. Local secrets may exist in `/Users/vMac/.env`, but never print them.

Relevant variable names:

- `NOTION_DEV_TOKEN` or `NOTION_TOKEN`
- `HUBSPOT_CLIENT_ID`
- `HUBSPOT_CLIENT_SECRET`
- `HUBSPOT_REFRESH_TOKEN`

Notion source ids currently used by `lib/notion.ts`:

- Emails: `57ef50bd430b46639382431b071cfccb`
- Modules: `595a324c994f4bce8a06d61fcc42a36d`

## Safe Workflow

1. Start by inspecting the repo:

```bash
cd /Users/vMac/04_marketing/email-studio-site
git status --short
```

2. Read the relevant files before editing. Prefer targeted changes over broad rewrites.

3. Keep data mutations out of scope by default:

- No HubSpot writes.
- No Notion writes.
- No credential changes.
- No access-policy changes.
- No new Sites project.
- No public exposure of private endpoints or bearer tokens.

4. Validate before claiming completion:

```bash
npm run lint
npm run build
```

5. For UI changes, run a local production check when practical:

```bash
npm run start
```

Then inspect the affected route in a browser or with a targeted fetch.

6. Commit focused changes locally with a clear message. Do not commit `.env`, generated screenshots, `.playwright-cli/`, `dist/` churn, or secrets.

7. Publishing requires the OpenAI Sites connector or Codex handoff. If Codex does not have the Sites connector, stop after commit and hand the exact commit hash to Codex for push, save-version, and deploy.

## Deployment Handoff

When handing deployment to Codex, provide:

- Repo path: `/Users/vMac/04_marketing/email-studio-site`
- Commit hash to publish.
- Sites project id from `.openai/hosting.json`.
- Validation results from `npm run lint` and `npm run build`.
- Any routes that need live verification.

The Sites deployment sequence is:

1. Push the exact committed source state to the Sites source repository using a short-lived Sites credential.
2. Save a new Sites version using the pushed commit SHA.
3. Deploy that saved version to production.
4. Poll deployment status until terminal.
5. Verify the production URL and affected endpoints.

Do not invent Sites IDs or reuse stale short-lived credentials.

## Design Rules

- This is an operator tool, not a landing page.
- Favor dense, scannable, practical interfaces over decorative branding.
- Keep the multi-page structure: Studio, Emails, Modules, HubSpot Sync, Agent JSON.
- Studio iframe should use available desktop width and avoid unnecessary horizontal scrolling.
- Email series/journey labels should be readable tags, not opaque legacy codes.
- Palette is its own Studio section, not part of Launch.

## Current Constraints

- `/api/hubspot/audit` is read-only and compares HubSpot marketing emails to Notion rows.
- HubSpot matching is currently normalized name first, then subject.
- Module extraction comes from HubSpot marketing email JSON widgets/flex areas.
- Notion relation counts are detected generically from relation properties.
- The app does not yet perform conflict-resolution writes back into Notion or HubSpot.

## Completion Bar

A task is complete only when:

- The requested change is implemented in the correct source files.
- `npm run lint` passes.
- `npm run build` passes unless a real external blocker is documented.
- UI changes are checked in browser or targeted route output.
- Production claims are backed by a Sites deployment status and live verification.
- Any skipped write/publish step is explicitly called out.
