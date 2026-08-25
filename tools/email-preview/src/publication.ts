import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";
import { activePublications, appendPublication, createPublicationEntry, createWithdrawalEntry, isApprovedCanonicalUrl, validateLedger, type PublicationEntry, type PublicationEvent } from "./publication-ledger.js";
import { assertExactSourceSha, assertCanonicalEmailCode, containsUnsafePublicUrl, sha256Bytes, validatePublicReadBack, type PublicReadBack } from "./github.js";
import { loadConfig, repositoryRoot } from "./config.js";
import type { PreviewSelection } from "./types.js";
import { validateProvenance } from "./provenance.js";
import type { Provenance } from "./types.js";

export interface PublicationCliArgs {
  command: "candidate" | "withdraw-preflight" | "withdraw-candidate" | "append" | "validate-gallery" | "validate-site" | "read-back";
  site?: string;
  emailCode?: string;
  sourceSha?: string;
  canonicalBase?: string;
  pagesDeploymentId?: string;
  workflowRunId?: string;
  workflowAttempt?: string;
  publicationTimestamp?: string;
  out?: string;
  ledger?: string;
  candidate?: string;
  pageUrl?: string;
  canonicalPr?: number;
  reason?: "owner-requested" | "safety-rollback";
}

const FLAGS = new Set(["site", "email-code", "source-sha", "canonical-base", "pages-deployment-id", "workflow-run-id", "workflow-attempt", "publication-timestamp", "out", "ledger", "candidate", "page-url", "canonical-pr", "reason"]);

function getRequired(values: Record<string, string>, name: string): string {
  const value = values[name];
  if (!value || value.startsWith("--")) throw new Error("--" + name + " is required");
  return value;
}

function parsePositiveSha(values: Record<string, string>): string {
  return assertExactSourceSha(getRequired(values, "source-sha"));
}

export function parsePublicationArgs(argv: string[]): PublicationCliArgs {
  const command = argv[2] as PublicationCliArgs["command"] | undefined;
  if (!command || !["candidate", "withdraw-preflight", "withdraw-candidate", "append", "validate-gallery", "validate-site", "read-back"].includes(command)) throw new Error("publication command is required");
  const values: Record<string, string> = {};
  for (let index = 3; index < argv.length; index += 2) {
    const token = argv[index];
    if (!token?.startsWith("--") || !FLAGS.has(token.slice(2))) throw new Error("unknown publication option");
    const name = token.slice(2);
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) throw new Error("--" + name + " is required");
    if (name in values) throw new Error("duplicate publication option");
    values[name] = value;
  }
  const result: PublicationCliArgs = {command};
  if (command === "candidate") {
    result.site = getRequired(values, "site");
    result.emailCode = assertCanonicalEmailCode(getRequired(values, "email-code"));
    result.sourceSha = parsePositiveSha(values);
    result.canonicalBase = getRequired(values, "canonical-base");
    result.pagesDeploymentId = getRequired(values, "pages-deployment-id");
    result.workflowRunId = getRequired(values, "workflow-run-id");
    result.workflowAttempt = getRequired(values, "workflow-attempt");
    result.publicationTimestamp = values["publication-timestamp"] || new Date().toISOString();
    result.out = getRequired(values, "out");
  } else if (command === "withdraw-preflight" || command === "withdraw-candidate") {
    result.ledger = getRequired(values, "ledger");
    result.emailCode = assertCanonicalEmailCode(getRequired(values, "email-code"));
    result.sourceSha = parsePositiveSha(values);
    result.canonicalPr = Number.parseInt(getRequired(values, "canonical-pr"), 10);
    if (!Number.isInteger(result.canonicalPr) || result.canonicalPr < 1) throw new Error("positive --canonical-pr is required");
    if (command === "withdraw-candidate") {
      result.pagesDeploymentId = getRequired(values, "pages-deployment-id");
      result.workflowRunId = getRequired(values, "workflow-run-id");
      result.workflowAttempt = getRequired(values, "workflow-attempt");
      result.publicationTimestamp = values["publication-timestamp"] || new Date().toISOString();
      const reason = getRequired(values, "reason");
      if (reason !== "owner-requested" && reason !== "safety-rollback") throw new Error("approved withdrawal reason is required");
      result.reason = reason;
      result.out = getRequired(values, "out");
    }
  } else if (command === "append") {
    result.ledger = getRequired(values, "ledger");
    result.candidate = getRequired(values, "candidate");
  } else if (command === "validate-gallery") {
    result.site = getRequired(values, "site");
  } else if (command === "validate-site") {
    result.site = getRequired(values, "site");
    result.emailCode = assertCanonicalEmailCode(getRequired(values, "email-code"));
    result.sourceSha = parsePositiveSha(values);
  } else {
    result.site = getRequired(values, "site");
    result.emailCode = assertCanonicalEmailCode(getRequired(values, "email-code"));
    result.sourceSha = parsePositiveSha(values);
    result.pageUrl = getRequired(values, "page-url");
  }
  return result;
}

