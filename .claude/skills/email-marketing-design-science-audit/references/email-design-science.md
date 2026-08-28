# Email Design Science

Use this reference for email-specific design, UX, accessibility, color, rendering, and composition audits.

## Email Is Not Web

Email clients have uneven support and often alter HTML, CSS, images, fonts, and dark-mode colors. Prefer conservative layouts:

- 600px maximum wrapper;
- table-based layout for structure;
- inline critical styles;
- real text for headings, prices, order details, CTA labels, and disclaimers;
- no JavaScript, forms, sticky UI, CSS Grid, required Flexbox, or hover-dependent behavior;
- readable with images blocked.

## Visual Hierarchy And Scannability

Most email decisions happen quickly. Audit:

- subject and preheader set a truthful promise;
- first viewport makes the email job obvious;
- one dominant message and one primary CTA in most emails;
- short paragraphs, strong section labels, and sparse emphasis;
- no competing equal-weight CTAs;
- key operational details appear before decorative content;
- links and CTAs use descriptive labels.

## Color Science In Email

Apply color science conservatively:

- measure text/background contrast in light and dark mode;
- keep CTA contrast high even if clients alter colors;
- avoid using accent colors as large fills unless contrast and brand role are clear;
- avoid relying on hue alone for state;
- do not use transparent logos or pale accents where dark mode can invert or obscure them.

Use `color-science-palette-audit` for deeper palette checks.

## Accessibility

Minimum audit criteria:

- meaningful image alt text or empty alt for decorative images;
- readable text size: usually 16px body on mobile;
- descriptive CTA and link labels;
- link purpose understandable out of context where possible;
- logical reading order when columns stack;
- CTA/tap targets around 44px high;
- sufficient contrast in light and dark modes;
- no key content embedded only in images;
- semantic `lang`, title/preheader handling, and presentation tables where appropriate.

Automated accessibility tools help but do not fully model email-client rendering.

## Dark Mode And Image Blocking

Audit both:

- Apple Mail/Gmail dark mode if possible;
- logos and images on light and dark backgrounds;
- text remains visible when images are blocked;
- CTAs remain visible if background colors are altered;
- fallback text and live text wordmarks exist where needed.

## Lifecycle Role Fit

Email design should match the job:

- welcome: orient and set expectations;
- education: teach one decision at a time;
- promotional: one clear offer or product story without pressure;
- abandoned cart: help recover uncertainty, not just push purchase;
- consultation reminder: prepare, manage, or attend;
- transactional/order: accuracy first, atmosphere second;
- reorder: confirm specs/details without implying unavailable saved data;
- win-back: offer help without guilt or false urgency.

## Source Anchors

- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- WebAIM email accessibility guidance: https://webaim.org/techniques/email/
- Email Markup Consortium reports and resources: https://www.emailmarkup.org/
- Can I Email client support: https://www.caniemail.com/
- Litmus email accessibility and testing resources: https://www.litmus.com/
- Email on Acid testing resources: https://www.emailonacid.com/
