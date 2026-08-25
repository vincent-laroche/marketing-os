import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { sha256 } from "../src/provenance.js";
import { generateGallery, type GalleryConfig } from "../src/gallery.js";

const sourceSha = "a".repeat(40);
const sourcePath = "shopify-messaging/emails/01-cr-1.html";

function configFor(previewPublic: boolean, campaignKey = "campaign:J2"): GalleryConfig {
  return {
    selections: [{
      email_code: "CR-1",
      campaign_key: campaignKey,
      source_path: sourcePath,
      persona: "normal-customer",
      states: ["missing-first-name"],
      preview_public: previewPublic,
    }],
  };
}

async function writePreview(root: string, options: {visibility: "public" | "private"; campaign?: string; artifactUrl?: string}): Promise<void> {
  const dir = path.join(root, "CR-1");
  await fs.mkdir(dir, {recursive: true});
  const rendered = `<!doctype html><html><head><meta name="robots" content="noindex,nofollow,noarchive"></head><body>${options.artifactUrl ?? "Fictional preview"}</body></html>`;
  const desktop = Buffer.from("desktop");
  const mobile = Buffer.from("mobile");
  await fs.writeFile(path.join(dir, "rendered.html"), rendered);
  await fs.writeFile(path.join(dir, "desktop.png"), desktop);
  await fs.writeFile(path.join(dir, "mobile.png"), mobile);
  await fs.writeFile(path.join(dir, "provenance.json"), JSON.stringify({
    schema_version: 1,
    email_code: "CR-1",
    source_path: sourcePath,
    source_commit_sha: sourceSha,
    related_issue: 101,
    related_pr: 202,
    persona: "normal-customer",
    states: ["missing-first-name"],
    compiler_version: "1.0.0",
    source_sha256: sha256("source"),
    rendered_sha256: sha256(rendered),
    outputs: ["rendered.html", "desktop.png", "mobile.png"],
    output_sha256: {
      "rendered.html": sha256(rendered),
      "desktop.png": sha256(desktop),
      "mobile.png": sha256(mobile),
    },
    repository: "vincent-laroche/email-marketing-ops",
    campaign_key: options.campaign ?? "campaign:J2",
    fixture_sha256: sha256("fixture"),
    compiler_lock_sha256: sha256("lock"),
    generated_at: "2026-08-25T12:00:00.000Z",
    visibility: options.visibility,
    issue_url: "https://github.com/vincent-laroche/email-marketing-ops/issues/101",
    pr_url: "https://github.com/vincent-laroche/email-marketing-ops/pull/202",
  }, null, 2));
}

test("an empty public site is safe, indexed nowhere, and has useful no-JavaScript navigation", async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "email-preview-gallery-empty-"));
  try {
    const result = await generateGallery(root, configFor(false));
    const index = await fs.readFile(path.join(root, "index.html"), "utf8");
    assert.equal(result.publicEmails, 0);
    assert.match(index, /noindex,nofollow,noarchive/);
    assert.match(index, /No public previews have been deliberately published/);
    assert.match(index, /id="main-content"/);
    assert.match(index, /Content-Security-Policy/);
    assert.match(await fs.readFile(path.join(root, "robots.txt"), "utf8"), /Disallow:\s*\//);
  } finally {
    await fs.rm(root, {recursive: true, force: true});
  }
});

test("gallery excludes private and per-Email-gated previews and escapes campaign metadata", async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "email-preview-gallery-selection-"));
  try {
    await writePreview(root, {visibility: "public", campaign: "campaign:<script>alert(1)</script>"});
    const index = await generateGallery(root, configFor(true, "campaign:<script>alert(1)</script>"));
    const html = await fs.readFile(path.join(root, "index.html"), "utf8");
    assert.equal(index.publicEmails, 1);
    assert.match(html, /campaign:&lt;script&gt;alert\(1\)&lt;\/script&gt;/);
    assert.doesNotMatch(html, /<script>alert\(1\)<\/script>/);
    assert.match(html, /data-campaign="campaign:&lt;script&gt;alert\(1\)&lt;\/script&gt;"/);
    assert.match(html, /CR-1\/detail\.html/);
    assert.match(await fs.readFile(path.join(root, "CR-1", "detail.html"), "utf8"), /rendered\.html/);
    assert.match(await fs.readFile(path.join(root, "CR-1", "detail.html"), "utf8"), /desktop\.png/);
    assert.match(await fs.readFile(path.join(root, "CR-1", "detail.html"), "utf8"), /mobile\.png/);
    assert.match(await fs.readFile(path.join(root, "CR-1", "detail.html"), "utf8"), /provenance\.json/);

    await fs.rm(path.join(root, "CR-1"), {recursive: true, force: true});
    await writePreview(root, {visibility: "public"});
    const privateIndex = await generateGallery(root, configFor(false));
    assert.equal(privateIndex.publicEmails, 0);
    assert.match(await fs.readFile(path.join(root, "index.html"), "utf8"), /No public previews/);
  } finally {
    await fs.rm(root, {recursive: true, force: true});
  }
});

test("gallery refuses private artifact URLs in a public rendered output", async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "email-preview-gallery-private-url-"));
  try {
    await writePreview(root, {visibility: "public", artifactUrl: "https://github.com/example/actions/runs/1/artifacts/2"});
    await assert.rejects(() => generateGallery(root, configFor(true)), /private artifact|unsafe public preview output/i);
  } finally {
    await fs.rm(root, {recursive: true, force: true});
  }
});

test("gallery UI uses current web brand tokens rather than the Email Reference palette", async () => {
  const css = await fs.readFile(path.resolve(import.meta.dirname, "../assets/gallery.css"), "utf8");
  for (const token of ["#efe7d2", "#f7f1de", "#15140f", "#ed6f5c"]) assert.match(css, new RegExp(token));
  for (const emailOnly of ["#f6efd9", "#ede3cc", "#151411", "#ea6452"]) assert.doesNotMatch(css, new RegExp(emailOnly));
});
