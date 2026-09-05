// Each row costs ~1,972 bytes of scaffolding. Contents inside a single column are also
// individually draggable in the editor, so test whether packing modules as contents rather
// than as rows keeps the UX while removing the per-row overhead.
import { readFileSync, writeFileSync } from 'node:fs';
import { randomUUID } from 'node:crypto';
import { parseBuiltEmail } from './seed-design.mjs';
import { loadEnv } from './env.mjs';
const { UNLAYER_PAT_TOKEN: TOKEN } = loadEnv(['UNLAYER_PAT_TOKEN']);

let n = 0; const id = p => `${p}_${++n}`;
const content = html => ({
  id: id('html'), type: 'html',
  values: { html, containerPadding: '0px', _meta: {}, hideable: true, deletable: true, draggable: true, duplicatable: true },
});

function design(parsed, mode) {
  const htmls = parsed.modules.map((m, i) =>
    i === 0 && parsed.styles.length ? `${parsed.styles.join('\n')}\n${m.html}` : m.html);
  const rows = mode === 'row-per-module'
    ? htmls.map(h => ({ id: id('row'), cells: [1],
        columns: [{ id: id('col'), contents: [content(h)], values: {} }],
        values: { padding: '0px' } }))
    : [{ id: id('row'), cells: [1],
        columns: [{ id: id('col'), contents: htmls.map(content), values: {} }],
        values: { padding: '0px' } }];
  return {
    counters: { u_row: rows.length, u_column: rows.length, u_content_html: htmls.length },
    schemaVersion: 21,
    body: { id: randomUUID(), rows,
      values: { backgroundColor: 'transparent', contentWidth: '600px', preheaderText: parsed.preheader } },
  };
}

const exportHtml = async d => {
  const res = await fetch('https://api.unlayer.com/v3/templates/export/html?projectId=289096', {
    method: 'POST',
    headers: { Authorization: `Bearer ${TOKEN}`, 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ displayMode: 'email', design: d }),
  });
  if (!res.ok) throw new Error(`${res.status} ${(await res.text()).slice(0,200)}`);
  return (await res.json()).data.html;
};

const LIMIT = 50 * 1024;
console.log(`${'file'.padEnd(18)} ${'orig'.padStart(7)} ${'row-per-mod'.padStart(12)} ${'single-row'.padStart(11)} ${'saved'.padStart(7)}  verbatim`);
console.log('-'.repeat(72));
for (const f of ['29-c-0.html', '43-nl-10.html', '01-cr-1.html']) {
  const parsed = parseBuiltEmail(`../shopify-messaging/emails/${f}`);
  const orig = readFileSync(`../shopify-messaging/emails/${f}`, 'utf8').length;
  n = 0; const a = await exportHtml(design(parsed, 'row-per-module'));
  n = 0; const b = await exportHtml(design(parsed, 'single-row'));
  const verbatim = parsed.modules.every(m => b.includes(m.html));
  if (f === '29-c-0.html') writeFileSync('c0-packed.html', b);
  console.log(
    `${f.padEnd(18)} ${String(orig).padStart(7)} ${String(a.length).padStart(12)}` +
    `${(a.length>=LIMIT?' OVER':'     ')} ${String(b.length).padStart(11)}${b.length>=LIMIT?' OVER':'     '}` +
    ` ${String(a.length-b.length).padStart(7)}  ${verbatim ? 'yes' : 'NO'}`
  );
}
