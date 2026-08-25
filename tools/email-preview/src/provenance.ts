import { createHash } from "node:crypto";
import type { PreviewArgs, Provenance } from "./types.js";

export const sha256 = (value: string | Buffer) => createHash("sha256").update(value).digest("hex");

export function provenance(args: PreviewArgs, source: string, rendered: string): Provenance {
  if (!/^[0-9a-f]{40}$/.test(args.commitSha)) throw new Error("exact 40-character source commit SHA required");
  return {
    schema_version: 1,
    email_code: args.emailCode,
    source_path: args.source,
    source_commit_sha: args.commitSha,
    related_issue: args.issue,
    related_pr: args.pr ?? null,
    persona: args.persona,
    state: args.state,
    compiler_version: "1.0.0",
    source_sha256: sha256(source),
    rendered_sha256: sha256(rendered),
    outputs: ["rendered.html", "desktop.png", "mobile.png"]
  };
}
