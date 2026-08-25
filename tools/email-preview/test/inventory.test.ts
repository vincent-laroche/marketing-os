import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { repositoryRoot } from "../src/config.js";
import { classifyToken, emailCodeFor, inventory, renderMarkdown } from "../src/inventory.js";
import { REPORT_PATH } from "../src/inventory-cli.js";

const resolvable = new Set(["customer", "unsubscribe_url", "abandoned_checkout", "line_item"]);

test("token classifier separates real variables from authoring placeholders", () => {
  assert.equal(classifyToken('customer.first_name | default: "there"', resolvable), "resolved");
  assert.equal(classifyToken("unsubscribe_url", resolvable), "resolved");
  assert.equal(classifyToken("last_viewed_product", resolvable), "unresolved-variable");
  assert.equal(classifyToken("deal.hsc_quote_base_type", resolvable), "unresolved-variable");
  assert.equal(classifyToken("dynamic: the 3 bestselling systems", resolvable), "authoring-placeholder");
  assert.equal(classifyToken("image: the bench, mid-ventilation", resolvable), "authoring-placeholder");
  assert.equal(classifyToken("promo code — auto-apply at checkout", resolvable), "authoring-placeholder");
});

test("email codes match the canonical Campaign OS codes", () => {
  assert.equal(emailCodeFor("04-cr-4.html"), "CR-4");
  assert.equal(emailCodeFor("13-pp-7b.html"), "PP-7b", "casing must come from the manifest, not the filename");
  assert.equal(emailCodeFor("34-nl-01.html"), "NL-01");
});

test("every email code resolves to a canonical Campaign OS Issue", async () => {
  const report = await inventory();
  const issues = JSON.parse(
    await fs.readFile(path.resolve(repositoryRoot, "github-campaign-os/issue-sync-report.json"), "utf8")
  ).issues as Record<string, number>;
  for (const source of report.sources) {
    assert.ok(issues[`email:${source.emailCode}`], `no canonical Issue for ${source.emailCode}`);
  }
});

test("inventory covers all 53 sources and never reports a blocked source as ready", async () => {
  const report = await inventory();
  assert.equal(report.total, 53);
  assert.equal(report.ready + report.blocked, 53);
  assert.equal(new Set(report.sources.map(source => source.emailCode)).size, 53);
  for (const source of report.sources) {
    if (source.blocker === "none") {
      assert.equal(source.message, "");
      assert.equal(source.liveUnresolvedVariables.length, 0);
      assert.equal(source.liveAuthoringPlaceholders.length, 0);
    } else {
      assert.notEqual(source.message, "");
    }
  }
});

test("a source blocked only by a build note has clean live copy", async () => {
  const report = await inventory();
  for (const source of report.sources.filter(item => item.blocker === "build-note-comment")) {
    assert.equal(source.liveUnresolvedVariables.length, 0);
    assert.equal(source.liveAuthoringPlaceholders.length, 0);
    assert.ok(source.commentUnresolvedVariables.length > 0);
  }
});

test("the committed readiness report is reproducible from the sources", async () => {
  const expected = renderMarkdown(await inventory());
  const actual = await fs.readFile(path.resolve(repositoryRoot, REPORT_PATH), "utf8");
  assert.equal(actual, expected, `${REPORT_PATH} is stale; run npm run inventory -- --write`);
});
