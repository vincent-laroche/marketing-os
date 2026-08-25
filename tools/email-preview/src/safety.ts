import { parse, serialize } from "parse5";

const approvedPublicMailto = new Set(["info@hairsolutions.co"]);
const approvedHosts = new Set(["hairsolutions.co", "www.hairsolutions.co", "res.cloudinary.com"]);
const forbiddenTags = new Set(["script", "form", "iframe", "frame", "frameset", "object", "embed", "applet", "base"]);
const resourceAttributes = new Set(["href", "src", "action", "poster", "background", "xlink:href"]);
const sensitiveDestination = /(checkout|unsubscribe|preference|edit-notifications|account|tracking)/i;
const tokenLike = /(?:^|[?&;])(token|key|signature|access_token|customer[_-]?id|email)=/i;

type HtmlNode = {tagName?: string; nodeName?: string; attrs?: Array<{name: string; value: string}>; childNodes?: HtmlNode[]; value?: string};

export function injectNoIndex(html: string): string {
  const meta = '<meta name="robots" content="noindex,nofollow,noarchive">';
  return /<meta[^>]+name=["']robots["']/i.test(html)
    ? html.replace(/(<meta[^>]+name=["']robots["'][^>]+content=["'])[^"']*(["'][^>]*>)/i, "$1noindex,nofollow,noarchive$2")
    : html.replace(/<head(?:\s[^>]*)?>/i, match => match + meta);
}

/** Remove every live customer-specific destination before the HTML enters a browser. */
export function rewriteSensitiveLinks(html: string): string {
  const document = parse(html) as unknown as HtmlNode;
  walk(document, node => {
    if (!node.attrs) return;
    for (const attr of node.attrs) {
      if (attr.name.toLowerCase() !== "href") continue;
      const value = decodeHtmlUrl(attr.value);
      if (value.toLowerCase().startsWith("mailto:")) {
        const address = value.slice(7).split("?", 1)[0]!.toLowerCase();
        if (!approvedPublicMailto.has(address)) throw unsafe("direct email address");
      }
      if (sensitiveDestination.test(value)) {
        attr.value = "#preview-inert";
        setAttr(node.attrs, "aria-disabled", "true");
        setAttr(node.attrs, "data-preview-link-kind", destinationKind(value));
      }
    }
  });
  return serialize(document as never);
}

export function assertSafeRenderedHtml(html: string): void {
  if (/\{\{|\{%|}}|%}/.test(html)) throw unsafe("unresolved Liquid");
  if (!/<meta[^>]+name=["']robots["'][^>]+content=["'][^"']*noindex[^"']*nofollow[^"']*noarchive/i.test(html)) throw unsafe("missing preview robots policy");
  for (const address of html.match(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g) ?? []) {
    if (!approvedPublicMailto.has(address.toLowerCase())) throw unsafe("direct email address");
  }
  for (const comment of html.match(/<!--[\s\S]*?-->/g) ?? []) assertNoHiddenUrl(comment);
  const document = parse(html) as unknown as HtmlNode;
  walk(document, node => {
    const tag = node.tagName?.toLowerCase();
    if (tag && forbiddenTags.has(tag)) throw unsafe("active HTML element");
    if (!node.attrs) return;
    const attributes = new Map(node.attrs.map(attr => [attr.name.toLowerCase(), attr.value]));
    if ([...attributes.keys()].some(name => name.startsWith("on"))) throw unsafe("event handler attribute");
    if (tag === "link" && /stylesheet/i.test(attributes.get("rel") ?? "")) throw unsafe("remote stylesheet");
    if (tag === "style" && /@import|url\s*\(/i.test(textContent(node))) throw unsafe("remote stylesheet");
    for (const [name, raw] of attributes) {
      if (resourceAttributes.has(name)) assertSafeUrl(raw);
      if (name === "srcset") for (const candidate of raw.split(",")) assertSafeUrl(candidate.trim().split(/\s+/, 1)[0]!);
      if (name === "style") for (const url of cssUrls(raw)) assertSafeUrl(url);
      if (name.startsWith("data-")) assertNoHiddenUrl(raw);
    }
    if (tag === "img" && isTrackingPixel(attributes)) throw unsafe("tracking pixel");
  });
}

function assertNoHiddenUrl(value: string): void {
  for (const url of value.match(/(?:https?:|javascript:|data:|vbscript:)[^\s"'<>)]*/gi) ?? []) {
    if (tokenLike.test(decodeHtmlUrl(url)) || sensitiveDestination.test(url)) throw unsafe("hidden customer-specific value");
    if (/^https:\/\/github\.com\/vincent-laroche\/email-marketing-ops\/(issues|pull)\/\d+$/i.test(url)) continue;
    assertSafeUrl(url);
  }
}
function cssUrls(value: string): string[] { return [...value.matchAll(/url\(\s*(['"]?)(.*?)\1\s*\)/gi)].map(match => match[2]!); }
function isTrackingPixel(attributes: Map<string, string>): boolean {
  const source = decodeHtmlUrl(attributes.get("src") ?? "");
  const width = attributes.get("width") ?? ""; const height = attributes.get("height") ?? ""; const style = attributes.get("style") ?? "";
  const one = (value: string) => /(?:^|[^\d])1(?:px)?(?:$|[^\d])/i.test(value);
  return /^https:/i.test(source) && ((one(width) && one(height)) || (/width\s*:\s*1(?:px)?/i.test(style) && /height\s*:\s*1(?:px)?/i.test(style)) || /(?:pixel|tracking|1x1|[,_/-]w_?1[,_/-])/i.test(source));
}

function assertSafeUrl(raw: string): void {
  const value = decodeHtmlUrl(raw).trim();
  if (!value || value.startsWith("#") || value.startsWith("/")) return;
  if (value.toLowerCase().startsWith("mailto:")) {
    const address = value.slice(7).split("?", 1)[0]!.toLowerCase();
    if (!approvedPublicMailto.has(address) || value.includes("?")) throw unsafe("direct email address");
    return;
  }
  let url: URL;
  try { url = new URL(value); } catch { throw unsafe("unsafe URL"); }
  if (url.protocol !== "https:" || !approvedHosts.has(url.hostname) || tokenLike.test(url.search)) throw unsafe("unsafe remote resource");
}

function walk(node: HtmlNode, visit: (node: HtmlNode) => void): void {
  visit(node);
  for (const child of node.childNodes ?? []) walk(child, visit);
}

function textContent(node: HtmlNode): string {
  return (node.value ?? "") + (node.childNodes ?? []).map(textContent).join("");
}

function setAttr(attrs: Array<{name: string; value: string}>, name: string, value: string): void {
  const existing = attrs.find(attr => attr.name.toLowerCase() === name);
  if (existing) existing.value = value;
  else attrs.push({name, value});
}

function destinationKind(value: string): string {
  if (/checkout/i.test(value)) return "checkout";
  if (/unsubscribe|preference|edit-notifications/i.test(value)) return "preferences";
  if (/account/i.test(value)) return "account";
  return "tracking";
}

function decodeHtmlUrl(value: string): string { return value.replace(/&amp;/gi, "&"); }
function unsafe(reason: string): Error { return new Error(`unsafe preview: ${reason}`); }
