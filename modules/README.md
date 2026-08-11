# Complete Local Email Module Collection

`all/` contains every HubSpot email module folder found in the local Email Marketing Studio source on
2026-07-27: 94 modules across `core`, `launch`, and `newsletter`.

The original local files are preserved byte-for-byte. Where an existing production module was missing a
primary source file locally, only that missing file was read from live HubSpot and added:

- 55 missing production files restored;
- zero existing local files replaced;
- 90 modules now contain `fields.json`, `meta.json`, and `module.html`;
- four local-only dark drafts remain without their original `fields.json`.

The four incomplete local-only drafts are:

- `core/faq_block_dark.module`
- `core/hero_dark.module`
- `core/proof_dark.module`
- `core/reassurance_dark.module`

Their light counterparts are complete, but no field definition was copied or invented for the dark
variants. Use `module-inventory.csv` or `module-inventory.json` to track rebranding progress and source
status. `repair-manifest.json` records the targeted repair and preservation verification.

## Atelier Zero output

`atelier-zero/` contains the non-destructive Atelier Zero v7 conversion of all 94 modules. The four
local-only dark drafts use a copy of their paired light-module field schema in this output only; the
rebrand script verified that each light/dark pair references the identical field set before copying.
All 94 output modules now have `module.html`, `fields.json`, and `meta.json`.

The output passed current-palette, contrast, schema, field-parity, and representative desktop/mobile
render checks. Copy claims, links, media decisions, HubSpot upload/rendering, and final owner approval
remain separate release gates; see the dated compliance report in `records/`.

No module was uploaded, changed, published, or deleted in HubSpot.
