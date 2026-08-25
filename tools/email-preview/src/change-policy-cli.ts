import fs from "node:fs/promises";
import { isBuildNoteOnlyChange } from "./change-policy.js";

function argument(name: string): string {
  const index = process.argv.indexOf(name);
  const value = index >= 0 ? process.argv[index + 1] : undefined;
  if (!value) throw new Error(`Missing ${name}`);
  return value;
}

async function main(): Promise<void> {
  const beforePath = argument("--before");
  const afterPath = argument("--after");
  const [before, after] = await Promise.all([
    fs.readFile(beforePath, "utf8"),
    fs.readFile(afterPath, "utf8"),
  ]);
  if (!isBuildNoteOnlyChange(before, after)) {
    throw new Error("Changed blocked Email is not confined to one-line BUILD NOTE comments");
  }
  console.log(JSON.stringify({ allowed: true, reason: "build-note-only" }));
}

main().catch(error => {
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
});
