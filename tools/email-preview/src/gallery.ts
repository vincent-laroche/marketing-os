import fs from "node:fs/promises";
import path from "node:path";
import { packageRoot } from "./config.js";
import type { Provenance } from "./types.js";

const site = path.resolve(process.argv[2] || "email-previews/site");
const entries: Array<{dir: string; data: Provenance}> = [];

await fs.mkdir(site, { recursive: true });
for (const entry of await fs.readdir(site, { withFileTypes: true })) {
  if (!entry.isDirectory()) continue;
  try {
    const data = JSON.parse(await fs.readFile(path.join(site, entry.name, "provenance.json"), "utf8")) as Provenance;
    entries.push({ dir: entry.name, data });
  } catch {}
}

entries.sort((a, b) => a.data.email_code.localeCompare(b.data.email_code, undefined, { numeric: true }));
const cards = entries.map(({dir, data}) => `<article class="card"><a href="${dir}/rendered.html"><img src="${dir}/desktop.png" alt="${data.email_code} desktop preview"><strong>${data.email_code}</strong></a><p>Commit <code>${data.source_commit_sha.slice(0, 12)}</code> · Issue #${data.related_issue}${data.related_pr ? ` · PR #${data.related_pr}` : ""}</p></article>`).join("\n");
const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Email Preview Gallery</title><link rel="stylesheet" href="assets/gallery.css"></head><body><header><p>Hair Solutions Co.</p><h1>Email Preview Gallery</h1><p>Fictional fixture data only. Each preview is tied to an exact source revision.</p></header><main>${cards || "<p>No public previews have been deliberately published.</p>"}</main></body></html>`;
await fs.mkdir(path.join(site, "assets"), { recursive: true });
await fs.writeFile(path.join(site, "index.html"), html);
await fs.copyFile(path.join(packageRoot, "assets/gallery.css"), path.join(site, "assets/gallery.css"));
await fs.copyFile(path.join(packageRoot, "assets/robots.txt"), path.join(site, "robots.txt"));
