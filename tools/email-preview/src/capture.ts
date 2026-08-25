import fs from "node:fs/promises";
import path from "node:path";
import { chromium } from "@playwright/test";

export async function capture(htmlPath: string, outDir: string): Promise<void> {
  const browser = await chromium.launch({ headless: true });
  try {
    for (const [name, width, height] of [["desktop.png", 1440, 900], ["mobile.png", 390, 844]] as const) {
      const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
      await page.goto(`file://${path.resolve(htmlPath)}`, { waitUntil: "networkidle" });
      await page.screenshot({ path: path.join(outDir, name), fullPage: true });
      await page.close();
    }
  } finally {
    await browser.close();
  }
  for (const file of ["desktop.png", "mobile.png"]) {
    const stat = await fs.stat(path.join(outDir, file));
    if (stat.size === 0) throw new Error(`empty screenshot: ${file}`);
  }
}
