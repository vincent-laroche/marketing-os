import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { templates } from "../templates/src/templates.mjs";

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const templateRoot = path.join(projectRoot, "templates");
const outputRoot = path.join(templateRoot, "html");
const brandRoot = "/Users/vMac/02_dev/design-system";
const logoRoot = "/Users/vMac/06_design/brand/logos";

const assets = {
  logoDark: {
    file: path.join(logoRoot, "wordmark-dark-on-transparent-bg.png"),
    sha256: "bab0253b01f557ffd9f2da129338e0d7ccdeb24c0d0bdba8c17a6cd2901a444a"
  },
  logoLight: {
    file: path.join(logoRoot, "wordmark-light-on-dark-bg.png"),
    sha256: "13af00a7c638573f267bc4788378d0e3071e4d5f352a1415484b8658a6204264"
  },
  interTight: {
    file: path.join(brandRoot, "fonts/InterTight-Roman-VariableFont.woff2"),
    sha256: "86c90d2c18f0de0a808e3e70dcb3a5aea81d922d9ce4c8a194eac88355b9960a"
  },
  inter: {
    file: path.join(brandRoot, "fonts/Inter-Roman-VariableFont.woff2"),
    sha256: "bff0f2e92cf937b8f279fdcc2bc40cdcf6668ce0cc5fd74de5f3738f674a4676"
  },
  playfair: {
    file: path.join(brandRoot, "fonts/PlayfairDisplay-Italic-VariableFont.woff2"),
    sha256: "f49054a4f59943e00b8a94db32a61698d9519360fd8bc68318f81bf278def603"
  },
  mono: {
    file: path.join(brandRoot, "fonts/JetBrainsMono-VariableFont.woff2"),
    sha256: "dea05c900f787a8d7866e6f50a3b37523e506724fef41cff0064af80e506568b"
  }
};

function digest(buffer) {
  return createHash("sha256").update(buffer).digest("hex");
}

async function verifiedAsset(name) {
  const asset = assets[name];
  const buffer = await readFile(asset.file);
  const actual = digest(buffer);
  if (actual !== asset.sha256) {
    throw new Error(`${name} hash mismatch: expected ${asset.sha256}, received ${actual}`);
  }
  return buffer;
}

function dataUri(buffer, mime) {
  return `data:${mime};base64,${buffer.toString("base64")}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function pageShell({ title, description, rootPrefix, body }) {
  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="color-scheme" content="light">
    <title>${escapeHtml(title)} · Hair Solutions Co.</title>
    <link rel="icon" href="data:,">
    <link rel="stylesheet" href="${rootPrefix}shared.css">
  </head>
  <body>
    <header class="library-header">
      <div>
        <p class="index-meta">ATELIER ZERO V7 · REVIEW-ONLY TEMPLATE</p>
        <h1>${escapeHtml(title)}<span class="terminal">.</span></h1>
      </div>
      <div>
        <p>${escapeHtml(description)}</p>
        ${rootPrefix ? `<p style="margin-top:16px"><a class="back-link" href="${rootPrefix}index.html">Back to template library</a></p>` : ""}
      </div>
    </header>
    ${body}
  </body>
</html>
`.replace(/[ \t]+$/gm, "");
}

function renderFrame(frame, index, total) {
  const formatLabel = frame.format === "square"
    ? "1080 × 1080 · 160px inset"
    : frame.format === "portrait"
      ? "1080 × 1350 · 160px vertical / 80px horizontal"
      : "1080 × 1920 · 250px vertical / 160px outer text guard";
  return `<section class="frame">
    <div class="frame-meta"><span>FRAME ${String(index + 1).padStart(2, "0")} / ${String(total).padStart(2, "0")}</span><span>${formatLabel}</span></div>
    <article class="artboard ${frame.format} ${frame.tone}${frame.blocked ? " blocked" : ""}">
      ${frame.markup.trim()}
      <span class="safe-zone" aria-hidden="true"></span>
    </article>
  </section>`;
}

