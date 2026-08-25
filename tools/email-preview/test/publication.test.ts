import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { canonicalEmailUrl, parsePublicationArgs } from '../src/publication.js';

test('canonical public URLs are HTTPS and scoped to the Pages origin', () => {
  assert.equal(canonicalEmailUrl('https://email-preview.hairsolutions.co/', 'CR-1'), 'https://email-preview.hairsolutions.co/CR-1/detail.html');
  assert.throws(() => canonicalEmailUrl('http://email-preview.hairsolutions.co/', 'CR-1'), /HTTPS/i);
  assert.throws(() => canonicalEmailUrl('https://evil.example/', 'CR-1'), /approved/i);
});

test('publication command input accepts only controlled values', () => {
  assert.throws(() => parsePublicationArgs(['node', 'publication.ts', 'candidate', '--site', 'x']), /email-code|required/i);
  const args = parsePublicationArgs(['node', 'publication.ts', 'candidate', '--site', 'site', '--email-code', 'CR-1', '--source-sha', 'a'.repeat(40), '--canonical-base', 'https://email-preview.hairsolutions.co/', '--pages-deployment-id', 'd1', '--workflow-run-id', 'r1', '--workflow-attempt', '1', '--out', 'candidate.json']);
  assert.equal(args.command, 'candidate');
  assert.equal(args.emailCode, 'CR-1');
});

test('static-site validation rejects source, fixture, log, and private artifact leakage', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'email-preview-publication-'));
  try {
    await fs.mkdir(path.join(root, 'CR-1'), {recursive: true});
    await fs.writeFile(path.join(root, 'index.html'), '<meta name=\"robots\" content=\"noindex,nofollow,noarchive\">');
    await fs.writeFile(path.join(root, 'robots.txt'), 'User-agent: *\nDisallow: /\n');
    await fs.writeFile(path.join(root, 'CR-1', 'rendered.html'), 'https://github.com/x/y/actions/runs/1/artifacts/2');
    await assert.rejects(() => import('../src/publication.js').then(module => module.validateStaticSite(root, 'CR-1', 'a'.repeat(40))), /private artifact|unsafe/i);
  } finally {
    await fs.rm(root, {recursive: true, force: true});
  }
});
