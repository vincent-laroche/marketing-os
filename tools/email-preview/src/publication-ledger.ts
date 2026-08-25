import { z } from "zod";
import { validateProvenance } from "./provenance.js";
import type { Provenance } from "./types.js";

/** The two origins that may be approved for the public gallery. */
export const DEFAULT_PAGES_ORIGIN = "https://vincent-laroche.github.io/marketing-os";
export const APPROVED_CUSTOM_ORIGIN = "https://email-preview.hairsolutions.co";

const SHA256 = z.string().regex(/^[0-9a-f]{64}$/);
const SOURCE_SHA = z.string().regex(/^[0-9a-f]{40}$/);
const OUTPUT_DIGESTS = z.object({
  "rendered.html": SHA256,
  "desktop.png": SHA256,
  "mobile.png": SHA256,
}).strict();

export interface PublicationEntry {
  event: "published";
  email_code: string;
  campaign_key: string;
  source_path: string;
  source_commit_sha: string;
  canonical_issue: number;
  canonical_pr: number;
  persona: string;
  states: string[];
  output_sha256: {
    "rendered.html": string;
    "desktop.png": string;
    "mobile.png": string;
  };
  publication_timestamp: string;
  canonical_url: string;
  pages_deployment_id: string;
  workflow_run_id: string;
  workflow_attempt: string;
}

export interface WithdrawalEntry {
  event: "withdrawn";
  email_code: string;
  campaign_key: string;
  source_path: string;
  source_commit_sha: string;
  canonical_issue: number;
  canonical_pr: number;
  publication_timestamp: string;
  former_canonical_url: string;
  withdrawn_source_commit_sha: string;
  withdrawn_pages_deployment_id: string;
  pages_deployment_id: string;
  workflow_run_id: string;
  workflow_attempt: string;
  reason: "owner-requested" | "safety-rollback";
}

export type PublicationEvent = PublicationEntry | WithdrawalEntry;

export interface PublicationLedger {
  schema_version: 2;
  events: PublicationEvent[];
}

const publicationEntrySchema = z.object({
  event: z.literal("published"),
  email_code: z.string().regex(/^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$/),
  campaign_key: z.string().regex(/^campaign:[A-Za-z0-9_-]+$/),
  source_path: z.string().regex(/^shopify-messaging\/emails\/[0-9]+-[a-z0-9-]+\.html$/),
  source_commit_sha: SOURCE_SHA,
  canonical_issue: z.number().int().positive(),
  canonical_pr: z.number().int().positive(),
  persona: z.string().regex(/^[a-z0-9-]+$/),
  states: z.array(z.string().regex(/^[a-z0-9-]+$/)).min(1),
  output_sha256: OUTPUT_DIGESTS,
  publication_timestamp: z.string().datetime(),
  canonical_url: z.string().url(),
  pages_deployment_id: z.string().regex(/^[A-Za-z0-9._-]+$/),
  workflow_run_id: z.string().regex(/^[A-Za-z0-9._-]+$/),
  workflow_attempt: z.string().regex(/^[A-Za-z0-9._-]+$/),
}).strict();

const withdrawalEntrySchema = z.object({
  event: z.literal("withdrawn"),
  email_code: z.string().regex(/^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$/),
  campaign_key: z.string().regex(/^campaign:[A-Za-z0-9_-]+$/),
  source_path: z.string().regex(/^shopify-messaging\/emails\/[0-9]+-[a-z0-9-]+\.html$/),
  source_commit_sha: SOURCE_SHA,
  canonical_issue: z.number().int().positive(),
  canonical_pr: z.number().int().positive(),
  publication_timestamp: z.string().datetime(),
  former_canonical_url: z.string().url(),
  withdrawn_source_commit_sha: SOURCE_SHA,
  withdrawn_pages_deployment_id: z.string().regex(/^[A-Za-z0-9._-]+$/),
  pages_deployment_id: z.string().regex(/^[A-Za-z0-9._-]+$/),
  workflow_run_id: z.string().regex(/^[A-Za-z0-9._-]+$/),
  workflow_attempt: z.string().regex(/^[A-Za-z0-9._-]+$/),
  reason: z.enum(["owner-requested", "safety-rollback"]),
}).strict();

const ledgerSchema = z.object({
  schema_version: z.literal(2),
  events: z.array(z.discriminatedUnion("event", [publicationEntrySchema, withdrawalEntrySchema])),
}).strict();

