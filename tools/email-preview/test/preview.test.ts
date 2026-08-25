import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import test from "node:test";
import { loadConfig, loadFixture } from "../src/config.js";
import { renderLiquid } from "../src/liquid.js";
import { assertSafeRenderedHtml, injectNoIndex, rewriteSensitiveLinks } from "../src/safety.js";
import { provenance } from "../src/provenance.js";
import { isAllowedCaptureRequest } from "../src/capture.js";
import { compilePreview, parseArgs } from "../src/cli.js";

const HEAD = execFileSync("git", ["rev-parse", "HEAD"], {encoding: "utf8"}).trim();

test("fixture registry is fictional, reusable, and produces exact outputs", () => {
  const config = loadConfig();
  const fixture = loadFixture("normal-customer", "product-heavy");
  assert.deepEqual(config.outputs, ["rendered.html", "desktop.png", "mobile.png"]);
  assert.equal(config.preview_public, false);
  assert.equal((fixture.customer as {first_name: string}).first_name, "Alex");
  assert.equal((fixture.abandoned_checkout as {line_items: unknown[]}).line_items.length, 5);
  assert.equal(config.selections.length, 53);
  assert.ok(config.selections.every((selection: {preview_public: boolean}) => selection.preview_public === false));
  assert.equal("first_name" in (loadFixture("normal-customer", "missing-first-name").customer as object), false);
  assert.throws(() => Object.assign(fixture, { customer: {} }), /read only|frozen|extensible/i);
});

test("renderer fails closed when a variable is unresolved", async () => {
  await assert.rejects(() => renderLiquid("<p>{{ missing.value }}</p>", {}), /failed closed/i);
});

test("renderer fails closed when unsupported Liquid remains", async () => {
  await assert.rejects(() => renderLiquid("<p>{% unsupported_tag %}</p>", {}), /failed closed/i);
});

test("renderer rejects LiquidJS constructs outside the preview allowlist", async () => {
  await assert.rejects(() => renderLiquid("{% assign x = 1 %}{{ x }}", {}), /allowlist|failed closed/i);
});

test("rendered HTML is noindex and rejects customer-specific live URLs", () => {
  const safe = injectNoIndex("<html><head></head><body><a href=\"#preview-inert-checkout\">Preview</a></body></html>");
  assert.match(safe, /noindex,nofollow/);
  assert.doesNotThrow(() => assertSafeRenderedHtml(safe));
  assert.doesNotThrow(() => assertSafeRenderedHtml('<html><head><meta name="robots" content="noindex,nofollow,noarchive"></head><body><a href="mailto:info@hairsolutions.co">Support</a></body></html>'));
  assert.throws(() => assertSafeRenderedHtml('<html><head><meta name="robots" content="noindex,nofollow,noarchive"></head><body><a href="mailto:customer@example.com">Customer</a></body></html>'), /direct email address/);
  assert.throws(() => assertSafeRenderedHtml('<html><head><meta name="robots" content="noindex,nofollow,noarchive"></head><body><a href="https://example.com/checkout?token=real">x</a></body></html>'), /unsafe preview/);
});

test("structural safety rejects active content, unsafe protocols, remote hosts, tokens, and pixels", () => {
  const wrap = (body: string) => `<html><head><meta name="robots" content="noindex,nofollow,noarchive"></head><body>${body}</body></html>`;
  for (const html of [
    wrap('<script>alert(1)</script>'),
    wrap('<form action="#"><input></form>'),
    wrap('<iframe src="https://hairsolutions.co"></iframe>'),
    wrap('<img src="x" onerror="alert(1)">'),
    wrap('<a href="javascript:alert(1)">x</a>'),
    wrap('<img src="data:image/png;base64,AA==">'),
    wrap('<a href="vbscript:msgbox(1)">x</a>'),
    wrap('<img src="http://res.cloudinary.com/x.png">'),
    wrap('<img src="https://example.com/x.png">'),
    wrap('<img src="https://res.cloudinary.com/x.png?token=secret">'),
    wrap('<img src="https://res.cloudinary.com/x.png" width="1" height="1">'),
    wrap('<style>@import url("https://example.com/style.css");</style>'),
    wrap('Contact customer@example.com')
  ]) assert.throws(() => assertSafeRenderedHtml(html), /unsafe preview/);
});

