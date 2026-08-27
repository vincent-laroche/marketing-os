import { writeFile } from "node:fs/promises";

const [outputPath] = process.argv.slice(2);
const token = process.env.NOTION_API_KEY;
if (!outputPath || !token) throw new Error("NOTION_API_KEY and an output path are required.");

const runner = `async () => cloudflare.request({
  method: "PUT",
  path: "/accounts/" + accountId + "/workers/scripts/marketing-os-notion-sync/secrets",
  body: ${JSON.stringify({ name: "NOTION_API_KEY", type: "secret_text", text: token })}
})`;

await writeFile(outputPath, JSON.stringify({ code: runner }));
