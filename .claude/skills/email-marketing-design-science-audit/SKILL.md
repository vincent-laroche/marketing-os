---
name: email-marketing-design-science-audit
description: Audits HubSpot and ecommerce marketing emails with science-backed email UX, color, accessibility, rendering, dark-mode, mobile, deliverability, compliance, lifecycle, and brand-system criteria. Use when reviewing email mockups, HubSpot marketing emails, lifecycle campaigns, transactional-style templates, HTML email, subject/preheader/CTA structure, email modules, or Hair Solutions Co. email design. Do not use for sending campaigns, changing CRM data, broad deliverability operations, or website-only UI audits.
---

# Email Marketing Design Science Audit

## Workflow

1. Identify the artifact: screenshot, HTML email, HubSpot draft, module library, copy brief, subject/preheader, lifecycle sequence, or platform spec.
2. Classify the audit mode:
   - **Design review**: screenshot, Figma, exported mockup, or Markdown spec.
   - **HTML review**: coded email, HubSpot coded template, or exported HTML.
   - **HubSpot builder review**: drag-and-drop or Design Manager module/template.
   - **Lifecycle review**: sequence/journey logic, segmentation, timing, consent, and personalization.
3. Read references just in time:
   - `references/email-design-science.md` for color, accessibility, mobile, dark mode, UX, and rendering science.
   - `references/hubspot-email-builder.md` for HubSpot-specific builder and Design Manager constraints.
   - `references/tools-and-deliverability.md` for current tools, deliverability, sender rules, and compliance.
   - `references/hsc-email-platform-gap.md` when working with Hair Solutions Co. email design.
4. For HTML files, run:

```bash
python3 scripts/audit_email_html.py path/to/email.html --json
```

5. Evaluate the core lenses:
   - color science and contrast in light/dark modes;
   - email UI/UX hierarchy, scannability, CTA clarity, and cognitive load;
   - accessibility: semantic text, alt text, reading order, link purpose, target size, contrast;
   - mobile and inbox constraints: 600px layout, 480px breakpoint, stacking, image blocking, no unsupported critical interactions;
   - client/rendering risk: Gmail, Apple Mail, Outlook, iOS/Android, dark mode, image blocking;
   - HubSpot implementation risk: module editability, personalization tokens, required footer/unsubscribe, plain-text version, preview/test send;
   - deliverability and compliance risk: consent, unsubscribe, sender identity, subject/preheader truthfulness, spam-like patterns;
   - lifecycle role fit: welcome, education, abandon cart, consultation, order, shipping, reorder, win-back, retention.
6. Use `color-science-palette-audit` for palette-specific decisions and `website-ux-science-audit` only for web-page logic that also applies to email.
7. Separate measured checks from expert judgment. Automated checks cannot prove inbox rendering quality or conversion quality.

## Output Standard

1. Start with a verdict: approve, approve with fixes, or do not approve.
2. Lead with ranked findings:
   - **P0 compliance, access, or deliverability blocker**
   - **P1 conversion, trust, or accessibility risk**
   - **P2 mobile, rendering, hierarchy, or lifecycle friction**
   - **P3 polish, consistency, or optimization**
3. For each finding include: evidence type, affected module/area, issue, why it matters, exact fix, and verification method.
4. Include a test matrix: Gmail web, Gmail mobile, Apple Mail light/dark, Outlook Windows, iOS Mail, image-blocked state, and HubSpot preview/plain-text where relevant.
5. Finish with the next safe action: edit copy, revise module, run HTML audit, send HubSpot test email, Litmus/Email on Acid test, accessibility check, or legal/deliverability verification.

## Guardrails

1. Do not send, schedule, publish, or modify HubSpot emails without explicit approval.
2. Do not treat an email screenshot as proof of HTML, mobile, dark-mode, or Outlook compatibility.
3. Do not claim legal compliance from design review alone; verify sender identity, unsubscribe, consent, and jurisdictional requirements.
4. Do not hide required transactional, policy, order, shipping, or support information behind decorative modules.
5. Do not use urgency, shame, medical claims, fake scarcity, guaranteed-result claims, or misleading personalization.

## Error Handling

1. If the artifact is incomplete, audit what is available and name missing proof: HTML, screenshot, HubSpot preview, subject/preheader, list/segment, or compliance fields.
2. If live HubSpot access is unavailable, work from exports/screenshots and state that HubSpot builder verification was not performed.
3. If HTML uses unsupported CSS or interactive patterns, flag client risk and recommend an email-safe fallback rather than a web-style fix.
4. If automated output conflicts with visual judgment, report both and prioritize user-impact plus inbox-client evidence.
5. If the request crosses into campaign sending, CRM mutation, workflow activation, or customer-impacting data changes, stop for explicit approval.

## Resources

- `scripts/audit_email_html.py`: deterministic HTML email audit helper.
- `references/email-design-science.md`: science-backed email design and accessibility review criteria.
- `references/hubspot-email-builder.md`: HubSpot-specific review and implementation criteria.
- `references/tools-and-deliverability.md`: tools, sender rules, compliance, and deliverability checks.
- `references/hsc-email-platform-gap.md`: findings from the attached Hair Solutions email platform spec.
