import { DashboardShell, PageHeader, Stat, StatusPill } from "@/app/components";
import { notionSources } from "@/lib/data";
import { getDashboardData } from "@/lib/notion";

export default async function SystemsPage() {
  const data = await getDashboardData();

  return (
    <DashboardShell data={data}>
      <PageHeader eyebrow="Systems" title="Marketing operating system">
        <p>
          The source boards behind the launch: Reels, Stories, carousel education, asset readiness, metrics, customer
          intelligence, and Notion source mapping.
        </p>
      </PageHeader>

      <section className="statsGrid">
        <Stat label="Reel queue" value={data.reels.length} note="Short-form ideas available for launch and remixing." />
        <Stat label="Story rhythm" value={data.stories.length} note="Recurring daily trust and interaction system." />
        <Stat label="Asset needs" value={data.assetNeeds.length} note="Production assets and consent controls." />
        <Stat label="DM routes" value={data.objections.length} note="Customer questions mapped to content responses." />
      </section>

      <section className="systemGrid">
        <article className="systemPanel">
          <div className="sectionTitleRow">
            <div>
              <p className="eyebrow">Reels queue</p>
              <h2>Short-form production backlog</h2>
            </div>
          </div>
          <div className="tableWrap">
            <table>
              <thead><tr><th>Reel</th><th>Hook</th><th>Priority</th><th>CTA</th><th>Shot List</th></tr></thead>
              <tbody>
                {data.reels.map((reel) => (
                  <tr key={reel.title}>
                    <td>{reel.title}</td>
                    <td>{reel.hook}</td>
                    <td>{reel.priority}</td>
                    <td>{reel.cta}</td>
                    <td>{reel.shotList}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>

        <article className="systemPanel">
          <p className="eyebrow">Stories system</p>
          <h2>Recurring daily rhythm</h2>
          <div className="storyGrid">
            {data.stories.map((story) => (
              <div className="storyCell" key={story.day}>
                <strong>{story.day}</strong>
                <span>{story.type}</span>
                <small>{story.frames} frames · {story.sticker}</small>
                <p>{story.cta}</p>
                <StatusPill>{story.highlight}</StatusPill>
              </div>
            ))}
          </div>
        </article>

        <article className="systemPanel">
          <p className="eyebrow">Carousel / feed system</p>
          <h2>Saveable education routes</h2>
          <div className="conceptList">
            {data.carouselConcepts.map((concept) => (
              <div key={concept.post}>
                <strong>{concept.post}</strong>
                <p>{concept.hook}</p>
                <small>{concept.pillar} · {concept.cta}</small>
                <em>{concept.caution}</em>
              </div>
            ))}
          </div>
        </article>

        <article className="systemPanel">
          <p className="eyebrow">Asset library</p>
          <h2>Production and consent checklist</h2>
          <div className="tableWrap">
            <table>
              <thead><tr><th>Asset</th><th>Type</th><th>Format</th><th>Consent</th><th>Notes</th></tr></thead>
              <tbody>
                {data.assetNeeds.map((asset) => (
                  <tr key={asset.name}>
                    <td>{asset.name}</td>
                    <td>{asset.type}</td>
                    <td>{asset.format}</td>
                    <td>{asset.consent}</td>
                    <td>{asset.notes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>

        <article className="systemPanel">
          <p className="eyebrow">Metrics review</p>
          <h2>90-day learning loop</h2>
          <div className="weekGrid">
            {data.metricWeeks.map((week) => (
              <div key={week.week}>
                <strong>{week.week}</strong>
                <p>{week.notes}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="systemPanel">
          <p className="eyebrow">DM intelligence</p>
          <h2>Objection routing</h2>
          <div className="objectionList">
            {data.objections.map((item) => (
              <div key={item.question}>
                <strong>{item.question}</strong>
                <p>{item.response}</p>
                <small>
                  {item.category} · {item.reel ? "Reel" : "No reel"} · {item.carousel ? "Carousel" : "No carousel"} · {item.faq ? "FAQ" : "No FAQ"}
                </small>
              </div>
            ))}
          </div>
        </article>

        <article className="systemPanel sourcePanel">
          <p className="eyebrow">Source map</p>
          <h2>Notion pages and databases</h2>
          <div className="sourceGrid">
            {notionSources.map((source) => (
              <div key={source.id}>
                <strong>{source.name}</strong>
                <p>{source.role}</p>
                <code>{source.id}</code>
              </div>
            ))}
          </div>
        </article>
      </section>
    </DashboardShell>
  );
}
