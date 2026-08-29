import { desc, eq } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import { createHash } from "node:crypto";
import { auditEvents, canonicalCampaigns, emailRevisions, exportPackageScreenshotManifests, exportPackageScreenshots, exportPackages, flowRecipeVersions, InsertUser, productSnapshots, qaRuns, shopifyHandoffEvidence, users } from "../drizzle/schema";
import { ENV } from './_core/env';
import { CanonicalEmail, getCanonicalEmail, getCanonicalEmails, getJourneyRecipe } from "./canonical";
import { notifyOwner } from "./_core/notification";
import { buildExportArtifact, buildScreenshotEvidenceManifest } from "./exportPackage";
import type { QaResult } from "./qa";
import { deriveReleaseStage } from "./release";
import { storagePut } from "./storage";

let _db: ReturnType<typeof drizzle> | null = null;

// Lazily create the drizzle instance so local tooling can run without a DB.
export async function getDb() {
  if (!_db && process.env.DATABASE_URL) {
    try {
      _db = drizzle(process.env.DATABASE_URL);
    } catch (error) {
      console.warn("[Database] Failed to connect:", error);
      _db = null;
    }
  }
  return _db;
}

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) {
    throw new Error("User openId is required for upsert");
  }

  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot upsert user: database not available");
    return;
  }

  try {
    const values: InsertUser = {
      openId: user.openId,
    };
    const updateSet: Record<string, unknown> = {};

    const textFields = ["name", "email", "loginMethod"] as const;
    type TextField = (typeof textFields)[number];

    const assignNullable = (field: TextField) => {
      const value = user[field];
      if (value === undefined) return;
      const normalized = value ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    };

    textFields.forEach(assignNullable);

    if (user.lastSignedIn !== undefined) {
      values.lastSignedIn = user.lastSignedIn;
      updateSet.lastSignedIn = user.lastSignedIn;
    }
    if (user.role !== undefined) {
      values.role = user.role;
      updateSet.role = user.role;
    } else if (user.openId === ENV.ownerOpenId) {
      values.role = 'admin';
      updateSet.role = 'admin';
    }

    if (!values.lastSignedIn) {
      values.lastSignedIn = new Date();
    }

    if (Object.keys(updateSet).length === 0) {
      updateSet.lastSignedIn = new Date();
    }

    await db.insert(users).values(values).onDuplicateKeyUpdate({
      set: updateSet,
    });
  } catch (error) {
    console.error("[Database] Failed to upsert user:", error);
    throw error;
  }
}

export async function getUserByOpenId(openId: string) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get user: database not available");
    return undefined;
  }

  const result = await db.select().from(users).where(eq(users.openId, openId)).limit(1);

  return result.length > 0 ? result[0] : undefined;
}

function normalizeDbDate(value: Date | string | null | undefined) {
  return value instanceof Date ? value : value ? new Date(value) : null;
}

async function audit(eventType: string, detail: Record<string, unknown>, emailKey?: string, actorId?: number) {
  const db = await getDb();
  if (!db) return;
  await db.insert(auditEvents).values({ eventType, emailKey, detail, actorId });
}

async function syncCanonicalCampaignRecords() {
  const db = await getDb();
  if (!db) return;
  for (const email of getCanonicalEmails()) {
    await db.insert(canonicalCampaigns).values({
      emailKey: email.key,
      sourceDigest: email.sourceDigest,
      sourcePath: "Email Reference File/emails_master 831f4e0d84e0831992d481ae881cfede_all.csv",
      series: email.series,
      shopifySurface: email.shopifySurface,
      sourceStatus: email.sourceStatus,
      canonicalDocument: email,
    }).onDuplicateKeyUpdate({
      set: {
        sourceDigest: email.sourceDigest,
        series: email.series,
        shopifySurface: email.shopifySurface,
        sourceStatus: email.sourceStatus,
        canonicalDocument: email,
      },
    });
  }
}

async function persistFlowRecipeRecords(recipes: Awaited<ReturnType<typeof listFlowRecipes>>) {
  const db = await getDb();
  if (!db) return;
  for (const recipe of recipes) {
    const checksum = createHash("sha256").update(JSON.stringify(recipe)).digest("hex");
    const existing = await db.select().from(flowRecipeVersions).where(eq(flowRecipeVersions.checksum, checksum)).limit(1);
    if (existing.length) continue;
    await db.insert(flowRecipeVersions).values({ journey: recipe.journey, version: recipe.version, checksum, definition: recipe });
  }
}

