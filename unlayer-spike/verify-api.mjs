// Phase 1 gate: confirm the Cloud API v3 endpoints the build depends on actually
// work with this account's PAT. Prints statuses and shapes only — never the token.
import { loadEnv } from './env.mjs';

const { UNLAYER_PAT_TOKEN: TOKEN } = loadEnv(['UNLAYER_PAT_TOKEN']);
if (!TOKEN) { console.error('UNLAYER_PAT_TOKEN not found in ~/.env'); process.exit(1); }

const BASE = 'https://api.unlayer.com/v3';
const PROJECT = '289096';
const headers = { Authorization: `Bearer ${TOKEN}`, Accept: 'application/json' };

const checks = [
  ['GET', '/me/subscription', null],
  ['GET', `/projects/${PROJECT}`, null],
  ['GET', `/blocks?projectId=${PROJECT}`, null],
  ['GET', '/templates/schema', null],
  ['GET', `/templates?projectId=${PROJECT}`, null],
];

const shape = (v, d = 0) => {
  if (v === null) return 'null';
  if (Array.isArray(v)) return `[${v.length}]${v.length && d < 2 ? ` of ${shape(v[0], d + 1)}` : ''}`;
  if (typeof v === 'object') {
    const k = Object.keys(v);
    return d < 2 ? `{${k.slice(0, 12).join(', ')}${k.length > 12 ? ', …' : ''}}` : `{${k.length} keys}`;
  }
  return typeof v;
};

let failures = 0;
for (const [method, path] of checks) {
  try {
    const res = await fetch(BASE + path, { method, headers });
    const text = await res.text();
    let body = null;
    try { body = JSON.parse(text); } catch { /* non-JSON */ }
    const ok = res.status >= 200 && res.status < 300;
    if (!ok) failures++;
    console.log(`${ok ? 'OK  ' : 'FAIL'} ${res.status}  ${method} ${path}`);
    console.log(`      ${body ? shape(body) : text.slice(0, 160)}`);
  } catch (error) {
    failures++;
    console.log(`FAIL  ---  ${method} ${path}\n      ${error.message}`);
  }
}
console.log(`\n${failures ? `${failures} endpoint(s) failed` : 'all endpoints reachable'}`);
process.exit(failures ? 1 : 0);
