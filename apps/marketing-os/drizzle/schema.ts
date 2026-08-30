import { int, json, longtext, mysqlEnum, mysqlTable, text, timestamp, varchar } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  /**
   * Surrogate primary key. Auto-incremented numeric value managed by the database.
   * Use this for relations between tables.
   */
  id: int("id").autoincrement().primaryKey(),
  /** Manus OAuth identifier (openId) returned from the OAuth callback. Unique per user. */
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

export const canonicalCampaigns = mysqlTable("canonicalCampaigns", {
  emailKey: varchar("emailKey", { length: 48 }).primaryKey(),
  sourceDigest: varchar("sourceDigest", { length: 64 }).notNull(),
  sourcePath: varchar("sourcePath", { length: 255 }).notNull(),
  series: varchar("series", { length: 32 }).notNull(),
  shopifySurface: varchar("shopifySurface", { length: 32 }).notNull(),
  sourceStatus: varchar("sourceStatus", { length: 32 }).notNull(),
  canonicalDocument: json("canonicalDocument").notNull(),
  syncedAt: timestamp("syncedAt").defaultNow().onUpdateNow().notNull(),
});

export const emailRevisions = mysqlTable("emailRevisions", {
  id: int("id").autoincrement().primaryKey(),
  emailKey: varchar("emailKey", { length: 48 }).notNull(),
  sourceDigest: varchar("sourceDigest", { length: 64 }).notNull(),
  provider: varchar("provider", { length: 32 }).notNull().default("beefree"),
  providerDocument: longtext("providerDocument").notNull(),
  renderedHtml: longtext("renderedHtml"),
  subject: text("subject"),
  previewText: text("previewText"),
  createdBy: int("createdBy"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export const qaRuns = mysqlTable("qaRuns", {
  id: int("id").autoincrement().primaryKey(),
  emailKey: varchar("emailKey", { length: 48 }).notNull(),
  revisionId: int("revisionId"),
  status: varchar("status", { length: 32 }).notNull(),
  summary: text("summary").notNull(),
  checks: json("checks").notNull(),
  createdBy: int("createdBy"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export const exportPackages = mysqlTable("exportPackages", {
  id: int("id").autoincrement().primaryKey(),
  emailKey: varchar("emailKey", { length: 48 }).notNull(),
  sourceDigest: varchar("sourceDigest", { length: 64 }).notNull(),
  checksum: varchar("checksum", { length: 64 }).notNull(),
  renderedHtml: longtext("renderedHtml").notNull(),
  manifest: json("manifest").notNull(),
  artifactKey: varchar("artifactKey", { length: 512 }).notNull(),
  artifactUrl: text("artifactUrl").notNull(),
  qaSummary: text("qaSummary").notNull(),
  status: varchar("status", { length: 32 }).notNull().default("exported"),
  createdBy: int("createdBy"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export const flowRecipeVersions = mysqlTable("flowRecipeVersions", {
  id: int("id").autoincrement().primaryKey(),
  journey: varchar("journey", { length: 96 }).notNull(),
  version: varchar("version", { length: 32 }).notNull(),
  checksum: varchar("checksum", { length: 64 }).notNull(),
  definition: json("definition").notNull(),
  createdBy: int("createdBy"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export const exportPackageScreenshots = mysqlTable("exportPackageScreenshots", {
  id: int("id").autoincrement().primaryKey(),
  exportPackageId: int("exportPackageId").notNull(),
  viewport: varchar("viewport", { length: 32 }).notNull(),
  storageKey: varchar("storageKey", { length: 512 }).notNull(),
  storageUrl: text("storageUrl").notNull(),
  capturedBy: int("capturedBy"),
  capturedAt: timestamp("capturedAt").defaultNow().notNull(),
});

export const exportPackageScreenshotManifests = mysqlTable("exportPackageScreenshotManifests", {
  id: int("id").autoincrement().primaryKey(),
  exportPackageId: int("exportPackageId").notNull(),
  checksum: varchar("checksum", { length: 64 }).notNull(),
  manifest: json("manifest").notNull(),
  artifactKey: varchar("artifactKey", { length: 512 }).notNull(),
  artifactUrl: text("artifactUrl").notNull(),
  createdBy: int("createdBy"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export const productSnapshots = mysqlTable("productSnapshots", {
  id: int("id").autoincrement().primaryKey(),
  emailKey: varchar("emailKey", { length: 48 }).notNull(),
  productId: varchar("productId", { length: 128 }).notNull(),
  title: text("title").notNull(),
  handle: varchar("handle", { length: 255 }).notNull(),
  status: varchar("status", { length: 32 }).notNull(),
  featuredImageUrl: text("featuredImageUrl"),
  price: varchar("price", { length: 48 }),
  capturedBy: int("capturedBy"),
  capturedAt: timestamp("capturedAt").defaultNow().notNull(),
});

export const shopifyHandoffEvidence = mysqlTable("shopifyHandoffEvidence", {
  id: int("id").autoincrement().primaryKey(),
  emailKey: varchar("emailKey", { length: 48 }).notNull(),
  targetSurface: varchar("targetSurface", { length: 32 }).notNull(),
  shopifyDraftUrl: text("shopifyDraftUrl").notNull(),
  evidenceNote: text("evidenceNote").notNull(),
  status: varchar("status", { length: 32 }).notNull().default("shopify_draft_verified"),
  createdBy: int("createdBy"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export const auditEvents = mysqlTable("auditEvents", {
  id: int("id").autoincrement().primaryKey(),
  eventType: varchar("eventType", { length: 64 }).notNull(),
  emailKey: varchar("emailKey", { length: 48 }),
  detail: json("detail").notNull(),
  actorId: int("actorId"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export const marketingSyncReceipts = mysqlTable("marketingSyncReceipts", {
  runId: varchar("runId", { length: 64 }).primaryKey(),
  source: varchar("source", { length: 48 }).notNull(),
  status: varchar("status", { length: 32 }).notNull(),
  recordCount: int("recordCount").notNull(),
  changedCount: int("changedCount").notNull(),
  blockedCount: int("blockedCount").notNull(),
  completedAt: timestamp("completedAt").notNull(),
  receivedAt: timestamp("receivedAt").defaultNow().onUpdateNow().notNull(),
});
