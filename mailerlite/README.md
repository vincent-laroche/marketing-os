# mailerlite/ — Legacy MailerLite artifacts (superseded)

> **Superseded platform path, 2026-08-24:** all marketing campaigns and lifecycle journeys now
> live in Shopify Messaging + Shopify Flow. The live MailerLite account has zero campaigns.
> This folder is retained as legacy build output, migration evidence, and API reference only.
> Do not create, push, restore, or activate campaigns/automations from these instructions unless
> Vincent explicitly reopens MailerLite scope.

Twenty-two journey emails (PP ×8, CR ×4, WB ×4, RO ×6) were previously rebuilt for MailerLite from the
authoritative copy deck `../Email Reference File/emails_modules_hubspot versionr/` and the Figma Email Design System v3
(`9Il504CQE8jLaUTBVzphqc`, page 291:724). They are no longer an active delivery path.

## Files

- `build_emails.py` — renderer + validator. Run: `python3 build_emails.py`
- `ml_components.py` — design-token component library (bone/ink/coral, Inter Tight/Inter/JetBrains Mono, 600px)
- `ml_content_pp.py` / `ml_content_cr.py` / `ml_content_wb.py` / `ml_content_ro.py` — per-series content (verbatim master copy)
- `products.json` — real Shopify hybrid products used in WB-2's grid (snapshot 2026-08-18)
- `emails/*.html` — the 22 generated emails (3–10 KB each, MailerLite `{$field}` syntax)
- `BUILD-LEDGER.md` — account state, per-email flags, blockers
- `AUTOMATION-ASSEMBLY.md` — exact MailerLite UI steps for the 4 journey automations

## Historical MailerLite creation mechanics

All 22 are pushed as **draft campaigns** via `POST /api/campaigns` with inline HTML
(`push_campaigns.py`) — see `API-SURFACE.md`. Automation *steps* can also be created via the
undocumented `POST /api/automations/{id}/steps`, but writing content to them needs a
**domain-authenticated** sender, unlike campaigns which need only a verified one. CR-1/CR-2/CR-4 then get their
dashed placeholder swapped for the native E-commerce → Abandoned cart block.

## Rules

- Copy changes → edit `ml_content_*.py`, re-run the builder. Never edit `emails/*.html` directly.
- `{$...}` tokens must never render empty (master rule) — field sync first.
- No sends, no automation activation, no contact imports without Vincent's explicit approval.
