import { loadEnv } from './env.mjs';
const { UNLAYER_PAT_TOKEN: TOKEN } = loadEnv(['UNLAYER_PAT_TOKEN']);
const r = await fetch('https://api.unlayer.com/v3/blocks?projectId=289096', {
  headers: { Authorization: `Bearer ${TOKEN}`, Accept: 'application/json' },
});
const j = await r.json();
console.log('status', r.status);
const items = j.data ?? j;
console.log('count:', Array.isArray(items) ? items.length : '(not array)');
for (const b of (Array.isArray(items) ? items : [items])) {
  console.log('\n--- block ---');
  for (const [k, v] of Object.entries(b)) {
    const s = typeof v === 'object' && v !== null ? JSON.stringify(v) : String(v);
    console.log(`  ${k}: ${s.length > 220 ? s.slice(0, 220) + ' …' : s}`);
  }
}
