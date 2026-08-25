import fs from "node:fs/promises";
import path from "node:path";
import { loadConfig, loadFixture, repositoryRoot } from "./config.js";
import { renderLiquid } from "./liquid.js";
import { assertSafeRenderedHtml, injectNoIndex } from "./safety.js";

/**
 * Source-readiness inventory for the Shopify Messaging emails.
 *
 * The renderer is the ground truth for ready/blocked: a source is ready only when it
 * renders and clears every safety gate. This module adds the *reason* a source is
 * rejected, so a real business-data gap is never confused with a mechanical defect.
 *
 * It classifies. It never repairs a source and never relaxes a gate.
 */

/** How a `{{ … }}` token stands against the fictional fixtures. */
export type TokenKind = "resolved" | "unresolved-variable" | "authoring-placeholder";

/** Why a source is blocked, named after how it must be remediated. */
export type Blocker =
  /** Renders and clears every safety gate. */
  | "none"
  /** Only a `<!-- BUILD NOTE -->` comment carries an unresolved token. Mechanical. */
  | "build-note-comment"
  /** Live copy references a real dynamic value with no Shopify variable decided. */
  | "unresolved-variable"
  /** Live copy carries a loud placeholder standing in for real business data. */
  | "authoring-placeholder"
  /** Rendered, but a safety gate rejected the output. */
  | "safety";

export interface SourceReport {
  file: string;
  emailCode: string;
  blocker: Blocker;
  message: string;
  liveUnresolvedVariables: string[];
  liveAuthoringPlaceholders: string[];
  commentUnresolvedVariables: string[];
}

export interface Inventory {
  schema_version: 1;
  total: number;
  ready: number;
  blocked: number;
  byBlocker: Partial<Record<Blocker, number>>;
  sources: SourceReport[];
}

const COMMENT = /<!--[\s\S]*?-->/g;
const OUTPUT = /\{\{([\s\S]*?)\}\}/g;
/** A Liquid output expression: an identifier path, optionally filtered. */
const EXPRESSION = /^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*(\s*\|[\s\S]+)?$/;

/** `04-cr-4.html` becomes `CR-4`, the canonical code used by the Campaign OS manifest. */
export function emailCodeFor(file: string): string {
  return path.basename(file, ".html").replace(/^\d+-/, "").toUpperCase();
}

export function classifyToken(body: string, resolvable: ReadonlySet<string>): TokenKind {
  const token = body.trim();
  if (!EXPRESSION.test(token)) return "authoring-placeholder";
  const root = token.split("|")[0]!.trim().split(".")[0]!;
  return resolvable.has(root) ? "resolved" : "unresolved-variable";
}

function tokensIn(text: string): string[] {
  return [...text.matchAll(OUTPUT)].map(match => match[1]!.trim());
}

/** Roots the fixture supplies, plus the bindings `{% for %}` introduces while rendering. */
function resolvableRoots(fixture: Record<string, unknown>): Set<string> {
  return new Set([...Object.keys(fixture), "line_item", "forloop"]);
}

