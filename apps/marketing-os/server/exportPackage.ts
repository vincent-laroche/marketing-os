import { createHash } from "node:crypto";
import type { CanonicalEmail } from "./canonical";
import type { QaResult } from "./qa";

export type ExportSnapshot = {
  productId: string;
  title: string;
  handle: string;
  status: string;
  price: string | null;
  capturedAt: Date | string;
};

export function buildExportArtifact(input: {
  email: CanonicalEmail;
  renderedHtml: string;
  providerDocument: string | null;
  revisionId: number | null;
  qa: QaResult;
  productSnapshots: ExportSnapshot[];
  generatedAt: string;
}) {
  const imageManifest = Array.from(input.renderedHtml.matchAll(/<img\b[^>]*\bsrc\s*=\s*["']([^"']+)["'][^>]*>/gi), match => match[1]);
  const utmManifest = Array.from(input.renderedHtml.matchAll(/https?:\/\/[^"'\s>]+/gi), match => match[0]).filter(url => /utm_source=/i.test(url));
  const manifest = {
    emailKey: input.email.key,
    sourceDigest: input.email.sourceDigest,
    provider: "beefree",
    revisionId: input.revisionId,
    subject: input.email.subject,
    previewText: input.email.previewText,
    cta: input.email.cta,
    mergeTagMap: { firstname: "Shopify customer first-name mapping with fallback" },
    productSnapshots: input.productSnapshots.map(snapshot => ({ ...snapshot, capturedAt: new Date(snapshot.capturedAt).toISOString() })),
    imageManifest,
    utmManifest,
    screenshots: {
      required: true,
      status: "manual_visual_capture_required",
      checklist: ["320px viewport", "375px viewport", "430px viewport", "desktop viewport", "Gmail dark-mode visual check"],
    },
    shopifyChecklist: [
      "Open Shopify Messaging manually.",
      "Create or update a draft only.",
      "Verify segment, sender, preview, and UTM values.",
      "Record draft URL and evidence in Campaign OS.",
      "Do not schedule, activate, or send from Campaign OS.",
    ],
  };
  const document = {
    manifest,
    renderedHtml: input.renderedHtml,
    providerDocument: input.providerDocument,
    qa: input.qa,
    generatedAt: input.generatedAt,
  };
  const checksum = createHash("sha256").update(JSON.stringify(document)).digest("hex");
  return { manifest, document, checksum };
}

export function buildScreenshotEvidenceManifest(input: {
  exportPackageId: number;
  exportChecksum: string;
  screenshots: Array<{ id: number; viewport: string; storageUrl: string; capturedAt: Date | string }>;
  generatedAt: string;
}) {
  const manifest = {
    exportPackageId: input.exportPackageId,
    exportChecksum: input.exportChecksum,
    screenshots: input.screenshots.map(screenshot => ({ ...screenshot, capturedAt: new Date(screenshot.capturedAt).toISOString() })),
    generatedAt: input.generatedAt,
    status: "evidence_attached",
  };
  const checksum = createHash("sha256").update(JSON.stringify(manifest)).digest("hex");
  return { manifest, checksum };
}
