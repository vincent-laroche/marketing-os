import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import {materializePreviewDirectory} from "../src/materialize.js";

const outputs = ["desktop.png", "mobile.png", "provenance.json", "rendered.html"];

test("materializer replaces the versioned compiler symlink with an exact self-contained directory", async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "preview-materialize-"));
  try {
    const canonical = path.join(root, "CR-1");
    const versions = path.join(root, "CR-1.versions");
    const version = path.join(versions, "v1");
    await fs.mkdir(version, {recursive: true});
    for (const output of outputs) await fs.writeFile(path.join(version, output), output);
    await fs.symlink(path.relative(root, version), canonical);

    await materializePreviewDirectory(canonical);

    assert.equal((await fs.lstat(canonical)).isDirectory(), true);
    assert.deepEqual((await fs.readdir(canonical)).sort(), outputs);
    await assert.rejects(fs.access(versions));
  } finally {
    await fs.rm(root, {recursive: true, force: true});
  }
});

test("materializer fails closed without replacing a non-symlink output", async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "preview-materialize-"));
  try {
    const canonical = path.join(root, "CR-1");
    await fs.mkdir(canonical);
    await assert.rejects(() => materializePreviewDirectory(canonical), /atomic symlink/i);
    assert.equal((await fs.lstat(canonical)).isDirectory(), true);
  } finally {
    await fs.rm(root, {recursive: true, force: true});
  }
});

test("materializer rejects a symlink outside its matching versions directory", async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "preview-materialize-"));
  try {
    const canonical = path.join(root, "CR-1");
    const external = path.join(root, "external");
    await fs.mkdir(external);
    await fs.mkdir(path.join(root, "CR-1.versions"));
    await fs.symlink(path.relative(root, external), canonical);
    await assert.rejects(() => materializePreviewDirectory(canonical), /outside/i);
    assert.equal((await fs.lstat(canonical)).isSymbolicLink(), true);
  } finally {
    await fs.rm(root, {recursive: true, force: true});
  }
});
