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
  const scopes: Array<Map<string, unknown>> = [new Map([["forloop", {index: 1, index0: 0, first: true, last: false, length: 1}]])];
  for (const match of source.matchAll(/\{%\s*([\s\S]*?)\s*%\}|\{\{\s*([\s\S]*?)\s*\}\}/g)) {
    const tag = match[1]?.trim(); const output = match[2]?.trim();
    if (output) { assertPath(output.split("|")[0]!.trim(), fixture, scopes); continue; }
    if (tag === "endfor") { if (scopes.length === 1) throw new Error("Liquid rendering failed closed: unbalanced loop"); scopes.pop(); continue; }
    const loop = tag?.match(/^for\s+([A-Za-z_]\w*)\s+in\s+([A-Za-z_][\w.]*)\s+limit:\d+$/);
    if (loop) { const iterable = resolvePath(loop[2]!, fixture, scopes); if (iterable === undefined) throw unknown(); scopes.push(new Map([[loop[1]!, Array.isArray(iterable) ? iterable[0] : iterable], ["forloop", {index: 1, index0: 0, first: true, last: false, length: 1}]])); continue; }
    const condition = tag?.match(/^if\s+([A-Za-z_][\w.]*)\s*(?:==|!=|>|>=|<|<=)/);
    if (condition) assertPath(condition[1]!, fixture, scopes);
  }
  if (scopes.length !== 1) throw new Error("Liquid rendering failed closed: unbalanced loop");
}

function assertPath(path: string, fixture: Record<string, unknown>, scopes: Array<Map<string, unknown>>): void {
  const [root] = path.split(".");
  if (resolvePath(path, fixture, scopes) === undefined && (hasBinding(root!, scopes) || !fixtureAllowsPath(fixture, path))) throw unknown();
}

function hasBinding(root: string, scopes: Array<Map<string, unknown>>): boolean {
  return scopes.some(scope => scope.has(root));
}

function resolvePath(dotted: string, fixture: Record<string, unknown>, scopes: Array<Map<string, unknown>>): unknown {
  const [root, ...rest] = dotted.split(".");
  for (let index = scopes.length - 1; index >= 0; index--) if (scopes[index]!.has(root!)) return rest.length ? valueAtPath(scopes[index]!.get(root!), rest.join(".")) : scopes[index]!.get(root!);
  return valueAtPath(fixture, dotted);
}
function unknown(): Error { return new Error("Liquid rendering failed closed: unknown variable"); }

function valueAtPath(value: unknown, dotted: string): unknown {
  return dotted.split(".").reduce<unknown>((current, segment) => Array.isArray(current) && segment === "first" ? current[0] : current && typeof current === "object" ? (current as Record<string, unknown>)[segment] : undefined, value);
}
