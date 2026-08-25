import { DashboardShell, PageHeader, Stat, StatusPill } from "@/app/components";
import { formatCounts, missingPostFields, recommendedPostTime } from "@/lib/data";
import { getDashboardData } from "@/lib/notion";

export default async function CalendarPage() {
  const data = await getDashboardData();
  const counts = formatCounts(data.launchPosts);
  const missingAssets = data.launchPosts.filter((post) => missingPostFields(post).includes("Cloudinary URL")).length;

  return (
    <DashboardShell data={data}>
      <PageHeader eyebrow="Calendar" title="30-day launch calendar">
        <p>
          A scannable calendar for sequencing formats, CTAs, asset gaps, and posting windows. This is built for daily
          production checks, not a decorative campaign overview.
        </p>
      </PageHeader>

      <section className="statsGrid">
        <Stat label="Carousels" value={counts.Carousel || 0} note="Saveable education and objection-handling posts." />
        <Stat label="Reels" value={(counts.Reel || 0) + (counts["Reel + Stories"] || 0) + (counts["Founder Reel"] || 0)} note="Reach and founder/product proof content." />
        <Stat label="Static posts" value={(counts.Static || 0) + (counts["Static + Stories"] || 0)} note="Proof, product, quote, and brand moments." />
        <Stat label="Missing URLs" value={missingAssets} note="Posts without a Cloudinary source URL in Notion." />
      </section>

      <section className="calendarBoard" aria-label="30-day content calendar">
        {data.launchPosts.map((post) => {
          const missing = missingPostFields(post);
          return (
            <article className="calendarTile" key={post.day}>
              <div className="tileHeader">
                <strong>Day {post.day}</strong>
                <span>{recommendedPostTime(post)}</span>
              </div>
              <h2>{post.title}</h2>
              <p>{post.pillar}</p>
              <div className="tileMeta">
                <StatusPill tone="info">{post.format}</StatusPill>
                <StatusPill tone={missing.length ? "warn" : "good"}>{missing.length ? `${missing.length} gaps` : "Ready"}</StatusPill>
              </div>
              <small>{post.cta}</small>
            </article>
          );
        })}
      </section>
    </DashboardShell>
  );
}
