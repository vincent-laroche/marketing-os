import assert from "node:assert/strict";
import test from "node:test";
import {
  appendPublication,
  activePublications,
  createWithdrawalEntry,
  createPublicationEntry,
  emptyLedger,
  validateLedger,
  type PublicationEntry,
} from "../src/publication-ledger.js";

const digest = "a".repeat(64);
const sourceSha = "b".repeat(40);

function entry(overrides: Partial<PublicationEntry> = {}): PublicationEntry {
  return {
    email_code: "CR-1",
    event: "published",
    campaign_key: "campaign:J2",
    source_path: "shopify-messaging/emails/01-cr-1.html",
    source_commit_sha: sourceSha,
    canonical_issue: 101,
    canonical_pr: 202,
    persona: "normal-customer",
    states: ["missing-first-name"],
    output_sha256: {"rendered.html": digest, "desktop.png": digest, "mobile.png": digest},
    publication_timestamp: "2026-08-25T12:00:00.000Z",
    canonical_url: "https://email-preview.hairsolutions.co/CR-1/detail.html",
    pages_deployment_id: "pages-123",
    workflow_run_id: "456",
    workflow_attempt: "1",
    ...overrides,
  };
}

test("empty ledger validates and append is deterministic", () => {
  const first = appendPublication(emptyLedger(), entry());
  assert.equal(first.events.length, 1);
  assert.deepEqual(appendPublication(emptyLedger(), entry()), first);
  assert.doesNotThrow(() => validateLedger(first));
});

test("ledger rejects duplicate Email plus source SHA identities and mutated history", () => {
  const first = appendPublication(emptyLedger(), entry());
  assert.throws(() => appendPublication(first, entry()), /duplicate Email.*source SHA/i);
  assert.throws(() => validateLedger({schema_version: 2, events: [entry(), entry({publication_timestamp: "2026-08-25T12:01:00.000Z"})]}), /duplicate Email.*source SHA/i);
});

test("ledger rejects malformed digests, non-HTTPS URLs, unapproved origins, and noncanonical paths", () => {
  for (const candidate of [
    entry({output_sha256: {"rendered.html": "bad", "desktop.png": digest, "mobile.png": digest}}),
    entry({canonical_url: "http://email-preview.hairsolutions.co/CR-1/"}),
    entry({canonical_url: "https://evil.example/CR-1/"}),
    entry({canonical_url: "https://email-preview.hairsolutions.co/CR-1/"}),
    entry({canonical_url: "https://email-preview.hairsolutions.co/other/detail.html"}),
  ]) assert.throws(() => validateLedger({schema_version: 2, events: [candidate]}));
});

test("publish, withdraw, and republish reduce to the latest active state", () => {
  const published = entry();
  const withdrawn = createWithdrawalEntry(published, {
    sourceCommitSha: "c".repeat(40), canonicalPr: 203, pagesDeploymentId: "pages-124",
    workflowRunId: "457", workflowAttempt: "1", reason: "owner-requested",
    publicationTimestamp: "2026-08-25T13:00:00.000Z",
  });
  const afterWithdrawal = appendPublication(appendPublication(emptyLedger(), published), withdrawn);
  assert.equal(activePublications(afterWithdrawal).size, 0);
  assert.throws(() => appendPublication(emptyLedger(), withdrawn), /exact active public Email/i);
  const republished = entry({source_commit_sha: "d".repeat(40), canonical_pr: 204, publication_timestamp: "2026-08-25T14:00:00.000Z"});
  assert.equal(activePublications(appendPublication(afterWithdrawal, republished)).get("CR-1")?.canonical_pr, 204);
});

test("publication entry binds only public provenance and approved deployment identity", () => {
  const provenance = {
    schema_version: 1 as const,
    email_code: "CR-1",
    source_path: "shopify-messaging/emails/01-cr-1.html",
    source_commit_sha: sourceSha,
    related_issue: 101,
    related_pr: 202,
    persona: "normal-customer",
    states: ["missing-first-name"],
    compiler_version: "1.0.0",
    source_sha256: digest,
    rendered_sha256: digest,
    outputs: ["rendered.html", "desktop.png", "mobile.png"] as ["rendered.html", "desktop.png", "mobile.png"],
    output_sha256: {"rendered.html": digest, "desktop.png": digest, "mobile.png": digest},
    repository: "vincent-laroche/marketing-os" as const,
    campaign_key: "campaign:J2",
    fixture_sha256: digest,
    compiler_lock_sha256: digest,
    generated_at: "2026-08-25T12:00:00.000Z",
    visibility: "public" as const,
    issue_url: "https://github.com/vincent-laroche/marketing-os/issues/101",
    pr_url: "https://github.com/vincent-laroche/marketing-os/pull/202",
  };
  const created = createPublicationEntry(provenance, {
    canonicalUrl: "https://email-preview.hairsolutions.co/CR-1/detail.html",
    pagesDeploymentId: "pages-123",
    workflowRunId: "456",
    workflowAttempt: "1",
    publicationTimestamp: "2026-08-25T12:00:00.000Z",
  });
  assert.equal(created.email_code, "CR-1");
  assert.equal(created.canonical_issue, 101);
  assert.throws(() => createPublicationEntry({...provenance, visibility: "private"}, {
    canonicalUrl: "https://email-preview.hairsolutions.co/CR-1/detail.html",
    pagesDeploymentId: "pages-123",
    workflowRunId: "456",
    workflowAttempt: "1",
  }), /public provenance/i);
});