export async function getCampaignPortfolio() {
  await syncCanonicalCampaignRecords();
  const canonical = getCanonicalEmails();
  const db = await getDb();
  if (!db) {
    return canonical.map(email => ({
      ...email,
      latestRevision: null,
      latestQa: null,
      latestHandoff: null,
      revisionCount: 0,
      releaseStage: deriveReleaseStage({ sourceStatus: email.sourceStatus, hasRevision: false, hasShopifyDraftEvidence: false }),
    }));
  }

  const [revisions, qa, handoffs] = await Promise.all([
    db.select().from(emailRevisions).orderBy(desc(emailRevisions.id)),
    db.select().from(qaRuns).orderBy(desc(qaRuns.id)),
    db.select().from(shopifyHandoffEvidence).orderBy(desc(shopifyHandoffEvidence.id)),
  ]);
  const latestRevision = new Map<string, typeof revisions[number]>();
  const revisionCount = new Map<string, number>();
  for (const revision of revisions) {
    revisionCount.set(revision.emailKey, (revisionCount.get(revision.emailKey) ?? 0) + 1);
    if (!latestRevision.has(revision.emailKey)) latestRevision.set(revision.emailKey, revision);
  }
  const latestQa = new Map<string, typeof qa[number]>();
  for (const item of qa) if (!latestQa.has(item.emailKey)) latestQa.set(item.emailKey, item);
  const latestHandoff = new Map<string, typeof handoffs[number]>();
  for (const item of handoffs) if (!latestHandoff.has(item.emailKey)) latestHandoff.set(item.emailKey, item);

  return canonical.map(email => ({
    ...email,
    latestRevision: latestRevision.get(email.key) ?? null,
    latestQa: latestQa.get(email.key) ?? null,
    latestHandoff: latestHandoff.get(email.key) ?? null,
    revisionCount: revisionCount.get(email.key) ?? 0,
    releaseStage: deriveReleaseStage({
      sourceStatus: email.sourceStatus,
      hasRevision: latestRevision.has(email.key),
      qaStatus: latestQa.get(email.key)?.status,
      hasShopifyDraftEvidence: latestHandoff.has(email.key),
    }),
  }));
}

export async function getCampaignDetail(emailKey: string) {
  const canonical = getCanonicalEmail(emailKey);
  if (!canonical) return null;
  const db = await getDb();
  if (!db) return { canonical, revisions: [], qaRuns: [], handoffs: [], exportPackages: [], productSnapshots: [], screenshots: [], screenshotManifests: [] };
  const [revisions, qa, handoffs, packages, snapshots, screenshotRecords, screenshotManifestRecords] = await Promise.all([
    db.select().from(emailRevisions).where(eq(emailRevisions.emailKey, emailKey)).orderBy(desc(emailRevisions.id)),
    db.select().from(qaRuns).where(eq(qaRuns.emailKey, emailKey)).orderBy(desc(qaRuns.id)),
    db.select().from(shopifyHandoffEvidence).where(eq(shopifyHandoffEvidence.emailKey, emailKey)).orderBy(desc(shopifyHandoffEvidence.id)),
    db.select().from(exportPackages).where(eq(exportPackages.emailKey, emailKey)).orderBy(desc(exportPackages.id)),
    db.select().from(productSnapshots).where(eq(productSnapshots.emailKey, emailKey)).orderBy(desc(productSnapshots.id)),
    db.select().from(exportPackageScreenshots).orderBy(desc(exportPackageScreenshots.id)),
    db.select().from(exportPackageScreenshotManifests).orderBy(desc(exportPackageScreenshotManifests.id)),
  ]);
  const packageIds = new Set(packages.map(item => item.id));
  return { canonical, revisions, qaRuns: qa, handoffs, exportPackages: packages, productSnapshots: snapshots, screenshots: screenshotRecords.filter(item => packageIds.has(item.exportPackageId)), screenshotManifests: screenshotManifestRecords.filter(item => packageIds.has(item.exportPackageId)) };
}

