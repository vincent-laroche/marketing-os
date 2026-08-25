import fs from "node:fs";
import path from "node:path";
import { z } from "zod";

const configSchema = z.object({
  schema_version: z.literal(1),
  default_persona: z.string().min(1),
  default_state: z.string().min(1),
  preview_public: z.boolean(),
  allowed_source_root: z.literal("shopify-messaging/emails"),
  outputs: z.tuple([z.literal("rendered.html"), z.literal("desktop.png"), z.literal("mobile.png")])
});

export const packageRoot = path.resolve(import.meta.dirname, "..");
export const repositoryRoot = path.resolve(packageRoot, "../..");

export function loadConfig() {
  return configSchema.parse(JSON.parse(fs.readFileSync(path.join(packageRoot, "preview-config.json"), "utf8")));
}

export function loadFixture(persona: string, state: string): Record<string, unknown> {
  const base = JSON.parse(fs.readFileSync(path.join(packageRoot, "fixtures/personas", `${persona}.json`), "utf8"));
  const override = JSON.parse(fs.readFileSync(path.join(packageRoot, "fixtures/states", `${state}.json`), "utf8"));
  return deepMerge(base, override);
}

function deepMerge(left: Record<string, unknown>, right: Record<string, unknown>): Record<string, unknown> {
  const result = structuredClone(left);
  for (const [key, value] of Object.entries(right)) {
    const current = result[key];
    result[key] = value && current && typeof value === "object" && typeof current === "object" && !Array.isArray(value) && !Array.isArray(current)
      ? deepMerge(current as Record<string, unknown>, value as Record<string, unknown>)
      : value;
  }
  return result;
}
