import {
  assetNeeds,
  carouselConcepts,
  launchPosts,
  metricWeeks,
  objections,
  reels,
  stories,
  type AssetNeed,
  type Concept,
  type LaunchPost,
  type MetricWeek,
  type Objection,
  type ReelIdea,
  type StoryDay
} from "./data";

type RawPage = Record<string, unknown>;

const NOTION_VERSION = "2022-06-28";

const databases = {
  content: "75c49060adad4abe8a8d6fd602598e7a",
  reels: "5217a0ee1688430c81839089c5bf7d49",
  stories: "b66877d2d6b140ca8da29420a6c7de6f",
  carousel: "ee75467aee7845cd8fdd81033af3bb9d",
  assets: "21ac7d178aa347fcbe1c15781ede8934",
  metrics: "8b4fe2893bda49178ceef77ebc1ef3a5",
  objections: "86deb72afb29437e8c3fa65e33ea1467"
};

export type DashboardData = {
  synced: boolean;
  syncNote: string;
  updatedAt: string;
  launchPosts: LaunchPost[];
  reels: ReelIdea[];
  stories: StoryDay[];
  carouselConcepts: Concept[];
  assetNeeds: AssetNeed[];
  metricWeeks: MetricWeek[];
  objections: Objection[];
};

function getTitle(page: RawPage, name: string) {
  const prop = getProp(page, name);
  const text = Array.isArray(prop?.title) ? prop.title.map((part: any) => part.plain_text || "").join("") : "";
  return text.trim();
}

function getText(page: RawPage, name: string) {
  const prop = getProp(page, name);
  if (!prop) return "";
  if (typeof prop.rich_text !== "undefined" && Array.isArray(prop.rich_text)) {
    return prop.rich_text.map((part: any) => part.plain_text || "").join("").trim();
  }
  if (typeof prop.url === "string") return prop.url;
  if (typeof prop.select?.name === "string") return prop.select.name;
  if (typeof prop.status?.name === "string") return prop.status.name;
  if (typeof prop.number === "number") return String(prop.number);
  return "";
}

function getDate(page: RawPage, name: string) {
  const prop = getProp(page, name);
  return typeof prop?.date?.start === "string" ? prop.date.start : "";
}

function getCheckbox(page: RawPage, name: string) {
  return getProp(page, name)?.checkbox === true;
}

function getProp(page: RawPage, name: string): any {
  const props = page.properties as Record<string, unknown> | undefined;
  return props?.[name] as any;
}

function dayFromTitle(title: string) {
  const match = title.match(/Day\s+(\d+)/i);
  return match ? Number(match[1]) : 999;
}

function applyReviewCorrections(post: LaunchPost): LaunchPost {
  if (post.day === 1) {
    return {
      ...post,
      asset: post.asset || "Pure wordmark tile, off-white/obsidian variant",
      caption: "Eight years ago, this was OneHead Hair. Today it becomes Hair Solutions Co.\n\nWe've spent the last year rebuilding everything: how we make hair systems, how we photograph them, how we talk about them, and who we're talking to.\n\nThis is what comes next.\n\nStay close. Reply with a question."
    };
  }

  if (post.day === 5) {
    return {
      ...post,
      title: "Lace Elite, photographed honestly.",
      hook: "Lace Elite, photographed honestly.",
      asset: "Lace Elite hero product photo on paper card",
      notes: "Swiss-lace product trust. Stories: macro frames of lace and hairline."
    };
  }

  if (post.day === 7) {
    return {
      ...post,
      format: "Reel + Stories",
      metric: "Watch time, profile visits, replies",
      asset: "Consented quote voiceover, proof frame, subtle product B-roll",
      notes: "Second week-one reel. Proof + trust. Anonymize unless consent is confirmed. Stories: repost with review prompt."
    };
  }

  if (post.day === 12) {
    return {
      ...post,
      title: "The base types, explained.",
      hook: "The base types, explained.",
      pillar: "Base types / education",
      asset: "5-slide guide: lace, skin/poly, mono, hybrid, frontal",
      notes: "Education + saves. Stories: base-type quiz."
    };
  }

  return post;
}

async function queryDatabase(token: string, databaseId: string): Promise<RawPage[]> {
  const response = await fetch(`https://api.notion.com/v1/databases/${databaseId}/query`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      "Notion-Version": NOTION_VERSION
    },
    body: JSON.stringify({ page_size: 100 }),
    next: { revalidate: 300 }
  });

  if (!response.ok) {
    throw new Error(`Notion query failed for ${databaseId}: ${response.status}`);
  }

  const data = await response.json();
  return Array.isArray(data.results) ? data.results : [];
}

