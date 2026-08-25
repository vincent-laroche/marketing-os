import { cp, mkdir, rm, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));
const source = resolve(root, "src");
const output = resolve(root, "dist");

await rm(output, { recursive: true, force: true });
await mkdir(output, { recursive: true });

for (const file of ["index.html", "styles.css", "app.js", "data.js"]) {
  await cp(resolve(source, file), resolve(output, file));
}

await writeFile(resolve(output, "robots.txt"), "User-agent: *\nDisallow: /\n", "utf8");

console.log(`Built sanitized public gallery: ${output}`);
