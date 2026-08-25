import Link from "next/link";
import {
  draftCaption,
  isOperationalTime,
  missingPostFields,
  postProductionStatus,
  recommendedPostTime,
  type LaunchPost,
  type StoryDay
} from "@/lib/data";
import type { DashboardData } from "@/lib/notion";

const navItems = [
  { href: "/daily", label: "Daily View" },
  { href: "/calendar", label: "Calendar" },
  { href: "/mockups", label: "Mockups" },
  { href: "/systems", label: "Systems" }
];

export function DashboardShell({ children, data }: { children: React.ReactNode; data: DashboardData }) {
  return (
    <main className="appShell">
      <aside className="sideNav">
        <Link className="brandMark" href="/daily">
          <span>HSC</span>
          <strong>Social Studio</strong>
        </Link>
        <nav aria-label="Dashboard pages">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href}>
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="syncPanel">
          <StatusPill tone={data.synced ? "good" : "warn"}>{data.synced ? "Live Notion" : "Seed Snapshot"}</StatusPill>
          <p>{data.syncNote}</p>
          <small>Refresh: {formatDateTime(data.updatedAt)}</small>
        </div>
      </aside>
      <section className="pageShell">{children}</section>
    </main>
  );
}

export function PageHeader({
  eyebrow,
  title,
  children,
  actions
}: {
  eyebrow: string;
  title: string;
  children?: React.ReactNode;
  actions?: React.ReactNode;
}) {
  return (
    <header className="pageHeader">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        {children ? <div className="headerCopy">{children}</div> : null}
      </div>
      {actions ? <div className="headerActions">{actions}</div> : null}
    </header>
  );
}

export function StatusPill({ children, tone = "neutral" }: { children: React.ReactNode; tone?: "good" | "warn" | "bad" | "neutral" | "info" }) {
  return <span className={`statusPill ${tone}`}>{children}</span>;
}

export function Stat({ label, value, note }: { label: string; value: string | number; note: string }) {
  return (
    <article className="statBox">
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{note}</p>
    </article>
  );
}

export function HubSpotShortcuts() {
  return (
    <section className="shortcutGrid" aria-label="Social platform shortcuts">
      <a className="shortcutCard primary" href="https://app.hubspot.com/social-composer/50966981?create=true&from=manage" target="_blank" rel="noreferrer">
        <span>HubSpot Social</span>
        <strong>Create a new post</strong>
        <p>Open the composer with the account context already set.</p>
      </a>
      <a className="shortcutCard" href="https://app.hubspot.com/social/50966981/manage/published" target="_blank" rel="noreferrer">
        <span>Social Home</span>
        <strong>Manage published posts</strong>
        <p>Go straight to the HubSpot social publishing dashboard.</p>
      </a>
    </section>
  );
}

export function PostDetailCard({ post, surface = "feed" }: { post: LaunchPost; surface?: "feed" | "reel" | "mockup" }) {
  const missing = missingPostFields(post);
  const timeIsFallback = isOperationalTime(post);
  const url = post.cloudinaryUrl || post.canvaUrl || post.reelFile;
  const completion = postCompletionPlan(post);

  return (
    <article className={`postDetail ${surface}`}>
      <div className="postTopline">
        <span>Day {post.day}</span>
        <StatusPill tone={missing.length ? "warn" : "good"}>{postProductionStatus(post)}</StatusPill>
      </div>
      <section className="nextStepPanel" aria-label="Recommended next step">
        <div className="nextStepHeader">
          <span>Recommended next step</span>
          <StatusPill tone={completion.tone}>{completion.status}</StatusPill>
        </div>
        <strong>{completion.nextStep}</strong>
        <div className="completionTracks">
          <div>
            <span>Done</span>
            <p>{completion.done.length ? completion.done.join(", ") : "No tracked completion items are done yet."}</p>
          </div>
          <div>
            <span>Pending</span>
            <p>{completion.pending.length ? completion.pending.join(", ") : "Ready to schedule in HubSpot."}</p>
          </div>
        </div>
      </section>
      <h3>{post.title}</h3>
      <div className="productionPreview">
        <div className="previewFrame">
          <span>{post.cloudinaryUrl ? "Cloudinary linked" : "Visual mockup"}</span>
        </div>
        <div>
          <strong>{post.format}</strong>
          <p>{post.asset}</p>
        </div>
      </div>
      <dl className="detailGrid">
        <div><dt>Time</dt><dd>{recommendedPostTime(post)} {timeIsFallback ? <small>operational fallback</small> : null}</dd></div>
        <div><dt>Format</dt><dd>{post.format}</dd></div>
        <div><dt>Status</dt><dd>{post.status || "Not set in Notion"}</dd></div>
        <div><dt>Channel</dt><dd>{post.channel || "Instagram"}</dd></div>
        <div><dt>Caption Status</dt><dd>{post.captionStatus || "Not set in Notion"}</dd></div>
        <div><dt>Pillar</dt><dd>{post.pillar}</dd></div>
        <div><dt>Hook</dt><dd>{post.hook}</dd></div>
        <div><dt>CTA</dt><dd>{post.cta}</dd></div>
        <div><dt>Metric</dt><dd>{post.metric}</dd></div>
        <div><dt>Asset Needed</dt><dd>{post.asset}</dd></div>
        <div><dt>Cloudinary URL</dt><dd>{post.cloudinaryUrl ? linkOut(post.cloudinaryUrl) : "Missing in Notion"}</dd></div>
        <div><dt>Canva / Source</dt><dd>{url ? linkOut(url) : "Missing in Notion"}</dd></div>
      </dl>
      <div className="captionBlock">
        <strong>{post.caption ? "Caption" : "Draft caption"}</strong>
        <p>{draftCaption(post)}</p>
      </div>
      {missing.length ? <p className="missingLine">Missing: {missing.join(", ")}</p> : null}
    </article>
  );
}