export async function attachExportPackageScreenshot(input: { exportPackageId: number; viewport: string; dataUrl: string; userId: number }) {
  const matched = input.dataUrl.match(/^data:image\/(png|jpeg|webp);base64,([A-Za-z0-9+/=]+)$/);
  if (!matched) throw new Error("Screenshot must be a PNG, JPEG, or WebP data URL.");
  const bytes = Buffer.from(matched[2], "base64");
  if (bytes.length > 4_000_000) throw new Error("Screenshot exceeds the 4 MB evidence limit.");
  const db = await getDb();
  if (!db) throw new Error("Screenshot evidence persistence is not available.");
  const packages = await db.select().from(exportPackages).where(eq(exportPackages.id, input.exportPackageId)).limit(1);
  const packageRecord = packages[0];
  if (!packageRecord) throw new Error("Export package not found.");
  const extension = matched[1] === "jpeg" ? "jpg" : matched[1];
  const artifact = await storagePut(`campaign-os/export-packages/${packageRecord.emailKey}/${packageRecord.id}/screenshots/${input.viewport}.${extension}`, bytes, `image/${matched[1]}`);
  const result = await db.insert(exportPackageScreenshots).values({
    exportPackageId: input.exportPackageId,
    viewport: input.viewport,
    storageKey: artifact.key,
    storageUrl: artifact.url,
    capturedBy: input.userId,
  });
  const screenshotId = Number((result as unknown as [{ insertId?: number }])[0]?.insertId ?? 0);
  const screenshots = await db.select().from(exportPackageScreenshots).where(eq(exportPackageScreenshots.exportPackageId, input.exportPackageId)).orderBy(desc(exportPackageScreenshots.id));
  const { manifest, checksum } = buildScreenshotEvidenceManifest({
    exportPackageId: input.exportPackageId,
    exportChecksum: packageRecord.checksum,
    screenshots,
    generatedAt: new Date().toISOString(),
  });
  const evidenceArtifact = await storagePut(`campaign-os/export-packages/${packageRecord.emailKey}/${input.exportPackageId}/screenshot-manifests/${checksum}.json`, JSON.stringify(manifest, null, 2), "application/json");
  const evidenceResult = await db.insert(exportPackageScreenshotManifests).values({
    exportPackageId: input.exportPackageId,
    checksum,
    manifest,
    artifactKey: evidenceArtifact.key,
    artifactUrl: evidenceArtifact.url,
    createdBy: input.userId,
  });
  const evidenceManifestId = Number((evidenceResult as unknown as [{ insertId?: number }])[0]?.insertId ?? 0);
  await audit("export_screenshot_recorded", { screenshotId, evidenceManifestId, exportPackageId: input.exportPackageId, viewport: input.viewport }, packageRecord.emailKey, input.userId);
  return { screenshotId, storageUrl: artifact.url, evidenceManifestId, evidenceManifestUrl: evidenceArtifact.url };
}

export async function captureProductSnapshot(input: { emailKey: string; product: { id: string; title: string; handle: string; status: string; featuredImageUrl: string | null; price: string | null }; userId: number }) {
  const db = await getDb();
  if (!db) throw new Error("Product snapshot persistence is not available.");
  const result = await db.insert(productSnapshots).values({
    emailKey: input.emailKey,
    productId: input.product.id,
    title: input.product.title,
    handle: input.product.handle,
    status: input.product.status,
    featuredImageUrl: input.product.featuredImageUrl,
    price: input.product.price,
    capturedBy: input.userId,
  });
  const snapshotId = Number((result as unknown as [{ insertId?: number }])[0]?.insertId ?? 0);
  await audit("product_snapshot_captured", { snapshotId, productId: input.product.id, handle: input.product.handle }, input.emailKey, input.userId);
  return { snapshotId };
}

export async function saveRevision(input: { emailKey: string; sourceDigest: string; providerDocument: string; renderedHtml?: string; subject?: string; previewText?: string; userId: number }) {
  const canonical = getCanonicalEmail(input.emailKey);
  if (!canonical) throw new Error("Canonical email not found.");
  if (input.sourceDigest !== canonical.sourceDigest) throw new Error("Revision source digest does not match the canonical source.");
  if ((input.subject ?? canonical.subject) !== canonical.subject) throw new Error("Revision subject must preserve the canonical source verbatim.");
  if ((input.previewText ?? canonical.previewText) !== canonical.previewText) throw new Error("Revision preview text must preserve the canonical source verbatim.");
  const db = await getDb();
  if (!db) throw new Error("Campaign persistence is not available.");
  const result = await db.insert(emailRevisions).values({
    emailKey: input.emailKey,
    sourceDigest: input.sourceDigest,
    providerDocument: input.providerDocument,
    renderedHtml: input.renderedHtml || null,
    subject: input.subject || null,
    previewText: input.previewText || null,
    createdBy: input.userId,
  });
  const revisionId = Number((result as unknown as [{ insertId?: number }])[0]?.insertId ?? 0);
  await audit("revision_saved", { revisionId, provider: "beefree", hasHtml: Boolean(input.renderedHtml) }, input.emailKey, input.userId);
  return { revisionId };
}

export async function saveQaRun(input: { emailKey: string; result: QaResult; userId: number }) {
  const db = await getDb();
  if (!db) throw new Error("QA persistence is not available.");
  await db.insert(qaRuns).values({
    emailKey: input.emailKey,
    status: input.result.status,
    summary: input.result.summary,
    checks: input.result.checks,
    createdBy: input.userId,
  });
  await audit("qa_completed", { status: input.result.status, summary: input.result.summary }, input.emailKey, input.userId);
  if (input.result.status === "qa_failed") {
    const failures = input.result.checks.filter(check => check.status === "fail").map(check => check.label).join(", ");
    const delivered = await notifyOwner({
      title: `Campaign OS · QA blocked for ${input.emailKey}`,
      content: `Deterministic QA failed for ${input.emailKey}. Blocking checks: ${failures || "review the QA report"}. No Shopify action was taken.`,
    });
    await audit("owner_notification_attempted", { type: "qa_failed", delivered }, input.emailKey, input.userId);
  }
}

