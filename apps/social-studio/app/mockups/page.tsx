import { DashboardShell, MockupCard, PageHeader, StatusPill } from "@/app/components";
import { designRecipes, palette, type LaunchPost } from "@/lib/data";
import { getDashboardData } from "@/lib/notion";

const formatOrder: LaunchPost["format"][] = ["Static + Stories", "Static", "Carousel", "Founder Reel", "Reel + Stories", "Reel"];

export default async function MockupsPage() {
  const data = await getDashboardData();

  return (
    <DashboardShell data={data}>
      <PageHeader eyebrow="Mockups" title="Production mockup wall">
        <p>
          Practical creative cards for every planned launch post: format ratio, hook hierarchy, asset slot, CTA, and
          readiness state. These are direction boards for production, not final exports.
        </p>
      </PageHeader>

      <section className="mockSystemStrip">
        <article>
          <h2>Palette controls</h2>
          <div className="swatchRow">
            {palette.map((color) => (
              <span key={color.hex} title={`${color.name} ${color.hex}`} style={{ background: color.hex }} />
            ))}
          </div>
        </article>
        <article>
          <h2>Recipe controls</h2>
          <div className="recipeChips">
            {designRecipes.map((recipe) => <StatusPill key={recipe.name}>{recipe.name}</StatusPill>)}
          </div>
        </article>
      </section>

      {formatOrder.map((format) => {
        const posts = data.launchPosts.filter((post) => post.format === format);
        if (!posts.length) return null;
        return (
          <section className="mockSection" key={format}>
            <div className="sectionTitleRow">
              <div>
                <p className="eyebrow">{format}</p>
                <h2>{posts.length} planned creative{posts.length === 1 ? "" : "s"}</h2>
              </div>
            </div>
            <div className="mockGrid">
              {posts.map((post) => <MockupCard post={post} key={post.day} />)}
            </div>
          </section>
        );
      })}
    </DashboardShell>
  );
}
