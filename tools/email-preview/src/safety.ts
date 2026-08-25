import { parse } from "parse5";

const forbidden = [/https?:\/\/[^"']*(checkout|unsubscribe)/i, /customer[_-]?id/i, /access_token/i, /[?&](token|key|signature)=/i];

export function assertSafeRenderedHtml(html: string): void {
  parse(html);
  if (/{{|{%|}}|%}/.test(html)) throw new Error("unsafe preview: unresolved Liquid");
  for (const pattern of forbidden) {
    if (pattern.test(html)) throw new Error(`unsafe preview: forbidden customer-specific value (${pattern.source})`);
  }
  if (/mailto:[^"']+@/i.test(html)) throw new Error("unsafe preview: direct email address");
  if (!/<meta[^>]+name=["']robots["'][^>]+noindex/i.test(html)) {
    html = html.replace(/<head>/i, '<head><meta name="robots" content="noindex,nofollow">');
  }
}

export function injectNoIndex(html: string): string {
  return /<meta[^>]+name=["']robots["']/i.test(html)
    ? html
    : html.replace(/<head>/i, '<head><meta name="robots" content="noindex,nofollow">');
}
