// Phase 2: seed a real, already-published email into an Unlayer design, export it back,
// and prove nothing was lost. CR-1 is the subject because it is published, so there is a
// known-good reference.
import { readFileSync, writeFileSync } from 'node:fs';
import { parseBuiltEmail, buildDesign } from './seed-design.mjs';
import { loadEnv } from './env.mjs';

const SRC = '../shopify-messaging/emails/01-cr-1.html';
const { UNLAYER_PAT_TOKEN: TOKEN } = loadEnv(['UNLAYER_PAT_TOKEN']);

const parsed = parseBuiltEmail(SRC);
const design = buildDesign(parsed);
writeFileSync('cr1-design.json', JSON.stringify(design, null, 2));

// Validate the generated design against Unlayer's own schema before loading it anywhere.
const val = await fetch('https://api.unlayer.com/v3/templates/validate?projectId=289096', {
  method: 'POST',
  headers: { Authorization: `Bearer ${TOKEN}`, 'Content-Type': 'application/json', Accept: 'application/json' },
  body: JSON.stringify({ design }),
});
const valBody = await val.json().catch(() => null);
console.log('schema validate:', val.status, JSON.stringify(valBody).slice(0, 300), '\n');

const res = await fetch('https://api.unlayer.com/v3/templates/export/html?projectId=289096', {
  method: 'POST',
  headers: { Authorization: `Bearer ${TOKEN}`, 'Content-Type': 'application/json', Accept: 'application/json' },
  body: JSON.stringify({ displayMode: 'email', design }),
});
if (!res.ok) { console.log('export failed', res.status, (await res.text()).slice(0, 400)); process.exit(1); }
const out = (await res.json()).data.html;
writeFileSync('cr1-export.html', out);

const original = readFileSync(SRC, 'utf8');
let failed = 0;
const check = (label, ok) => { if (!ok) failed++; console.log(`${ok ? 'PASS' : 'FAIL'}  ${label}`); };

console.log(`original ${original.length}b -> export ${out.length}b\n`);

console.log('module fragments survive verbatim:');
for (const m of parsed.modules) check(`  ${m.family}`, out.includes(m.html));

console.log('\nstyles and preheader:');
for (const [i, s] of parsed.styles.entries()) check(`  style block ${i + 1}`, out.includes(s));
check('  preheader text present', out.includes(parsed.preheader.slice(0, 40)));

console.log('\nLiquid integrity (every token in the original):');
const tokens = [...new Set([...original.matchAll(/\{\{[^}]{1,80}\}\}/g)].map(m => m[0]))];
for (const t of tokens) check(`  ${t}`, out.includes(t));

console.log('\ncompliance and brand:');
check('  unsubscribe link present', /\{\{\s*unsubscribe_url\s*\}\}/.test(out));
check('  no page background painted (§5)', /<body[^>]*background-color:\s*transparent/i.test(out));
check('  card colour #F6EFD9 present', out.includes('#F6EFD9'));
check('  no #TODO- placeholder introduced', !out.includes('#TODO-'));
check('  under Shopify 50KB section limit', out.length < 50 * 1024);

console.log(`\n${failed ? `${failed} CHECK(S) FAILED` : 'ROUND-TRIP CLEAN'}`);
process.exit(failed ? 1 : 0);