export async function getDashboardData(): Promise<DashboardData> {
  const token = process.env.NOTION_DEV_TOKEN || process.env.NOTION_TOKEN;
  const fallback: DashboardData = {
    synced: false,
    syncNote: "Using the verified seed snapshot from the Notion hub fetch.",
    updatedAt: "2026-06-29",
    launchPosts,
    reels,
    stories,
    carouselConcepts,
    assetNeeds,
    metricWeeks,
    objections
  };

  if (!token) return fallback;

  try {
    const [contentRows, reelRows, storyRows, carouselRows, assetRows, metricRows, objectionRows] = await Promise.all([
      queryDatabase(token, databases.content),
      queryDatabase(token, databases.reels),
      queryDatabase(token, databases.stories),
      queryDatabase(token, databases.carousel),
      queryDatabase(token, databases.assets),
      queryDatabase(token, databases.metrics),
      queryDatabase(token, databases.objections)
    ]);

    return {
      synced: true,
      syncNote: "Live Notion refresh succeeded.",
      updatedAt: new Date().toISOString(),
      launchPosts: contentRows
        .map((row) => {
          const title = getTitle(row, "Post");
          return applyReviewCorrections({
            day: dayFromTitle(title),
            title: title.replace(/^Day\s+\d+\s+—\s+/i, ""),
            hook: getText(row, "Hook"),
            format: (getText(row, "Format") || "Static") as LaunchPost["format"],
            pillar: getText(row, "Pillar"),
            metric: getText(row, "Metric to Watch"),
            cta: getText(row, "CTA"),
            asset: getText(row, "Asset Needed"),
            notes: getText(row, "Notes"),
            date: getDate(row, "Date"),
            caption: getText(row, "Caption"),
            cloudinaryUrl: getText(row, "Cloudinary Asset"),
            canvaUrl: getText(row, "Canva Link"),
            shopifyUrl: getText(row, "Shopify Link"),
            reelFile: getText(row, "Reel File"),
            captionStatus: getText(row, "Caption Status"),
            channel: getText(row, "Channel"),
            status: getText(row, "Status")
          });
        })
        .sort((a, b) => a.day - b.day),
      reels: reelRows.map((row) => ({
        title: getTitle(row, "Reel"),
        hook: getText(row, "Hook"),
        format: getText(row, "Format"),
        priority: getText(row, "Priority"),
        cta: getText(row, "CTA"),
        shotList: getText(row, "Shot List")
      })),
      stories: storyRows.map((row) => ({
        day: getTitle(row, "Day"),
        type: getText(row, "Story Type"),
        frames: getText(row, "Frames"),
        sticker: getText(row, "Sticker"),
        cta: getText(row, "CTA"),
        highlight: getText(row, "Highlight")
      })),
      carouselConcepts: carouselRows.map((row) => ({
        post: getTitle(row, "Post"),
        pillar: getText(row, "Pillar"),
        hook: getText(row, "Hook"),
        cta: getText(row, "CTA"),
        caution: getText(row, "Notes")
      })),
      assetNeeds: assetRows.map((row) => ({
        name: getTitle(row, "Asset Name"),
        type: getText(row, "Asset Type"),
        format: getText(row, "Format"),
        consent: getText(row, "Usage Rights / Consent"),
        notes: getText(row, "Notes")
      })),
      metricWeeks: metricRows
        .map((row) => ({ week: getTitle(row, "Week"), notes: getText(row, "Notes") }))
        .sort((a, b) => Number(a.week.match(/\d+/)?.[0] || 0) - Number(b.week.match(/\d+/)?.[0] || 0)),
      objections: objectionRows.map((row) => ({
        question: getTitle(row, "Question / Objection"),
        category: getText(row, "Category"),
        response: getText(row, "Recommended Content Response"),
        reel: getCheckbox(row, "Needs Reel?"),
        carousel: getCheckbox(row, "Needs Carousel?"),
        faq: getCheckbox(row, "Needs FAQ?")
      }))
    };
  } catch (error) {
    return {
      ...fallback,
      syncNote: error instanceof Error ? `Live Notion refresh failed, using seed snapshot: ${error.message}` : fallback.syncNote
    };
  }
}