export async function inventory(): Promise<Inventory> {
  const config = loadConfig();
  const directory = path.resolve(repositoryRoot, config.allowed_source_root);
  const files = (await fs.readdir(directory)).filter(file => file.endsWith(".html")).sort();
  const fixture = loadFixture(config.default_persona, config.default_state);
  const resolvable = resolvableRoots(fixture);

  const sources: SourceReport[] = [];
  for (const file of files) {
    const source = await fs.readFile(path.join(directory, file), "utf8");
    const comments = source.match(COMMENT)?.join("\n") ?? "";
    const live = source.replace(COMMENT, "");

    const collect = (text: string, kind: TokenKind) =>
      [...new Set(tokensIn(text).filter(token => classifyToken(token, resolvable) === kind))].sort();

    const liveUnresolvedVariables = collect(live, "unresolved-variable");
    const liveAuthoringPlaceholders = collect(live, "authoring-placeholder");
    const commentUnresolvedVariables = collect(comments, "unresolved-variable");

    let blocker: Blocker = "none";
    let message = "";
    try {
      const rendered = injectNoIndex(await renderLiquid(source, fixture));
      try {
        assertSafeRenderedHtml(rendered);
      } catch (error) {
        blocker = "safety";
        message = error instanceof Error ? error.message : String(error);
      }
    } catch (error) {
      message = error instanceof Error ? error.message : String(error);
      blocker = liveAuthoringPlaceholders.length > 0
        ? "authoring-placeholder"
        : liveUnresolvedVariables.length > 0
          ? "unresolved-variable"
          : "build-note-comment";
    }

    sources.push({
      file,
      emailCode: emailCodeFor(file),
      blocker,
      message,
      liveUnresolvedVariables,
      liveAuthoringPlaceholders,
      commentUnresolvedVariables
    });
  }

  const byBlocker: Partial<Record<Blocker, number>> = {};
  for (const source of sources) byBlocker[source.blocker] = (byBlocker[source.blocker] ?? 0) + 1;

  return {
    schema_version: 1,
    total: sources.length,
    ready: sources.filter(source => source.blocker === "none").length,
    blocked: sources.filter(source => source.blocker !== "none").length,
    byBlocker,
    sources
  };
}

const HEADINGS: Record<Exclude<Blocker, "none">, string> = {
  "build-note-comment": "Blocked only by a `<!-- BUILD NOTE -->` comment",
  "unresolved-variable": "Blocked by an undecided dynamic variable in live copy",
  "authoring-placeholder": "Blocked by a loud placeholder standing in for real business data",
  safety: "Blocked by a safety gate"
};

const cell = (values: string[]) =>
  values.length === 0 ? "—" : values.map(value => "`" + value.replace(/\|/g, "\\|") + "`").join("<br>");

/** Deterministic report. Regenerated by `npm run inventory -- --write`. */
export function renderMarkdown(report: Inventory): string {
  const lines = [
    "# Shopify Messaging source-readiness inventory",
    "",
    "> Generated by `tools/email-preview/src/inventory.ts`. Do not edit by hand.",
    "> Regenerate with `npm --prefix tools/email-preview run inventory -- --write`.",
    "",
    "A source is **ready** only when the fail-closed preview compiler renders it against the",
    "fictional fixtures and it clears every safety gate. Nothing here is a send approval.",
    "",
    `**${report.ready} ready · ${report.blocked} blocked · ${report.total} total.**`,
    "",
    "| Blocker | Emails | Remediation |",
    "|---|---:|---|",
    `| Ready | ${report.byBlocker.none ?? 0} | None. |`,
    `| \`build-note-comment\` | ${report.byBlocker["build-note-comment"] ?? 0} | Mechanical. The live copy is clean; a build note still carries an untranslated merge tag. |`,
    `| \`unresolved-variable\` | ${report.byBlocker["unresolved-variable"] ?? 0} | Decide the Shopify variable, then add a fictional fixture value. Requires Vincent. |`,
    `| \`authoring-placeholder\` | ${report.byBlocker["authoring-placeholder"] ?? 0} | Supply the real business data. Must stay blocked until then. |`,
    `| \`safety\` | ${report.byBlocker.safety ?? 0} | Fix the source. Never relax the gate. |`,
    ""
  ];

  for (const blocker of ["none", "build-note-comment", "unresolved-variable", "authoring-placeholder", "safety"] as const) {
    const group = report.sources.filter(source => source.blocker === blocker);
    if (group.length === 0) continue;
    lines.push(`## ${blocker === "none" ? "Ready" : HEADINGS[blocker]} (${group.length})`, "");
    lines.push("| Email | Source | Live variables | Live placeholders | Build-note variables |", "|---|---|---|---|---|");
    for (const source of group) {
      lines.push(
        `| ${source.emailCode} | \`${source.file}\` | ${cell(source.liveUnresolvedVariables)} | ${cell(source.liveAuthoringPlaceholders)} | ${cell(source.commentUnresolvedVariables)} |`
      );
    }
    lines.push("");
  }

  return lines.join("\n");
}
