export type JsonValue = null | boolean | number | string | JsonValue[] | { [key: string]: JsonValue };

export interface PreviewArgs {
  source: string;
  emailCode: string;
  commitSha: string;
  issue: number;
  pr?: number;
  persona: string;
  state: string;
  out: string;
}

export interface Provenance {
  schema_version: 1;
  email_code: string;
  source_path: string;
  source_commit_sha: string;
  related_issue: number;
  related_pr: number | null;
  persona: string;
  state: string;
  compiler_version: string;
  source_sha256: string;
  rendered_sha256: string;
  outputs: ["rendered.html", "desktop.png", "mobile.png"];
}