export async function createExportPackage(input: { email: CanonicalEmail; renderedHtml: string; qa: QaResult; userId: number }) {
  const db = await getDb();
  if (!db) throw new Error("Export package persistence is not available.");
  const [revisions, snapshots] = await Promise.all([
    db.select().from(emailRevisions).where(eq(emailRevisions.emailKey, input.email.key)).orderBy(desc(emailRevisions.id)).limit(1),
    db.select().from(productSnapshots).where(eq(productSnapshots.emailKey, input.email.key)).orderBy(desc(productSnapshots.id)),
  ]);
  const revision = revisions[0] ?? null;
  const { manifest, document: artifactDocument, checksum } = buildExportArtifact({
    email: input.email,
    renderedHtml: input.renderedHtml,
    providerDocument: revision?.providerDocument ?? null,
    revisionId: revision?.id ?? null,
    qa: input.qa,
    productSnapshots: snapshots,
    generatedAt: new Date().toISOString(),
  });
  const artifact = await storagePut(`campaign-os/export-packages/${input.email.key}/${checksum}.json`, JSON.stringify(artifactDocument, null, 2), "application/json");
  const result = await db.insert(exportPackages).values({
    emailKey: input.email.key,
    sourceDigest: input.email.sourceDigest,
    checksum,
    renderedHtml: input.renderedHtml,
    manifest,
    artifactKey: artifact.key,
    artifactUrl: artifact.url,
    qaSummary: input.qa.summary,
    createdBy: input.userId,
  });
  const packageId = Number((result as unknown as [{ insertId?: number }])[0]?.insertId ?? 0);
  await audit("handoff_package_prepared", { packageId, checksum }, input.email.key, input.userId);
  const delivered = await notifyOwner({
    title: `Campaign OS · handoff package ready for ${input.email.key}`,
    content: `An immutable Shopify review package is ready for ${input.email.key}. The package is exported but has not created a draft, schedule, activation, audience change, or send.`,
  });
  await audit("owner_notification_attempted", { type: "handoff_ready", delivered, packageId }, input.email.key, input.userId);
  return { packageId, checksum, manifest, artifactUrl: artifact.url };
}

export async function recordHandoffEvidence(input: { emailKey: string; shopifyDraftUrl: string; evidenceNote: string; userId: number }) {
  const canonical = getCanonicalEmail(input.emailKey);
  if (!canonical) throw new Error("Canonical email not found.");
  const db = await getDb();
  if (!db) throw new Error("Handoff persistence is not available.");
  await db.insert(shopifyHandoffEvidence).values({
    emailKey: input.emailKey,
    targetSurface: canonical.shopifySurface,
    shopifyDraftUrl: input.shopifyDraftUrl,
    evidenceNote: input.evidenceNote,
    createdBy: input.userId,
  });
  await audit("shopify_draft_evidence_recorded", { targetSurface: canonical.shopifySurface }, input.emailKey, input.userId);
  return { recorded: true, status: "shopify_draft_verified" };
}

export async function listFlowRecipes() {
  const journeys = ["J1 · Post-Purchase", "J2 · Cart Recovery", "J3 · Win-Back", "J4 · Reorder", "J5 · Consultation", "W · Newsletter Welcome", "N · Newsletter Programme"];
  const recipes = journeys.map(journey => ({ journey, ...getJourneyRecipe(journey) }));
  await persistFlowRecipeRecords(recipes);
  return recipes;
}

export async function getRecentAuditEvents() {
  const db = await getDb();
  if (!db) return [];
  const events = await db.select().from(auditEvents).orderBy(desc(auditEvents.id)).limit(20);
  return events.map(event => ({ ...event, createdAt: normalizeDbDate(event.createdAt) }));
}

export async function notifySourceBlockers(userId: number) {
  const blocked = getCanonicalEmails().filter(email => email.sourceStatus !== "ready");
  const keys = blocked.map(email => email.key).join(", ");
  const delivered = await notifyOwner({
    title: `Campaign OS · ${blocked.length} source dependencies require review`,
    content: `Current source blockers or unresolved inputs: ${keys || "none"}. This is an owner notification only; no campaign, audience, Flow, or Shopify Messaging state was changed.`,
  });
  await audit("owner_notification_attempted", { type: "source_dependency_scan", delivered, blockedCount: blocked.length }, undefined, userId);
  return { delivered, blockedCount: blocked.length };
}
