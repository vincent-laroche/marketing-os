import { Liquid } from "liquidjs";

const engine = new Liquid({
  strictFilters: true,
  strictVariables: true,
  lenientIf: false,
  dynamicPartials: false
});

export async function renderLiquid(source: string, fixture: Record<string, unknown>): Promise<string> {
  let rendered: string;
  try {
    rendered = await engine.parseAndRender(source, fixture);
  } catch (error) {
    throw new Error(`Liquid rendering failed closed: ${error instanceof Error ? error.message : String(error)}`);
  }
  if (/{{|{%|}}|%}/.test(rendered)) {
    throw new Error("Liquid rendering failed closed: unresolved Liquid remains");
  }
  return rendered;
}
