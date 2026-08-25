import fs from "node:fs/promises";
import path from "node:path";
import { repositoryRoot } from "./config.js";
import { inventory, renderMarkdown } from "./inventory.js";

export const REPORT_PATH = "shopify-messaging/PREVIEW-READINESS.md";

async function main() {
  const mode = process.argv.includes("--write") ? "write" : process.argv.includes("--check") ? "check" : "json";
  const report = await inventory();

  if (mode === "json") {
    console.log(JSON.stringify(report, null, 2));
    return;
  }

  const target = path.resolve(repositoryRoot, REPORT_PATH);
  const markdown = renderMarkdown(report);

  if (mode === "write") {
    await fs.writeFile(target, markdown);
    console.log(JSON.stringify({ wrote: REPORT_PATH, ready: report.ready, blocked: report.blocked }));
    return;
  }

  const current = await fs.readFile(target, "utf8").catch(() => "");
  if (current !== markdown) {
    throw new Error(`${REPORT_PATH} is stale; run npm --prefix tools/email-preview run inventory -- --write`);
  }
  console.log(JSON.stringify({ checked: REPORT_PATH, ready: report.ready, blocked: report.blocked }));
}

main().catch(error => {
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
});
