import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { assertSoleActiveWithdrawal, assertWithdrawalPullRequest, assertWithdrawalSelection, canonicalEmailUrl, nextGitHubPage, parsePublicationArgs, resolveLocalSiteTarget, validateGallery } from '../src/publication.js';

test('local site link resolution maps the root form action to the gallery index', () => {
  assert.equal(resolveLocalSiteTarget('./', 'index.html'), 'index.html');
  assert.equal(resolveLocalSiteTarget('../index.html', 'CR-1/detail.html'), 'index.html');
  assert.equal(resolveLocalSiteTarget('rendered.html', 'CR-1/detail.html'), 'CR-1/rendered.html');
});

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

test('withdrawal candidate input requires exact rollback identity and an approved reason', () => {
  const preflight = parsePublicationArgs([
    'node', 'publication.ts', 'withdraw-preflight',
    '--ledger', 'email-previews/publication-ledger.json',
    '--email-code', 'CR-1',
    '--source-sha', 'b'.repeat(40),
    '--canonical-pr', '83',
  ]);
  assert.equal(preflight.command, 'withdraw-preflight');
  assert.equal(preflight.canonicalPr, 83);
  const args = parsePublicationArgs([
    'node', 'publication.ts', 'withdraw-candidate',
    '--ledger', 'email-previews/publication-ledger.json',
    '--email-code', 'CR-1',
    '--source-sha', 'b'.repeat(40),
    '--canonical-pr', '83',
    '--pages-deployment-id', 'pages-disabled-123',
    '--workflow-run-id', 'manual-83',
    '--workflow-attempt', '1',
    '--reason', 'safety-rollback',
    '--out', 'withdrawal.json',
  ]);
  assert.equal(args.command, 'withdraw-candidate');
  assert.equal(args.canonicalPr, 83);
  assert.equal(args.reason, 'safety-rollback');
  assert.throws(() => parsePublicationArgs([
    'node', 'publication.ts', 'withdraw-candidate',
    '--ledger', 'email-previews/publication-ledger.json',
    '--email-code', 'CR-1',
    '--source-sha', 'b'.repeat(40),
    '--canonical-pr', '83',
    '--pages-deployment-id', 'pages-disabled-123',
    '--workflow-run-id', 'manual-83',
    '--workflow-attempt', '1',
    '--reason', 'convenience',
    '--out', 'withdrawal.json',
  ]), /approved withdrawal reason/i);
});

test('withdrawal selection must be false and match the exact active publication', () => {
  const active = {email_code: 'CR-1', campaign_key: 'campaign:J2', source_path: 'shopify-messaging/emails/01-cr-1.html'};
  assert.doesNotThrow(() => assertWithdrawalSelection({selections: [{...active, preview_public: false}]}, active));
  assert.throws(() => assertWithdrawalSelection({selections: [{...active, preview_public: true}]}, active), /preview_public false/i);
  assert.throws(() => assertWithdrawalSelection({selections: [{...active, source_path: 'shopify-messaging/emails/02-cr-2.html', preview_public: false}]}, active), /exact active/i);
});

test('Pages-disable withdrawal is limited to the sole active Email', () => {
  assert.doesNotThrow(() => assertSoleActiveWithdrawal(new Map([['CR-1', {}]]), 'CR-1'));
  assert.throws(() => assertSoleActiveWithdrawal(new Map([['CR-1', {}], ['CR-2', {}]]), 'CR-1'), /sole active/i);
  assert.throws(() => assertSoleActiveWithdrawal(new Map(), 'CR-1'), /sole active/i);
});

test('withdrawal PR evidence binds one merged PR to the exact rollback revision', () => {
  const sha = 'b'.repeat(40);
  assert.doesNotThrow(() => assertWithdrawalPullRequest([{number: 83, merged_at: '2026-08-25T12:00:00Z', head: {sha}, merge_commit_sha: 'c'.repeat(40)}], sha, 83));
  assert.throws(() => assertWithdrawalPullRequest([{number: 83, merged_at: null, head: {sha}, merge_commit_sha: sha}], sha, 83), /unique merged/i);
  assert.throws(() => assertWithdrawalPullRequest([{number: 84, merged_at: '2026-08-25T12:00:00Z', head: {sha}}], sha, 83), /does not match/i);
  assert.throws(() => assertWithdrawalPullRequest([
    {number: 83, merged_at: '2026-08-25T12:00:00Z', head: {sha}},
    {number: 84, merged_at: '2026-08-25T12:01:00Z', merge_commit_sha: sha},
  ], sha, 83), /unique merged/i);
});

test('withdrawal PR pagination follows only the GitHub next link', () => {
  const next = 'https://api.github.com/repositories/123/commits/' + 'b'.repeat(40) + '/pulls?page=2';
  assert.equal(nextGitHubPage(`<${next}>; rel="next", <${next.replace('page=2', 'page=4')}>; rel="last"`), next);
  assert.equal(nextGitHubPage(`<${next}>; rel="prev"`), undefined);
  assert.throws(() => nextGitHubPage('<https://evil.example/page=2>; rel="next"'), /pagination URL is invalid/i);
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

test('site-wide validation accepts a safe zero-public-email gallery', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'email-preview-zero-gallery-'));
  try {
    await fs.writeFile(path.join(root, 'index.html'), '<meta http-equiv="Content-Security-Policy" content="default-src none"><meta name="robots" content="noindex,nofollow,noarchive"><form action="./"></form>');
    await fs.writeFile(path.join(root, 'robots.txt'), 'User-agent: *\nDisallow: /\n');
    await assert.doesNotReject(() => validateGallery(root));
  } finally {
    await fs.rm(root, {recursive: true, force: true});
  }
});
