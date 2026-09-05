// Export a composition from the Unlayer editor back into the repository.
//
// WHERE IT WRITES, AND WHY NOT shopify-messaging/emails/
//
// Two of Vincent's decisions pull against each other:
//
//   - The AGENTS.md §1 amendment (#138) allows composition to originate in the Unlayer block
//     editor rather than the Module Stack CSV.
//   - The return-to-palette decision (2026-09-05, #141) makes every one of the 53 emails
//     builder output, with KNOWN_DIVERGENT empty and enforced by
//     tests/email_operations/test_build53_reproducibility.py.
//
// Writing composed HTML over shopify-messaging/emails/ would break the second immediately and
// reintroduce the untracked hand-edit drift that hid a regression for twelve days.
//
// So a composition is written to shopify-messaging/composed/ instead. The builder's output
// stays canonical and reproducible; a composition is a reviewable proposal beside it, and the
// difference between the two is visible rather than silent. Promoting a composition into the
// canonical set stays a deliberate, separate act.
//
// The ledger records the declared module order (from the CSV) against the composed order, so
// the §1 amendment's "descriptive, not generative" is auditable rather than asserted.
import { readFileSync, writeFileSync, mkdirSync, existsSync, readdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { join } from 'node:path';

const REPO = join(process.cwd(), '..');
const OUT_DIR = join(REPO, 'shopify-messaging', 'composed');
const LEDGER = join(OUT_DIR, 'composition-ledger.json');
const EMAILS_CSV_GLOB = 'emails_master';

const sha256 = s => createHash('sha256').update(s).digest('hex');

function headSha() {
  try {
    return execFileSync('git', ['rev-parse', 'HEAD'], { cwd: REPO }).toString().trim();
  } catch { return null; }
}

function worktreeClean() {
  try {
    return execFileSync('git', ['status', '--porcelain'], { cwd: REPO }).toString().trim() === '';
  } catch { return false; }
}

/** Module order declared in the Email Reference File.
 *
 * Parsed by the repository's own module_map, not re-implemented here: the CSV has quoted
 * fields containing newlines and commas, and a line-splitting parser silently returns the
 * wrong stack rather than failing.
 */
export function declaredStack(file) {
  const py = `
import csv, glob, json, os, re, sys
sys.path.insert(0, os.path.join("tools", "build53"))
import module_map as mm
code = re.sub(r"^\\d+-", "", sys.argv[1]).replace(".html", "").upper()
path = glob.glob(os.path.join("Email Reference File", "emails_master*_all.csv"))[0]
for row in csv.DictReader(open(path, encoding="utf-8")):
    if row["Email name"].upper().startswith(code + " "):
        print(json.dumps([mm.family_of(raw) for _req, raw in mm.parse_stack(row["Module Stack"])]))
        break
else:
    print("[]")
`;
  try {
    const out = execFileSync('python3', ['-c', py, file], { cwd: REPO }).toString().trim();
    return JSON.parse(out);
  } catch {
    return [];
  }
}

/** Module order actually composed, read back from the exported HTML's own markers. */
export function composedOrder(html) {
  return [...html.matchAll(/<!-- module: ([^>]+?) -->/g)].map(m => m[1].trim());
}

export function writeComposition({ file, html, design }) {
  if (!/^[0-9]{2}-[a-z0-9-]+\.html$/.test(file)) throw new Error(`unsafe filename: ${file}`);
  mkdirSync(OUT_DIR, { recursive: true });

  const canonicalPath = join(REPO, 'shopify-messaging', 'emails', file);
  const canonical = existsSync(canonicalPath) ? readFileSync(canonicalPath, 'utf8') : null;

  const composed = composedOrder(html);
  const declared = declaredStack(file);

  const entry = {
    file,
    composed_at: new Date().toISOString(),
    source_commit_sha: headSha(),
    source_worktree_clean: worktreeClean(),
    canonical_sha256: canonical ? sha256(canonical) : null,
    composed_sha256: sha256(html),
    identical_to_canonical: canonical === html,
    declared_module_order: declared,
    composed_module_order: composed,
    order_changed: JSON.stringify(declared) !== JSON.stringify(composed),
    bytes: html.length,
    shopify_limit_bytes: 50 * 1024,
    over_shopify_limit: html.length >= 50 * 1024,
  };

  writeFileSync(join(OUT_DIR, file), html, 'utf8');
  writeFileSync(join(OUT_DIR, file.replace(/\.html$/, '.design.json')),
                JSON.stringify(design, null, 2), 'utf8');

  const ledger = existsSync(LEDGER)
    ? JSON.parse(readFileSync(LEDGER, 'utf8'))
    : { schema_version: 1, note: 'Compositions are proposals beside the builder output, never a replacement for it.', events: [] };
  ledger.events.push(entry);
  writeFileSync(LEDGER, JSON.stringify(ledger, null, 2) + '\n', 'utf8');

  return entry;
}
