import { Liquid } from "liquidjs";

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
  const loopBindings = new Set<string>(["line_item", "forloop"]);
  for (const match of source.matchAll(/\{%\s*for\s+([A-Za-z_]\w*)\s+in\s+([A-Za-z_][\w.]*)\s+limit:\d+\s*%\}/g)) {
    loopBindings.add(match[1]!);
    if (!hasPath(fixture, match[2]!)) throw new Error("Liquid rendering failed closed: unknown variable");
  }
  for (const match of source.matchAll(/\{\{\s*([A-Za-z_][\w.]*)((?:\s*\|\s*default:\s*(?:"[^"]*"|'[^']*'))?)\s*\}\}/g)) {
    const expression = match[1]!;
    const allowsBlank = /\|\s*default:/.test(match[2]!);
    if (!loopBindings.has(expression.split(".")[0]!) && !hasPath(fixture, expression) && !allowsBlank) throw new Error("Liquid rendering failed closed: unknown variable");
  }
  for (const match of source.matchAll(/\{%\s*if\s+([A-Za-z_][\w.]*)\s*(?:==|!=|>|>=|<|<=)/g)) {
    const expression = match[1]!;
    if (!loopBindings.has(expression.split(".")[0]!) && !hasPath(fixture, expression)) throw new Error("Liquid rendering failed closed: unknown variable");
  }
}

function hasPath(value: Record<string, unknown>, dotted: string): boolean {
  let current: unknown = value;
  for (const segment of dotted.split(".")) {
    if (!current || typeof current !== "object" || !(segment in current)) return false;
    current = (current as Record<string, unknown>)[segment];
  }
  return true;
}