function postCompletionPlan(post: LaunchPost) {
  const done: string[] = [];
  const pending: string[] = [];

  if (post.date) done.push("date set");
  else pending.push("date");

  if (post.time) done.push("time set");
  else pending.push("posting time");

  if (post.caption) done.push("caption approved");
  else pending.push("final caption");

  if (post.cloudinaryUrl) done.push("Cloudinary asset linked");
  else pending.push("Cloudinary URL");

  if (post.canvaUrl) done.push("Canva/source linked");
  else pending.push("Canva/source link");

  if (post.format.includes("Reel")) {
    if (post.reelFile) done.push("reel file linked");
    else pending.push("reel file");
  }

  if (post.status) done.push(`status: ${post.status}`);
  else pending.push("Notion status");

  const nextStep = getRecommendedNextStep(post);
  const status = pending.length ? `${done.length}/${done.length + pending.length} complete` : "Ready";
  const tone: "good" | "warn" | "bad" | "neutral" | "info" = pending.length ? "warn" : "good";

  return { done, pending, nextStep, status, tone };
}

function getRecommendedNextStep(post: LaunchPost) {
  if (!post.cloudinaryUrl) return "Upload or select the final creative in Cloudinary, then paste the source URL into Notion.";
  if (post.format.includes("Reel") && !post.reelFile) return "Attach the final Reel file or export link before scheduling.";
  if (!post.caption) return "Review the draft caption, approve it, and add the final caption to Notion.";
  if (!post.date || !post.time) return "Confirm the publishing date and exact posting time.";
  if (!post.canvaUrl) return "Add the Canva or source production link for traceability.";
  if (!post.status) return "Set the Notion status to ready, then schedule the post in HubSpot.";
  return "Schedule or confirm this post in HubSpot Social.";
}

export function StorySchedule({ story }: { story: StoryDay }) {
  return (
    <article className="storySchedule">
      <div className="postTopline">
        <span>{story.day}</span>
        <StatusPill tone="info">{story.frames} frames</StatusPill>
      </div>
      <h3>{story.type}</h3>
      <dl className="detailGrid compact">
        <div><dt>9:00 AM</dt><dd>Opening frame and context</dd></div>
        <div><dt>2:00 PM</dt><dd>{story.sticker}</dd></div>
        <div><dt>7:30 PM</dt><dd>{story.cta}</dd></div>
        <div><dt>Highlight</dt><dd>{story.highlight}</dd></div>
      </dl>
    </article>
  );
}

export function MockupCard({ post }: { post: LaunchPost }) {
  const isReel = post.format.includes("Reel");
  const isCarousel = post.format === "Carousel";
  const missing = missingPostFields(post);

  return (
    <article className={`mockCard ${isReel ? "reelShape" : ""}`}>
      <div className="mockCanvas">
        <div className="mockChrome">
          <span>Day {post.day}</span>
          <span>{isReel ? "9:16" : isCarousel ? "Carousel" : "4:5"}</span>
        </div>
        <div className="mockMediaSlot">
          <span>{post.cloudinaryUrl ? "Cloudinary asset linked" : "Asset slot"}</span>
        </div>
        <strong>{post.hook}</strong>
        <small>{post.pillar}</small>
      </div>
      <div className="mockDetails">
        <h3>{post.title}</h3>
        <p>{post.asset}</p>
        <div className="mockMetaRow">
          <StatusPill tone={missing.length ? "warn" : "good"}>{postProductionStatus(post)}</StatusPill>
          <span>{recommendedPostTime(post)}</span>
        </div>
      </div>
    </article>
  );
}

export function linkOut(url: string) {
  return (
    <a href={url} target="_blank" rel="noreferrer">
      {url}
    </a>
  );
}

function formatDateTime(value: string) {
  if (!value) return "Unknown";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
}
