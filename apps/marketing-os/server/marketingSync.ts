import { createHmac, timingSafeEqual } from "node:crypto";
import { desc, eq } from "drizzle-orm";
import { auditEvents, marketingSyncReceipts } from "../drizzle/schema";
import { getDb } from "./db";

export type MarketingSyncReceipt = {
  runId: string;
  source: "cloudflare-worker";
  status: "completed";
  recordCount: number;
  changedCount: number;
  blockedCount: number;
  completedAt: string;
};

export function verifyMarketingSyncSignature(rawBody: string, signature: string | undefined, secret: string | undefined) {
  if (!secret || !signature?.startsWith("sha256=")) return false;
  const expected = `sha256=${createHmac("sha256", secret).update(rawBody).digest("hex")}`;
  const received = signature;
  return expected.length === received.length && timingSafeEqual(Buffer.from(expected), Buffer.from(received));
}

export function parseMarketingSyncReceipt(value: unknown): MarketingSyncReceipt | null {
  if (!value || typeof value !== "object") return null;
  const input = value as Record<string, unknown>;
  const validCount = (item: unknown) => typeof item === "number" && Number.isInteger(item) && item >= 0;
  if (
    typeof input.runId !== "string" || !/^[A-Za-z0-9-]{8,64}$/.test(input.runId) ||
    input.source !== "cloudflare-worker" || input.status !== "completed" ||
    !validCount(input.recordCount) || !validCount(input.changedCount) || !validCount(input.blockedCount) ||
    typeof input.completedAt !== "string" || Number.isNaN(Date.parse(input.completedAt))
  ) return null;
  return input as MarketingSyncReceipt;
}

export async function recordMarketingSyncReceipt(receipt: MarketingSyncReceipt) {
  const db = await getDb();
  if (!db) throw new Error("Marketing sync receipt persistence is unavailable.");
  const completedAt = new Date(receipt.completedAt);
  await db.insert(marketingSyncReceipts).values({ ...receipt, completedAt }).onDuplicateKeyUpdate({
    set: { status: receipt.status, recordCount: receipt.recordCount, changedCount: receipt.changedCount, blockedCount: receipt.blockedCount, completedAt },
  });
  await db.insert(auditEvents).values({
    eventType: "notion_worker_sync_receipt",
    detail: { runId: receipt.runId, source: receipt.source, status: receipt.status, recordCount: receipt.recordCount, changedCount: receipt.changedCount, blockedCount: receipt.blockedCount },
  });
  return receipt;
}

export async function getMarketingSyncHealth() {
  const db = await getDb();
  if (!db) return { configured: Boolean(process.env.NOTION_API_KEY), latestRun: null };
  const [latestRun] = await db.select().from(marketingSyncReceipts).orderBy(desc(marketingSyncReceipts.receivedAt)).limit(1);
  return { configured: Boolean(process.env.NOTION_API_KEY), latestRun: latestRun ?? null };
}

export async function requestMarketingReconciliation(actorId: number) {
  const token = process.env.NOTION_API_KEY;
  const workerUrl = "https://marketing-os-notion-sync.notionsync.workers.dev/sync";
  if (!token) throw new Error("Notion synchronization is not configured.");
  const response = await fetch(workerUrl, { method: "POST", headers: { Authorization: `Bearer ${token}` } });
  if (!response.ok) throw new Error(`Synchronization Worker rejected the request (${response.status}).`);
  const result = await response.json() as { accepted: boolean; runId: string; recordCount?: number; changedCount?: number; blockedCount?: number };
  const db = await getDb();
  if (db) await db.insert(auditEvents).values({
    eventType: "notion_worker_reconciliation_requested",
    actorId,
    detail: { runId: result.runId, accepted: result.accepted, operations: "disabled" },
  });
  return { runId: result.runId, accepted: result.accepted, operations: "disabled" as const };
}
