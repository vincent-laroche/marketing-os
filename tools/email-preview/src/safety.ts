import { parse } from "parse5";

const forbidden = [/https?:\/\/[^"']*(checkout|unsubscribe)/i, /customer[_-]?id/i, /access_token/i, /[?&](token|key|signature)=/i];
const approvedPublicMailto = new Set(["info@hairsolutions.co"]);

export function assertSafeRenderedHtml(html: string): void {
  parse(html);
  if (/{{|{%|}}|%}/.test(html)) throw new Error("unsafe preview: unresolved Liquid");
  for (const pattern of forbidden) {
    if (pattern.test(html)) throw new Error(`unsafe preview: forbidden customer-specific value (${pattern.source})`);
  }
  for (const match of html.matchAll(/mailto:([^"'\s>]+)/gi)) {
    let address: string;
    try {
      address = decodeURIComponent(match[1].split("?", 1)[0]).toLowerCase();
    } catch {
      throw new Error("unsafe preview: direct email address");
    }
    if (!approvedPublicMailto.has(address)) throw new Error("unsafe preview: direct email address");
  }
  if (!/<meta[^>]+name=["']robots["'][^>]+noindex/i.test(html)) {
    html = html.replace(/<head>/i, '<head><meta name="robots" content="noindex,nofollow">');
  }
}

export function injectNoIndex(html: string): string {
  return /<meta[^>]+name=["']robots["']/i.test(html)
    ? html
    : html.replace(/<head>/i, '<head><meta name="robots" content="noindex,nofollow">');
}
