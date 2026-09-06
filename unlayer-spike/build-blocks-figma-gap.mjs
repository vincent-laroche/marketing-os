// The 5 component families #150 found missing from the Bone/Paper/Ink library:
// Action/Button (all styles), Email/Footer, Email/Divider, Email/Pre-Header, Email/Navigation.
// Sourced from the real, governed Figma "Email Design System" file (fileKey 9Il504CQE8jLaUTBVzphqc),
// hand-converted to email-safe HTML — Figma's own JSON isn't email markup, so this isn't a mechanical
// export. Each file was checked against the same rigor as the batch folders: balanced tags,
// transparent outer wrapper, palette confined to the approved hexes.
//
// These don't fit the family-with-bone+ink-pair shape the rest of this generator assumes: some are
// White-only (no Figma-evidenced Bone/Ink variant), Footer/Navigation are Ink+White pairs, and the
// three button styles (Coral/Ink/Ghost) are independent, not shade variants of one family. So this
// is a flat list, not a shade-paired map.
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const DIR = join(process.cwd(), '..', 'figma-email-design-system', 'modules');

const ENTRIES = [
  { file: 'button__coral.html', name: 'Button — Primary CTA (Coral)', category: 'Actions' },
  { file: 'button__ink.html', name: 'Button — Primary CTA (Ink)', category: 'Actions' },
  { file: 'button__ghost.html', name: 'Button — Secondary CTA (Ghost)', category: 'Actions' },
  { file: 'divider__white.html', name: 'Divider (White)', category: 'Structure' },
  { file: 'preheader__white.html', name: 'Pre-Header (White)', category: 'Structure' },
  { file: 'navigation__white.html', name: 'Navigation — Centered Logo (White)', category: 'Structure' },
  { file: 'navigation__ink.html', name: 'Navigation — With Links (Ink)', category: 'Structure' },
  { file: 'footer__white.html', name: 'Footer — Full (White)', category: 'Structure' },
  { file: 'footer__ink.html', name: 'Footer — Full (Ink)', category: 'Structure' },
];

export function buildFigmaGapBlocks(startId = 1000) {
  const present = new Set(readdirSync(DIR));
  const blocks = [];
  let n = startId;

  for (const { file, name, category } of ENTRIES) {
    if (!present.has(file)) continue; // fail quiet-but-visible: just skip, never fabricate a block
    const html = readFileSync(join(DIR, file), 'utf8').trim();
    const i = ++n;
    blocks.push({
      id: i,
      name,
      category,
      tags: ['figma-gap-fill', file.replace('.html', '')],
      displayMode: 'email',
      thumbnailUrl: null,
      data: {
        id: `fgap_${i}_row`,
        cells: [1],
        columns: [{
          id: `fgap_${i}_col`,
          contents: [{
            id: `fgap_${i}_html`,
            type: 'html',
            values: {
              html,
              containerPadding: '0px',
              _meta: { htmlID: `fgap_${i}_html`, htmlClassNames: `u_content_html az-fgap-${file.replace('.html', '')}` },
              anchor: '',
              hideable: true, deletable: true, draggable: true,
              duplicatable: true, selectable: true, locked: false,
            },
          }],
          values: {
            _meta: { htmlID: `fgap_${i}_col`, htmlClassNames: 'u_column' },
            border: {}, padding: '0px', backgroundColor: '',
          },
        }],
        values: {
          _meta: { htmlID: `fgap_${i}_row`, htmlClassNames: 'u_row' },
          anchor: '', locked: false, columns: false, padding: '0px',
          hideable: true, deletable: true, draggable: true, selectable: true,
          duplicatable: true, noStackMobile: false,
          backgroundColor: '', columnsBackgroundColor: '',
          backgroundImage: { url: '', fullWidth: true, repeat: 'no-repeat', size: 'custom', position: 'center' },
          hideDesktop: false,
        },
      },
    });
  }
  return blocks;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const blocks = buildFigmaGapBlocks();
  console.log(`generated ${blocks.length}/${ENTRIES.length} gap-fill blocks`);
  for (const b of blocks) console.log(`  ${b.name}`);
}
