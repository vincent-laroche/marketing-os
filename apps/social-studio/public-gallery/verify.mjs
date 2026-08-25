import { access, readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));
const source = resolve(root, "src");
const output = resolve(root, "dist");

async function read(path) {
  return readFile(path, "utf8");
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const index = await read(resolve(source, "index.html"));
const app = await read(resolve(source, "app.js"));
const data = await read(resolve(source, "data.js"));
const worker = await read(resolve(root, "worker/index.ts"));
const wrangler = await read(resolve(root, "wrangler.jsonc"));

assert(/<meta name="robots" content="noindex, nofollow"\s*\/>/.test(index), "index.html must be noindex");
assert(/<meta name="googlebot" content="noindex, nofollow"\s*\/>/.test(index), "index.html must noindex Googlebot");
assert(index.includes('id="daily-gallery"'), "daily gallery anchor missing");
assert(index.includes('id="feed-assembly"'), "feed assembly anchor missing");
assert(data.includes("dayCount = 30"), "public data must define 30 days");
assert(data.includes("gridSlotCount = 3"), "public data must define three grid slots");
assert(data.includes("storySlotCount = 5"), "public data must define five Story slots");
assert(data.includes("date: null"), "public schedule dates must remain unset");
assert(data.includes("time: null"), "public schedule times must remain unset");
assert(!app.includes("notion"), "public renderer must not reference Notion");
assert(!app.includes("fetch("), "public renderer must not make runtime fetch calls");
assert(!app.includes("/api/"), "public renderer must not expose API routes");
assert(!app.includes("document.cookie"), "public renderer must not use cookies");
assert(worker.includes('headers.set("X-Robots-Tag", "noindex, nofollow")'), "Worker must set X-Robots-Tag");
assert(worker.includes("connect-src 'none'"), "Worker CSP must disable network connections");
assert(wrangler.includes('"custom_domain": true'), "custom domain must be configured");
assert(wrangler.includes('"preview_urls": false'), "preview URLs must stay disabled");
assert(wrangler.includes('"run_worker_first": true'), "Worker must run first for security headers");

for (const file of ["index.html", "styles.css", "app.js", "data.js", "robots.txt"]) {
  await access(resolve(output, file));
}

const built = await read(resolve(output, "index.html"));
assert(built.includes('noindex, nofollow'), "built index.html must preserve noindex");
assert(!built.includes("/home/ubuntu"), "built output must not contain local paths");

console.log("Public gallery verification passed: isolated assets, 30 days, 3 grid slots/day, 5 Story slots/day, noindex, no runtime integrations.");
