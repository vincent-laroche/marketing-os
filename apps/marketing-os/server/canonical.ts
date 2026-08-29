import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

export type CanonicalEmail = {
  key: string;
  name: string;
  body: string;
  buildStatus: string;
  cta: string;
  channel: string;
  missingModules: string;
  moduleStack: string;
  modulesUsed: string;
  position: string;
  previewText: string;
  series: string;
  seriesTotal: string;
  subject: string;
  subscriptionType: string;
  workflowIds: string;
  sourceDigest: string;
  sourceStatus: "source_blocked" | "needs_input" | "ready";
  blockers: string[];
  dependencies: string[];
  shopifySurface: "Messaging" | "Flow" | "Campaign";
};

const currentDir = dirname(fileURLToPath(import.meta.url));
const canonicalCsvPath = join(currentDir, "data", "canonical-emails.csv");
let cachedEmails: CanonicalEmail[] | null = null;

function parseCsv(csv: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = "";
  let quoted = false;

  for (let index = 0; index < csv.length; index += 1) {
    const char = csv[index];
    const next = csv[index + 1];

    if (quoted && char === '"' && next === '"') {
      field += '"';
      index += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (!quoted && char === ",") {
      row.push(field);
      field = "";
    } else if (!quoted && (char === "\n" || char === "\r")) {
      if (char === "\r" && next === "\n") index += 1;
      row.push(field);
      if (row.some(value => value.length > 0)) rows.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }

  row.push(field);
  if (row.some(value => value.length > 0)) rows.push(row);
  return rows;
}

function asRecord(headers: string[], row: string[]) {
  return headers.reduce<Record<string, string>>((record, header, index) => {
    record[header] = row[index] ?? "";
    return record;
  }, {});
}

function getShopifySurface(key: string, series: string): CanonicalEmail["shopifySurface"] {
  if (key.startsWith("NL-")) return "Campaign";
  if (key.startsWith("CR-") || key.startsWith("BR-") || key.startsWith("W-")) return "Messaging";
  if (series.toLowerCase().includes("newsletter")) return "Campaign";
  return "Flow";
}

function toList(value: string) {
  return value
    .split(/\n|;|\|/)
    .map(item => item.trim())
    .filter(Boolean);
}

function deriveStatus(record: Record<string, string>) {
  const blockers = toList(record["Missing Modules"]);
  const body = record.Body || "";
  const dependencies: string[] = [];
  const addDependency = (condition: boolean, label: string) => {
    if (condition) dependencies.push(label);
  };

  addDependency(/\bGATED\b/i.test(body), "Audience or form dependency");
  addDependency(/\[(?:OFFER|TBC|TODO|INSERT|CONFIRM)[^\]]*\]/i.test(body), "Real-data input required");
  addDependency(/story|testimonial/i.test(record["Modules Used"] || "") && /placeholder|real customer/i.test(body), "Approved customer proof required");

  if (blockers.length > 0) return { sourceStatus: "source_blocked" as const, blockers, dependencies };
  if (dependencies.length > 0) return { sourceStatus: "needs_input" as const, blockers, dependencies };
  return { sourceStatus: "ready" as const, blockers, dependencies };
}

export function getCanonicalEmails(): CanonicalEmail[] {
  if (cachedEmails) return cachedEmails;

  const [headers, ...rows] = parseCsv(readFileSync(canonicalCsvPath, "utf8"));
  cachedEmails = rows
    .map(row => asRecord(headers, row))
    .filter(record => record["Email name"]?.trim())
    .map(record => {
      const name = record["Email name"].trim();
      const key = name.split("·")[0]?.trim() || name;
      const { sourceStatus, blockers, dependencies } = deriveStatus(record);
      const sourceDigest = createHash("sha256")
        .update([name, record.Body, record.Subject, record["Preview Text"], record["Module Stack"]].join("\u0000"))
        .digest("hex");

      return {
        key,
        name,
        body: record.Body || "",
        buildStatus: record["Build Status"] || "Unclassified",
        cta: record.CTA || "",
        channel: record["Email Channel"] || "Email",
        missingModules: record["Missing Modules"] || "",
        moduleStack: record["Module Stack"] || "",
        modulesUsed: record["Modules Used"] || "",
        position: record.Position || "",
        previewText: record["Preview Text"] || "",
        series: record.Series || "Unassigned",
        seriesTotal: record["Series Total"] || "",
        subject: record.Subject || "",
        subscriptionType: record["Subscription Type"] || "",
        workflowIds: record["Workflow IDs"] || "",
        sourceDigest,
        sourceStatus,
        blockers,
        dependencies,
        shopifySurface: getShopifySurface(key, record.Series || ""),
      };
    })
    .sort((left, right) => left.key.localeCompare(right.key, undefined, { numeric: true }));

  return cachedEmails;
}

export function getCanonicalEmail(emailKey: string) {
  return getCanonicalEmails().find(email => email.key === emailKey) ?? null;
}

export type JourneyRecipe = {
  version: string;
  target: string;
  rule: string;
  safety: string;
  steps: string[];
  collisionRule: string;
  exitRule: string;
  frequencyRule: string;
};

export function getJourneyRecipe(journey: string): JourneyRecipe {
  const recipes: Record<string, JourneyRecipe> = {
    "J1 · Post-Purchase": {
      version: "2026.08.25",
      target: "Shopify Flow + Messaging",
      rule: "Post-purchase sequence; PP-4 is fulfilment-triggered. Apply journey-j1-active at entry and remove it at completion.",
      safety: "J4 cannot enroll while journey-j1-active is present.",
      steps: ["Order or fulfilment trigger", "Apply journey-j1-active", "Deliver approved sequence through the manually configured Shopify surface", "Clear journey-j1-active on completion"],
      collisionRule: "J1 takes precedence over J4.",
      exitRule: "Completion clears the enrollment tag; purchase-related content is never sent outside the approved sequence.",
      frequencyRule: "Journey emails take precedence over newsletter eligibility.",
    },
    "J2 · Cart Recovery": {
      version: "2026.08.25",
      target: "Shopify Messaging",
      rule: "Native abandoned-cart, checkout, and browse recovery sequence. Apply journey-j2-active only while enrolled.",
      safety: "A purchase exits recovery before a delayed message can release.",
      steps: ["Native cart, checkout, or browse event", "Apply journey-j2-active", "Run approved native Messaging sequence", "Exit and clear tag on purchase or sequence completion"],
      collisionRule: "Active J2 customers are excluded from newsletter selection.",
      exitRule: "A purchase exits recovery before delayed delivery.",
      frequencyRule: "Journey emails win the two-per-seven-day cap.",
    },
    "J3 · Win-Back": {
      version: "2026.08.25",
      target: "Shopify Flow",
      rule: "Lapsed-customer sequence that concludes in a real sunset decision.",
      safety: "Do not enroll while journey-j4-active is present; sunset must suppress future contact.",
      steps: ["Lapsed-customer segment check", "Confirm journey-j4-active is absent", "Apply journey-j3-active", "Run approved sequence", "Apply sunset suppression or clear tag at completion"],
      collisionRule: "J4 takes precedence; J3 is suppressed until J4 exits.",
      exitRule: "Sunset must produce an enforceable future-contact suppression state.",
      frequencyRule: "Active J3 customers are excluded from newsletter selection.",
    },
    "J4 · Reorder": {
      version: "2026.08.25",
      target: "Shopify Flow",
      rule: "Delivery-based reorder timing with journey-j4-active applied only during enrollment.",
      safety: "J1 has precedence. Purchase exits and completion clears journey-j4-active.",
      steps: ["Delivery-based timing check", "Confirm journey-j1-active is absent", "Apply journey-j4-active", "Run approved reorder sequence", "Exit on purchase and clear tag"],
      collisionRule: "J1 takes precedence; J4 suppresses J3 while active.",
      exitRule: "Purchase exits the sequence and clears journey-j4-active.",
      frequencyRule: "Journey emails win the two-per-seven-day cap.",
    },
    "J5 · Consultation": {
      version: "2026.08.25",
      target: "Shopify Flow",
      rule: "Customer joined segment based on consultation-interest, because Basic does not support Send HTTP Request.",
      safety: "Tag-driven entry only; do not create an external trigger or activate automatically.",
      steps: ["Customer receives consultation-interest tag", "Customer joins approved J5 segment", "Apply journey-j5-active", "Run manually installed Flow recipe", "Clear tag on completion or approved exit"],
      collisionRule: "J5-active customers are excluded from newsletter selection.",
      exitRule: "Completion or explicit exit clears journey-j5-active.",
      frequencyRule: "Active J5 customers are excluded from newsletter selection.",
    },
    "W · Newsletter Welcome": {
      version: "2026.08.25",
      target: "Shopify Messaging",
      rule: "Native welcome automation, gated on the newsletter capture form.",
      safety: "Keep inactive until the form and consent path are verified.",
      steps: ["Verified newsletter form consent", "Join eligible welcome audience", "Run manually configured native Messaging sequence", "Record verification evidence"],
      collisionRule: "Welcome eligibility must respect the global frequency guardrail.",
      exitRule: "Consent withdrawal or unsubscribe blocks future delivery.",
      frequencyRule: "Journey emails take precedence over newsletter campaigns.",
    },
    "N · Newsletter Programme": {
      version: "2026.08.25",
      target: "Shopify Messaging Campaigns",
      rule: "One-off campaigns with a recomputed audience at every send.",
      safety: "Two marketing emails per contact per seven days; journeys always win the slot.",
      steps: ["Recompute eligible audience", "Exclude suppression and active J2/J3/J5 enrollment tags", "Prepare campaign package", "Create Shopify draft manually", "Record draft evidence and deliberate activation separately"],
      collisionRule: "Newsletter yields to all active journeys.",
      exitRule: "No automatic enrollment; each campaign is a separate deliberate review.",
      frequencyRule: "Maximum two marketing emails per contact per seven days.",
    },
  };

  return recipes[journey] ?? {
    version: "2026.08.25",
    target: "Shopify review required",
    rule: "No automated recipe has been generated for this source record.",
    safety: "Manual review required before any platform action.",
    steps: ["Review canonical source", "Resolve dependencies", "Create a deliberate Shopify review package"],
    collisionRule: "No automated collision behavior is defined.",
    exitRule: "No automated exit behavior is defined.",
    frequencyRule: "Manual review is required before any frequency decision.",
  };
}
