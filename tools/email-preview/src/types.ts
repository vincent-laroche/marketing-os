export type JsonValue = null | boolean | number | string | JsonValue[] | { [key: string]: JsonValue };

export interface PreviewArgs {
  source: string;
  emailCode: string;
  campaign: string;
  commitSha: string;
  issue: number;
  pr: number;
  persona: string;
  states: string[];
  out: string;
  visibility: "private" | "public";
  workflowRun?: string;
  workflowAttempt?: string;
  workflowRevision?: string;
}

export interface PreviewSelection {
  email_code: string;
  campaign_key: string;
  source_path: string;
  persona: string;
  states: string[];
  preview_public: boolean;
}

export interface Provenance {
  schema_version: 1;
  email_code: string;
  source_path: string;
  source_commit_sha: string;
  related_issue: number;
  related_pr: number;
  persona: string;
  states: string[];
  compiler_version: string;
  source_sha256: string;
  rendered_sha256: string;
  outputs: ["rendered.html", "desktop.png", "mobile.png"];
  output_sha256: Record<"rendered.html" | "desktop.png" | "mobile.png", string>;
  repository: string;
  campaign_key: string;
  fixture_sha256: string;
  compiler_lock_sha256: string;
  generated_at: string;
  visibility: "private" | "public";
  issue_url: string;
  pr_url: string;
  workflow?: {run: string; attempt: string; revision: string};
  canonical_url?: string;
}
