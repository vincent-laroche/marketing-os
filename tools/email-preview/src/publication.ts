import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { appendPublication, createPublicationEntry, isApprovedCanonicalUrl, validateLedger, type PublicationEntry } from "./publication-ledger.js";
import { assertExactSourceSha, assertCanonicalEmailCode, sha256Bytes, validatePublicReadBack, type PublicReadBack } from "./github.js";
import { loadConfig } from "./config.js";
import type { PreviewSelection } from "./types.js";
import { validateProvenance } from "./provenance.js";
import type { Provenance } from "./types.js";

export interface PublicationCliArgs {
  command: "candidate" | "append" | "validate-site" | "read-back";
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
}

const FLAGS = new Set(["site", "email-code", "source-sha", "canonical-base", "pages-deployment-id", "workflow-run-id", "workflow-attempt", "publication-timestamp", "out", "ledger", "candidate", "page-url"]);

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
  if (!command || !["candidate", "append", "validate-site", "read-back"].includes(command)) throw new Error("publication command is required");
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
  } else if (command === "append") {
    result.ledger = getRequired(values, "ledger");
    result.candidate = getRequired(values, "candidate");
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

function assertLocalLinks(files: string[], htmlFiles: Array<{path: string; text: string}>): void {
  const available = new Set(files);
  const attribute = /\b(?:href|src|action)=["']([^"']+)["']/gi;
  for (const file of htmlFiles) {
    for (const match of file.text.matchAll(attribute)) {
      const reference = match[1]!;
      if (reference.startsWith("#") || /^(?:mailto:|tel:|https?:)/i.test(reference)) continue;
      if (/^(?:javascript:|vbscript:|data:|\/\/)/i.test(reference)) throw new Error("public site contains an unsafe URL");
      let resolved: URL;
      try { resolved = new URL(reference, `https://preview.invalid/${file.path}`); } catch { throw new Error("public site contains an invalid local link"); }
      const target = decodeURIComponent(resolved.pathname).replace(/^\/+/, "");
      const candidate = target.endsWith("/") ? target + "index.html" : target;
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
  const files = await walkFiles(site);
  if (!files.includes("index.html") || !files.includes("robots.txt")) throw new Error("public site is incomplete");
  if (files.some(file => /(?:^|\/)(?:fixtures?|logs?|source(?:s)?|node_modules|private)(?:\/|$)|(?:^|\/)[^/]*\.versions(?:\/|$)|\.map$|\.log$/i.test(file))) throw new Error("public site contains private build files");
  const textFiles = files.filter(file => /\.(?:html|json|txt|css|js)$/i.test(file));
  const htmlFiles: Array<{path: string; text: string}> = [];
  for (const file of textFiles) {
    const text = await fs.readFile(path.join(site, file), "utf8");
    if (file.endsWith(".html")) htmlFiles.push({path: file, text});
    if (/\{\{|\}\}|\{%|%\}/.test(text)) throw new Error("public site contains Liquid");
    if (/(?:actions\/runs\/\d+\/artifacts\/\d+|actions\/artifacts\/\d+|artifact-url|actions\/download-artifact)/i.test(text)) throw new Error("public site contains a private artifact URL");
    if (/(?:javascript:|vbscript:|data:|customer[_-]?id=|token=|unsubscribe|checkout\.shopify\.com)/i.test(text)) throw new Error("public site contains an unsafe URL");
  }
  assertLocalLinks(files, htmlFiles);
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
  const index = await fs.readFile(path.join(site, "index.html"), "utf8");
  if (!/noindex\s*,\s*nofollow\s*,\s*noarchive/i.test(index) || !/Content-Security-Policy/i.test(index)) throw new Error("public site index lacks indexing and CSP safeguards");
  const robots = await fs.readFile(path.join(site, "robots.txt"), "utf8");
  if (!/Disallow:\s*\//i.test(robots)) throw new Error("public site robots policy is not restrictive");
  return provenance;
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
  const entry = JSON.parse(await fs.readFile(path.resolve(args.candidate!), "utf8")) as PublicationEntry;
  const updated = appendPublication(ledger, entry);
  await fs.writeFile(path.resolve(args.ledger!), JSON.stringify(updated, null, 2) + "\n");
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
    const expected = provenance.output_sha256[relative.split("/").pop() as keyof typeof provenance.output_sha256];
    if (expected && sha256Bytes(body) !== expected) throw new Error("Pages read-back digest mismatch");
    responses.push({path: relative, status: response.status, body});
  }
  validatePublicReadBack(responses, {sourceSha: args.sourceSha!, expectedDigests: provenance.output_sha256});
}

async function main(): Promise<void> {
  const args = parsePublicationArgs(process.argv);
  if (args.command === "candidate") await candidate(args);
  else if (args.command === "append") await append(args);
  else if (args.command === "validate-site") await validateStaticSite(args.site!, args.emailCode!, args.sourceSha!);
  else await readBack(args);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch(error => { console.error(error instanceof Error ? error.message : "publication failed closed"); process.exitCode = 1; });
}
