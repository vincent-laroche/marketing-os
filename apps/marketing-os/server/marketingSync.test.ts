import { describe, expect, it } from "vitest";
import { createHmac } from "node:crypto";
import { parseMarketingSyncReceipt, verifyMarketingSyncSignature } from "./marketingSync";

const receipt = {
  runId: "a3d837bd-4a10-4c4d-9a2f-44f5b0e2a953",
  source: "cloudflare-worker",
  status: "completed",
  recordCount: 53,
  changedCount: 0,
  blockedCount: 0,
  completedAt: "2026-08-27T01:00:00.000Z",
} as const;

describe("Marketing OS synchronization receipts", () => {
  it("accepts a valid, aggregate-only Worker receipt", () => {
    expect(parseMarketingSyncReceipt(receipt)).toEqual(receipt);
  });

  it("rejects receipt payloads that include malformed run state or impossible counts", () => {
    expect(parseMarketingSyncReceipt({ ...receipt, status: "published" })).toBeNull();
    expect(parseMarketingSyncReceipt({ ...receipt, recordCount: -1 })).toBeNull();
  });

  it("requires an exact HMAC signature before accepting Worker input", () => {
    const raw = JSON.stringify(receipt);
    const secret = "test-notion-worker-secret";
    const signature = `sha256=${createHmac("sha256", secret).update(raw).digest("hex")}`;
    expect(verifyMarketingSyncSignature(raw, signature, secret)).toBe(true);
    expect(verifyMarketingSyncSignature(raw, "sha256=invalid", secret)).toBe(false);
  });
});
