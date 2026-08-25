import { createHash } from "node:crypto";
import { z } from "zod";
import type { PreviewArgs, Provenance } from "./types.js";

export const sha256 = (value: string | Buffer) => createHash("sha256").update(value).digest("hex");

export function provenance(args: PreviewArgs, source: string, rendered: string, extras: Pick<Provenance, "output_sha256" | "campaign_key" | "fixture_sha256" | "compiler_lock_sha256" | "generated_at" | "visibility"> & {identity: Record<string, unknown>}): Provenance {
  if (!/^[0-9a-f]{40}$/.test(args.commitSha)) throw new Error("exact 40-character source commit SHA required");
  if (!Number.isInteger(args.issue) || args.issue < 1) throw new Error("positive canonical Issue required");
  if (!Number.isInteger(args.pr) || args.pr < 1) throw new Error("positive PR required");
  return {
    schema_version: 1,
    email_code: args.emailCode,
    source_path: args.source,
    source_commit_sha: args.commitSha,
    related_issue: args.issue,
    related_pr: args.pr,
    persona: args.persona,
    states: args.states,
    compiler_version: "1.0.0",
    source_sha256: sha256(source),
    rendered_sha256: sha256(rendered),
    outputs: ["rendered.html", "desktop.png", "mobile.png"],
    output_sha256: extras.output_sha256,
    repository: "vincent-laroche/email-marketing-ops",
    campaign_key: extras.campaign_key,
    fixture_sha256: extras.fixture_sha256,
    compiler_lock_sha256: extras.compiler_lock_sha256,
    generated_at: extras.generated_at,
    visibility: extras.visibility,
    issue_url: `https://github.com/vincent-laroche/email-marketing-ops/issues/${args.issue}`,
    pr_url: `https://github.com/vincent-laroche/email-marketing-ops/pull/${args.pr}`,
    workflow: args.workflowRun && args.workflowAttempt && args.workflowRevision ? {run: args.workflowRun, attempt: args.workflowAttempt, revision: args.workflowRevision} : undefined
  };
}

const provenanceSchema = z.object({
  schema_version: z.literal(1), email_code: z.string().min(1), source_path: z.string().min(1), source_commit_sha: z.string().regex(/^[0-9a-f]{40}$/), related_issue: z.number().int().positive(), related_pr: z.number().int().positive(), persona: z.string().min(1), states: z.array(z.string()).min(1), compiler_version: z.string().min(1), source_sha256: z.string().regex(/^[0-9a-f]{64}$/), rendered_sha256: z.string().regex(/^[0-9a-f]{64}$/), outputs: z.tuple([z.literal("rendered.html"), z.literal("desktop.png"), z.literal("mobile.png")]), output_sha256: z.record(z.string(), z.string().regex(/^[0-9a-f]{64}$/)), repository: z.literal("vincent-laroche/email-marketing-ops"), campaign_key: z.string().regex(/^campaign:/), fixture_sha256: z.string().regex(/^[0-9a-f]{64}$/), compiler_lock_sha256: z.string().regex(/^[0-9a-f]{64}$/), generated_at: z.string().datetime(), visibility: z.enum(["private", "public"]), issue_url: z.string().url(), pr_url: z.string().url(), workflow: z.object({run: z.string(), attempt: z.string(), revision: z.string()}).optional()
}).strict();
export function validateProvenance(value: unknown): Provenance { return provenanceSchema.parse(value) as Provenance; }
