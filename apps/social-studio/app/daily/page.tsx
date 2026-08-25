import {
  DashboardShell,
  FeedSquareCard,
  HubSpotShortcuts,
  InstagramFeedMockup,
  PageHeader,
  StatusPill,
  StoryFrameStrip
} from "@/app/components";
import { recommendedPostTime, storyPlanForLaunchDay, type LaunchPost } from "@/lib/data";
import { getDashboardData } from "@/lib/notion";

function groupPostsByDay(posts: LaunchPost[]) {
  const groups = new Map<number, LaunchPost[]>();
  for (const post of posts) {
    const current = groups.get(post.day) || [];
    current.push(post);
    groups.set(post.day, current);
  }
  return [...groups.entries()]
    .sort(([dayA], [dayB]) => dayA - dayB)
    .map(([day, dayPosts]) => ({ day, posts: dayPosts }));
}

function displayDate(posts: LaunchPost[]) {
  const date = posts.map((post) => post.date).find(Boolean);
  if (!date) return "Date not set";
  const parsed = new Date(date.includes("T") ? date : `${date}T12:00:00`);
  if (Number.isNaN(parsed.getTime())) return date;
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric" }).format(parsed);
}

function timeSummary(posts: LaunchPost[]) {
  return [...new Set(posts.map((post) => recommendedPostTime(post)))].join(" · ");
}

export default async function DailyPage() {
  const data = await getDashboardData();
  const dayGroups = groupPostsByDay(data.launchPosts);
  const mockupPosts = data.launchPosts.filter((post) => !post.format.includes("Reel")).slice(0, 9);

  return (
    <DashboardShell data={data}>
      <PageHeader
        eyebrow="Daily display gallery"
        title="Instagram planner / 30-day visual"
        actions={<StatusPill tone="warn">Read-only assembly view</StatusPill>}
      >
        <p>
          One row per launch day. Grid posts stay square and Stories sit beside them so you can confirm the full day
          before placing final photos and exports into the linked asset slots.
        </p>
      </PageHeader>

      <HubSpotShortcuts />

      <section className="galleryLegend" aria-label="Gallery legend">
        <div>
          <span className="eyebrow">Visual rule</span>
          <strong>Grid first, Stories alongside</strong>
          <p>Each day groups every post with the five visual Story slots for that day.</p>
        </div>
        <div>
          <span className="eyebrow">Data rule</span>
          <strong>Dates and times stay honest</strong>
          <p>Notion dates are shown when present; otherwise the card exposes the missing field or operational fallback.</p>
        </div>
        <a className="galleryMockupLink" href="#feed-assembly">Jump to feed assembly</a>
      </section>

      <nav className="dayJump" aria-label="Jump to launch day">
        {dayGroups.map(({ day }) => (
          <a key={day} href={`#day-${day}`}>{String(day).padStart(2, "0")}</a>
        ))}
      </nav>

      <section className="dailyStack" aria-label="Day-by-day Instagram and Stories gallery">
        {dayGroups.map(({ day, posts }) => {
          const story = storyPlanForLaunchDay(day, data.stories);
          return (
            <article className="dailyGalleryRow" id={`day-${day}`} key={day}>
              <header className="galleryDayRail">
                <span className="galleryDayLabel">Launch day</span>
                <strong>{String(day).padStart(2, "0")}</strong>
                <time>{displayDate(posts)}</time>
                <StatusPill tone="info">{posts.length} grid {posts.length === 1 ? "post" : "posts"}</StatusPill>
                <small>{timeSummary(posts)}</small>
              </header>

              <div className="dailyVisualGrid">
                <section className="gallerySection" aria-labelledby={`feed-title-${day}`}>
                  <div className="gallerySectionHeader">
                    <div>
                      <span className="eyebrow">Instagram grid</span>
                      <h2 id={`feed-title-${day}`}>{posts.length} square {posts.length === 1 ? "slot" : "slots"}</h2>
                    </div>
                    <span className="galleryHint">Place final photos here</span>
                  </div>
                  <div className="feedSquareGrid">
                    {posts.map((post, index) => <FeedSquareCard post={post} position={index + 1} key={`${post.day}-${post.title}-${index}`} />)}
                  </div>
                </section>

                <section className="gallerySection storiesSection" aria-labelledby={`stories-title-${day}`}>
                  <div className="gallerySectionHeader">
                    <div>
                      <span className="eyebrow">Stories alongside</span>
                      <h2 id={`stories-title-${day}`}>5 visual Story slots</h2>
                    </div>
                    <span className="galleryHint">Source rhythm: {story.frames}</span>
                  </div>
                  <StoryFrameStrip day={day} story={story} />
                </section>
              </div>
            </article>
          );
        })}
      </section>

      <section className="feedAssemblySection" id="feed-assembly" aria-labelledby="feed-assembly-title">
        <div className="sectionTitleRow">
          <div>
            <p className="eyebrow">Separate mockup surface</p>
            <h2 id="feed-assembly-title">Instagram feed assembly</h2>
            <p>Use this 3 × 3 frame to test the visual rhythm separately from the day-by-day confirmation gallery.</p>
          </div>
          <a className="textLink" href="/mockups">Open the full Mockups wall →</a>
        </div>
        <InstagramFeedMockup posts={mockupPosts} />
      </section>
    </DashboardShell>
  );
}
