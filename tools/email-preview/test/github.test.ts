import assert from 'node:assert/strict';
import test from 'node:test';
import {
  buildLedgerPullRequestPlan,
  buildTemporaryEvidenceComment,
  replaceBoundedComment,
  resolveCanonicalEmailIssue,
  resolveMergedPullRequest,
  validatePublicReadBack,
} from '../src/github.js';

test('canonical Issue and merged pull request resolution fail closed on ambiguity', () => {
  assert.equal(resolveCanonicalEmailIssue([{key: 'email:CR-1', number: 101}]).number, 101);
  assert.throws(() => resolveCanonicalEmailIssue([]), /exactly one canonical Email Issue/i);
  assert.throws(() => resolveCanonicalEmailIssue([{key: 'email:CR-1', number: 101}, {key: 'email:CR-1', number: 102}]), /exactly one canonical Email Issue/i);
  assert.equal(resolveMergedPullRequest([{number: 202, merged: true, headSha: 'a'.repeat(40), mergeCommitSha: 'b'.repeat(40)}], 'a'.repeat(40)).number, 202);
  assert.throws(() => resolveMergedPullRequest([], 'a'.repeat(40)), /exactly one merged pull request/i);
  assert.throws(() => resolveMergedPullRequest([{number: 202, merged: false, headSha: 'a'.repeat(40)}], 'a'.repeat(40)), /exactly one merged pull request/i);
});

test('temporary evidence is marker-bounded, safe, and idempotently replaceable', () => {
  const first = buildTemporaryEvidenceComment({
    sourceSha: 'a'.repeat(40),
    successful: ['CR-1'],
    blocked: [{emailCode: 'BR-1', category: 'unresolved-variable'}],
    artifactUrl: 'https://github.com/vincent-laroche/email-marketing-ops/actions/runs/1/artifacts/2',
    expiresAt: '2026-08-26T12:00:00.000Z',
    reproductionCommand: 'gh workflow run email-preview-publish.yml -f email_code=CR-1 -f source_sha=' + 'a'.repeat(40),
  });
  assert.match(first, /<!-- email-preview:begin -->/);
  assert.match(first, /<!-- email-preview:end -->/);
  assert.match(first, /unresolved-variable/);
  assert.doesNotMatch(first, /fixture|rendered\.html|Alex|customer@example/i);
  const updated = replaceBoundedComment('before\n' + first + '\nafter', first.replaceAll('CR-1', 'CR-2'));
  assert.match(updated, /^before\n/);
  assert.match(updated, /CR-2/);
  assert.doesNotMatch(updated, /CR-1/);
  assert.match(updated, /\nafter$/);
});

test('read-back verifies status, source SHA, digests, and no Liquid', () => {
  const body = JSON.stringify({
    schema_version: 1,
    email_code: 'CR-1',
    source_path: 'shopify-messaging/emails/01-cr-1.html',
    source_commit_sha: 'a'.repeat(40),
    related_issue: 101,
    related_pr: 202,
    persona: 'normal-customer',
    states: ['missing-first-name'],
    compiler_version: '1.0.0',
    source_sha256: 'e'.repeat(64),
    rendered_sha256: 'b'.repeat(64),
    outputs: ['rendered.html', 'desktop.png', 'mobile.png'],
    output_sha256: {'rendered.html': 'b'.repeat(64), 'desktop.png': 'c'.repeat(64), 'mobile.png': 'd'.repeat(64)},
    repository: 'vincent-laroche/email-marketing-ops',
    campaign_key: 'campaign:J2',
    fixture_sha256: 'f'.repeat(64),
    compiler_lock_sha256: '1'.repeat(64),
    generated_at: '2026-08-25T12:00:00.000Z',
    visibility: 'public',
    issue_url: 'https://github.com/vincent-laroche/email-marketing-ops/issues/101',
    pr_url: 'https://github.com/vincent-laroche/email-marketing-ops/pull/202',
  });
  assert.doesNotThrow(() => validatePublicReadBack([{path: 'CR-1/provenance.json', status: 200, body}], {sourceSha: 'a'.repeat(40)}));
  assert.throws(() => validatePublicReadBack([{path: 'CR-1/rendered.html', status: 200, body: '{{ unresolved }}'}], {sourceSha: 'a'.repeat(40)}), /Liquid/i);
  assert.throws(() => validatePublicReadBack([{path: 'CR-1/provenance.json', status: 500, body}], {sourceSha: 'a'.repeat(40)}), /HTTP/i);
});

test('ledger PR plan is restricted to one automation branch and one ledger file', () => {
  const plan = buildLedgerPullRequestPlan({sourceSha: 'a'.repeat(40), entryCount: 1});
  assert.equal(plan.branch, 'automation/email-preview-publication-ledger');
  assert.deepEqual(plan.files, ['email-previews/publication-ledger.json']);
  assert.equal(plan.base, 'main');
  assert.match(plan.title, /publication ledger/i);
});