export const emptyLedger = (): PublicationLedger => ({schema_version: 2, events: []});

export function isApprovedCanonicalUrl(raw: string, extraOrigins: readonly string[] = []): boolean {
  let url: URL;
  try { url = new URL(raw); } catch { return false; }
  if (url.protocol !== "https:" || url.username || url.password || url.search || url.hash) return false;
  const origins = [DEFAULT_PAGES_ORIGIN, APPROVED_CUSTOM_ORIGIN, ...extraOrigins]
    .map(origin => origin.replace(/\/$/, ""));
  return origins.some(origin => {
    try {
      const approved = new URL(origin);
      if (url.origin !== approved.origin) return false;
      const approvedPath = approved.pathname.replace(/\/$/, "");
      return approvedPath === "" || url.pathname === approvedPath || url.pathname.startsWith(`${approvedPath}/`);
    } catch { return false; }
  });
}

function assertEntryInvariants(entry: PublicationEntry, extraOrigins: readonly string[] = []): void {
  const parsed = publicationEntrySchema.safeParse(entry);
  if (!parsed.success) throw new Error("invalid publication ledger entry");
  if (!isApprovedCanonicalUrl(entry.canonical_url, extraOrigins)) throw new Error("canonical URL is not an approved HTTPS Pages origin");
  const canonical = new URL(entry.canonical_url);
  const expectedPath = canonical.origin === new URL(DEFAULT_PAGES_ORIGIN).origin
    ? `/marketing-os/${entry.email_code}/detail.html`
    : `/${entry.email_code}/detail.html`;
  if (canonical.pathname !== expectedPath) throw new Error("canonical URL does not identify the exact Email detail page");
  if (new Set(entry.states).size !== entry.states.length) throw new Error("publication states must be unique");
  const sortedStates = [...entry.states].sort();
  if (JSON.stringify(sortedStates) !== JSON.stringify(entry.states)) throw new Error("publication states must be deterministic");
}

function assertWithdrawalInvariants(entry: WithdrawalEntry, extraOrigins: readonly string[] = []): void {
  if (!withdrawalEntrySchema.safeParse(entry).success) throw new Error("invalid withdrawal ledger entry");
  if (!isApprovedCanonicalUrl(entry.former_canonical_url, extraOrigins)) throw new Error("former canonical URL is not an approved HTTPS Pages origin");
  const expected = new URL(entry.former_canonical_url).origin === new URL(DEFAULT_PAGES_ORIGIN).origin
    ? `/marketing-os/${entry.email_code}/detail.html`
    : `/${entry.email_code}/detail.html`;
  if (new URL(entry.former_canonical_url).pathname !== expected) throw new Error("former canonical URL does not identify the exact Email detail page");
}

export function activePublications(ledger: PublicationLedger): Map<string, PublicationEntry> {
  const active = new Map<string, PublicationEntry>();
  for (const event of ledger.events) {
    if (event.event === "published") active.set(event.email_code, event);
    else active.delete(event.email_code);
  }
  return active;
}

export function validateLedger(value: unknown, extraOrigins: readonly string[] = []): PublicationLedger {
  const parsed = ledgerSchema.safeParse(value);
  if (!parsed.success) throw new Error("invalid publication ledger");
  const ledger = parsed.data as PublicationLedger;
  const identities = new Set<string>();
  const active = new Map<string, PublicationEntry>();
  let priorTimestamp = Number.NEGATIVE_INFINITY;
  for (const entry of ledger.events) {
    const timestamp = Date.parse(entry.publication_timestamp);
    if (timestamp < priorTimestamp) throw new Error("publication ledger is not append-ordered");
    priorTimestamp = timestamp;
    if (entry.event === "published") assertEntryInvariants(entry, extraOrigins);
    else assertWithdrawalInvariants(entry, extraOrigins);
    const identity = `${entry.event}\u0000${entry.email_code}\u0000${entry.source_commit_sha}`;
    if (identities.has(identity)) throw new Error("duplicate Email+source SHA publication identity; historical entry mutation is forbidden");
    identities.add(identity);
    if (entry.event === "published") active.set(entry.email_code, entry);
    else {
      const current = active.get(entry.email_code);
      if (
        !current
        || current.canonical_url !== entry.former_canonical_url
        || current.source_commit_sha !== entry.withdrawn_source_commit_sha
        || current.pages_deployment_id !== entry.withdrawn_pages_deployment_id
      ) throw new Error("withdrawal requires the exact active public Email");
      active.delete(entry.email_code);
    }
  }
  return ledger;
}

