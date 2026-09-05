// Reads ~/.env directly. The canonical secrets file is ~/.env (AGENTS-SECRETS-MASTER.md);
// this spike never keeps its own copy of a credential and never logs a value.
import { readFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';

export function loadEnv(keys) {
  const out = {};
  let raw = '';
  try {
    raw = readFileSync(join(homedir(), '.env'), 'utf8');
  } catch (error) {
    throw new Error(`Could not read ~/.env: ${error.message}`);
  }
  for (const line of raw.split('\n')) {
    const m = /^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$/.exec(line);
    if (!m) continue;
    const [, k, v] = m;
    if (!keys.includes(k)) continue;
    out[k] = v.trim().replace(/^(['"])(.*)\1$/, '$2');
  }
  return out;
}
