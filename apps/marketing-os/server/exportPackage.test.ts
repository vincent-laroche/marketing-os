import { describe, expect, it } from "vitest";
import { getCanonicalEmail } from "./canonical";
import { buildExportArtifact, buildScreenshotEvidenceManifest } from "./exportPackage";
import { evaluateEmailQa } from "./qa";

describe("immutable export package", () => {
  it("preserves evidence and extracts image and UTM manifests deterministically", () => {
    const email = getCanonicalEmail("BR-1");
    expect(email).toBeTruthy();
    const html = '<a href="https://example.com/shop?utm_source=shopify&utm_medium=email&utm_campaign=br-1">Shop</a><img src="https://cdn.example.com/product.jpg" alt="Product" />';
    const qa = evaluateEmailQa("BR-1", html);
    const input = { email: email!, renderedHtml: html, providerDocument: '{"page":{}}', revisionId: 3, qa, productSnapshots: [], generatedAt: "2026-08-25T00:00:00.000Z" };
    const first = buildExportArtifact(input);
    const second = buildExportArtifact(input);
    expect(first.checksum).toBe(second.checksum);
    expect(first.manifest.imageManifest).toEqual(["https://cdn.example.com/product.jpg"]);
    expect(first.manifest.utmManifest).toHaveLength(1);
    expect(first.document.providerDocument).toBe('{"page":{}}');
    expect(first.manifest.screenshots.status).toBe("manual_visual_capture_required");
  });

  it("links screenshot uploads through a separately immutable evidence manifest", () => {
    const evidence = buildScreenshotEvidenceManifest({
      exportPackageId: 17,
      exportChecksum: "a".repeat(64),
      screenshots: [{ id: 4, viewport: "desktop", storageUrl: "/manus-storage/example.png", capturedAt: "2026-08-25T00:00:00.000Z" }],
      generatedAt: "2026-08-25T01:00:00.000Z",
    });
    expect(evidence.checksum).toHaveLength(64);
    expect(evidence.manifest.screenshots[0].viewport).toBe("desktop");
    expect(evidence.manifest.status).toBe("evidence_attached");
  });
});
