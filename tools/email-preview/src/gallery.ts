import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { assertSafeRenderedHtml } from "./safety.js";
import { loadConfig, packageRoot } from "./config.js";
import { isApprovedCanonicalUrl } from "./publication-ledger.js";
import { sha256, validateProvenance } from "./provenance.js";
import type { PreviewSelection, Provenance } from "./types.js";

export interface GalleryConfig {
  selections: PreviewSelection[];
}

export interface GalleryEntry {
  directory: string;
  provenance: Provenance;
  selection: PreviewSelection;
}

export interface GalleryResult {
  site: string;
  publicEmails: number;
  campaigns: number;
  entries: GalleryEntry[];
}

const REQUIRED_OUTPUTS = ["rendered.html", "desktop.png", "mobile.png"] as const;
const ROBOTS = "User-agent: *\nDisallow: /\n";
const CSP = "default-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'; img-src 'self'; style-src 'self'; script-src 'self'";
const PRIVATE_ARTIFACT = /(?:actions\/runs\/\d+\/artifacts\/\d+|actions\/artifacts\/\d+|artifact-url|actions\/download-artifact)/i;
const LIQUID = /\{\{|\}\}|\{%|%\}/;

/** Escape every value that came from provenance or the Campaign OS config. */
export function escapeHtml(value: string): string {
  return value.replace(/[&<>"']/g, character => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[character]!));
}

function slug(value: string): string {
  const result = value.replace(/[^A-Za-z0-9_-]/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, "");
  if (!result || result.length > 100 || result === "." || result === "..") throw new Error("unsafe public Email path");
  return result;
}

function hrefSegment(value: string): string {
  if (!/^[A-Za-z0-9][A-Za-z0-9_-]*$/.test(value)) throw new Error("unsafe public Email path");
  return value;
}

function selectionMatches(provenance: Provenance, selection: PreviewSelection): boolean {
  return selection.preview_public
    && selection.email_code === provenance.email_code
    && selection.campaign_key === provenance.campaign_key
    && selection.source_path === provenance.source_path
    && selection.persona === provenance.persona
    && JSON.stringify([...selection.states].sort()) === JSON.stringify([...provenance.states].sort());
}

function canonicalGitHubReference(raw: string, kind: "issues" | "pull", number: number): boolean {
  try {
    const url = new URL(raw);
    return url.protocol === "https:" && url.hostname === "github.com" && !url.username && !url.password && !url.search && !url.hash
      && url.pathname === `/vincent-laroche/email-marketing-ops/${kind}/${number}`;
  } catch {
    return false;
  }
}

async function readPublicEntry(site: string, directory: string, config: GalleryConfig): Promise<GalleryEntry | undefined> {
  const folder = path.join(site, directory);
  let data: unknown;
  try {
    data = JSON.parse(await fs.readFile(path.join(folder, "provenance.json"), "utf8"));
  } catch (error: unknown) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return undefined;
    throw new Error("invalid public preview provenance");
  }
  let provenance: Provenance;
  try {
    provenance = validateProvenance(data);
  } catch {
    throw new Error("invalid public preview provenance");
  }
  if (provenance.visibility !== "public") return undefined;
  const selection = config.selections.find(item => item.email_code === provenance.email_code);
  if (!selection || !selection.preview_public) return undefined;
  if (!selectionMatches(provenance, selection)) throw new Error("public provenance does not match the exact config selection");
  const publicPath = hrefSegment(directory);
  if (slug(provenance.email_code) !== publicPath) throw new Error("public preview directory does not match Email code");
  const files = await Promise.all(REQUIRED_OUTPUTS.map(async file => {
    const value = await fs.readFile(path.join(folder, file));
    const expected = provenance.output_sha256[file];
    if (!expected || sha256(value) !== expected) throw new Error("public preview output digest does not match provenance");
    return [file, value] as const;
  }));
  const rendered = files.find(([file]) => file === "rendered.html")![1].toString("utf8");
  if (LIQUID.test(rendered)) throw new Error("unsafe public preview output: Liquid remains");
  if (PRIVATE_ARTIFACT.test(rendered) || PRIVATE_ARTIFACT.test(JSON.stringify(provenance))) throw new Error("private artifact URL in public preview");
  try {
    assertSafeRenderedHtml(rendered);
  } catch {
    throw new Error("unsafe public preview output");
  }
  if (!canonicalGitHubReference(provenance.issue_url, "issues", provenance.related_issue)
    || !canonicalGitHubReference(provenance.pr_url, "pull", provenance.related_pr)) {
    throw new Error("public provenance contains an unsafe canonical reference");
  }
  if (provenance.canonical_url && !isApprovedCanonicalUrl(provenance.canonical_url)) throw new Error("unsafe public canonical URL");
  return {directory: publicPath, provenance, selection};
}

function campaignSlug(campaign: string): string {
  return "campaign-" + slug(campaign.replace(/^campaign:/, ""));
}

function pageHead(title: string, includeScript = false): string {
  const prefix = includeScript ? "assets/" : "../assets/";
  return "<head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><meta name=\"robots\" content=\"noindex,nofollow,noarchive\"><meta http-equiv=\"Content-Security-Policy\" content=\"" + CSP + "\"><title>" + escapeHtml(title) + "</title><link rel=\"stylesheet\" href=\"" + prefix + "gallery.css\"></head>";
}

function card(entry: GalleryEntry): string {
  const data = entry.provenance;
  const dir = hrefSegment(entry.directory);
  const code = escapeHtml(data.email_code);
  const campaign = escapeHtml(data.campaign_key);
  const sourceSha = escapeHtml(data.source_commit_sha);
  return "<article class=\"card\" data-email-code=\"" + code + "\" data-campaign=\"" + campaign + "\"><a class=\"card-image\" href=\"" + dir + "/detail.html\"><img src=\"" + dir + "/desktop.png\" loading=\"lazy\" alt=\"" + code + " desktop screenshot\"></a><div class=\"card-body\"><p class=\"eyebrow\">" + campaign + "</p><h3><a href=\"" + dir + "/detail.html\">" + code + "</a></h3><p>Source revision <code>" + sourceSha + "</code></p><nav aria-label=\"" + code + " preview links\"><a href=\"" + dir + "/rendered.html\">Interactive HTML</a><a href=\"" + dir + "/desktop.png\">Desktop screenshot</a><a href=\"" + dir + "/mobile.png\">Mobile screenshot</a><a href=\"" + dir + "/provenance.json\">Provenance</a></nav></div></article>";
}

function renderIndex(entries: GalleryEntry[]): string {
  const groups = new Map<string, GalleryEntry[]>();
  for (const entry of entries) groups.set(entry.provenance.campaign_key, [...(groups.get(entry.provenance.campaign_key) ?? []), entry]);
  const campaigns = [...groups.keys()].sort((a, b) => a.localeCompare(b, undefined, {numeric: true}));
  const sections = campaigns.map(campaign => {
    const heading = escapeHtml(campaign);
    const id = campaignSlug(campaign);
    const cards = groups.get(campaign)!.sort((a, b) => a.provenance.email_code.localeCompare(b.provenance.email_code, undefined, {numeric: true})).map(card).join("\n");
    return "<section class=\"campaign-group\" id=\"" + escapeHtml(id) + "\" aria-labelledby=\"" + escapeHtml(id) + "-heading\" data-campaign=\"" + heading + "\"><h2 id=\"" + escapeHtml(id) + "-heading\">" + heading + "</h2><div class=\"card-grid\">" + cards + "</div></section>";
  }).join("\n");
  const body = sections || "<p class=\"empty-state\">No public previews have been deliberately published.</p>";
  const options = campaigns.map(campaign => "<option value=\"" + escapeHtml(campaign) + "\">" + escapeHtml(campaign) + "</option>").join("");
  return "<!doctype html><html lang=\"en\">" + pageHead("Email Preview Gallery", true) + "<body><a class=\"skip-link\" href=\"#main-content\">Skip to previews</a><header class=\"site-header\"><p class=\"eyebrow\">Hair Solutions Co.</p><h1>Email Preview Gallery</h1><p>Fictional fixture data only. Public previews are tied to an exact source revision.</p></header><main id=\"main-content\" tabindex=\"-1\"><form class=\"filters\" method=\"get\" action=\"./\" aria-label=\"Filter public previews\"><div><label for=\"search\">Search Email code</label><input id=\"search\" name=\"search\" type=\"search\" autocomplete=\"off\" placeholder=\"Search by code\"></div><div><label for=\"campaign-filter\">Campaign</label><select id=\"campaign-filter\" name=\"campaign\"><option value=\"\">All Campaigns</option>" + options + "</select></div></form>" + body + "</main><footer><p>Preview evidence only. This gallery is not a send, schedule, or activation surface.</p></footer><script src=\"assets/gallery.js\" defer></script></body></html>";
}

function renderDetail(entry: GalleryEntry): string {
  const data = entry.provenance;
  const code = escapeHtml(data.email_code);
  const campaign = escapeHtml(data.campaign_key);
  const issueUrl = escapeHtml(data.issue_url);
  const prUrl = escapeHtml(data.pr_url);
  const commitUrl = "https://github.com/" + data.repository + "/commit/" + encodeURIComponent(data.source_commit_sha);
  const states = data.states.map(escapeHtml).join(", ");
  return "<!doctype html><html lang=\"en\">" + pageHead(data.email_code + " Preview") + "<body><a class=\"skip-link\" href=\"../index.html\">Back to gallery index</a><header class=\"site-header compact\"><p class=\"eyebrow\">" + campaign + "</p><h1>" + code + "</h1><p>Fictional fixture preview bound to source revision <code>" + escapeHtml(data.source_commit_sha) + "</code>.</p></header><main id=\"main-content\" tabindex=\"-1\"><section class=\"preview-links\" aria-labelledby=\"outputs-heading\"><h2 id=\"outputs-heading\">Preview outputs</h2><p><a href=\"rendered.html\">Open interactive HTML preview</a></p><p><a href=\"desktop.png\"><img class=\"full-preview\" src=\"desktop.png\" alt=\"" + code + " full desktop screenshot\"></a></p><p><a href=\"mobile.png\">Open full mobile screenshot</a></p><p><a href=\"provenance.json\">Open separate provenance file</a></p></section><section class=\"provenance-panel\" aria-labelledby=\"provenance-heading\"><h2 id=\"provenance-heading\">Provenance</h2><dl><dt>Campaign</dt><dd>" + campaign + "</dd><dt>Source path</dt><dd><code>" + escapeHtml(data.source_path) + "</code></dd><dt>Persona</dt><dd>" + escapeHtml(data.persona) + "</dd><dt>States</dt><dd>" + states + "</dd><dt>Issue</dt><dd><a href=\"" + issueUrl + "\">Canonical Email Issue #" + data.related_issue + "</a></dd><dt>Pull request</dt><dd><a href=\"" + prUrl + "\">Source pull request #" + data.related_pr + "</a></dd><dt>Source commit</dt><dd><a href=\"" + commitUrl + "\"><code>" + escapeHtml(data.source_commit_sha) + "</code></a></dd></dl></section></main><footer><p><a href=\"../index.html\">Back to gallery index</a></p></footer></body></html>";
}

/** Build a complete static gallery from already-rendered, verified public outputs. */
export async function generateGallery(siteDirectory: string, config: GalleryConfig = loadConfig()): Promise<GalleryResult> {
  const site = path.resolve(siteDirectory);
  await fs.mkdir(site, {recursive: true});
  const entries: GalleryEntry[] = [];
  const children = await fs.readdir(site, {withFileTypes: true});
  for (const child of children.filter(item => item.isDirectory()).sort((a, b) => a.name.localeCompare(b.name))) {
    if (child.name === "assets") continue;
    const entry = await readPublicEntry(site, child.name, config);
    if (entry) entries.push(entry);
  }
  const entryDirectories = new Set(entries.map(entry => entry.directory));
  for (const child of children) {
    if (child.isDirectory()) {
      if (child.name !== "assets" && !entryDirectories.has(child.name)) await fs.rm(path.join(site, child.name), {recursive: true, force: true});
    } else if (child.name !== "index.html" && child.name !== "robots.txt") {
      await fs.rm(path.join(site, child.name), {force: true});
    }
  }
  for (const entry of entries) {
    const folder = path.join(site, entry.directory);
    const allowed = new Set([...REQUIRED_OUTPUTS, "provenance.json"]);
    for (const child of await fs.readdir(folder, {withFileTypes: true})) {
      if (!allowed.has(child.name)) await fs.rm(path.join(folder, child.name), {recursive: true, force: true});
    }
  }
  await fs.rm(path.join(site, "assets"), {recursive: true, force: true});
  await fs.mkdir(path.join(site, "assets"), {recursive: true});
  await fs.copyFile(path.join(packageRoot, "assets/gallery.css"), path.join(site, "assets/gallery.css"));
  await fs.copyFile(path.join(packageRoot, "assets/gallery.js"), path.join(site, "assets/gallery.js"));
  await fs.writeFile(path.join(site, "robots.txt"), ROBOTS);
  await fs.writeFile(path.join(site, "index.html"), renderIndex(entries));
  for (const entry of entries) await fs.writeFile(path.join(site, entry.directory, "detail.html"), renderDetail(entry));
  return {site, publicEmails: entries.length, campaigns: new Set(entries.map(entry => entry.provenance.campaign_key)).size, entries};
}

async function main(): Promise<void> {
  const result = await generateGallery(process.argv[2] || "email-previews/site");
  console.log(JSON.stringify({site: result.site, publicEmails: result.publicEmails, campaigns: result.campaigns}));
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch(error => { console.error(error instanceof Error ? error.message : "gallery failed closed"); process.exitCode = 1; });
}
