import assert from "node:assert/strict";
import test from "node:test";
import { loadConfig, loadFixture } from "../src/config.js";
import { renderLiquid } from "../src/liquid.js";
import { assertSafeRenderedHtml, injectNoIndex } from "../src/safety.js";
import { provenance } from "../src/provenance.js";

test("fixture registry is fictional, reusable, and produces exact outputs", () => {
  const config = loadConfig();
  const fixture = loadFixture("normal-customer", "product-heavy");
  assert.deepEqual(config.outputs, ["rendered.html", "desktop.png", "mobile.png"]);
  assert.equal(config.preview_public, false);
  assert.equal((fixture.customer as {first_name: string}).first_name, "Alex");
  assert.equal((fixture.abandoned_checkout as {line_items: unknown[]}).line_items.length, 3);
});

test("renderer fails closed when a variable is unresolved", async () => {
  await assert.rejects(() => renderLiquid("<p>{{ missing.value }}</p>", {}), /failed closed/i);
});

test("renderer fails closed when unsupported Liquid remains", async () => {
  await assert.rejects(() => renderLiquid("<p>{% unsupported_tag %}</p>", {}), /failed closed/i);
});

test("rendered HTML is noindex and rejects customer-specific live URLs", () => {
  const safe = injectNoIndex("<html><head></head><body><a href=\"#preview-inert-checkout\">Preview</a></body></html>");
  assert.match(safe, /noindex,nofollow/);
  assert.doesNotThrow(() => assertSafeRenderedHtml(safe));
  assert.throws(() => assertSafeRenderedHtml('<html><head><meta name="robots" content="noindex"></head><body><a href="https://example.com/checkout?token=real">x</a></body></html>'), /unsafe preview/);
});

test("provenance binds exact source SHA, Issue, PR, and three outputs", () => {
  const result = provenance({source: "shopify-messaging/emails/01-cr-1.html", emailCode: "CR-1", commitSha: "a".repeat(40), issue: 8, pr: 70, persona: "normal-customer", state: "missing-first-name", out: "unused"}, "source", "rendered");
  assert.equal(result.source_commit_sha, "a".repeat(40));
  assert.equal(result.related_issue, 8);
  assert.equal(result.related_pr, 70);
  assert.deepEqual(result.outputs, ["rendered.html", "desktop.png", "mobile.png"]);
});
