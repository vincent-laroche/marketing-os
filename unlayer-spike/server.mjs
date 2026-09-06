// Zero-dependency spike server. Serves the editor page and the seeded design.
// The PAT never reaches the browser: only projectId does, and export happens here.
import { createServer } from 'node:http';
import { readFileSync } from 'node:fs';
import { parseBuiltEmail, buildDesign } from './seed-design.mjs';
import { buildBlocks } from './build-blocks.mjs';
import { buildBonelnkBlocks } from './build-blocks-bpi.mjs';
import { writeComposition } from './compose.mjs';
import { loadEnv } from './env.mjs';

const PORT = Number(process.env.PORT || 4300);
const PROJECT_ID = 289096;
const { UNLAYER_PAT_TOKEN: TOKEN } = loadEnv(['UNLAYER_PAT_TOKEN']);
if (!TOKEN) { console.error('UNLAYER_PAT_TOKEN missing from ~/.env'); process.exit(1); }

const EMAILS = '../shopify-messaging/emails';

// Pack every module as a content inside one column: contents stay individually draggable
// while avoiding ~1,972 bytes of per-row scaffolding, which is what kept C-0 under
// Shopify's 50 KB custom-code limit.
function packedDesign(file) {
  const parsed = parseBuiltEmail(`${EMAILS}/${file}`);
  const d = buildDesign(parsed);
  const contents = d.body.rows.map(r => r.columns[0].contents[0]);
  d.body.rows = [{
    id: 'row_1', cells: [1],
    columns: [{ id: 'col_1', contents, values: {} }],
    values: { padding: '0px', backgroundColor: '', columns: false },
  }];
  d.counters = { u_row: 1, u_column: 1, u_content_html: contents.length };
  return { design: d, families: parsed.modules.map(m => m.family) };
}

const json = (res, code, body) => {
  res.writeHead(code, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(body));
};

createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);

  if (url.pathname === '/' || url.pathname === '/index.html') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(readFileSync(new URL('./index.html', import.meta.url), 'utf8'));
    return;
  }

  if (url.pathname === '/api/config') return json(res, 200, { projectId: PROJECT_ID });

  if (url.pathname === '/api/blocks') {
    const library = url.searchParams.get('library') || 'atelier-zero';
    try {
      if (library === 'bone-ink') return json(res, 200, { blocks: buildBonelnkBlocks() });
      const themes = url.searchParams.get('dark') === '1' ? ['light', 'dark'] : ['light'];
      return json(res, 200, { blocks: buildBlocks({ themes }) });
    } catch (e) { return json(res, 500, { error: e.message }); }
  }

  if (url.pathname === '/api/design') {
    const file = url.searchParams.get('file') || '01-cr-1.html';
    if (!/^[0-9a-z-]+\.html$/.test(file)) return json(res, 400, { error: 'bad file' });
    try { return json(res, 200, packedDesign(file)); }
    catch (e) { return json(res, 500, { error: e.message }); }
  }

  if (url.pathname === '/api/export' && req.method === 'POST') {
    let raw = '';
    for await (const chunk of req) raw += chunk;
    try {
      const { design } = JSON.parse(raw);
      const r = await fetch(`https://api.unlayer.com/v3/templates/export/html?projectId=${PROJECT_ID}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${TOKEN}`, 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ displayMode: 'email', design }),
      });
      if (!r.ok) return json(res, 502, { error: `export ${r.status}` });
      const html = (await r.json()).data.html;
      return json(res, 200, { html, bytes: html.length, limit: 50 * 1024 });
    } catch (e) { return json(res, 500, { error: e.message }); }
  }

  if (url.pathname === '/api/compose' && req.method === 'POST') {
    let raw = '';
    for await (const chunk of req) raw += chunk;
    try {
      const { design, file } = JSON.parse(raw);
      const r = await fetch(`https://api.unlayer.com/v3/templates/export/html?projectId=${PROJECT_ID}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${TOKEN}`, 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ displayMode: 'email', design }),
      });
      if (!r.ok) return json(res, 502, { error: `export ${r.status}` });
      const html = (await r.json()).data.html;
      return json(res, 200, writeComposition({ file, html, design }));
    } catch (e) { return json(res, 500, { error: e.message }); }
  }

  json(res, 404, { error: 'not found' });
}).listen(PORT, '127.0.0.1', () => {
  console.log(`unlayer spike -> http://127.0.0.1:${PORT}`);
});
