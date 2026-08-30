import { BeefreeWorkspace } from "@/components/BeefreeWorkspace";
import { AccessGate } from "@/components/AccessGate";
import { DraftEvidenceControl, PreparePackageControl, ScreenshotUploadGate } from "@/components/HandoffSafetyControls";
import { ReleaseGate } from "@/components/ReleaseGate";
import { WorkspaceShell } from "@/components/WorkspaceShell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Textarea } from "@/components/ui/textarea";
import { trpc } from "@/lib/trpc";
import { useAuth } from "@/_core/hooks/useAuth";
import { startLogin } from "@/const";
import {
  AlertTriangle,
  ArrowUpRight,
  BellRing,
  CheckCircle2,
  ChevronRight,
  CircleAlert,
  ClipboardCheck,
  Download,
  FileArchive,
  Filter,
  Layers3,
  Link2,
  Loader2,
  LockKeyhole,
  PackageCheck,
  Search,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
import { useMemo, useState } from "react";

function stateMeta(sourceStatus: string, qaStatus?: string | null) {
  if (sourceStatus === "source_blocked") return { label: "Blocked", className: "status-blocked" };
  if (sourceStatus === "needs_input") return { label: "Needs input", className: "status-warning" };
  if (qaStatus === "qa_failed") return { label: "QA failed", className: "status-blocked" };
  if (qaStatus === "qa_passed") return { label: "QA passed", className: "status-ready" };
  return { label: "Source ready", className: "status-neutral" };
}

function surfaceClass(surface: string) {
  return surface === "Flow" ? "surface-flow" : surface === "Campaign" ? "surface-campaign" : "surface-messaging";
}

function formatTime(value: Date | string | null | undefined) {
  if (!value) return "Not yet saved";
  return new Date(value).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

function downloadEvidence(filename: string, content: string, type: string) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function ScreenshotEvidenceUpload({ packageId, screenshots, evidenceManifestUrl, onSaved }: { packageId: number; screenshots: Array<{ id: number; viewport: string; storageUrl: string }>; evidenceManifestUrl?: string; onSaved: () => void }) {
  const [viewport, setViewport] = useState("desktop");
  const upload = trpc.campaigns.handoff.uploadScreenshot.useMutation({ onSuccess: onSaved });
  const onFileChange = (file: File | undefined) => {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === "string") upload.mutate({ exportPackageId: packageId, viewport: viewport as "320px" | "375px" | "430px" | "desktop" | "gmail-dark-mode", dataUrl: reader.result });
    };
    reader.readAsDataURL(file);
  };
  return <div className="screenshot-evidence"><div><strong>Responsive evidence</strong><p>Attach the rendered email capture; this stores evidence only and never sends.</p></div><div className="screenshot-controls"><select value={viewport} onChange={event => setViewport(event.target.value)}><option value="320px">320px</option><option value="375px">375px</option><option value="430px">430px</option><option value="desktop">Desktop</option><option value="gmail-dark-mode">Gmail dark mode</option></select><input type="file" accept="image/png,image/jpeg,image/webp" disabled={upload.isPending} onChange={event => onFileChange(event.target.files?.[0])} /></div>{screenshots.length ? <div className="screenshot-links">{screenshots.map(screenshot => <a key={screenshot.id} href={screenshot.storageUrl} target="_blank" rel="noreferrer">{screenshot.viewport}</a>)}{evidenceManifestUrl ? <a href={evidenceManifestUrl} target="_blank" rel="noreferrer">Evidence manifest</a> : null}</div> : null}</div>;
}

