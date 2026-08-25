import fs from "node:fs/promises";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {execFileSync} from "node:child_process";
import {canonicalIssueFor, loadConfig, loadFixture, packageRoot, repositoryRoot, selectionFor} from "./config.js";
import {renderLiquid} from "./liquid.js";
import {assertSafeRenderedHtml, injectNoIndex, rewriteSensitiveLinks} from "./safety.js";
import {provenance, sha256} from "./provenance.js";
import {capture} from "./capture.js";
import type {PreviewArgs} from "./types.js";

export function parseArgs(argv: string[]): PreviewArgs {
  const values = Object.fromEntries(argv.slice(2).flatMap((value, index, all) => value.startsWith("--") && all[index + 1] ? [[value.slice(2), all[index + 1]!]] : []));
  const required = ["source", "email-code", "commit-sha", "issue", "pr", "out"];
  for (const name of required) if (!values[name]) throw new Error(`--${name} is required`);
  const issue = Number(values.issue);
  const pr = Number(values.pr);
  if (!Number.isInteger(issue) || issue < 1) throw new Error("positive canonical Issue required");
  if (!Number.isInteger(pr) || pr < 1) throw new Error("positive PR required");
  const workflow = [values["workflow-run"], values["workflow-attempt"], values["workflow-revision"]];
  if (workflow.some(Boolean) && workflow.some(value => !value)) throw new Error("workflow provenance requires run, attempt, and revision");
  return {source: values.source!, emailCode: values["email-code"]!, commitSha: values["commit-sha"]!, issue, pr, persona: values.persona || "normal-customer", state: values.state || "missing-first-name", out: values.out!, workflowRun: values["workflow-run"], workflowAttempt: values["workflow-attempt"], workflowRevision: values["workflow-revision"]};
}

export async function compilePreview(args: PreviewArgs, capturePreview: typeof capture = capture): Promise<void> {
  if (!/^[0-9a-f]{40}$/.test(args.commitSha)) throw new Error("exact 40-character source commit SHA required");
  const config = loadConfig();
  const source = path.posix.normalize(args.source.replace(/\\/g, "/"));
  selectionFor(config, {email_code: args.emailCode, source_path: source, persona: args.persona, state: args.state});
  if (args.issue !== canonicalIssueFor(args.emailCode)) throw new Error("Issue does not match the canonical Email selection");
  const sourcePath = path.resolve(repositoryRoot, source);
  const allowedRoot = path.resolve(repositoryRoot, config.allowed_source_root) + path.sep;
  if (!sourcePath.startsWith(allowedRoot)) throw new Error("source path is outside the approved email root");
  const sourceContents = await fs.readFile(sourcePath, "utf8");
  let committedSource: Buffer;
  try { committedSource = execFileSync("git", ["show", `${args.commitSha}:${source}`], {cwd: repositoryRoot, stdio: ["ignore", "pipe", "ignore"]}); } catch { throw new Error("source is not available at the requested commit"); }
  if (!Buffer.from(sourceContents).equals(committedSource)) throw new Error("source does not match the requested commit");
  const fixture = loadFixture(args.persona, args.state);
  const selection = selectionFor(config, {email_code: args.emailCode, source_path: source, persona: args.persona, state: args.state});
  const metadata = JSON.stringify({repository: "vincent-laroche/email-marketing-ops", campaign: selection.campaign_key, email: args.emailCode, source_sha256: sha256(sourceContents), commit: args.commitSha, issue: args.issue, pr: args.pr, fixture_sha256: sha256(JSON.stringify(fixture))});
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
    const output_sha256 = Object.fromEntries(await Promise.all(["rendered.html", "desktop.png", "mobile.png"].map(async file => [file, sha256(await fs.readFile(path.join(temporaryDir, file)))]))) as Record<"rendered.html" | "desktop.png" | "mobile.png", string>;
    const lock = await fs.readFile(path.join(packageRoot, "package-lock.json"));
    const detail = provenance(args, sourceContents, rendered, {output_sha256, campaign_key: selection.campaign_key, fixture_sha256: sha256(JSON.stringify(fixture)), compiler_lock_sha256: sha256(lock), generated_at: new Date().toISOString(), visibility: selection.preview_public ? "public" : "private"});
    await fs.writeFile(path.join(temporaryDir, "provenance.json"), JSON.stringify(detail, null, 2) + "\n");
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
  const backup = `${finalDir}.previous-${process.pid}`;
  let movedPrior = false;
  try {
    try { await fs.rename(finalDir, backup); movedPrior = true; } catch (error: unknown) { if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error; }
    await fs.rename(temporaryDir, finalDir);
    if (movedPrior) await fs.rm(backup, {recursive: true, force: true});
  } catch (error) {
    if (movedPrior) {
      try { await fs.rename(backup, finalDir); } catch {}
    }
    throw error;
  }
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv);
  await compilePreview(args);
  console.log(JSON.stringify({email_code: args.emailCode, outputs: ["rendered.html", "desktop.png", "mobile.png"], provenance: "provenance.json"}));
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch(error => { console.error(error instanceof Error ? error.message : "preview compiler failed closed"); process.exitCode = 1; });
}