function renderTemplate(template, manifestEntry) {
  const body = `<main class="gallery" aria-label="${escapeHtml(template.title)} frames">
    ${template.frames.map((frame, index) => renderFrame(frame, index, template.frames.length)).join("\n")}
  </main>`;
  return pageShell({
    title: template.title,
    description: `${manifestEntry.purpose}. Placeholders are intentionally non-production until the owning source and approval record are attached.`,
    rootPrefix: "../",
    body
  });
}

function renderIndex(manifest) {
  const cards = manifest.templates.map((entry) => {
    const template = templates.find((candidate) => candidate.id === entry.id);
    return `<article class="index-card">
      <div>
        <p class="index-meta">${escapeHtml(entry.category)} · ${escapeHtml(entry.canvas)} · ${entry.slides} frame${entry.slides === 1 ? "" : "s"}</p>
        <h2>${escapeHtml(template.title)}</h2>
        <p>${escapeHtml(entry.purpose)}</p>
      </div>
      <a class="template-link" href="${escapeHtml(entry.category)}/${escapeHtml(entry.id)}.html">Open HTML template</a>
    </article>`;
  }).join("\n");
  return pageShell({
    title: "Social template library",
    description: "Sixteen individual HTML templates. Every proof, product, offer, announcement, and source-media field remains blocked until verified.",
    rootPrefix: "",
    body: `<main class="index-grid">${cards}</main>`
  });
}

async function buildSharedCss() {
  const [sourceCss, logoDark, logoLight, interTight, inter, playfair, mono] = await Promise.all([
    readFile(path.join(templateRoot, "src/template.css"), "utf8"),
    verifiedAsset("logoDark"),
    verifiedAsset("logoLight"),
    verifiedAsset("interTight"),
    verifiedAsset("inter"),
    verifiedAsset("playfair"),
    verifiedAsset("mono")
  ]);

  return `/* Generated from canonical Atelier Zero v7 assets. Do not edit directly. */
@font-face{font-family:"Inter Tight";src:url("${dataUri(interTight, "font/woff2")}") format("woff2");font-style:normal;font-weight:100 900;font-display:swap}
@font-face{font-family:"Inter";src:url("${dataUri(inter, "font/woff2")}") format("woff2");font-style:normal;font-weight:100 900;font-display:swap}
@font-face{font-family:"Playfair Display";src:url("${dataUri(playfair, "font/woff2")}") format("woff2");font-style:italic;font-weight:400 900;font-display:swap}
@font-face{font-family:"JetBrains Mono";src:url("${dataUri(mono, "font/woff2")}") format("woff2");font-style:normal;font-weight:100 800;font-display:swap}
:root{--logo-dark:url("${dataUri(logoDark, "image/png")}");--logo-light:url("${dataUri(logoLight, "image/png")}");--paper-grain:none}
${sourceCss}`;
}

async function main() {
  const manifest = JSON.parse(await readFile(path.join(templateRoot, "manifest.json"), "utf8"));
  const manifestIds = manifest.templates.map((entry) => entry.id);
  const sourceIds = templates.map((template) => template.id);
  if (new Set(manifestIds).size !== manifestIds.length || new Set(sourceIds).size !== sourceIds.length) {
    throw new Error("Template IDs must be unique.");
  }
  if (manifestIds.join("\n") !== sourceIds.join("\n")) {
    throw new Error("Template source and manifest order do not match.");
  }

  await Promise.all(["feed", "stories", "carousels", "reels"].map((category) =>
    mkdir(path.join(outputRoot, category), { recursive: true })
  ));
  await writeFile(path.join(outputRoot, "shared.css"), await buildSharedCss());
  await writeFile(path.join(outputRoot, "index.html"), renderIndex(manifest));

  for (const template of templates) {
    const manifestEntry = manifest.templates.find((entry) => entry.id === template.id);
    await writeFile(
      path.join(outputRoot, template.category, `${template.id}.html`),
      renderTemplate(template, manifestEntry)
    );
  }

  console.log(`Built ${templates.length} individual HTML templates in ${outputRoot}`);
}

await main();
