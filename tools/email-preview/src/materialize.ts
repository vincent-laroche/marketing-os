import fs from "node:fs/promises";
import path from "node:path";
import {fileURLToPath} from "node:url";

const EXPECTED_FILES = ["desktop.png", "mobile.png", "provenance.json", "rendered.html"];

/**
 * Convert the compiler's atomic, versioned symlink into a self-contained directory.
 * Review artifacts and Pages archives must never depend on an adjacent versions tree.
 */
export async function materializePreviewDirectory(rawCanonicalPath: string): Promise<void> {
  const canonicalPath = path.resolve(rawCanonicalPath);
  const parent = path.dirname(canonicalPath);
  const versionsPath = `${canonicalPath}.versions`;
  const temporaryPath = path.join(parent, `.${path.basename(canonicalPath)}.materialize-${process.pid}-${Date.now()}`);

  const stat = await fs.lstat(canonicalPath).catch(() => { throw new Error("preview output is missing"); });
  if (!stat.isSymbolicLink()) throw new Error("preview output is not the compiler's atomic symlink");

  const realTarget = await fs.realpath(canonicalPath);
  const realVersions = await fs.realpath(versionsPath).catch(() => { throw new Error("preview versions directory is missing"); });
  const relativeTarget = path.relative(realVersions, realTarget);
  if (!relativeTarget || relativeTarget.startsWith("..") || path.isAbsolute(relativeTarget)) {
    throw new Error("preview symlink target is outside its versions directory");
  }

  try {
    await fs.cp(realTarget, temporaryPath, {recursive: true, errorOnExist: true, force: false});
    const entries = (await fs.readdir(temporaryPath)).sort();
    if (JSON.stringify(entries) !== JSON.stringify(EXPECTED_FILES)) {
      throw new Error("preview output does not contain the exact public artifact set");
    }
    for (const entry of entries) {
      if (!(await fs.lstat(path.join(temporaryPath, entry))).isFile()) {
        throw new Error("preview artifact contains a non-file output");
      }
    }
    await fs.unlink(canonicalPath);
    await fs.rename(temporaryPath, canonicalPath);
    await fs.rm(versionsPath, {recursive: true, force: true});
  } catch (error) {
    await fs.rm(temporaryPath, {recursive: true, force: true});
    throw error;
  }
}

async function main(): Promise<void> {
  const output = process.argv[2];
  if (!output || process.argv.length !== 3) throw new Error("exactly one preview output path is required");
  await materializePreviewDirectory(output);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch(error => {
    console.error(error instanceof Error ? error.message : "preview materialization failed closed");
    process.exitCode = 1;
  });
}
