import fs from "node:fs/promises";
import path from "node:path";
import { loadConfig, loadFixture, repositoryRoot } from "./config.js";
import { renderLiquid } from "./liquid.js";
import { assertSafeRenderedHtml, injectNoIndex } from "./safety.js";
import { provenance } from "./provenance.js";
import { capture } from "./capture.js";
import type { PreviewArgs } from "./types.js";

function parseArgs(argv: string[]): PreviewArgs {
  const values = Object.fromEntries(argv.slice(2).map((value, index, all) => value.startsWith("--") ? [value.slice(2), all[index + 1]] : null).filter(Boolean) as [string, string][]);
  const required = ["source", "email-code", "commit-sha", "issue", "out"];
  for (const name of required) if (!values[name]) throw new Error(`--${name} is required`);
  return {source: values.source, emailCode: values["email-code"], commitSha: values["commit-sha"], issue: Number(values.issue), pr: values.pr ? Number(values.pr) : undefined, persona: values.persona || "normal-customer", state: values.state || "missing-first-name", out: values.out};
}

async function main() {
  const args = parseArgs(process.argv);
  const config = loadConfig();
  const sourcePath = path.resolve(repositoryRoot, args.source);
  const allowedRoot = path.resolve(repositoryRoot, config.allowed_source_root) + path.sep;
  if (!sourcePath.startsWith(allowedRoot)) throw new Error("source path is outside the approved email root");
  const source = await fs.readFile(sourcePath, "utf8");
  const rendered = injectNoIndex(await renderLiquid(source, loadFixture(args.persona, args.state)));
  assertSafeRenderedHtml(rendered);
  await fs.mkdir(args.out, { recursive: true });
  const htmlPath = path.join(args.out, "rendered.html");
  await fs.writeFile(htmlPath, rendered);
  await capture(htmlPath, args.out);
  await fs.writeFile(path.join(args.out, "provenance.json"), JSON.stringify(provenance(args, source, rendered), null, 2) + "\n");
  console.log(JSON.stringify({email_code: args.emailCode, outputs: config.outputs, provenance: "provenance.json"}));
}

main().catch(error => { console.error(error instanceof Error ? error.message : error); process.exitCode = 1; });