export function canonicalEmailUrl(base: string, emailCode: string): string {
  assertCanonicalEmailCode(emailCode);
  let url: URL;
  try { url = new URL(base); } catch { throw new Error("canonical base URL is invalid"); }
  if (url.protocol !== "https:" || url.search || url.hash || !isApprovedCanonicalUrl(url.toString())) throw new Error("canonical base URL is not an approved HTTPS Pages origin");
  const prefix = url.toString().replace(/\/?$/, "/");
  return prefix + emailCode + "/detail.html";
}

async function walkFiles(root: string, directory = root): Promise<string[]> {
  const files: string[] = [];
  for (const item of await fs.readdir(directory, {withFileTypes: true})) {
    const full = path.join(directory, item.name);
    if (item.isDirectory()) files.push(...await walkFiles(root, full));
    else files.push(path.relative(root, full).split(path.sep).join("/"));
  }
  return files.sort();
}

export function resolveLocalSiteTarget(reference: string, filePath: string): string {
  let resolved: URL;
  try { resolved = new URL(reference, `https://preview.invalid/${filePath}`); } catch { throw new Error("public site contains an invalid local link"); }
  const target = decodeURIComponent(resolved.pathname).replace(/^\/+/, "");
  if (!target) return "index.html";
  return target.endsWith("/") ? target + "index.html" : target;
}

function assertLocalLinks(files: string[], htmlFiles: Array<{path: string; text: string}>): void {
  const available = new Set(files);
  const attribute = /\b(?:href|src|action)=["']([^"']+)["']/gi;
  for (const file of htmlFiles) {
    for (const match of file.text.matchAll(attribute)) {
      const reference = match[1]!;
      if (reference.startsWith("#") || /^(?:mailto:|tel:|https?:)/i.test(reference)) continue;
      if (/^(?:javascript:|vbscript:|data:|\/\/)/i.test(reference)) throw new Error("public site contains an unsafe URL");
      const candidate = resolveLocalSiteTarget(reference, file.path);
      if (!available.has(candidate)) throw new Error("public site contains a broken local link");
    }
  }
}

function selectionMatches(provenance: Provenance, selection: PreviewSelection): boolean {
  return selection.preview_public
    && selection.email_code === provenance.email_code
    && selection.campaign_key === provenance.campaign_key
    && selection.source_path === provenance.source_path
    && selection.persona === provenance.persona
    && JSON.stringify([...selection.states].sort()) === JSON.stringify([...provenance.states].sort());
}

export async function validateStaticSite(siteDirectory: string, emailCode: string, sourceSha: string, config = loadConfig()): Promise<Provenance> {
  const site = path.resolve(siteDirectory);
  assertCanonicalEmailCode(emailCode);
  assertExactSourceSha(sourceSha);
  await validateGallery(site);
  const files = await walkFiles(site);
  const provenancePath = path.join(site, emailCode, "provenance.json");
  let provenance: Provenance;
  try { provenance = validateProvenance(JSON.parse(await fs.readFile(provenancePath, "utf8"))); } catch { throw new Error("public site provenance is invalid"); }
  const selections = config.selections.filter(selection => selection.email_code === emailCode);
  if (selections.length !== 1 || !selectionMatches(provenance, selections[0]!) || provenance.visibility !== "public" || provenance.source_commit_sha !== sourceSha) throw new Error("public site provenance does not bind the exact public selection");
  for (const output of provenance.outputs) {
    const outputPath = path.join(site, emailCode, output);
    const actual = await fs.readFile(outputPath).catch(() => { throw new Error("public site output is missing"); });
    if (sha256Bytes(actual) !== provenance.output_sha256[output]) throw new Error("public site output digest does not match provenance");
  }
  if (!files.includes(`${emailCode}/detail.html`)) throw new Error("public site Email detail page is missing");
  return provenance;
}