test("provenance binds exact source SHA, Issue, PR, and three outputs", () => {
  const extras = {output_sha256: {"rendered.html": "a", "desktop.png": "b", "mobile.png": "c"}, campaign_key: "campaign:J2", fixture_sha256: "fixture", compiler_lock_sha256: "lock", generated_at: "2026-08-25T00:00:00.000Z", visibility: "private" as const};
  const result = provenance({source: "shopify-messaging/emails/01-cr-1.html", emailCode: "CR-1", commitSha: "a".repeat(40), issue: 8, pr: 70, persona: "normal-customer", state: "missing-first-name", out: "unused"}, "source", "rendered", extras);
  assert.equal(result.source_commit_sha, "a".repeat(40));
  assert.equal(result.related_issue, 8);
  assert.equal(result.related_pr, 70);
  assert.deepEqual(result.outputs, ["rendered.html", "desktop.png", "mobile.png"]);
  assert.throws(() => provenance({source: "shopify-messaging/emails/01-cr-1.html", emailCode: "CR-1", commitSha: "a".repeat(40), issue: 8, pr: 0, persona: "normal-customer", state: "missing-first-name", out: "unused"}, "source", "rendered", extras), /positive PR/);
});

test("sensitive destinations are replaced without retaining their original value", () => {
  const rewritten = rewriteSensitiveLinks('<html><head></head><body><a href="https://hairsolutions.co/account?customer_id=123">Account</a></body></html>');
  assert.match(rewritten, /href="#preview-inert"/);
  assert.match(rewritten, /aria-disabled="true"/);
  assert.doesNotMatch(rewritten, /customer_id=123/);
});

test("capture interception permits only local documents and allowlisted HTTPS images", () => {
  assert.equal(isAllowedCaptureRequest("file:///tmp/preview.html", "document"), true);
  assert.equal(isAllowedCaptureRequest("data:text/html,x", "document"), true);
  assert.equal(isAllowedCaptureRequest("blob:null/x", "image"), true);
  assert.equal(isAllowedCaptureRequest("https://res.cloudinary.com/demo/image/upload/x.png", "image"), true);
  assert.equal(isAllowedCaptureRequest("https://res.cloudinary.com/demo/image/upload/x.png", "script"), false);
  assert.equal(isAllowedCaptureRequest("https://example.com/x.png", "image"), false);
});

test("CLI requires a PR and exact canonical selection identity", async () => {
  assert.throws(() => parseArgs(["node", "cli.ts", "--source", "shopify-messaging/emails/01-cr-1.html", "--email-code", "CR-1", "--commit-sha", "a".repeat(40), "--issue", "1", "--out", "tmp"]), /--pr is required/);
  await assert.rejects(() => compilePreview({source: "shopify-messaging/emails/01-cr-1.html", emailCode: "CR-2", commitSha: "a".repeat(40), issue: 1, pr: 2, persona: "normal-customer", state: "missing-first-name", out: "tmp"}), /approved canonical selection/);
});

test("incomplete capture fails without replacing a prior verified output", async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "email-preview-test-"));
  const out = path.join(root, "preview");
  await fs.mkdir(out);
  await fs.writeFile(path.join(out, "sentinel.txt"), "prior-output");
  try {
    await assert.rejects(() => compilePreview({source: "shopify-messaging/emails/01-cr-1.html", emailCode: "CR-1", commitSha: HEAD, issue: 10, pr: 2, persona: "normal-customer", state: "missing-first-name", out}, async (_html, target) => {
      await fs.writeFile(path.join(target, "desktop.png"), "partial");
    }), /incomplete preview output/);
    assert.equal(await fs.readFile(path.join(out, "sentinel.txt"), "utf8"), "prior-output");
  } finally {
    await fs.rm(root, {recursive: true, force: true});
  }
});