export default function Workspace() {
  const { isAuthenticated, loading } = useAuth();
  const portfolio = trpc.campaigns.portfolio.useQuery(undefined, { enabled: isAuthenticated });
  const recipes = trpc.campaigns.flow.recipes.useQuery(undefined, { enabled: isAuthenticated });
  const audit = trpc.campaigns.audit.useQuery(undefined, { enabled: isAuthenticated });
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<"all" | "blocked" | "ready">("all");
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [handoffNote, setHandoffNote] = useState("");
  const [draftUrl, setDraftUrl] = useState("");
  const [catalogQuery, setCatalogQuery] = useState("");
  const catalog = trpc.campaigns.catalog.search.useQuery({ query: catalogQuery }, { enabled: isAuthenticated && catalogQuery.trim().length > 1 });

  const emails = portfolio.data ?? [];
  const selected = emails.find(email => email.key === selectedKey) ?? emails[0] ?? null;
  const detail = trpc.campaigns.detail.useQuery({ emailKey: selected?.key ?? "CR-1" }, { enabled: isAuthenticated && Boolean(selected) });
  const runQa = trpc.campaigns.qa.run.useMutation({ onSuccess: () => void detail.refetch() });
  const prepareHandoff = trpc.campaigns.handoff.prepare.useMutation({ onSuccess: () => void detail.refetch() });
  const notifySourceBlockers = trpc.campaigns.alerts.notifySourceBlockers.useMutation({ onSuccess: () => void audit.refetch() });
  const recordEvidence = trpc.campaigns.handoff.recordEvidence.useMutation({
    onSuccess: () => {
      setDraftUrl("");
      setHandoffNote("");
      void detail.refetch();
    },
  });
  const captureSnapshot = trpc.campaigns.catalog.snapshot.useMutation({ onSuccess: () => void detail.refetch() });

  const filtered = useMemo(() => emails.filter(email => {
    const searchable = `${email.key} ${email.name} ${email.series} ${email.subject}`.toLowerCase();
    if (!searchable.includes(query.toLowerCase())) return false;
    if (filter === "blocked") return email.sourceStatus === "source_blocked" || email.sourceStatus === "needs_input";
    if (filter === "ready") return email.sourceStatus === "ready";
    return true;
  }), [emails, filter, query]);

  const grouped = useMemo(() => filtered.reduce<Record<string, typeof emails>>((groups, email) => {
    (groups[email.series] ||= []).push(email);
    return groups;
  }, {}), [filtered]);
  const metrics = useMemo(() => ({
    total: emails.length,
    ready: emails.filter(email => email.sourceStatus === "ready").length,
    blocked: emails.filter(email => email.sourceStatus === "source_blocked").length,
    needsInput: emails.filter(email => email.sourceStatus === "needs_input").length,
    creativeSaved: emails.filter(email => ["creative_saved", "qa_passed", "shopify_draft_verified"].includes(email.releaseStage)).length,
    qaPassed: emails.filter(email => ["qa_passed", "shopify_draft_verified"].includes(email.releaseStage)).length,
    draftVerified: emails.filter(email => email.releaseStage === "shopify_draft_verified").length,
  }), [emails]);
  const latestRevision = detail.data?.revisions?.[0];
  const latestQa = detail.data?.qaRuns?.[0];
  const latestExport = detail.data?.exportPackages?.[0];
  const selectedState = selected ? stateMeta(selected.sourceStatus, latestQa?.status) : stateMeta("source_blocked");

  if (loading) return <div className="page-loader"><Loader2 className="h-5 w-5 animate-spin" />Checking access to Campaign OS…</div>;
  if (!isAuthenticated) return <WorkspaceShell isAuthenticated={false} onSignIn={() => startLogin()}><span /></WorkspaceShell>;
  if (portfolio.isLoading) return <div className="page-loader"><Loader2 className="h-5 w-5 animate-spin" />Loading canonical campaign portfolio…</div>;
  if (portfolio.isError) return <div className="page-loader page-error"><AlertTriangle className="h-5 w-5" />{portfolio.error.message}</div>;

  return (
    <div className="campaign-page">
      <header className="campaign-header">
        <div>
          <p className="eyebrow">Operations console · Shopify marketing control plane</p>
          <h1>Campaign workspace</h1>
          <p className="lede">One canonical email at a time. Save evidence, verify readiness, then hand off deliberately.</p>
        </div>
        <div className="header-safety"><LockKeyhole className="h-4 w-4" /><span>Sending, scheduling, activation, and audience changes are unavailable here.</span></div>
      </header>

      <section className="metric-grid" aria-label="Campaign readiness metrics">
        <article className="metric-card"><span>Canonical emails</span><strong>{metrics.total}</strong><p>All source records imported verbatim</p></article>
        <article className="metric-card metric-ready"><span>Source ready</span><strong>{metrics.ready}</strong><p>Eligible for editorial QA, not activation</p></article>
        <article className="metric-card metric-warning"><span>Needs input</span><strong>{metrics.needsInput}</strong><p>Real-data or audience dependency remains</p></article>
        <article className="metric-card metric-blocked"><span>Hard blocked</span><strong>{metrics.blocked}</strong><p>Required module or source dependency missing</p></article>
      </section>
      <section className="release-matrix" aria-label="Release readiness stages">
        <div><span>Creative saved</span><strong>{metrics.creativeSaved}</strong><p>Durable provider JSON and HTML evidence</p></div>
        <div><span>QA passed</span><strong>{metrics.qaPassed}</strong><p>Deterministic gates clear; visual review remains</p></div>
        <div><span>Shopify draft verified</span><strong>{metrics.draftVerified}</strong><p>Manual read-back evidence recorded</p></div>
        <div><span>Activation evidence</span><strong>0</strong><p>Only recorded manually after out-of-band approval</p></div>
        <div><span>Post-send measurement</span><strong>0</strong><p>Unavailable until a verified Shopify send exists</p></div>
      </section>

      <ReleaseGate isAuthenticated={isAuthenticated} alertPending={notifySourceBlockers.isPending} onAlert={() => notifySourceBlockers.mutate()} />

      <div className="portfolio-layout">
        <section className="portfolio-panel">
          <div className="panel-heading"><div><p className="eyebrow">Portfolio</p><h2>53 canonical email records</h2></div><Layers3 className="h-5 w-5" /></div>
          <div className="portfolio-controls">
            <label className="search-field"><Search className="h-4 w-4" /><Input value={query} onChange={event => setQuery(event.target.value)} placeholder="Search email, subject, series" /></label>
            <div className="filter-group"><Filter className="h-4 w-4" />{(["all", "ready", "blocked"] as const).map(value => <button key={value} className={filter === value ? "filter-active" : ""} onClick={() => setFilter(value)}>{value === "all" ? "All" : value === "ready" ? "Ready" : "Needs review"}</button>)}</div>
          </div>
          <ScrollArea className="portfolio-scroll">
            {Object.entries(grouped).map(([series, seriesEmails]) => <div className="series-group" key={series}>
              <p className="series-label">{series}<span>{seriesEmails.length}</span></p>
              {seriesEmails.map(email => {
                const meta = stateMeta(email.sourceStatus, email.latestQa?.status);
                return <button key={email.key} className={selected?.key === email.key ? "email-row email-row-active" : "email-row"} onClick={() => setSelectedKey(email.key)}>
                  <span className="email-key">{email.key}</span>
                  <span className="email-row-copy"><strong>{email.name.split("·")[1]?.trim() || email.name}</strong><small>{email.shopifySurface} · {email.revisionCount} revision{email.revisionCount === 1 ? "" : "s"}</small></span>
                  <span className={`status-chip ${meta.className}`}>{meta.label}</span>
                </button>;
              })}
            </div>)}
          </ScrollArea>
        </section>

        {selected ? <section className="workspace-panel">
          <div className="workspace-titlebar">
            <div><p className="eyebrow">{selected.series} · {selected.shopifySurface}</p><h2><span>{selected.key}</span>{selected.name.split("·")[1]?.trim() || selected.name}</h2><p>{selected.position || "Canonical sequence position not specified"}</p></div>
            <span className={`status-chip ${selectedState.className}`}>{selectedState.label}</span>
          </div>
          <div className="workspace-meta"><span><strong>Source digest</strong><code>{selected.sourceDigest.slice(0, 12)}…</code></span><span><strong>Last revision</strong>{formatTime(latestRevision?.createdAt)}</span><span><strong>Shopify surface</strong>{selected.shopifySurface}</span></div>

          <div className="workspace-grid">
            <article className="source-card"><div className="card-head"><div><p className="eyebrow">Canonical source</p><h3>Verbatim source, never overwritten</h3></div><LockKeyhole className="h-4 w-4" /></div>
              <dl className="metadata-list"><div><dt>Subject</dt><dd>{selected.subject || "Source input missing"}</dd></div><div><dt>Preview text</dt><dd>{selected.previewText || "Source input missing"}</dd></div><div><dt>CTA</dt><dd>{selected.cta || "Source input missing"}</dd></div></dl>
              <div className="source-body">{selected.body || "No canonical body was found."}</div>
            </article>
            <article className="source-card"><div className="card-head"><div><p className="eyebrow">Required composition</p><h3>Modules & dependencies</h3></div><PackageCheck className="h-4 w-4" /></div>
              <p className="module-stack">{selected.moduleStack || "No source module stack recorded."}</p>
              <div className="dependency-list">{selected.blockers.map(item => <p className="dependency-blocked" key={item}><CircleAlert className="h-4 w-4" />{item}</p>)}{selected.dependencies.map(item => <p className="dependency-warning" key={item}><AlertTriangle className="h-4 w-4" />{item}</p>)}{!selected.blockers.length && !selected.dependencies.length ? <p className="dependency-ready"><CheckCircle2 className="h-4 w-4" />No unresolved source dependency detected.</p> : null}</div>
            </article>
          </div>

          <section className="evidence-section"><div className="section-heading"><div><p className="eyebrow">Revision evidence</p><h3>Immutable editor documents and exported HTML</h3></div><p>Downloadable evidence is retained per revision; canonical copy stays separate and unchanged.</p></div>{detail.data?.revisions?.length ? <div className="revision-list">{detail.data.revisions.map(revision => <details key={revision.id}><summary><span>Revision #{revision.id}</span><span>{formatTime(revision.createdAt)}</span><span>{revision.provider}</span><ChevronRight className="h-4 w-4" /></summary><div className="revision-actions"><Button size="sm" variant="outline" onClick={() => downloadEvidence(`${selected.key}-revision-${revision.id}.json`, revision.providerDocument, "application/json")}><Download className="mr-2 h-3.5 w-3.5" />Provider JSON</Button>{revision.renderedHtml ? <Button size="sm" variant="outline" onClick={() => downloadEvidence(`${selected.key}-revision-${revision.id}.html`, revision.renderedHtml || "", "text/html")}><Download className="mr-2 h-3.5 w-3.5" />Rendered HTML</Button> : null}</div><pre>{revision.renderedHtml || revision.providerDocument}</pre></details>)}</div> : <p className="empty-note">No persisted revision yet. Save from the editor to create retained provider JSON and rendered HTML evidence.</p>}</section>

          <section className="editor-section"><div className="section-heading"><div><p className="eyebrow">Creative workspace</p><h3>Provider-safe Beefree editor</h3></div><p>Saving produces a new revision with provider JSON and rendered HTML; it never changes the canonical source.</p></div><BeefreeWorkspace emailKey={selected.key} subject={selected.subject} previewText={selected.previewText} /></section>

          <section className="readiness-section">
            <div className="section-heading"><div><p className="eyebrow">Release verification</p><h3>Deterministic QA & controlled handoff</h3></div><p>QA blocks unsafe or incomplete packages before Shopify review.</p></div>
            <div className="readiness-grid">
              <article className="qa-card"><div className="card-head"><h4>Pre-handoff QA</h4><Button size="sm" variant="outline" disabled={!isAuthenticated || runQa.isPending} onClick={() => runQa.mutate({ emailKey: selected.key, renderedHtml: latestRevision?.renderedHtml || undefined })}><ClipboardCheck className="mr-2 h-4 w-4" />Run QA</Button></div>
                {latestQa ? <><p className={latestQa.status === "qa_passed" ? "qa-summary qa-passed" : "qa-summary qa-failed"}>{latestQa.summary}</p><div className="qa-checks">{(latestQa.checks as Array<{ id: string; label: string; status: string; detail: string }>).map(check => <div key={check.id} className={`qa-check qa-${check.status}`}><span>{check.status === "pass" ? <CheckCircle2 className="h-4 w-4" /> : check.status === "fail" ? <CircleAlert className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}</span><div><strong>{check.label}</strong><p>{check.detail}</p></div></div>)}</div></> : <p className="empty-note">Run deterministic QA after saving a revision. Visual screenshots and Shopify verification remain separate manual gates.</p>}
              </article>
              <article className="handoff-card"><div className="card-head"><h4>Shopify Messaging handoff</h4><a href="https://admin.shopify.com/store/one-head-hair/apps/shopify-messaging" target="_blank" rel="noreferrer"><ArrowUpRight className="h-4 w-4" />Open workspace</a></div>
                <p>Campaign OS can prepare an immutable package and record manual draft evidence. It never clicks send, schedule, or activate.</p>
                <div className="handoff-state"><FileArchive className="h-4 w-4" /><span>{latestExport ? `Package #${latestExport.id} · ${latestExport.checksum.slice(0, 10)}…` : "No approved package generated"}</span>{latestExport?.artifactUrl ? <a href={latestExport.artifactUrl} target="_blank" rel="noreferrer"><Download className="h-3.5 w-3.5" />Artifact</a> : null}</div>
                <PreparePackageControl isAuthenticated={isAuthenticated} hasRenderedHtml={Boolean(latestRevision?.renderedHtml)} pending={prepareHandoff.isPending} onPrepare={() => prepareHandoff.mutate({ emailKey: selected.key, renderedHtml: latestRevision?.renderedHtml || "" })} />
                <ScreenshotUploadGate hasExportPackage={Boolean(latestExport)}>{latestExport ? <ScreenshotEvidenceUpload packageId={latestExport.id} screenshots={detail.data?.screenshots?.filter(screenshot => screenshot.exportPackageId === latestExport.id) ?? []} evidenceManifestUrl={detail.data?.screenshotManifests?.find(manifest => manifest.exportPackageId === latestExport.id)?.artifactUrl} onSaved={() => void detail.refetch()} /> : null}</ScreenshotUploadGate>
                <div className="evidence-form"><Input value={draftUrl} onChange={event => setDraftUrl(event.target.value)} placeholder="Paste Shopify draft URL after manual creation" /><Textarea value={handoffNote} onChange={event => setHandoffNote(event.target.value)} placeholder="Record what you verified in Shopify" /><DraftEvidenceControl isAuthenticated={isAuthenticated} draftUrl={draftUrl} evidenceNote={handoffNote} pending={recordEvidence.isPending} onRecord={() => recordEvidence.mutate({ emailKey: selected.key, shopifyDraftUrl: draftUrl, evidenceNote: handoffNote })} /></div>
              </article>
            </div>
          </section>

          <section className="catalog-section"><div className="section-heading"><div><p className="eyebrow">Read-only Shopify catalog boundary</p><h3>Product snapshots, not live mutation</h3></div><p>Search becomes available after authenticated Shopify read credentials are configured.</p></div><label className="catalog-search"><Search className="h-4 w-4" /><Input value={catalogQuery} onChange={event => setCatalogQuery(event.target.value)} placeholder="Search Shopify catalog to capture a stable product snapshot" /></label>{catalogQuery.length > 1 && isAuthenticated ? <div className="catalog-results">{catalog.isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : catalog.data?.products.length ? catalog.data.products.map(product => <div key={product.id}><div><strong>{product.title}</strong><span>{product.id} · {product.status} · {product.price || "Price unavailable"}</span></div><Button size="sm" variant="outline" disabled={captureSnapshot.isPending} onClick={() => captureSnapshot.mutate({ emailKey: selected.key, product })}>Freeze snapshot</Button></div>) : <p>{catalog.data?.message || "No matching product record."}</p>}</div> : <p className="empty-note">Once configured, catalog search is read-only. Capturing a snapshot only stores the returned product evidence with this email; it never updates Shopify.</p>}{detail.data?.productSnapshots?.length ? <div className="snapshot-strip">{detail.data.productSnapshots.slice(0, 3).map(snapshot => <span key={snapshot.id}><PackageCheck className="h-3.5 w-3.5" />{snapshot.title} · {snapshot.price || "price unavailable"} · {formatTime(snapshot.capturedAt)}</span>)}</div> : null}</section>
        </section> : null}
      </div>

      <section className="lower-grid"><article className="recipe-panel"><div className="panel-heading"><div><p className="eyebrow">Automation recipes</p><h2>Flow and native Messaging readiness</h2></div><Sparkles className="h-5 w-5" /></div>{recipes.data?.map(recipe => <details className="recipe-row" key={recipe.journey}><summary><div><strong>{recipe.journey}</strong><p>{recipe.rule}</p></div><span className={surfaceClass(recipe.target.includes("Flow") ? "Flow" : recipe.target.includes("Campaign") ? "Campaign" : "Messaging")}>{recipe.target}</span><p className="recipe-safety">{recipe.safety}</p><ChevronRight className="h-4 w-4" /></summary><div className="recipe-artifact"><p><strong>Version:</strong> {recipe.version}</p><ol>{recipe.steps.map(step => <li key={step}>{step}</li>)}</ol><p><strong>Collision rule:</strong> {recipe.collisionRule}</p><p><strong>Exit rule:</strong> {recipe.exitRule}</p><p><strong>Frequency rule:</strong> {recipe.frequencyRule}</p></div></details>)}</article>
        <article className="audit-panel"><div className="panel-heading"><div><p className="eyebrow">Control ledger</p><h2>Recent audit events</h2></div><ClipboardCheck className="h-5 w-5" /></div>{audit.data?.length ? audit.data.map(event => <div className="audit-row" key={event.id}><span className="audit-marker" /><div><strong>{event.eventType.replaceAll("_", " ")}</strong><p>{event.emailKey || "Campaign OS"}</p></div><time>{formatTime(event.createdAt)}</time></div>) : <p className="empty-note">The ledger begins when a signed-in operator saves a revision, runs QA, prepares a package, or records Shopify draft evidence.</p>}</article>
      </section>
    </div>
  );
}
