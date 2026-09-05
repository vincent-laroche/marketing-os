import { describe, expect, it } from "vitest";

const approvedWorkerSources = [
  "4186d9fe-d6ab-4460-9622-cb7de438821e",
  "fbc9f1df-1126-83a3-a049-87874c8d1a99",
  "f309f1df-1126-821e-8d1b-8714c8bd2bb3",
  "d519f1df-1126-8203-ba7a-87a2e56b384d",
  "c789ba58-02d5-45d4-b6b0-201de04febcc",
  "da751d10-2cf6-48af-9184-f8160bb5e3bd",
  "bbc7227c-d718-4f82-b696-e7c7ed26a0be",
  "52eda403-7c9c-49d7-8f6e-cdc804d77fcf",
  "3c19f1df-1126-8128-83c1-000bf78a0768",
  "bdd0ebbf-2f42-417c-b846-f12ff393beac",
  "e59a1965-1b0a-42ca-bfa2-86904b604e3e",
];

const pause = (milliseconds: number) => new Promise(resolve => setTimeout(resolve, milliseconds));

async function notionFetch(input: RequestInfo | URL, init?: RequestInit) {
  let lastError: unknown;
  for (let attempt = 0; attempt < 3; attempt += 1) {
    try {
      return await fetch(input, init);
    } catch (error) {
      lastError = error;
      if (attempt < 2) await pause(500 * (attempt + 1));
    }
  }
  throw lastError;
}

describe("Notion worker credential", () => {
  it("authenticates against the current Notion identity endpoint", async () => {
    const token = process.env.NOTION_API_KEY;

    expect(token).toBeTruthy();

    const response = await notionFetch("https://api.notion.com/v1/users/me", {
      headers: {
        Authorization: `Bearer ${token}`,
        "Notion-Version": "2025-09-03",
      },
    });

    expect(response.status).toBe(200);
    const identity = await response.json() as { object?: string };
    expect(identity.object).toBe("user");
  }, 40_000);

  it("can perform a read-only bounded query against every approved Worker source", async () => {
    const token = process.env.NOTION_API_KEY;

    for (const dataSourceId of approvedWorkerSources) {
      const response = await notionFetch(
        `https://api.notion.com/v1/data_sources/${dataSourceId}/query`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
            "Notion-Version": "2025-09-03",
          },
          body: JSON.stringify({ page_size: 1 }),
        },
      );
      expect(response.status).toBe(200);
      const page = await response.json() as { object?: string };
      expect(page.object).toBe("list");
      await pause(350);
    }
  }, 90_000);
});
