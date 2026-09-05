// Seed an Unlayer design from an already-built email.
//
// The builder emits `<!-- module: <Family> -->` markers (build_emails.py email_doc), so a
// built email can be split back into its module fragments without re-running the build or
// re-deriving copy. Each fragment becomes one `content_html` in its own row, which is what
// makes the modules independently draggable in the editor.
//
// Head <style> blocks travel inside the first content, because the Unlayer design schema has
// no head-CSS field (body.values carries no style slot). The fidelity gate proved <style> and
// @media survive inside content_html.
import { readFileSync } from 'node:fs';
import { randomUUID } from 'node:crypto';

export function parseBuiltEmail(path) {
  const doc = readFileSync(path, 'utf8');

  const styles = [...doc.matchAll(/<style[^>]*>[\s\S]*?<\/style>/gi)].map(m => m[0]);

  const preheader = (/opacity:0;overflow:hidden;mso-hide:all;">([\s\S]*?)<\/div>/i.exec(doc)?.[1] ?? '')
    .replace(/&zwnj;|&nbsp;/g, '').trim();

  // Split on the module markers. Everything after the last module and before the closing
  // </td></tr></table> is the compliance strip, which is part of the final module's cell.
  const bodyMatch = /<body[^>]*>([\s\S]*)<\/body>/i.exec(doc);
  const body = bodyMatch ? bodyMatch[1] : doc;
  const parts = body.split(/<!-- module: ([^>]+?) -->/);

  const modules = [];
  for (let i = 1; i < parts.length; i += 2) {
    let frag = parts[i + 1] ?? '';
    // Trim the document tail off the final fragment.
    frag = frag.replace(/\n?<\/td><\/tr><\/table>\s*$/i, '');
    modules.push({ family: parts[i].trim(), html: frag.trim() });
  }
  return { styles, preheader, modules };
}

let n = 0;
const id = p => `${p}_${++n}`;

export function buildDesign({ styles, preheader, modules }) {
  const rows = modules.map((mod, i) => {
    // Re-attach the module marker the split consumed. It is what makes a composition
    // self-describing: the exported HTML carries its own module order, so the order can be
    // read back without trusting the design JSON, and a composition diffs against builder
    // output in the same shape.
    const marked = `<!-- module: ${mod.family} -->\n${mod.html}`;
    // Styles ride with the first module so they reach the export intact.
    const html = i === 0 && styles.length ? `${styles.join('\n')}\n${marked}` : marked;
    return {
      id: id('row'),
      cells: [1],
      columns: [{
        id: id('col'),
        contents: [{
          id: id('html'),
          type: 'html',
          values: {
            html,
            containerPadding: '0px',
            _meta: { htmlID: '', htmlClassNames: '' },
            // Surfaced in the editor so a module is identifiable while dragging.
            anchor: '',
            hideable: true, deletable: true, draggable: true, duplicatable: true,
          },
        }],
        values: {},
      }],
      values: { padding: '0px', backgroundColor: '', columns: false, noStackMobile: false },
    };
  });

  return {
    counters: { u_row: rows.length, u_column: rows.length, u_content_html: rows.length },
    schemaVersion: 21,
    body: {
      id: randomUUID(),
      rows,
      // AGENTS.md §5 — no page background; the client's own ground shows through.
      values: {
        backgroundColor: 'transparent',
        contentWidth: '600px',
        preheaderText: preheader,
        fontFamily: { label: 'Arial', value: 'arial,helvetica,sans-serif' },
      },
    },
  };
}
