import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import test from "node:test";

const root = path.resolve(import.meta.dirname, "../../..");

async function readWorkflow(name: string): Promise<string> {
  return fs.readFile(path.join(root, ".github/workflows", name), "utf8");
}

test("private review workflow is pull-request-only, minimally permissioned, pinned, and temporary", async () => {
  const workflow = await readWorkflow("email-preview-review.yml");
  assert.match(workflow, /pull_request:/);
  assert.doesNotMatch(workflow, /workflow_dispatch:/);
  assert.match(workflow, /contents:\s*read/);
  assert.match(workflow, /pull-requests:\s*write/);
  assert.match(workflow, /issues:\s*write/);
  assert.doesNotMatch(workflow, /pages:\s*(write|read)/);
  assert.match(workflow, /retention-days:\s*14/);
  for (const action of ["actions/checkout", "actions/setup-node", "actions/upload-artifact", "actions/github-script"]) {
    assert.match(workflow, new RegExp(`${action.replace(/[/.]/g, "[\\/.]")}@[0-9a-f]{40}`));
  }
  assert.match(workflow, /<!-- email-preview:begin -->/);
  assert.match(workflow, /<!-- email-preview:end -->/);
  assert.match(workflow, /expires_at/);
  assert.match(workflow, /github\.run_attempt/);
  assert.match(workflow, /run\", \"materialize/);
  assert.match(workflow, /gh run rerun/);
  assert.match(workflow, /\.\.\.summary\.successful, \.\.\.summary\.blocked/);
  assert.match(workflow, /Fail the review after preserving safe diagnostics/);
  assert.match(workflow, /change-policy/);
  assert.match(workflow, /npm --silent --prefix tools\/email-preview run inventory > preview-inventory\.json/);
  assert.match(workflow, /filter\(code => readyCodes\.has\(code\)\)/);
  assert.doesNotMatch(workflow, /Reproduce[^\n]*email-preview-publish/);
});

test("public publication is manual, accepts only Email code and exact SHA, and separates build/deploy/ledger permissions", async () => {
  const workflow = await readWorkflow("email-preview-publish.yml");
  const inputs = workflow.slice(workflow.indexOf("inputs:"), workflow.indexOf("permissions:"));
  assert.match(inputs, /email_code:/);
  assert.match(inputs, /source_sha:/);
  for (const forbidden of ["source_path:", "campaign:", "issue:", "pr:", "output_url:", "fixture"]) assert.doesNotMatch(inputs, new RegExp(forbidden));
  assert.match(workflow, /workflow_dispatch:/);
  assert.doesNotMatch(workflow, /pull_request:|push:|schedule:/);
  assert.match(workflow, /git merge-base --is-ancestor/);
  assert.match(workflow, /origin\/main/);
  assert.match(workflow, /preview_public/);
  assert.match(workflow, /pages:\s*write/);
  assert.match(workflow, /id-token:\s*write/);
  assert.match(workflow, /contents:\s*write/);
  assert.match(workflow, /pull-requests:\s*write/);
  assert.match(workflow, /pull-requests:\s*read/);
  assert.match(workflow, /actions:\s*read/);
  assert.match(workflow, /environment:\s*\n\s+name:\s+github-pages/);
  assert.match(workflow, /ledger-only|publication-ledger\.json/);
  assert.match(workflow, /pull request|pull-request/i);
  assert.match(workflow, /"run", "materialize"/);
  assert.match(workflow, /complete approved public set/);
  assert.match(workflow, /\.selections\[\].*preview_public == true/);
  assert.match(workflow, /for provenance in email-previews\/site\/\*\/provenance\.json/);
  assert.match(workflow, /for candidate in publication-candidates\/\*\.json/);
  assert.doesNotMatch(workflow, /find email-previews\/site[^\n]*\.versions/);
  assert.doesNotMatch(workflow, /gh pr edit/);
  assert.match(workflow, /merge the existing preview publication ledger PR/);
  assert.match(workflow, /git switch --force-create "\$LEDGER_BRANCH" origin\/main/);
  assert.match(workflow, /force-with-lease/);
  assert.match(workflow, /deployment_id:\s*\$\{\{ github\.sha \}\}/);
  assert.match(workflow, /github-pages-\$\{\{ github\.run_id \}\}-\$\{\{ github\.run_attempt \}\}/);
  assert.doesNotMatch(workflow, /steps\.deployment\.outputs\.deployment_id/);
  for (const action of ["actions/checkout", "actions/setup-node", "actions/configure-pages", "actions/upload-pages-artifact", "actions/deploy-pages"]) {
    assert.match(workflow, new RegExp(`${action.replace(/[/.]/g, "[\\/.]")}@[0-9a-f]{40}`));
  }
  assert.doesNotMatch(workflow, /github\.event\.inputs\.(source_path|issue|pr|campaign)/);
});
