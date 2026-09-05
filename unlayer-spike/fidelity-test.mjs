// Phase 2 kill gate: does Unlayer's HTML exporter preserve hand-authored Atelier Zero
// table markup verbatim when carried in a `content_html` block?
//
// Six modules spanning the hard cases go in as raw HTML; the export comes back and is
// checked for the structures that actually matter: the .az-* class hooks, the @media
// block, the card table, and the module palette.
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { randomUUID } from 'node:crypto';
import { loadEnv } from './env.mjs';

const { UNLAYER_PAT_TOKEN: TOKEN } = loadEnv(['UNLAYER_PAT_TOKEN']);
const PREVIEWS = join(process.cwd(), '..', 'Email Reference File',
  'Atelier Zero — Resolved HTML Module Previews (102)');

const MODULES = [
  'header_centered_logo',
  'layout_founder_wrapper',
  'commerce_cart_line_items',
  'comparison',
  'faq',
  'footer_preference_centre',
];

// The previews are standalone documents; the module itself is everything inside <body>.
const bodyOf = html => {
  const m = /<body[^>]*>([\s\S]*?)<\/body>/i.exec(html);
  return (m ? m[1] : html).trim();
};

let n = 0;
const id = () => `u${++n}`;

const htmlContent = html => ({
  id: id(), type: 'html', values: { html, containerPadding: '0px', _meta: {} },
});

const row = content => ({
  id: id(), cells: [1],
  columns: [{ id: id(), contents: [content], values: {} }],
  values: { padding: '0px', backgroundColor: '', columns: false },
});

const sources = {};
const rows = MODULES.map(slug => {
  const file = join(PREVIEWS, `core--${slug}_light.module.html`);
  const src = bodyOf(readFileSync(file, 'utf8'));
  sources[slug] = src;
  return row(htmlContent(src));
});

const design = {
  counters: { u_row: rows.length, u_content_html: rows.length, u_column: rows.length },
  schemaVersion: 21,
  body: {
    id: randomUUID(),
    rows,
    // AGENTS.md §5: an email paints no page background.
    values: { backgroundColor: 'transparent', contentWidth: '600px', preheaderText: '' },
  },
};
writeFileSync('fidelity-design.json', JSON.stringify(design, null, 2));

const res = await fetch('https://api.unlayer.com/v3/templates/export/html?projectId=289096', {
  method: 'POST',
  headers: { Authorization: `Bearer ${TOKEN}`, 'Content-Type': 'application/json', Accept: 'application/json' },
  body: JSON.stringify({ displayMode: 'email', design }),
});
const text = await res.text();
console.log('export status:', res.status);
if (!res.ok) { console.log(text.slice(0, 600)); process.exit(1); }

const body = JSON.parse(text);
const out = body?.data?.html ?? body?.html;
if (!out) { console.log('no html in response; keys:', Object.keys(body), JSON.stringify(body).slice(0,400)); process.exit(1); }
writeFileSync('fidelity-export.html', out);
console.log('exported bytes:', out.length);

// --- assertions that matter -------------------------------------------------
const checks = [
  ['.az-module-shell class survives',  () => out.includes('az-module-shell')],
  ['.az-content-pad class survives',   () => out.includes('az-content-pad')],
  ['@media max-width:480px survives',  () => /@media[^{]*max-width:\s*480px/.test(out)],
  ['card colour #F6EFD9 survives',     () => out.includes('#F6EFD9')],
  ['ink colour #151411 survives',      () => out.includes('#151411')],
  ['border-radius:16px survives',      () => out.includes('border-radius:16px')],
  ['no page background painted (§5)',  () => !/<body[^>]*background-color:\s*#F6EFD9/i.test(out)],
];
let failed = 0;
for (const [label, fn] of checks) {
  let ok = false; try { ok = fn(); } catch {}
  if (!ok) failed++;
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${label}`);
}

// Per-module: is the source markup present verbatim, or was it rewritten?
console.log('\nper-module verbatim check:');
for (const slug of MODULES) {
  const src = sources[slug];
  const table = /<table[\s\S]{0,400}?>/.exec(src)?.[0] ?? '';
  const verbatim = out.includes(src);
  const partial = table && out.includes(table.slice(0, 120));
  console.log(`  ${verbatim ? 'VERBATIM' : partial ? 'PARTIAL ' : 'MISSING '}  ${slug}`);
  if (!verbatim) failed++;
}
console.log(`\n${failed ? `${failed} check(s) failed` : 'ALL CHECKS PASSED'}`);
