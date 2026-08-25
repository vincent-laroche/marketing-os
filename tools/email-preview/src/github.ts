import { createHash } from "node:crypto";
import { validateProvenance } from "./provenance.js";
import type { PreviewSelection, Provenance } from "./types.js";

export const REVIEW_COMMENT_START = "<!-- email-preview:begin -->";
export const REVIEW_COMMENT_END = "<!-- email-preview:end -->";
const SHA = /^[0-9a-f]{40}$/;
const EMAIL_CODE = /^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$/;
const SAFE_CATEGORY = /^(build-note-comment|unresolved-variable|authoring-placeholder|render-failure|safety|unknown)$/;
const LIQUID = /\{\{|\{%/;
const PRIVATE_URL = /(?:actions\/runs\/\d+\/artifacts\/\d+|actions\/artifacts\/\d+|artifact-url|actions\/download-artifact)/i;
const UNSAFE_URL = /(?:javascript:|vbscript:|data:|customer[_-]?id=|token=|checkout\.shopify\.com)/i;
const UNSAFE_UNSUBSCRIBE_URL = /(?:https?:\/\/|\/\/|(?:href|src|action)\s*=\s*["']|url\(\s*["']?)[^"'\s)>]*unsubscribe/i;

export function containsUnsafePublicUrl(value: string): boolean {
  return UNSAFE_URL.test(value) || UNSAFE_UNSUBSCRIBE_URL.test(value);
}

export interface CanonicalIssueCandidate {
  key: string;
  number: number;
}

export interface PullRequestCandidate {
  number: number;
  merged: boolean;
  headSha?: string;
  mergeCommitSha?: string;
  sourceShas?: string[];
}

export function assertExactSourceSha(value: string): string {
  if (!SHA.test(value)) throw new Error("exact 40-character source SHA required");
  return value;
}

export function assertCanonicalEmailCode(value: string): string {
  if (!EMAIL_CODE.test(value)) throw new Error("canonical Email code required");
  return value;
}

export function assertSafeWorkflowInput(value: string, label: string): string {
  if (!value || /[\u0000-\u001f\u007f]/.test(value) || /[;&|\x60$()<>\n\r]/.test(value)) throw new Error("unsafe " + label);
  return value;
}

export function requirePublicSelection(config: {selections: PreviewSelection[]}, emailCode: string): PreviewSelection {
  assertCanonicalEmailCode(emailCode);
  const matches = config.selections.filter(selection => selection.email_code === emailCode);
  if (matches.length !== 1) throw new Error("exactly one canonical Email selection is required");
  if (!matches[0]!.preview_public) throw new Error("the exact Email selection is not preview_public");
  return matches[0]!;
}

export function resolveCanonicalEmailIssue(candidates: CanonicalIssueCandidate[]): CanonicalIssueCandidate {
  const matches = candidates.filter(candidate => candidate.key.startsWith("email:") && Number.isInteger(candidate.number) && candidate.number > 0);
  if (matches.length !== 1) throw new Error("exactly one canonical Email Issue is required");
  return matches[0]!;
}

export function resolveMergedPullRequest(candidates: PullRequestCandidate[], sourceSha: string): PullRequestCandidate {
  assertExactSourceSha(sourceSha);
  const matches = candidates.filter(candidate => candidate.merged && (
    candidate.headSha === sourceSha
    || candidate.mergeCommitSha === sourceSha
    || candidate.sourceShas?.includes(sourceSha)
  ));
  if (matches.length !== 1) throw new Error("exactly one merged pull request is required");
  return matches[0]!;
}

export interface TemporaryEvidenceInput {
  sourceSha: string;
  successful: string[];
  blocked: Array<{emailCode: string; category: string}>;
  artifactUrl: string;
  expiresAt: string;
  reproductionCommand: string;
}

function assertArtifactUrl(value: string): void {
  let url: URL;
  try { url = new URL(value); } catch { throw new Error("private artifact URL is invalid"); }
  if (url.protocol !== "https:" || !["github.com", "api.github.com"].includes(url.hostname) || !PRIVATE_URL.test(value)) throw new Error("private artifact URL is invalid");
}

function safeCodeList(values: string[]): string {
  return values.map(assertCanonicalEmailCode).sort((a, b) => a.localeCompare(b, undefined, {numeric: true})).join(", ") || "none";
}

export function buildTemporaryEvidenceComment(input: TemporaryEvidenceInput): string {
  assertExactSourceSha(input.sourceSha);
  assertArtifactUrl(input.artifactUrl);
  if (Number.isNaN(Date.parse(input.expiresAt))) throw new Error("artifact expiry is invalid");
  assertSafeWorkflowInput(input.reproductionCommand, "reproduction command");
  const blocked = input.blocked.map(item => {
    assertCanonicalEmailCode(item.emailCode);
    if (!SAFE_CATEGORY.test(item.category)) throw new Error("unsafe preview blocker category");
    return item.emailCode + " (" + item.category + ")";
  }).sort((a, b) => a.localeCompare(b, undefined, {numeric: true})).join(", ") || "none";
  return [
    REVIEW_COMMENT_START,
    "### Email preview review",
    "",
    "- Source SHA: [" + input.sourceSha + "]",
    "- Successful: " + safeCodeList(input.successful),
    "- Blocked: " + blocked,
    "- Private artifact: " + input.artifactUrl,
    "- Artifact expires at: [" + input.expiresAt + "]",
    "- Reproduce this revision: [" + input.reproductionCommand + "]",
    "",
    REVIEW_COMMENT_END,
  ].join("\n");
}

export function replaceBoundedComment(existing: string, replacement: string): string {
  if (!replacement.includes(REVIEW_COMMENT_START) || !replacement.includes(REVIEW_COMMENT_END)) throw new Error("replacement is missing comment markers");
  const pattern = new RegExp(REVIEW_COMMENT_START + "[\\s\\S]*?" + REVIEW_COMMENT_END, "g");
  const matches = existing.match(pattern) ?? [];
  if (matches.length > 1) throw new Error("multiple bounded preview comments found");
  if (matches.length === 1) return existing.replace(pattern, replacement);
  return existing.trimEnd() + (existing.trim() ? "\n\n" : "") + replacement + "\n";
}

export interface PublicReadBack {
  path: string;
  status: number;
  body: string | Buffer;
}

export interface ReadBackExpectation {
  sourceSha: string;
  emailCode: string;
  expectedDigests?: Record<string, string>;
}

export function validatePublicReadBack(files: PublicReadBack[], expectation: ReadBackExpectation): void {
  assertExactSourceSha(expectation.sourceSha);
  assertCanonicalEmailCode(expectation.emailCode);
  if (!files.length) throw new Error("public read-back returned no files");
  for (const file of files) {
    if (!/^2\d\d$/.test(String(file.status))) throw new Error("public read-back HTTP status failed");
    const body = Buffer.isBuffer(file.body) ? file.body : Buffer.from(file.body);
    if (PRIVATE_URL.test(body.toString("utf8")) || containsUnsafePublicUrl(body.toString("utf8"))) throw new Error("public read-back contains an unsafe URL");
    if (file.path.endsWith(".html") && LIQUID.test(body.toString("utf8"))) throw new Error("public read-back contains Liquid");
    if (file.path.endsWith("provenance.json")) {
      let value: Provenance;
      try { value = validateProvenance(JSON.parse(body.toString("utf8"))); } catch { throw new Error("public read-back provenance is invalid"); }
      if (value.visibility !== "public" || value.source_commit_sha !== expectation.sourceSha) throw new Error("public read-back source SHA or visibility mismatch");
      if (expectation.expectedDigests && file.path === `${expectation.emailCode}/provenance.json`) {
        for (const [name, digest] of Object.entries(expectation.expectedDigests)) {
          if (value.output_sha256[name as keyof typeof value.output_sha256] !== digest) throw new Error("public read-back output digest mismatch");
        }
      }
    }
  }
}

export interface LedgerPullRequestPlan {
  branch: "automation/email-preview-publication-ledger";
  base: "main";
  files: ["email-previews/publication-ledger.json"];
  title: string;
  body: string;
}

export function buildLedgerPullRequestPlan(input: {sourceSha: string; entryCount: number}): LedgerPullRequestPlan {
  assertExactSourceSha(input.sourceSha);
  if (!Number.isInteger(input.entryCount) || input.entryCount < 0) throw new Error("invalid publication entry count");
  return {
    branch: "automation/email-preview-publication-ledger",
    base: "main",
    files: ["email-previews/publication-ledger.json"],
    title: "chore(preview): record verified public publication ledger",
    body: "Append-only publication ledger update for source SHA [" + input.sourceSha + "] with " + input.entryCount + " verified publication(s).",
  };
}

export function sha256Bytes(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}
