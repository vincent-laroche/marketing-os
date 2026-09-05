// Does Shopify Liquid survive the Unlayer HTML exporter untouched?
// Uses the exact token forms found in shopify-messaging/emails/*.html.
import { writeFileSync } from 'node:fs';
import { randomUUID } from 'node:crypto';
import { loadEnv } from './env.mjs';
const { UNLAYER_PAT_TOKEN: TOKEN } = loadEnv(['UNLAYER_PAT_TOKEN']);

const TOKENS = [
  '{{ customer.first_name }}',
  '{{ customer.first_name | default: "there" }}',
  '{{ checkout.url }}',
  '{{ unsubscribe_url }}',
  '{{ line_item.product_title }}',
  '{{ abandoned_checkout.remaining_products_count }}',
  '{% if customer.first_name %}Hi{% else %}Hello{% endif %}',
  '{% for line_item in line_items %}{{ line_item.quantity }}{% endfor %}',
];

const html = `<table role="presentation" width="100%"><tr><td>
${TOKENS.map(t => `<p>${t}</p>`).join('\n')}
<a href="{{ checkout.url }}">Return to cart</a>
<a href="{{ unsubscribe_url }}">Unsubscribe</a>
</td></tr></table>`;

const design = {
  counters: { u_row: 1, u_column: 1, u_content_html: 1 },
  schemaVersion: 21,
  body: {
    id: randomUUID(),
    rows: [{
      id: 'r1', cells: [1],
      columns: [{ id: 'c1', contents: [{ id: 'h1', type: 'html', values: { html, containerPadding: '0px', _meta: {} } }], values: {} }],
      values: { padding: '0px' },
    }],
    values: { backgroundColor: 'transparent', contentWidth: '600px' },
  },
};

const res = await fetch('https://api.unlayer.com/v3/templates/export/html?projectId=289096', {
  method: 'POST',
  headers: { Authorization: `Bearer ${TOKEN}`, 'Content-Type': 'application/json', Accept: 'application/json' },
  body: JSON.stringify({ displayMode: 'email', design }),
});
const body = await res.json();
const out = body?.data?.html ?? body?.html;
writeFileSync('liquid-export.html', out ?? '');
console.log('status', res.status, '| bytes', (out || '').length, '\n');

let failed = 0;
for (const t of TOKENS) {
  const ok = out.includes(t);
  if (!ok) failed++;
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${t}`);
}
// The classic failure: quotes or braces HTML-escaped, or Liquid URL-encoded inside href.
const hazards = [
  ['no &quot; escaping of Liquid', !/\{\{[^}]*&quot;/.test(out)],
  ['no &#123; brace escaping',     !/&#123;/.test(out)],
  ['href Liquid not URL-encoded',  !/href="[^"]*%7B%7B/.test(out)],
  ['{% %} tags intact',            /\{%[^%]*%\}/.test(out)],
];
console.log('');
for (const [label, ok] of hazards) { if (!ok) failed++; console.log(`${ok ? 'PASS' : 'FAIL'}  ${label}`); }
console.log(`\n${failed ? `${failed} FAILED` : 'ALL LIQUID SURVIVED INTACT'}`);
