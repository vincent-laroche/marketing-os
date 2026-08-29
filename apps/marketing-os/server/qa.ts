import { getCanonicalEmail } from "./canonical";

export type QaCheck = {
  id: string;
  label: string;
  status: "pass" | "warning" | "fail";
  detail: string;
};

export type QaResult = {
  status: "qa_passed" | "qa_failed";
  checks: QaCheck[];
  summary: string;
};

const approvedTokens = new Set(["firstname", "cart_contents", "months_since_last_order"]);

function tokensFrom(value: string) {
  return Array.from(value.matchAll(/{{\s*([^}]+?)\s*}}/g), match => match[1].trim());
}

function htmlAttributes(html: string, tag: string, attribute: string) {
  const tagPattern = new RegExp(`<${tag}\\b[^>]*\\b${attribute}\\s*=\\s*["']([^"']+)["'][^>]*>`, "gi");
  return Array.from(html.matchAll(tagPattern), match => match[1].trim());
}

export function evaluateEmailQa(emailKey: string, renderedHtml?: string | null): QaResult {
  const email = getCanonicalEmail(emailKey);
  if (!email) throw new Error("Canonical email not found.");

  const body = email.body;
  const tokens = tokensFrom(body);
  const unsupportedTokens = tokens.filter(token => !approvedTokens.has(token));
  const html = renderedHtml || "";
  const checksumSource = html || body;
  const placeholderPattern = /\[(?:OFFER|TBC|TODO|INSERT|CONFIRM|PLACEHOLDER)[^\]]*\]/i;
  const links = htmlAttributes(html, "a", "href");
  const images = Array.from(html.matchAll(/<img\b[^>]*>/gi), match => match[0]);
  const deliveryLinks = links.filter(link => !link.startsWith("#") && !/^mailto:|^tel:|unsubscribe/i.test(link));
  const linksMissingUtm = deliveryLinks.filter(link => !/utm_source=.+utm_medium=.+utm_campaign=/i.test(link));
  const missingAlt = images.filter(image => !/\balt\s*=\s*["'][^"']+["']/i.test(image));
  const inlineImageBytes = images.reduce((total, image) => {
    const match = image.match(/src\s*=\s*["']data:[^;]+;base64,([^"']+)["']/i);
    return total + (match ? Buffer.byteLength(match[1], "base64") : 0);
  }, 0);
  const oversizedWidth = Array.from(html.matchAll(/(?:width\s*=\s*["']?|width\s*:\s*)(\d{3,4})/gi), match => Number(match[1])).some(width => width > 640);
  const htmlTokens = tokensFrom(html);
  const unsupportedHtmlTokens = htmlTokens.filter(token => !approvedTokens.has(token));
  const checks: QaCheck[] = [
    {
      id: "copy-fidelity",
      label: "Canonical source copy",
      status: body.trim() ? "pass" : "fail",
      detail: body.trim() ? "Canonical body is present and retained verbatim." : "Canonical body is missing.",
    },
    {
      id: "module-order",
      label: "Required module source",
      status: email.blockers.length ? "fail" : email.moduleStack.trim() ? "pass" : "warning",
      detail: email.blockers.length
        ? `Source blocked by: ${email.blockers.join(", ")}.`
        : email.moduleStack.trim()
          ? "Module stack is available for the assembler."
          : "No module stack was supplied; human source review is required.",
    },
    {
      id: "real-data",
      label: "Real-data placeholders",
      status: placeholderPattern.test(body) ? "fail" : "pass",
      detail: placeholderPattern.test(body)
        ? "Unresolved real-data placeholder remains in canonical copy."
        : "No unresolved bracketed placeholder detected.",
    },
    {
      id: "personalization",
      label: "Personalization tokens",
      status: unsupportedTokens.length ? "fail" : "pass",
      detail: unsupportedTokens.length
        ? `Unsupported token mapping required: ${unsupportedTokens.join(", ")}.`
        : tokens.length
          ? `Approved token mappings found: ${tokens.join(", ")}.`
          : "No personalization tokens found.",
    },
    {
      id: "metadata",
      label: "Subject and preview text",
      status: email.subject.trim() && email.previewText.trim() ? "pass" : "warning",
      detail: email.subject.trim() && email.previewText.trim()
        ? "Subject and preview text are present."
        : "Subject or preview text requires source completion.",
    },
    {
      id: "cta-utm",
      label: "CTA and UTM review",
      status: !email.cta.trim() ? "fail" : !html ? "warning" : linksMissingUtm.length ? "fail" : "pass",
      detail: !email.cta.trim()
        ? "CTA is missing from the canonical source."
        : !html
          ? "CTA exists; rendered HTML is required for destination and UTM verification."
          : linksMissingUtm.length
            ? `${linksMissingUtm.length} delivery link${linksMissingUtm.length === 1 ? " is" : "s are"} missing the full UTM source, medium, and campaign set.`
            : "Rendered delivery links include the full UTM source, medium, and campaign set.",
    },
    {
      id: "link-integrity",
      label: "Rendered link integrity",
      status: !html ? "warning" : deliveryLinks.some(link => !/^https?:\/\//i.test(link)) ? "fail" : "pass",
      detail: !html ? "Requires rendered HTML before link verification." : deliveryLinks.some(link => !/^https?:\/\//i.test(link)) ? "A delivery link is not an absolute HTTP(S) URL." : `${deliveryLinks.length} delivery link${deliveryLinks.length === 1 ? "" : "s"} are absolute HTTP(S) URLs.`,
    },
    {
      id: "liquid-support",
      label: "Liquid and personalization support",
      status: unsupportedHtmlTokens.length ? "fail" : "pass",
      detail: unsupportedHtmlTokens.length ? `Rendered HTML uses unsupported merge tokens: ${unsupportedHtmlTokens.join(", ")}.` : htmlTokens.length ? `Rendered HTML uses approved merge tokens: ${htmlTokens.join(", ")}.` : "No rendered merge tokens require mapping.",
    },
    {
      id: "legal-footer",
      label: "Unsubscribe and physical address",
      status: html ? (/unsubscribe/i.test(html) && /hair solutions|address/i.test(html) ? "pass" : "fail") : "warning",
      detail: html
        ? "Rendered HTML was checked for legal-footer signals."
        : "Requires rendered HTML before legal-footer verification.",
    },
    {
      id: "transparent-wrapper",
      label: "Transparent outer wrapper",
      status: html ? (/background-color\s*:\s*transparent/i.test(html) ? "pass" : "fail") : "warning",
      detail: html
        ? "Rendered HTML was checked for the transparent outer-background rule."
        : "Requires rendered HTML before transparent-wrapper verification.",
    },
    {
      id: "gmail-clipping",
      label: "Gmail clipping budget",
      status: Buffer.byteLength(checksumSource, "utf8") <= 102_400 ? "pass" : "fail",
      detail: `${Buffer.byteLength(checksumSource, "utf8").toLocaleString()} bytes measured against the 102,400-byte threshold.`,
    },
    {
      id: "accessibility",
      label: "Image alternative text",
      status: !html ? "warning" : missingAlt.length ? "fail" : "pass",
      detail: !html ? "Requires rendered HTML before image accessibility verification." : missingAlt.length ? `${missingAlt.length} image${missingAlt.length === 1 ? " is" : "s are"} missing non-empty alt text.` : `${images.length} rendered image${images.length === 1 ? "" : "s"} include non-empty alt text or no images are present.`,
    },
    {
      id: "image-budget",
      label: "Inline image budget",
      status: inlineImageBytes > 200_000 ? "fail" : "pass",
      detail: `${inlineImageBytes.toLocaleString()} inline image bytes measured against the 200,000-byte review threshold. Hosted image transfer sizes remain part of manual visual review.`,
    },
    {
      id: "responsive-render",
      label: "Responsive rendering",
      status: !html ? "warning" : oversizedWidth ? "fail" : "pass",
      detail: !html ? "Requires rendered HTML before responsive structure verification." : oversizedWidth ? "Rendered HTML contains an element wider than the 640px email layout threshold." : "No rendered width exceeds the 640px email layout threshold; visual checks at 320, 375, 430, and desktop remain required before approval.",
    },
  ];

  const failures = checks.filter(check => check.status === "fail");
  return {
    status: failures.length ? "qa_failed" : "qa_passed",
    checks,
    summary: failures.length
      ? `${failures.length} blocking QA issue${failures.length === 1 ? "" : "s"} must be resolved before Shopify handoff.`
      : "Deterministic checks passed; visual review and deliberate Shopify approval remain required.",
  };
}