/** Validate site-wide public safety, including the deliberate zero-Email gallery. */
export async function validateGallery(siteDirectory: string): Promise<void> {
  const site = path.resolve(siteDirectory);
  const files = await walkFiles(site);
  if (!files.includes("index.html") || !files.includes("robots.txt")) throw new Error("public site is incomplete");
  if (files.some(file => /(?:^|\/)(?:fixtures?|logs?|source(?:s)?|node_modules|private)(?:\/|$)|(?:^|\/)[^/]*\.versions(?:\/|$)|\.map$|\.log$/i.test(file))) throw new Error("public site contains private build files");
  const textFiles = files.filter(file => /\.(?:html|json|txt|css|js)$/i.test(file));
  const htmlFiles: Array<{path: string; text: string}> = [];
  for (const file of textFiles) {
    const text = await fs.readFile(path.join(site, file), "utf8");
    if (file.endsWith(".html")) htmlFiles.push({path: file, text});
    if (/\{\{|\{%/.test(text)) throw new Error("public site contains Liquid");
    if (/(?:actions\/runs\/\d+\/artifacts\/\d+|actions\/artifacts\/\d+|artifact-url|actions\/download-artifact)/i.test(text)) throw new Error("public site contains a private artifact URL");
    if (containsUnsafePublicUrl(text)) throw new Error("public site contains an unsafe URL");
  }
  assertLocalLinks(files, htmlFiles);
  const index = await fs.readFile(path.join(site, "index.html"), "utf8");
  if (!/noindex\s*,\s*nofollow\s*,\s*noarchive/i.test(index) || !/Content-Security-Policy/i.test(index)) throw new Error("public site index lacks indexing and CSP safeguards");
  const robots = await fs.readFile(path.join(site, "robots.txt"), "utf8");
  if (!/Disallow:\s*\//i.test(robots)) throw new Error("public site robots policy is not restrictive");
}

async function candidate(args: PublicationCliArgs): Promise<void> {
  const provenance = await validateStaticSite(args.site!, args.emailCode!, args.sourceSha!);
  const entry = createPublicationEntry(provenance, {
    canonicalUrl: canonicalEmailUrl(args.canonicalBase!, args.emailCode!),
    pagesDeploymentId: args.pagesDeploymentId!,
    workflowRunId: args.workflowRunId!,
    workflowAttempt: args.workflowAttempt!,
    publicationTimestamp: args.publicationTimestamp,
  });
  await fs.writeFile(path.resolve(args.out!), JSON.stringify(entry, null, 2) + "\n");
}

async function append(args: PublicationCliArgs): Promise<void> {
  const ledger = validateLedger(JSON.parse(await fs.readFile(path.resolve(args.ledger!), "utf8")));
  const entry = JSON.parse(await fs.readFile(path.resolve(args.candidate!), "utf8")) as PublicationEvent;
  const updated = appendPublication(ledger, entry);
  await fs.writeFile(path.resolve(args.ledger!), JSON.stringify(updated, null, 2) + "\n");
}

export function assertWithdrawalSelection(value: unknown, active: {email_code: string; campaign_key: string; source_path: string}): void {
  if (!value || typeof value !== "object" || !Array.isArray((value as {selections?: unknown}).selections)) throw new Error("rollback revision preview configuration is invalid");
  const matches = (value as {selections: Array<Record<string, unknown>>}).selections.filter(selection => selection.email_code === active.email_code);
  if (
    matches.length !== 1
    || matches[0]!.preview_public !== false
    || matches[0]!.campaign_key !== active.campaign_key
    || matches[0]!.source_path !== active.source_path
  ) throw new Error("withdrawal requires preview_public false for the exact active public Email");
}

export function assertSoleActiveWithdrawal(active: Map<string, unknown>, emailCode: string): void {
  if (active.size !== 1 || !active.has(emailCode)) throw new Error("Pages-disable withdrawal requires the exact sole active public Email");
}

export function assertWithdrawalPullRequest(value: unknown, sourceSha: string, canonicalPr: number): void {
  if (!Array.isArray(value)) throw new Error("withdrawal pull-request evidence is invalid");
  const matches = value.filter(candidate => {
    if (!candidate || typeof candidate !== "object") return false;
    const pr = candidate as {number?: unknown; merged_at?: unknown; merged?: unknown; head?: {sha?: unknown}; merge_commit_sha?: unknown};
    return (typeof pr.merged_at === "string" || pr.merged === true)
      && (pr.head?.sha === sourceSha || pr.merge_commit_sha === sourceSha);
  });
  if (matches.length !== 1) throw new Error("withdrawal requires the unique merged pull request for the exact rollback revision");
  if ((matches[0] as {number?: unknown}).number !== canonicalPr) throw new Error("withdrawal pull request does not match the unique merged rollback revision");
}

export function nextGitHubPage(linkHeader: string | null): string | undefined {
  if (!linkHeader) return undefined;
  for (const entry of linkHeader.split(",")) {
    const match = entry.trim().match(/^<([^>]+)>;\s*rel="([^"]+)"$/);
    if (match?.[2]?.split(/\s+/).includes("next")) {
      const url = new URL(match[1]);
      if (url.protocol !== "https:" || url.hostname !== "api.github.com") throw new Error("withdrawal pull-request pagination URL is invalid");
      return url.toString();
    }
  }
  return undefined;
}

async function verifyWithdrawalPullRequest(sourceSha: string, canonicalPr: number): Promise<void> {
  const token = process.env.GH_TOKEN;
  if (!token) throw new Error("GH_TOKEN is required to verify the withdrawal pull request");
  const candidates: unknown[] = [];
  let next: string | undefined = `https://api.github.com/repos/vincent-laroche/marketing-os/commits/${sourceSha}/pulls?per_page=100`;
  while (next) {
    const response = await fetch(next, {
      headers: {
        Accept: "application/vnd.github+json",
        Authorization: `Bearer ${token}`,
        "X-GitHub-Api-Version": "2022-11-28",
      },
    });
    if (!response.ok) throw new Error("withdrawal pull-request verification failed closed");
    const page = await response.json();
    if (!Array.isArray(page)) throw new Error("withdrawal pull-request verification failed closed");
    candidates.push(...page);
    next = nextGitHubPage(response.headers.get("link"));
  }
  assertWithdrawalPullRequest(candidates, sourceSha, canonicalPr);
}

function assertWithdrawalRevision(sourceSha: string, active: {email_code: string; campaign_key: string; source_path: string}): void {
  let config: unknown;
  try {
    const raw = execFileSync("git", ["show", `${sourceSha}:tools/email-preview/preview-config.json`], {cwd: repositoryRoot, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"]});
    config = JSON.parse(raw);
    execFileSync("git", ["cat-file", "-e", `${sourceSha}:${active.source_path}`], {cwd: repositoryRoot, stdio: "ignore"});
    execFileSync("git", ["merge-base", "--is-ancestor", sourceSha, "origin/main"], {cwd: repositoryRoot, stdio: "ignore"});
  } catch { throw new Error("withdrawal revision must be a merged commit with the exact Email source and preview configuration"); }
  assertWithdrawalSelection(config, active);
}

async function withdrawalPreflight(args: PublicationCliArgs): Promise<PublicationEntry> {
  const ledger = validateLedger(JSON.parse(await fs.readFile(path.resolve(args.ledger!), "utf8")));
  const activeSet = activePublications(ledger);
  assertSoleActiveWithdrawal(activeSet, args.emailCode!);
  const active = activeSet.get(args.emailCode!);
  if (!active) throw new Error("withdrawal requires the exact active public Email");
  assertWithdrawalRevision(args.sourceSha!, active);
  await verifyWithdrawalPullRequest(args.sourceSha!, args.canonicalPr!);
  return active;
}

async function withdrawalCandidate(args: PublicationCliArgs): Promise<void> {
  const active = await withdrawalPreflight(args);
  const entry = createWithdrawalEntry(active, {
    sourceCommitSha: args.sourceSha!, canonicalPr: args.canonicalPr!, pagesDeploymentId: args.pagesDeploymentId!,
    workflowRunId: args.workflowRunId!, workflowAttempt: args.workflowAttempt!, reason: args.reason!,
    publicationTimestamp: args.publicationTimestamp,
  });
  await fs.writeFile(path.resolve(args.out!), JSON.stringify(entry, null, 2) + "\n");
}

async function readBack(args: PublicationCliArgs): Promise<void> {
  const provenance = await validateStaticSite(args.site!, args.emailCode!, args.sourceSha!);
  let base: URL;
  try { base = new URL(args.pageUrl!); } catch { throw new Error("Pages URL is invalid"); }
  if (base.protocol !== "https:") throw new Error("Pages read-back requires HTTPS");
  if (!base.pathname.endsWith("/")) base.pathname += "/";
  const root = path.resolve(args.site!);
  const files = await walkFiles(root);
  const responses: PublicReadBack[] = [];
  for (const relative of files) {
    const response = await fetch(new URL(relative, base));
    const body = Buffer.from(await response.arrayBuffer());
    const output = relative.split("/").pop() as keyof typeof provenance.output_sha256;
    const expected = relative === `${args.emailCode}/${output}` ? provenance.output_sha256[output] : undefined;
    if (expected && sha256Bytes(body) !== expected) throw new Error("Pages read-back digest mismatch");
    responses.push({path: relative, status: response.status, body});
  }
  validatePublicReadBack(responses, {sourceSha: args.sourceSha!, emailCode: args.emailCode!, expectedDigests: provenance.output_sha256});
}

async function main(): Promise<void> {
  const args = parsePublicationArgs(process.argv);
  if (args.command === "candidate") await candidate(args);
  else if (args.command === "withdraw-preflight") await withdrawalPreflight(args);
  else if (args.command === "withdraw-candidate") await withdrawalCandidate(args);
  else if (args.command === "append") await append(args);
  else if (args.command === "validate-gallery") await validateGallery(args.site!);
  else if (args.command === "validate-site") await validateStaticSite(args.site!, args.emailCode!, args.sourceSha!);
  else await readBack(args);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch(error => { console.error(error instanceof Error ? error.message : "publication failed closed"); process.exitCode = 1; });
}
