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
import { assertPng, isAllowedCaptureRequest } from "../src/capture.js";
import { compilePreview, parseArgs } from "../src/cli.js";

const HEAD = execFileSync("git", ["rev-parse", "HEAD"], {encoding: "utf8"}).trim();

test("fixture registry is fictional, reusable, and produces exact outputs", () => {
  const config = loadConfig();
  const fixture = loadFixture("normal-customer", "product-heavy");
  assert.deepEqual(config.outputs, ["rendered.html", "desktop.png", "mobile.png"]);
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

test("renderer rejects unknown paths even when defaulted or nested under a loop binding", async () => {
  await assert.rejects(() => renderLiquid('{{ secret.token | default: "fallback" }}', {}), /unknown variable/);
  await assert.rejects(() => renderLiquid('{% for item in products limit:1 %}{{ item.secret }}{% endfor %}', {products: [{name: "fictional"}]}), /unknown variable/);
});

test("loop bindings are lexical and nested loops validate against their enclosing item", async () => {
  await assert.rejects(() => renderLiquid('{% for item in products limit:1 %}{{ item.title }}{% endfor %}{{ item.title }}', {products: [{title: "Fictional", variants: [{title: "Fictional variant"}]}]}), /unknown variable/);
  await assert.doesNotReject(() => renderLiquid('{% for item in products limit:1 %}{% for variant in item.variants limit:1 %}{{ variant.title }}{% endfor %}{% endfor %}', {products: [{title: "Fictional", variants: [{title: "Fictional variant"}]}]}));
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
    wrap('Contact customer@example.com'),
    wrap('<img style="background:url(https://example.com/pixel.png?token=x)">'),
    wrap('<img srcset="https://res.cloudinary.com/x.png 1x, https://example.com/x.png 2x">'),
    wrap('<div data-source="https://example.com/?token=x"></div>'),
    wrap('<!-- https://example.com/?customer_id=1 -->'),
    wrap('<img src="https://res.cloudinary.com/x.png" style="width:1px;height:1px">'),
    wrap('<img src="https://res.cloudinary.com/image/upload/w_1/x.png">')
    ,wrap('<a href="//example.com/customer?token=x">x</a>')
    ,wrap('<!-- //example.com/customer?token=x -->')
    ,wrap('<div style="background:url(https://res.cloudinary.com/pixel.png);width:1px;height:1px"></div>')
  ]) assert.throws(() => assertSafeRenderedHtml(html), /unsafe preview/);
});

test("provenance binds exact source SHA, Issue, PR, and three outputs", () => {
  const extras = {output_sha256: {"rendered.html": "a", "desktop.png": "b", "mobile.png": "c"}, campaign_key: "campaign:J2", fixture_sha256: "fixture", compiler_lock_sha256: "lock", generated_at: "2026-08-25T00:00:00.000Z", visibility: "private" as const};
  const identity = {repository: "vincent-laroche/email-marketing-ops"};
  const result = provenance({source: "shopify-messaging/emails/01-cr-1.html", emailCode: "CR-1", campaign: "campaign:J2", commitSha: "a".repeat(40), issue: 8, pr: 70, persona: "normal-customer", states: ["missing-first-name"], out: "unused"}, "source", "rendered", {...extras, identity});
  assert.equal(result.source_commit_sha, "a".repeat(40));
  assert.equal(result.related_issue, 8);
  assert.equal(result.related_pr, 70);
  assert.deepEqual(result.outputs, ["rendered.html", "desktop.png", "mobile.png"]);
  assert.throws(() => provenance({source: "shopify-messaging/emails/01-cr-1.html", emailCode: "CR-1", campaign: "campaign:J2", commitSha: "a".repeat(40), issue: 8, pr: 0, persona: "normal-customer", states: ["missing-first-name"], out: "unused"}, "source", "rendered", {...extras, identity}), /positive PR/);
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
  assert.equal(isAllowedCaptureRequest("https://res.cloudinary.com/x.png?token=secret", "image"), false);
  assert.equal(isAllowedCaptureRequest("//res.cloudinary.com/x.png", "image"), false);
});

test("PNG validation enforces exact capture widths", async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "email-preview-png-"));
  const png = path.join(root, "test.png");
  const bytes = Buffer.alloc(33); Buffer.from([137,80,78,71,13,10,26,10]).copy(bytes); bytes.writeUInt32BE(1440, 16); bytes.writeUInt32BE(10, 20);
  await fs.writeFile(png, bytes);
  try {
    await assert.doesNotReject(() => assertPng(png, 1440));
    await assert.rejects(() => assertPng(png, 390), /dimensions/);
  } finally { await fs.rm(root, {recursive: true, force: true}); }
});

test("CLI requires a PR, campaign, selected states, no unknown flags, and exact canonical identity", async () => {
  assert.throws(() => parseArgs(["node", "cli.ts", "--source", "shopify-messaging/emails/01-cr-1.html", "--email-code", "CR-1", "--campaign", "campaign:J2", "--commit-sha", "a".repeat(40), "--issue", "1", "--states", "missing-first-name", "--out", "tmp"]), /--pr is required/);
  await assert.rejects(() => compilePreview({source: "shopify-messaging/emails/01-cr-1.html", emailCode: "CR-2", campaign: "campaign:J2", commitSha: "a".repeat(40), issue: 1, pr: 2, persona: "normal-customer", states: ["missing-first-name"], out: "tmp"}), /approved canonical selection/);
  assert.throws(() => parseArgs(["node", "cli.ts", "--source", "shopify-messaging/emails/01-cr-1.html", "--email-code", "CR-1", "--campaign", "campaign:J2", "--commit-sha", "a".repeat(40), "--issue", "10", "--pr", "2", "--states", "missing-first-name", "--out", "tmp", "--unexpected", "x"]), /unknown option/);
  assert.throws(() => parseArgs(["node", "cli.ts", "--source", "shopify-messaging/emails/01-cr-1.html", "--email-code", "CR-1", "--campaign", "campaign:J2", "--commit-sha", "a".repeat(40), "--issue", "10", "--pr", "2", "--states", "missing-first-name", "--out", "tmp", "--unexpected"]), /unknown option/);
  assert.throws(() => parseArgs(["node", "cli.ts", "--source", "shopify-messaging/emails/01-cr-1.html", "--email-code", "CR-1", "--campaign", "campaign:J2", "--commit-sha", "a".repeat(40), "--issue", "10", "--pr"]), /--pr is required/);
});

test("incomplete capture fails without replacing a prior verified output", async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "email-preview-test-"));
  const out = path.join(root, "preview");
  await fs.mkdir(out);
  await fs.writeFile(path.join(out, "sentinel.txt"), "prior-output");
  try {
    await assert.rejects(() => compilePreview({source: "shopify-messaging/emails/01-cr-1.html", emailCode: "CR-1", campaign: "campaign:J2", commitSha: HEAD, issue: 10, pr: 2, persona: "normal-customer", states: ["missing-first-name"], out}, async (_html, target) => {
      await fs.writeFile(path.join(target, "desktop.png"), "partial");
    }), /incomplete preview output/);
    assert.equal(await fs.readFile(path.join(out, "sentinel.txt"), "utf8"), "prior-output");
  } finally {
    await fs.rm(root, {recursive: true, force: true});
  }
});
