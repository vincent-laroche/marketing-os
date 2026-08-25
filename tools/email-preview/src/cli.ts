import fs from "node:fs/promises";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {execFileSync} from "node:child_process";
import {canonicalIssueFor, loadConfig, loadFixture, packageRoot, repositoryRoot, selectionFor} from "./config.js";
import {renderLiquid} from "./liquid.js";
import {assertSafeRenderedHtml, injectNoIndex, rewriteSensitiveLinks} from "./safety.js";
import {provenance, sha256, validateProvenance as parseProvenance} from "./provenance.js";
import {assertPng, capture} from "./capture.js";
import type {PreviewArgs} from "./types.js";

export function parseArgs(argv: string[]): PreviewArgs {
  const allowed = new Set(["source", "email-code", "campaign", "commit-sha", "issue", "pr", "persona", "states", "out", "workflow-run", "workflow-attempt", "workflow-revision"]);
  const values: Record<string, string> = {};
  for (let index = 2; index < argv.length; index += 2) {
    const token = argv[index];
    if (!token?.startsWith("--") || !allowed.has(token.slice(2))) throw new Error("unknown option");
    const key = token.slice(2); const value = argv[index + 1];
    if (!value || value.startsWith("--")) throw new Error(`--${key} is required`);
    if (key in values) throw new Error("duplicate option");
    values[key] = value;
  }
  const required = ["source", "email-code", "campaign", "commit-sha", "issue", "pr", "states", "out"];
  for (const name of required) if (!values[name]) throw new Error(`--${name} is required`);
  const issue = Number(values.issue);
  const pr = Number(values.pr);
  if (!Number.isInteger(issue) || issue < 1) throw new Error("positive canonical Issue required");
  if (!Number.isInteger(pr) || pr < 1) throw new Error("positive PR required");
  const workflow = [values["workflow-run"], values["workflow-attempt"], values["workflow-revision"]];
  if (workflow.some(Boolean) && workflow.some(value => !value)) throw new Error("workflow provenance requires run, attempt, and revision");
  const states = [...new Set(values.states!.split(",").map(state => state.trim()).filter(Boolean))].sort();
  if (!states.length) throw new Error("at least one selected state is required");
  return {source: values.source!, emailCode: values["email-code"]!, campaign: values.campaign!, commitSha: values["commit-sha"]!, issue, pr, persona: values.persona || "normal-customer", states, out: values.out!, workflowRun: values["workflow-run"], workflowAttempt: values["workflow-attempt"], workflowRevision: values["workflow-revision"]};
}

export async function compilePreview(args: PreviewArgs, capturePreview: typeof capture = capture): Promise<void> {
  if (!/^[0-9a-f]{40}$/.test(args.commitSha)) throw new Error("exact 40-character source commit SHA required");
  const config = loadConfig();
  const source = path.posix.normalize(args.source.replace(/\\/g, "/"));
  selectionFor(config, {email_code: args.emailCode, source_path: source, campaign_key: args.campaign, persona: args.persona, states: args.states});
  if (args.issue !== canonicalIssueFor(args.emailCode)) throw new Error("Issue does not match the canonical Email selection");
  const sourcePath = path.resolve(repositoryRoot, source);
  const allowedRoot = path.resolve(repositoryRoot, config.allowed_source_root) + path.sep;
  if (!sourcePath.startsWith(allowedRoot)) throw new Error("source path is outside the approved email root");
  const sourceContents = await fs.readFile(sourcePath, "utf8");
  let committedSource: Buffer;
  try { committedSource = execFileSync("git", ["show", `${args.commitSha}:${source}`], {cwd: repositoryRoot, stdio: ["ignore", "pipe", "ignore"]}); } catch { throw new Error("source is not available at the requested commit"); }
  if (!Buffer.from(sourceContents).equals(committedSource)) throw new Error("source does not match the requested commit");
  const fixture = loadFixture(args.persona, args.states);
  const selection = selectionFor(config, {email_code: args.emailCode, source_path: source, campaign_key: args.campaign, persona: args.persona, states: args.states});
  const lock = await fs.readFile(path.join(packageRoot, "package-lock.json"));
  const identity = {repository: "vincent-laroche/email-marketing-ops", campaign: selection.campaign_key, email: args.emailCode, source_path: source, source_sha256: sha256(sourceContents), commit: args.commitSha, issue: args.issue, pr: args.pr, issue_url: `https://github.com/vincent-laroche/email-marketing-ops/issues/${args.issue}`, pr_url: `https://github.com/vincent-laroche/email-marketing-ops/pull/${args.pr}`, persona: args.persona, states: args.states, fixture_sha256: sha256(JSON.stringify(fixture)), compiler_version: "1.0.0", compiler_lock_sha256: sha256(lock), generated_at: new Date().toISOString(), visibility: selection.preview_public ? ("public" as const) : ("private" as const), workflow: args.workflowRun ? {run: args.workflowRun!, attempt: args.workflowAttempt!, revision: args.workflowRevision!} : undefined};
  const metadata = JSON.stringify(identity);
  const rendered = `<!-- preview-provenance:${metadata} -->\n${rewriteSensitiveLinks(injectNoIndex(await renderLiquid(sourceContents, fixture)))}`;
  assertSafeRenderedHtml(rendered);

  const finalDir = path.resolve(args.out);
  const temporaryDir = await fs.mkdtemp(path.join(path.dirname(finalDir), `.${path.basename(finalDir)}.preview-`));
  try {
    await fs.writeFile(path.join(temporaryDir, "rendered.html"), rendered);
    await capturePreview(path.join(temporaryDir, "rendered.html"), temporaryDir);
    for (const file of ["rendered.html", "desktop.png", "mobile.png"]) {
      try { await fs.access(path.join(temporaryDir, file)); } catch { throw new Error("incomplete preview output"); }
    }
    await Promise.all(([ ["desktop.png", 1440], ["mobile.png", 390] ] as const).map(([file, width]) => assertPng(path.join(temporaryDir, file), width)));
    const output_sha256 = Object.fromEntries(await Promise.all(["rendered.html", "desktop.png", "mobile.png"].map(async file => [file, sha256(await fs.readFile(path.join(temporaryDir, file)))]))) as Record<"rendered.html" | "desktop.png" | "mobile.png", string>;
    const detail = provenance(args, sourceContents, rendered, {output_sha256, campaign_key: selection.campaign_key, fixture_sha256: sha256(JSON.stringify(fixture)), compiler_lock_sha256: sha256(lock), generated_at: identity.generated_at, visibility: identity.visibility, identity});
    await fs.writeFile(path.join(temporaryDir, "provenance.json"), JSON.stringify(detail, null, 2) + "\n");
    await validateProvenance(path.join(temporaryDir, "provenance.json"), rendered);
    const expected = new Set(["rendered.html", "desktop.png", "mobile.png", "provenance.json"]);
    const entries = await fs.readdir(temporaryDir);
    if (entries.length !== expected.size || entries.some(entry => !expected.has(entry))) throw new Error("incomplete preview output");
    await promote(temporaryDir, finalDir);
  } catch (error) {
    await fs.rm(temporaryDir, {recursive: true, force: true});
    throw error;
  }
}

