export type ReleaseStage = "source_blocked" | "source_ready" | "creative_saved" | "qa_passed" | "shopify_draft_verified";

export function deriveReleaseStage(input: {
  sourceStatus: string;
  hasRevision: boolean;
  qaStatus?: string | null;
  hasShopifyDraftEvidence: boolean;
}): ReleaseStage {
  if (input.sourceStatus !== "ready") return "source_blocked";
  if (input.hasShopifyDraftEvidence) return "shopify_draft_verified";
  if (input.qaStatus === "qa_passed") return "qa_passed";
  if (input.hasRevision) return "creative_saved";
  return "source_ready";
}
