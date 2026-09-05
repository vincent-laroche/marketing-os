// Every block payload must be a schema-valid design, or the Blocks panel renders it empty.
import { buildBlocks } from './build-blocks.mjs';
import { loadEnv } from './env.mjs';
const { UNLAYER_PAT_TOKEN: TOKEN } = loadEnv(['UNLAYER_PAT_TOKEN']);
const blocks = buildBlocks({ themes: ['light'] });
let bad = 0;
for (const b of blocks) {
  const r = await fetch('https://api.unlayer.com/v3/templates/validate?projectId=289096', {
    method: 'POST',
    headers: { Authorization: `Bearer ${TOKEN}`, 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ design: b.design }),
  });
  const j = await r.json().catch(() => null);
  const ok = r.ok && j?.data?.valid;
  if (!ok) { bad++; console.log(`INVALID  ${b.name}  ${JSON.stringify(j).slice(0, 220)}`); }
}
console.log(bad ? `\n${bad}/${blocks.length} invalid` : `\nall ${blocks.length} block designs valid`);
