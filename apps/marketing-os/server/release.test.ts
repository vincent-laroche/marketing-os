import { describe, expect, it } from "vitest";
import { deriveReleaseStage } from "./release";

describe("release-stage state machine", () => {
  it("fails closed until source, revision, QA, and manual Shopify evidence are present in order", () => {
    expect(deriveReleaseStage({ sourceStatus: "source_blocked", hasRevision: true, qaStatus: "qa_passed", hasShopifyDraftEvidence: true })).toBe("source_blocked");
    expect(deriveReleaseStage({ sourceStatus: "ready", hasRevision: false, hasShopifyDraftEvidence: false })).toBe("source_ready");
    expect(deriveReleaseStage({ sourceStatus: "ready", hasRevision: true, qaStatus: "qa_failed", hasShopifyDraftEvidence: false })).toBe("creative_saved");
    expect(deriveReleaseStage({ sourceStatus: "ready", hasRevision: true, qaStatus: "qa_passed", hasShopifyDraftEvidence: false })).toBe("qa_passed");
    expect(deriveReleaseStage({ sourceStatus: "ready", hasRevision: true, qaStatus: "qa_passed", hasShopifyDraftEvidence: true })).toBe("shopify_draft_verified");
  });
});
