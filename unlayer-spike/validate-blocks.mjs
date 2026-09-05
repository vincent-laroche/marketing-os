// Blocks are validated by SHAPE against a real console-created block read back from
// GET /blocks, not against POST /templates/validate: a block's `data` is a bare row
// object, while the design validator only accepts whole documents (counters + body).
//
// This exists because an earlier generator emitted `design: { body: { rows } }`. The
// palette grouped by category but rendered nothing, and no validator caught it.
import { buildBlocks } from './build-blocks.mjs';

const REQUIRED_BLOCK = ['id', 'name', 'category', 'tags', 'displayMode', 'data'];
const REQUIRED_ROW = ['id', 'cells', 'columns', 'values'];

const blocks = buildBlocks({ themes: ['light'] });
let bad = 0;

for (const b of blocks) {
  const problems = [];
  for (const k of REQUIRED_BLOCK) if (!(k in b)) problems.push(`missing ${k}`);
  if (!Array.isArray(b.tags)) problems.push('tags must be an array, not a string');

  const row = b.data ?? {};
  for (const k of REQUIRED_ROW) if (!(k in row)) problems.push(`data missing ${k}`);
  if ('body' in row || 'counters' in row) problems.push('data is a document, must be a bare row');

  const content = row.columns?.[0]?.contents?.[0];
  if (content?.type !== 'html') problems.push('content is not type html');

  const html = content?.values?.html ?? '';
  if (!html.trim()) problems.push('empty html');
  if (/<body|<!doctype/i.test(html)) problems.push('html still wrapped in a document');

  if (problems.length) { bad++; console.log(`INVALID  ${b.name}: ${problems.join('; ')}`); }
}

console.log(bad ? `\n${bad}/${blocks.length} invalid` : `\nall ${blocks.length} blocks structurally valid`);
process.exit(bad ? 1 : 0);
