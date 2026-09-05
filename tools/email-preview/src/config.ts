import fs from "node:fs";
import path from "node:path";
import { z } from "zod";
import type { PreviewSelection } from "./types.js";

const selectionSchema = z.object({
  email_code: z.string().min(1),
  campaign_key: z.string().regex(/^campaign:/),
  source_path: z.string().startsWith("shopify-messaging/emails/").endsWith(".html"),
  persona: z.literal("normal-customer"),
  states: z.array(z.enum(["missing-first-name", "product-heavy"])).min(1),
  preview_public: z.boolean()
}).strict();

const configSchema = z.object({
  schema_version: z.literal(1),
  default_persona: z.string().min(1),
  default_state: z.string().min(1),
  allowed_source_root: z.literal("shopify-messaging/emails"),
  outputs: z.tuple([z.literal("rendered.html"), z.literal("desktop.png"), z.literal("mobile.png")]),
  selections: z.array(selectionSchema).length(53)
}).strict();

export const packageRoot = path.resolve(import.meta.dirname, "..");
/** Repository the inventory reads sources from.
 *
 * Overridable so the review workflow can run this exact compiler against a BASE_SHA worktree
 * and tell a *newly* failing preview from one that was already blocked and merely touched.
 * Without that comparison, any repository-wide change (an image-host migration, say) fails
 * the gate on every pre-existing blocker it happens to touch.
 *
 * Set only by CI. The default remains the checkout this package lives in.
 */
export const repositoryRoot = process.env.EMAIL_PREVIEW_REPO_ROOT
  ? path.resolve(process.env.EMAIL_PREVIEW_REPO_ROOT)
  : path.resolve(packageRoot, "../..");

export function loadConfig() {
  const config = configSchema.parse(JSON.parse(fs.readFileSync(path.join(packageRoot, "preview-config.json"), "utf8")));
  const manifest = JSON.parse(fs.readFileSync(path.join(repositoryRoot, "github-campaign-os/manifest.json"), "utf8")) as {records: Array<{key: string; email_code: string | null; parent_key: string | null; source_paths: string[]}>};
  const canonical = manifest.records.filter(record => record.key.startsWith("email:"));
  if (canonical.length !== 53 || config.selections.length !== canonical.length) throw new Error("preview config must select every canonical Email exactly once");
  const canonicalByCode = new Map(canonical.map(record => [record.email_code, record]));
  const selected = new Set<string>();
  for (const selection of config.selections) {
    const record = canonicalByCode.get(selection.email_code);
    if (!record || !record.parent_key || !record.source_paths.includes(selection.source_path) || record.parent_key !== selection.campaign_key || selected.has(selection.email_code)) {
      throw new Error("preview config selection does not match the canonical Campaign OS manifest");
    }
    selected.add(selection.email_code);
  }
  return config;
}

export function loadFixture(persona: string, states: string | string[]): Record<string, unknown> {
  const requested = typeof states === "string" ? [states] : states;
  if (persona !== "normal-customer" || requested.length === 0 || requested.some(state => !["missing-first-name", "product-heavy"].includes(state)) || /[/\\]/.test(persona + requested.join(""))) throw new Error("unknown fictional preview fixture");
  const base = personaSchema.parse(JSON.parse(fs.readFileSync(path.join(packageRoot, "fixtures/personas", `${persona}.json`), "utf8")));
  const fixture = requested.reduce((current, state) => deepMerge(current, stateSchema.parse(JSON.parse(fs.readFileSync(path.join(packageRoot, "fixtures/states", `${state}.json`), "utf8")))), base as Record<string, unknown>);
  Object.defineProperty(fixture, approvedPaths, {value: pathsOf(base), enumerable: false});
  return deepFreeze(fixture);
}

const productSchema = z.object({product_title: z.string().startsWith("Fictional"), variant_title: z.string(), quantity: z.number().int().positive()}).strict();
const personaSchema = z.object({
  customer: z.object({first_name: z.string()}).strict(),
  checkout: z.object({url: z.literal("#preview-inert-checkout")}).strict(),
  unsubscribe_url: z.literal("#preview-inert-unsubscribe"),
  abandoned_checkout: z.object({remaining_products_count: z.number().int().nonnegative(), line_items: z.array(productSchema).min(1)}).strict()
}).strict();
const stateSchema = z.discriminatedUnion("state", [
  z.object({state: z.literal("missing-first-name"), customer: z.object({first_name: z.null()}).strict()}).strict(),
  z.object({state: z.literal("product-heavy"), abandoned_checkout: z.object({remaining_products_count: z.number().int().nonnegative(), line_items: z.array(productSchema).length(5)}).strict()}).strict()
]);

function deepMerge(left: Record<string, unknown>, right: Record<string, unknown>): Record<string, unknown> {
  const result = structuredClone(left);
  for (const [key, value] of Object.entries(right)) {
    const current = result[key];
    result[key] = value && current && typeof value === "object" && typeof current === "object" && !Array.isArray(value) && !Array.isArray(current)
      ? deepMerge(current as Record<string, unknown>, value as Record<string, unknown>)
      : value === null ? undefined : value;
  if (value === null) delete result[key];
  }
  return result;
}

function deepFreeze<T>(value: T): T {
  if (value && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const nested of Object.values(value as Record<string, unknown>)) deepFreeze(nested);
  }
  return value;
}

export function selectionFor(config: ReturnType<typeof loadConfig>, args: Pick<PreviewSelection, "email_code" | "source_path" | "persona" | "campaign_key"> & {states: string[]}): PreviewSelection {
  const selection = config.selections.find(candidate => candidate.email_code === args.email_code);
  if (!selection || selection.source_path !== args.source_path || selection.persona !== args.persona || selection.campaign_key !== args.campaign_key || selection.states.length !== args.states.length || selection.states.some(state => !args.states.includes(state))) throw new Error("preview arguments do not match an approved canonical selection");
  return selection;
}

export const approvedPaths = Symbol("approved-fixture-paths");
export function fixtureAllowsPath(fixture: Record<string, unknown>, dotted: string): boolean {
  return ((fixture as Record<PropertyKey, unknown>)[approvedPaths] as Set<string> | undefined)?.has(dotted) ?? false;
}
function pathsOf(value: unknown, prefix = ""): Set<string> {
  const paths = new Set<string>();
  if (!value || typeof value !== "object") return paths;
  for (const [key, nested] of Object.entries(value as Record<string, unknown>)) {
    const current = prefix ? `${prefix}.${key}` : key; paths.add(current);
    for (const child of pathsOf(nested, current)) paths.add(child);
  }
  return paths;
}

export function canonicalIssueFor(emailCode: string): number {
  const report = JSON.parse(fs.readFileSync(path.join(repositoryRoot, "github-campaign-os/issue-sync-report.json"), "utf8")) as {issues: Record<string, number>};
  const issue = report.issues[`email:${emailCode}`];
  if (!Number.isInteger(issue) || issue < 1) throw new Error("canonical Email Issue is unavailable");
  return issue;
}
