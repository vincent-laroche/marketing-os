// Generate Unlayer blocks from the Bone/Paper/Ink library — Bone and Ink only, Paper excluded
// per Vincent's request. The library is confirmed as the current approved palette
// (AGENTS.md §1 supersession, 2026-09-06) but is missing 29 of the 52 Atelier Zero v7 families
// (all footers, both CTA buttons, FAQ, testimonial — see #150). This generator covers only the
// 30 families that exist; it does not fill those gaps.
//
// Files here are already bare table fragments (no <html>/<body> to strip), unlike the v7
// previews this spike was originally built against.
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

// This spike runs inside a git worktree (.claude/worktrees/<name>/unlayer-spike). Most of the
// batch folders are git-tracked and so exist inside the worktree — but mailerlite-blocks/ is
// gitignored (AGENTS-level rule: vendored/scratch, never repo content) and therefore exists
// ONLY in the main checkout, never in any worktree. `divider` lives solely in that folder, so
// resolving every dir as `join(process.cwd(), '..')` silently dropped it — the catch-and-continue
// in buildFamilyMap() below turned a missing directory into a missing family, with no error.
// The reverse trap also exists: a batch folder authored inside a worktree (git-tracked, just not
// yet merged to main) exists ONLY there, not in the main checkout. So each source dir is resolved
// against the worktree root first, falling back to the main checkout — never one root for all.
const REPO = process.env.BPI_REPO_ROOT || '/Users/vMac/04_marketing/marketing-os';
const WORKTREE_ROOT = join(process.cwd(), '..');
const SOURCE_DIRS = [
  'reshade-batch-1', 'reshade-batch-2', 'reshade-batch-3',
  'wb1-master-assembly', 'module-proof-batch', 'mailerlite-blocks',
  // The 7 families #150's block inventory found missing even after the Figma gap-fill
  // (build-blocks-figma-gap.mjs): hero_text_led, text_block_generic,
  // plain_text_founder_wrapper, testimonial, faq, trust_badge_row, promo_code_block.
  // Sourced from the same governed Figma "Lifecycle Modules" canvas (#287:727), which is
  // where the true Bone/Ink pairs live — unlike the earlier gap-fill's 9 files, these all
  // have genuine Figma-evidenced Bone AND Ink variants, so they fit this shade-paired
  // generator directly rather than needing the flat-list shape.
  'figma-lifecycle-gap-batch',
];
const SHADES = ['bone', 'ink']; // Paper deliberately excluded.

const CATEGORY = [
  [/^commerce__|^product__/, 'Commerce'],
  [/^header__|^footer__|^divider$/, 'Structure'],
  [/^signal__/, 'Actions'],
  [/^photo__|^grid__|^hero__/, 'Media'],
  [/^list__|^comparison$|^review__|^stat__|^timeline$/, 'Lists & proof'],
];
const categoryOf = slug => CATEGORY.find(([re]) => re.test(slug))?.[1] ?? 'Text & layout';

const titleOf = slug => slug
  .replace(/__/g, ' — ')
  .replace(/_/g, ' ')
  .replace(/\b\w/g, c => c.toUpperCase())
  .replace(/\bCta\b/, 'CTA').replace(/\bFaq\b/, 'FAQ').replace(/\b3up\b/i, '3-up');

function buildFamilyMap() {
  const map = {};
  for (const dir of SOURCE_DIRS) {
    let root = WORKTREE_ROOT, entries;
    try { entries = readdirSync(join(root, dir)); }
    catch {
      root = REPO;
      try { entries = readdirSync(join(root, dir)); } catch { continue; }
    }
    for (const name of entries) {
      const m = /^(.+)__(bone|paper|ink)\.html$/.exec(name);
      if (!m) continue;
      const [, rawFam, shade] = m;
      const fam = rawFam.replace(/-off$/, '_off').replace('sign-off', 'sign_off');
      if (shade === 'paper') continue; // never sourced
      (map[fam] ??= {})[shade] = join(root, dir, name);
    }
  }
  // Keep only families with both required shades — a partial family would silently drop one
  // side of the picker rather than fail loudly.
  return Object.fromEntries(
    Object.entries(map).filter(([, shades]) => SHADES.every(s => shades[s])));
}

export function buildBonelnkBlocks() {
  const families = buildFamilyMap();
  const blocks = [];
  let n = 0;

  for (const [fam, shades] of Object.entries(families).sort(([a], [b]) => a.localeCompare(b))) {
    for (const shade of SHADES) {
      const html = readFileSync(shades[shade], 'utf8').trim();
      const i = ++n;
      const shadeLabel = shade === 'bone' ? 'Bone' : 'Ink';
      blocks.push({
        id: i,
        name: `${titleOf(fam)} (${shadeLabel})`,
        category: categoryOf(fam),
        tags: ['bone-paper-ink', fam, shade],
        displayMode: 'email',
        thumbnailUrl: null,
        data: {
          id: `bpi_${i}_row`,
          cells: [1],
          columns: [{
            id: `bpi_${i}_col`,
            contents: [{
              id: `bpi_${i}_html`,
              type: 'html',
              values: {
                html,
                containerPadding: '0px',
                _meta: { htmlID: `bpi_${i}_html`, htmlClassNames: `u_content_html az-bpi-${fam}` },
                anchor: '',
                hideable: true, deletable: true, draggable: true,
                duplicatable: true, selectable: true, locked: false,
              },
            }],
            values: {
              _meta: { htmlID: `bpi_${i}_col`, htmlClassNames: 'u_column' },
              border: {}, padding: '0px', backgroundColor: '',
            },
          }],
          values: {
            _meta: { htmlID: `bpi_${i}_row`, htmlClassNames: 'u_row' },
            anchor: '', locked: false, columns: false, padding: '0px',
            hideable: true, deletable: true, draggable: true, selectable: true,
            duplicatable: true, noStackMobile: false,
            backgroundColor: '', columnsBackgroundColor: '',
            backgroundImage: { url: '', fullWidth: true, repeat: 'no-repeat', size: 'custom', position: 'center' },
            hideDesktop: false,
          },
        },
      });
    }
  }
  return blocks;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const blocks = buildBonelnkBlocks();
  const byCat = {};
  for (const b of blocks) (byCat[b.category] ??= []).push(b.name);
  console.log(`generated ${blocks.length} blocks (${blocks.length / 2} families x Bone+Ink)\n`);
  for (const [cat, names] of Object.entries(byCat).sort()) {
    console.log(`${cat} (${names.length})`);
    for (const nm of names) console.log(`   ${nm}`);
  }
}
