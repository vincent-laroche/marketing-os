// Generate the Unlayer Blocks palette from the Atelier Zero module library.
//
// Each module becomes one block whose payload is a single `content_html` carrying the
// module's HTML verbatim — the same mechanism the fidelity gate proved lossless. Nothing
// is rebuilt as native Unlayer content, so the .az-* hooks, @media block and palette survive.
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const PREVIEWS = join(process.cwd(), '..', 'Email Reference File',
  'Atelier Zero — Resolved HTML Module Previews (102)');

// Family -> palette category. Grouped the way someone reaches for a module, not by file scope.
const CATEGORY = [
  [/^(commerce|product)_/, 'Commerce'],
  [/^(header|footer)_/,    'Structure'],
  [/^(button|signal)_/,    'Actions'],
  [/^(photo|grid|column)_|^testimonial$/, 'Media'],
  [/^(list|stat)_|^(faq|comparison|timeline|proof)$/, 'Lists & proof'],
];
const categoryOf = slug => CATEGORY.find(([re]) => re.test(slug))?.[1] ?? 'Text & layout';

const titleOf = slug => slug
  .replace(/_/g, ' ')
  .replace(/\b\w/g, c => c.toUpperCase())
  .replace(/\bCta\b/, 'CTA').replace(/\bFaq\b/, 'FAQ').replace(/\b3up\b/i, '3-up');

const bodyOf = html => {
  const m = /<body[^>]*>([\s\S]*?)<\/body>/i.exec(html);
  return (m ? m[1] : html).trim();
};

export function buildBlocks({ themes = ['light'] } = {}) {
  const files = readdirSync(PREVIEWS).filter(f => f.endsWith('.module.html'));
  const blocks = [];
  let n = 0;

  for (const theme of themes) {
    for (const file of files.filter(f => f.endsWith(`_${theme}.module.html`)).sort()) {
      const [scope, rest] = file.replace('.module.html', '').split('--');
      const slug = rest.replace(new RegExp(`_${theme}$`), '');
      const html = bodyOf(readFileSync(join(PREVIEWS, file), 'utf8'));
      const i = ++n;

      blocks.push({
        id: i,
        name: titleOf(slug) + (theme === 'dark' ? ' (Dark)' : ''),
        category: categoryOf(slug),
        // Verified against a console-created block read back from GET /blocks:
        // `tags` is an ARRAY, and the payload key is `data` holding a SINGLE ROW
        // object — not `design` wrapping a full body/counters document.
        tags: [scope, slug.split('_')[0], theme],
        displayMode: 'email',
        thumbnailUrl: null,
        data: {
          id: `blk_${i}_row`,
          cells: [1],
          columns: [{
            id: `blk_${i}_col`,
            contents: [{
              id: `blk_${i}_html`,
              type: 'html',
              values: {
                html,
                containerPadding: '0px',
                _meta: { htmlID: `blk_${i}_html`, htmlClassNames: `u_content_html az-${slug}` },
                anchor: '',
                hideable: true, deletable: true, draggable: true,
                duplicatable: true, selectable: true, locked: false,
              },
            }],
            values: {
              _meta: { htmlID: `blk_${i}_col`, htmlClassNames: 'u_column' },
              border: {}, padding: '0px', backgroundColor: '',
            },
          }],
          values: {
            _meta: { htmlID: `blk_${i}_row`, htmlClassNames: 'u_row' },
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
  }
  return blocks;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const themes = process.argv.includes('--with-dark') ? ['light', 'dark'] : ['light'];
  const blocks = buildBlocks({ themes });
  const byCat = {};
  for (const b of blocks) (byCat[b.category] ??= []).push(b.name);
  console.log(`generated ${blocks.length} blocks from themes: ${themes.join(', ')}\n`);
  for (const [cat, names] of Object.entries(byCat).sort()) {
    console.log(`${cat} (${names.length})`);
    for (const nm of names.slice(0, 4)) console.log(`   ${nm}`);
    if (names.length > 4) console.log(`   … ${names.length - 4} more`);
  }
  const bytes = JSON.stringify(blocks).length;
  console.log(`\npayload: ${(bytes / 1024).toFixed(1)} KB`);
}
