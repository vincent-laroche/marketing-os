# Email preview emergency withdrawal

This is the complete rollback path for a public GitHub Pages email preview. It withdraws the
public surface and clears the canonical Campaign OS URL without rewriting publication history.
It does not send, schedule, activate, or alter any Shopify email.

## Authority and stopping rules

- An owner request or a safety incident recorded on the canonical Email Issue is required.
- Pages, repository visibility, DNS, and Cloudflare are separate external surfaces. Never make
  the private repository public as a workaround for missing GitHub Pages entitlement.
- A withdrawal is complete only when the public URL is unavailable, the withdrawal event is
  merged, the regenerated manifest is merged, and the Email Issue plus Project `Preview URL`
  read back blank.
- Do not delete or edit an earlier ledger event. The ledger is append-only.
- This emergency path is allowed only when the target is the sole active public Email. The
  withdrawal CLI enforces that invariant. Once multiple previews are public, use a selective
  remaining-set deployment; never disable Pages and withdraw only one ledger entry.

## Complete withdrawal sequence

1. On the canonical Email Issue, record the reason, incident evidence, requested scope, and
   owner approval. Open a dedicated rollback pull request.
2. Set the exact Email selection's `preview_public` value to `false`. Merge that reviewed source
   change before altering public hosting. Record the merged 40-character SHA and pull request.
3. Before altering hosting, run the fail-closed withdrawal preflight from the merged rollback
   revision. It verifies that the target is the sole active public Email, the exact rollback revision
   is merged to `main`, that revision sets `preview_public: false`, the source remains present, and
   exactly one merged pull request is associated with the supplied SHA and PR number:

   ```sh
   GH_TOKEN="$(gh auth token)" npx tsx tools/email-preview/src/publication.ts withdraw-preflight \
     --ledger email-previews/publication-ledger.json \
     --email-code CR-1 \
     --source-sha 0000000000000000000000000000000000000000 \
     --canonical-pr 000
   ```

   Stop before the hosting mutation if this command fails. Then validate a generated zero-public
   gallery and disable GitHub Pages for the repository through the GitHub API. This is an approval-gated
   external write. Read the Pages endpoint back as disabled and verify the former canonical URL
   no longer returns the preview. If any public file is still reachable, the rollback has failed.

   ```sh
   zero_site="$(mktemp -d)"
   npm --prefix tools/email-preview run gallery -- "$zero_site"
   npx tsx tools/email-preview/src/publication.ts validate-gallery --site "$zero_site"
   trash "$zero_site"
   ```
4. After the public URL is confirmed unavailable, generate a withdrawal candidate from the same
   merged rollback revision. Candidate generation repeats the full preflight before writing evidence.
   Use the former active
   Email code, the merged rollback SHA and PR, the Pages disable/deployment identity, the workflow
   or manual operation identity, and one approved reason:

   ```sh
   GH_TOKEN="$(gh auth token)" npx tsx tools/email-preview/src/publication.ts withdraw-candidate \
     --ledger email-previews/publication-ledger.json \
     --email-code CR-1 \
     --source-sha 0000000000000000000000000000000000000000 \
     --canonical-pr 000 \
     --pages-deployment-id pages-disabled-000 \
     --workflow-run-id manual-issue-000 \
     --workflow-attempt 1 \
     --reason safety-rollback \
     --out withdrawal.json
   ```

   Both preflight and candidate generation fail unless the ledger has exactly one active Email, the supplied SHA is
   merged to `main`, that revision sets the exact selection to `preview_public: false`, the source
   remains present, and the supplied PR is the unique merged PR associated with that revision.

5. Append the candidate with the validated CLI, commit only
   `email-previews/publication-ledger.json`, and merge that ledger-only pull request:

   ```sh
   npx tsx tools/email-preview/src/publication.ts append \
     --ledger email-previews/publication-ledger.json \
     --candidate withdrawal.json
   ```

6. From a clean checkout of the new `main`, regenerate the Campaign OS manifest. Review and merge
   that manifest-only change. An unmerged withdrawal must not clear the Project field.
7. Run the normal Campaign OS Issue and Project synchronization. Read back the exact Email item
   through GraphQL and confirm `Preview URL` is blank; also confirm the canonical Email Issue no
   longer advertises a public preview.
8. Recheck the former canonical URL over HTTPS. Record the Pages-disabled response, merged ledger
   event, merged manifest revision, Issue evidence, and exact Project-field read-back on the
   canonical Email Issue.

## Re-publication

Re-publication is a new reviewed event from a newer committed source revision. Re-enable Pages only
after the normal public-preview gates pass, dispatch the exact merged SHA, read back every public
file, and merge the new ledger event before Campaign OS exposes the URL again. Historical publish
and withdrawal events remain unchanged.
