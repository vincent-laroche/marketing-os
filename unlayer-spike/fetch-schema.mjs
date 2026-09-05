import { writeFileSync } from 'node:fs';
import { loadEnv } from './env.mjs';
const { UNLAYER_PAT_TOKEN: TOKEN } = loadEnv(['UNLAYER_PAT_TOKEN']);
const res = await fetch('https://api.unlayer.com/v3/templates/schema', {
  headers: { Authorization: `Bearer ${TOKEN}`, Accept: 'application/json' },
});
const body = await res.json();
writeFileSync('design-schema.json', JSON.stringify(body, null, 2));
console.log('status', res.status, '| bytes', JSON.stringify(body).length);
console.log('top-level keys:', Object.keys(body).join(', '));
console.log('required:', JSON.stringify(body.required));
console.log('properties:', Object.keys(body.properties || {}).join(', '));
console.log('$defs count:', Object.keys(body.$defs || {}).length);
console.log('$defs:', Object.keys(body.$defs || {}).slice(0, 40).join(', '));
