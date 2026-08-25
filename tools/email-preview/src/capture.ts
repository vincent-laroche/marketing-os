import fs from "node:fs/promises";
import path from "node:path";
import { chromium } from "@playwright/test";

const imageHosts = new Set(["hairsolutions.co", "www.hairsolutions.co", "res.cloudinary.com"]);
const PNG_SIGNATURE = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);

export function isAllowedCaptureRequest(url: string, resourceType: string): boolean {
  if (/^(file|data|blob):/i.test(url)) return true;
  try {
    const parsed = new URL(url);
    return parsed.protocol === "https:" && resourceType === "image" && imageHosts.has(parsed.hostname);
  } catch { return false; }
}

export async function capture(htmlPath: string, outDir: string): Promise<void> {
  const browser = await chromium.launch({headless: true});
  try {
    for (const [name, width, height] of [["desktop.png", 1440, 900], ["mobile.png", 390, 844]] as const) {
      const context = await browser.newContext({viewport: {width, height}, deviceScaleFactor: 1, locale: "en-US", timezoneId: "UTC", reducedMotion: "reduce"});
      const page = await context.newPage();
      await page.route("**/*", route => {
        if (isAllowedCaptureRequest(route.request().url(), route.request().resourceType())) return route.continue();
        return route.abort();
      });
      await page.goto(`file://${path.resolve(htmlPath)}`, {waitUntil: "networkidle"});
      await page.addStyleTag({content: "*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}"});
      await page.screenshot({path: path.join(outDir, name), fullPage: true});
      await page.close();
      await context.close();
    }
  } finally {
    await browser.close();
  }
  await Promise.all(["desktop.png", "mobile.png"].map(file => assertPng(path.join(outDir, file))));
}

export async function assertPng(file: string): Promise<void> {
  const contents = await fs.readFile(file);
  if (contents.length < 33 || !contents.subarray(0, 8).equals(PNG_SIGNATURE)) throw new Error("invalid screenshot PNG");
  const width = contents.readUInt32BE(16);
  const height = contents.readUInt32BE(20);
  if (width < 1 || height < 1) throw new Error("invalid screenshot dimensions");
}
