import { Liquid } from "liquidjs";
import { fixtureAllowsPath } from "./config.js";

const engine = new Liquid({
  strictFilters: true,
  strictVariables: false,
  lenientIf: false,
  dynamicPartials: false
});

export async function renderLiquid(source: string, fixture: Record<string, unknown>): Promise<string> {
  assertAllowedLiquid(source);
  assertKnownVariables(source, fixture);
  let rendered: string;
  try {
    rendered = await engine.parseAndRender(source, fixture);
  } catch (error) {
    throw new Error("Liquid rendering failed closed");
  }
  if (/{{|{%|}}|%}/.test(rendered)) {
    throw new Error("Liquid rendering failed closed: unresolved Liquid remains");
  }
  return rendered;
}

function assertAllowedLiquid(source: string): void {
  for (const match of source.matchAll(/\{%\s*([\s\S]*?)\s*%\}/g)) {
    const token = match[1]!.trim();
    if (!/^(endif|endfor)$/.test(token) &&
      !/^if\s+[A-Za-z_][\w.]*\s*(==|!=|>|>=|<|<=)\s*(blank|\d+|"[^"]*"|'[^']*')$/.test(token) &&
      !/^for\s+[A-Za-z_]\w*\s+in\s+[A-Za-z_][\w.]*\s+limit:\d+$/.test(token)) {
      throw new Error("Liquid rendering failed closed: tag outside preview allowlist");
    }
  }
  for (const match of source.matchAll(/\{\{\s*([\s\S]*?)\s*\}\}/g)) {
    const expression = match[1]!.trim();
    if (!/^[A-Za-z_][\w.]*(\s*\|\s*default:\s*("[^"]*"|'[^']*'))?$/.test(expression)) {
      throw new Error("Liquid rendering failed closed: output outside preview allowlist");
    }
  }
}

function assertKnownVariables(source: string, fixture: Record<string, unknown>): void {
  const loopBindings = new Map<string, unknown>([["forloop", {index: 1, index0: 0, first: true, last: false, length: 1}]]);
  for (const match of source.matchAll(/\{%\s*for\s+([A-Za-z_]\w*)\s+in\s+([A-Za-z_][\w.]*)\s+limit:\d+\s*%\}/g)) {
    if (!knownPath(fixture, match[2]!)) throw new Error("Liquid rendering failed closed: unknown variable");
    const iterable = valueAtPath(fixture, match[2]!);
    loopBindings.set(match[1]!, Array.isArray(iterable) ? iterable[0] : iterable);
  }
  for (const match of source.matchAll(/\{\{\s*([A-Za-z_][\w.]*)((?:\s*\|\s*default:\s*(?:"[^"]*"|'[^']*'))?)\s*\}\}/g)) {
    const expression = match[1]!;
    const [root, ...rest] = expression.split(".");
    if (loopBindings.has(root!)) {
      if (rest.length && !hasPath(loopBindings.get(root!), rest.join("."))) throw new Error("Liquid rendering failed closed: unknown variable");
    } else if (!knownPath(fixture, expression)) throw new Error("Liquid rendering failed closed: unknown variable");
  }
  for (const match of source.matchAll(/\{%\s*if\s+([A-Za-z_][\w.]*)\s*(?:==|!=|>|>=|<|<=)/g)) {
    const expression = match[1]!;
    const [root, ...rest] = expression.split(".");
    if (loopBindings.has(root!)) {
      if (rest.length && !hasPath(loopBindings.get(root!), rest.join("."))) throw new Error("Liquid rendering failed closed: unknown variable");
    } else if (!knownPath(fixture, expression)) throw new Error("Liquid rendering failed closed: unknown variable");
  }
}

function knownPath(fixture: Record<string, unknown>, dotted: string): boolean {
  return hasPath(fixture, dotted) || fixtureAllowsPath(fixture, dotted);
}
function valueAtPath(value: Record<string, unknown>, dotted: string): unknown {
  return dotted.split(".").reduce<unknown>((current, segment) => current && typeof current === "object" ? (current as Record<string, unknown>)[segment] : undefined, value);
}

function hasPath(value: unknown, dotted: string): boolean {
  let current: unknown = value;
  for (const segment of dotted.split(".")) {
    if (Array.isArray(current) && segment === "first") { current = current[0]; continue; }
    if (!current || typeof current !== "object" || !(segment in current)) return false;
    current = (current as Record<string, unknown>)[segment];
  }
  return true;
}