export function appendPublication(ledger: PublicationLedger, candidate: PublicationEvent, extraOrigins: readonly string[] = []): PublicationLedger {
  const current = validateLedger(ledger, extraOrigins);
  if (candidate.event === "published") assertEntryInvariants(candidate, extraOrigins);
  else assertWithdrawalInvariants(candidate, extraOrigins);
  const identity = `${candidate.event}\u0000${candidate.email_code}\u0000${candidate.source_commit_sha}`;
  if (current.events.some(entry => `${entry.event}\u0000${entry.email_code}\u0000${entry.source_commit_sha}` === identity)) {
    throw new Error("duplicate Email+source SHA publication identity; historical entry mutation is forbidden");
  }
  const result: PublicationLedger = {schema_version: 2, events: [...current.events, structuredClone(candidate)]};
  return validateLedger(result, extraOrigins);
}

export interface PublicationEntryOptions {
  canonicalUrl: string;
  pagesDeploymentId: string;
  workflowRunId: string;
  workflowAttempt: string;
  publicationTimestamp?: string;
  extraOrigins?: readonly string[];
}

export interface WithdrawalEntryOptions {
  sourceCommitSha: string;
  canonicalPr: number;
  pagesDeploymentId: string;
  workflowRunId: string;
  workflowAttempt: string;
  reason: WithdrawalEntry["reason"];
  publicationTimestamp?: string;
  extraOrigins?: readonly string[];
}

export function createWithdrawalEntry(active: PublicationEntry, options: WithdrawalEntryOptions): WithdrawalEntry {
  const result: WithdrawalEntry = {
    event: "withdrawn",
    email_code: active.email_code,
    campaign_key: active.campaign_key,
    source_path: active.source_path,
    source_commit_sha: options.sourceCommitSha,
    canonical_issue: active.canonical_issue,
    canonical_pr: options.canonicalPr,
    publication_timestamp: options.publicationTimestamp ?? new Date().toISOString(),
    former_canonical_url: active.canonical_url,
    withdrawn_source_commit_sha: active.source_commit_sha,
    withdrawn_pages_deployment_id: active.pages_deployment_id,
    pages_deployment_id: options.pagesDeploymentId,
    workflow_run_id: options.workflowRunId,
    workflow_attempt: options.workflowAttempt,
    reason: options.reason,
  };
  assertWithdrawalInvariants(result, options.extraOrigins);
  return result;
}

/** Convert verified public provenance into the ledger's metadata-only record. */
export function createPublicationEntry(value: Provenance, options: PublicationEntryOptions): PublicationEntry {
  const provenance = validateProvenance(value);
  if (provenance.visibility !== "public") throw new Error("publication requires public provenance");
  if (!isApprovedCanonicalUrl(options.canonicalUrl, options.extraOrigins)) throw new Error("canonical URL is not an approved HTTPS Pages origin");
  if (provenance.output_sha256["rendered.html"] !== provenance.rendered_sha256) throw new Error("rendered output digest does not match provenance");
  const states = [...new Set(provenance.states)].sort();
  if (states.length !== provenance.states.length) throw new Error("publication states must be unique");
  const result: PublicationEntry = {
    event: "published",
    email_code: provenance.email_code,
    campaign_key: provenance.campaign_key,
    source_path: provenance.source_path,
    source_commit_sha: provenance.source_commit_sha,
    canonical_issue: provenance.related_issue,
    canonical_pr: provenance.related_pr,
    persona: provenance.persona,
    states,
    output_sha256: {
      "rendered.html": provenance.output_sha256["rendered.html"]!,
      "desktop.png": provenance.output_sha256["desktop.png"]!,
      "mobile.png": provenance.output_sha256["mobile.png"]!,
    },
    publication_timestamp: options.publicationTimestamp ?? new Date().toISOString(),
    canonical_url: options.canonicalUrl,
    pages_deployment_id: options.pagesDeploymentId,
    workflow_run_id: options.workflowRunId,
    workflow_attempt: options.workflowAttempt,
  };
  assertEntryInvariants(result, options.extraOrigins);
  return result;
}
