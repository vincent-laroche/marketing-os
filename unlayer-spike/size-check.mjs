// The export adds Unlayer wrapper scaffolding. Measure the overhead across the size range
// so the largest emails are known-safe before 52 modules are ported.
import { readFileSync } from 'node:fs';
import { parseBuiltEmail, buildDesign } from './seed-design.mjs';
import { loadEnv } from './env.mjs';
const { UNLAYER_PAT_TOKEN: TOKEN } = loadEnv(['UNLAYER_PAT_TOKEN']);

const SAMPLES = [
  '29-c-0.html',        // largest, 25.7 KB
  '43-nl-10.html',      // 23.1 KB
  '53-nl-20.html',      // 22.4 KB
  '01-cr-1.html',       // 10.5 KB, known good
  '14-w-1.html',        // small
];

console.log('file                  original    export   ratio  modules  verbatim  <50KB');
console.log('-'.repeat(78));
let worst = 0, anyFail = 0;
for (const f of SAMPLES) {
  const path = `../shopify-messaging/emails/${f}`;
  const parsed = parseBuiltEmail(path);
  const design = buildDesign(parsed);
  const res = await fetch('https://api.unlayer.com/v3/templates/export/html?projectId=289096', {
    method: 'POST',
    headers: { Authorization: `Bearer ${TOKEN}`, 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ displayMode: 'email', design }),
  });
  if (!res.ok) { console.log(`${f.padEnd(20)} EXPORT FAILED ${res.status}`); anyFail++; continue; }
  const out = (await res.json()).data.html;
  const orig = readFileSync(path, 'utf8').length;
  const ratio = out.length / orig;
  worst = Math.max(worst, out.length);
  const verbatim = parsed.modules.every(m => out.includes(m.html));
  const under = out.length < 50 * 1024;
  if (!verbatim || !under) anyFail++;
  console.log(
    `${f.padEnd(20)} ${String(orig).padStart(8)} ${String(out.length).padStart(9)}` +
    `  ${ratio.toFixed(2)}x ${String(parsed.modules.length).padStart(7)}` +
    `  ${(verbatim ? 'yes' : 'NO').padStart(8)}  ${under ? 'ok' : 'OVER'}`
  );
}
console.log(`\nlargest export: ${(worst / 1024).toFixed(1)} KB of 50 KB`);
console.log(anyFail ? `${anyFail} problem(s)` : 'all samples safe');