async function promote(temporaryDir: string, finalDir: string): Promise<void> {
  const versions = `${finalDir}.versions`;
  await fs.mkdir(versions, {recursive: true});
  let existing: import("node:fs").Stats | undefined;
  try { existing = await fs.lstat(finalDir); } catch (error: unknown) { if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error; }
  if (existing && !existing.isSymbolicLink()) throw new Error("refusing non-atomic replacement of an existing output directory");
  const version = path.join(versions, `${Date.now()}-${process.pid}`);
  await fs.rename(temporaryDir, version);
  const switchLink = `${finalDir}.switch-${process.pid}`;
  await fs.symlink(path.relative(path.dirname(finalDir), version), switchLink);
  try { await fs.rename(switchLink, finalDir); } catch (error) { await fs.unlink(switchLink).catch(() => {}); throw error; }
}

async function validateProvenance(file: string, rendered: string): Promise<void> {
  const data = parseProvenance(JSON.parse(await fs.readFile(file, "utf8")));
  const marker = rendered.match(/^<!-- preview-provenance:(.*?) -->/);
  if (!marker) throw new Error("missing embedded provenance");
  let embedded: Record<string, unknown>;
  try { embedded = JSON.parse(marker[1]!); } catch { throw new Error("invalid embedded provenance"); }
  const checks: Array<[unknown, unknown]> = [[embedded.repository, data.repository], [embedded.campaign, data.campaign_key], [embedded.email, data.email_code], [embedded.source_path, data.source_path], [embedded.source_sha256, data.source_sha256], [embedded.commit, data.source_commit_sha], [embedded.issue, data.related_issue], [embedded.pr, data.related_pr], [embedded.issue_url, data.issue_url], [embedded.pr_url, data.pr_url], [embedded.persona, data.persona], [embedded.states, data.states], [embedded.fixture_sha256, data.fixture_sha256], [embedded.compiler_version, data.compiler_version], [embedded.compiler_lock_sha256, data.compiler_lock_sha256], [embedded.generated_at, data.generated_at], [embedded.visibility, data.visibility], [embedded.workflow, data.workflow]];
  if (checks.some(([left, right]) => JSON.stringify(left) !== JSON.stringify(right))) throw new Error("embedded provenance does not match final provenance");
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv);
  await compilePreview(args);
  console.log(JSON.stringify({email_code: args.emailCode, outputs: ["rendered.html", "desktop.png", "mobile.png"], provenance: "provenance.json"}));
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch(error => { console.error(error instanceof Error ? error.message : "preview compiler failed closed"); process.exitCode = 1; });
}
