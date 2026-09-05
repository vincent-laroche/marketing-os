import React from "react";
import { AccessGate } from "@/components/AccessGate";
import { startLogin } from "@/const";
import { useAuth } from "@/_core/hooks/useAuth";
import { socialCampaign, socialConcept, socialPublications, socialReadModel, humanizeGate } from "@/lib/socialReadModel";
import { AlertTriangle, CalendarDays, CheckCircle2, CircleOff, FileWarning, FolderLock, ImageOff, Layers3, Loader2, ShieldCheck } from "lucide-react";

export type SocialSurface = "overview" | "campaigns" | "concepts" | "calendar" | "studio" | "review" | "assets" | "distribution";

const surfaceMeta: Record<SocialSurface, { eyebrow: string; title: string; description: string }> = {
  overview: { eyebrow: "Social Media OS · Phase 1", title: "Social overview", description: "A read-only record of the Social Campaign → Content Concept → Publication hierarchy. This workspace does not publish, schedule, or write to social platforms." },
  campaigns: { eyebrow: "Social Media OS · canonical hierarchy", title: "Social campaigns", description: "Campaign records are visible only with their provenance, stage, and ownership decision." },
  concepts: { eyebrow: "Social Media OS · creative hierarchy", title: "Content concepts", description: "Master concepts remain distinct from platform-specific Publications and do not imply approved copy or assets." },
  calendar: { eyebrow: "Social Media OS · publication planning", title: "Publication calendar", description: "Only source-backed publication dates are shown. Empty dates are intentionally preserved as unscheduled." },
  studio: { eyebrow: "Social Media OS · production evidence", title: "Content studio", description: "Platform requirements are shown separately from absent copy, assets, claims, and rights evidence." },
  review: { eyebrow: "Social Media OS · readiness", title: "Review and gates", description: "Every operational prerequisite remains visible and blocked until its evidence is attached to the canonical Social source." },
  assets: { eyebrow: "Social Media OS · asset governance", title: "Assets and rights", description: "No approved social asset, consent, rights, or claim evidence has been supplied to the read model." },
  distribution: { eyebrow: "Social Media OS · external state", title: "Distribution status", description: "Platform status is read-only evidence. No social operation, schedule, publish action, or external link is exposed here." },
};

function StatusChip({ children, tone = "blocked" }: { children: React.ReactNode; tone?: "blocked" | "fixture" | "ready" }) {
  return <span className={`mos-status-chip mos-status-${tone}`}>{children}</span>;
}

function PublicationRail() {
  return <div className="social-publication-rail">{socialPublications.map((publication) => <article className="social-publication-card" key={publication.recordKey}><div><span className={`social-platform social-platform-${publication.platform.toLowerCase()}`}>{publication.platform}</span><StatusChip tone="fixture">Fixture</StatusChip></div><strong>{publication.format}</strong><span>{publication.readinessGates.filter((gate) => gate.status === "blocked").length} blocked gates</span></article>)}</div>;
}

export default function SocialWorkspace({ surface = "overview" }: { surface?: SocialSurface }) {
  const { isAuthenticated, loading } = useAuth();
  const meta = surfaceMeta[surface];
  if (loading) return <div className="page-loader"><Loader2 className="h-5 w-5 animate-spin" />Checking Marketing OS access…</div>;
  if (!isAuthenticated) return <AccessGate onSignIn={() => startLogin()} />;

  const blocked = socialPublications.flatMap((publication) => publication.readinessGates).filter((gate) => gate.status === "blocked").length;
  return <div className="marketing-page social-workspace"><header className="page-heading marketing-heading"><div><p>{meta.eyebrow}</p><h1>{meta.title}</h1><span>{meta.description}</span></div><div className="page-heading-actions"><StatusChip tone="fixture"><FileWarning className="h-3.5 w-3.5" />Fixture source</StatusChip><span className="readonly-pill"><ShieldCheck className="h-3.5 w-3.5" />Read-only</span></div></header><section className="social-provenance-banner"><div><span className="micro-label">Imported read model</span><strong>Social Media OS Phase 1 — commit <code>0bce0af</code></strong><p>{socialReadModel.nextEvidence}</p></div><span className="source-fingerprint">SHA-256 · {socialReadModel.source.fingerprint.slice(0, 12)}…</span></section>{surface === "overview" && <Overview blocked={blocked} />}{surface === "campaigns" && <Campaigns />}{surface === "concepts" && <Concepts />}{surface === "calendar" && <Calendar />}{surface === "studio" && <Studio />}{surface === "review" && <Review />}{surface === "assets" && <Assets />}{surface === "distribution" && <Distribution />}</div>;
}

function Overview({ blocked }: { blocked: number }) {
  return <><section className="mos-stat-grid"><Metric label="Production campaigns" value="0" note="No approved Social campaign records" tone="blocked" /><Metric label="Fixture campaigns" value={String(socialReadModel.counts.campaigns)} note="Clearly labelled repository records" tone="fixture" /><Metric label="Platform publications" value={String(socialReadModel.counts.publications)} note="Instagram, TikTok, Facebook lanes" tone="fixture" /><Metric label="Operation gates blocked" value={String(blocked)} note="No operation is authorized" tone="blocked" /></section><section className="mos-two-column"><article className="mos-surface-card"><div className="section-kicker"><Layers3 className="h-4 w-4" />Canonical hierarchy</div><h2>Campaign → concept → publications</h2><div className="social-hierarchy"><div><span>Campaign</span><strong>{socialCampaign?.name}</strong><small>{socialCampaign?.ownerDecision}</small></div><div><span>Content concept</span><strong>{socialConcept?.name}</strong><small>{socialConcept?.objective}</small></div></div><PublicationRail /></article><article className="mos-surface-card"><div className="section-kicker"><FolderLock className="h-4 w-4" />Blocked before operation</div><h2>Evidence still required</h2><ul className="mos-evidence-list"><li><strong>Copy and creative</strong><span>No approved platform copy, cover, or asset reference.</span></li><li><strong>Accessibility and tracking</strong><span>No alt or on-screen text evidence and no destination.</span></li><li><strong>Claims and rights</strong><span>No approved claim, consent, ownership, or permitted-use evidence.</span></li><li><strong>Human authority</strong><span>No explicit operation approval or verified external state.</span></li></ul></article></section></>;
}

function Campaigns() {
  return <section className="mos-surface-card"><div className="mos-table-header"><h2>Canonical campaign records</h2><StatusChip tone="fixture">1 fixture only</StatusChip></div><div className="mos-record-table"><div className="mos-row mos-row-head"><span>Record</span><span>Stage</span><span>Source</span><span>Operation state</span></div>{socialReadModel.campaigns.map((campaign) => <div className="mos-row" key={campaign.recordKey}><div><strong>{campaign.name}</strong><small>{campaign.recordKey}</small></div><StatusChip tone="fixture">{campaign.stage}</StatusChip><span>{campaign.source}</span><StatusChip>{campaign.verifiedExternalState.status}</StatusChip></div>)}</div></section>;
}

function Concepts() {
  return <section className="mos-two-column"><article className="mos-surface-card"><div className="section-kicker"><Layers3 className="h-4 w-4" />Master concept</div><h2>{socialConcept?.name}</h2><p>{socialConcept?.coreIdea}</p><dl className="mos-detail-grid"><div><dt>Pillar</dt><dd>{socialConcept?.pillar}</dd></div><div><dt>Audience</dt><dd>{socialConcept?.audience}</dd></div><div><dt>Copy state</dt><dd>{socialConcept?.approvedCopyState}</dd></div><div><dt>Evidence strength</dt><dd>{socialConcept?.evidenceStrength}</dd></div></dl></article><article className="mos-surface-card"><div className="section-kicker"><AlertTriangle className="h-4 w-4" />Concept boundaries</div><h2>Not approved as production</h2><ul className="mos-evidence-list"><li><strong>Asset</strong><span>{socialConcept?.asset.status}: {socialConcept?.asset.reference}</span></li><li><strong>Claim</strong><span>{socialConcept?.claim.status}: {socialConcept?.claim.summary}</span></li><li><strong>Rights</strong><span>{socialConcept?.rights.status}: {socialConcept?.rights.summary}</span></li></ul></article><article className="mos-surface-card mos-span-two"><div className="section-kicker"><CircleOff className="h-4 w-4" />Child publications</div><PublicationRail /></article></section>;
}

function Calendar() {
  return <section className="mos-surface-card"><div className="mos-table-header"><div><div className="section-kicker"><CalendarDays className="h-4 w-4" />Planning evidence</div><h2>No planned publication dates</h2><p>Empty calendar cells are preserved. The imported fixture Publications have no approved schedule.</p></div><StatusChip>0 scheduled</StatusChip></div><div className="mos-record-table"><div className="mos-row mos-row-head"><span>Publication</span><span>Format</span><span>Planned date</span><span>State</span></div>{socialPublications.map((publication) => <div className="mos-row" key={publication.recordKey}><span>{publication.platform}</span><span>{publication.format}</span><span>{publication.plannedDate ?? "No source-backed date"}</span><StatusChip>{publication.verifiedExternalState.status}</StatusChip></div>)}</div></section>;
}

function Studio() {
  return <section className="mos-two-column"><article className="mos-surface-card"><div className="section-kicker"><ImageOff className="h-4 w-4" />Creative source</div><h2>Inert asset state</h2><p>No approved asset reference is attached to the Social fixture. This interface intentionally renders no substitute image, customer quote, product claim, or invented creative.</p><div className="mos-empty-asset"><ImageOff className="h-7 w-7" /><span>No approved media attached</span></div></article><article className="mos-surface-card"><div className="section-kicker"><Layers3 className="h-4 w-4" />Platform requirements</div><h2>Publication-specific constraints</h2><ul className="mos-evidence-list">{socialPublications.map((publication) => <li key={publication.recordKey}><strong>{publication.platform} · {publication.format}</strong><span>{publication.safeArea}</span></li>)}</ul></article></section>;
}

function Review() {
  return <section className="mos-two-column"><article className="mos-surface-card mos-span-two"><div className="mos-table-header"><div><div className="section-kicker"><FileWarning className="h-4 w-4" />Readiness matrix</div><h2>All gates remain blocked</h2></div><StatusChip>{socialPublications.length * 7} blocked evidence checks</StatusChip></div><div className="mos-gate-grid">{socialPublications.map((publication) => <article key={publication.recordKey}><div><span className={`social-platform social-platform-${publication.platform.toLowerCase()}`}>{publication.platform}</span><strong>{publication.format}</strong></div>{publication.readinessGates.map((gate) => <div className="mos-gate-row" key={gate.gate}><CircleOff className="h-3.5 w-3.5" /><span>{humanizeGate(gate.gate)}</span><small>{gate.evidence}</small></div>)}</article>)}</div></article></section>;
}

function Assets() {
  return <section className="mos-two-column"><article className="mos-surface-card"><div className="section-kicker"><FolderLock className="h-4 w-4" />Approved asset registry</div><h2>Intentionally empty</h2><p>The Social Phase 1 read model has no approved media or rights-cleared asset. A visual file alone is not consent, ownership, or permitted-use evidence.</p><div className="mos-empty-asset"><FolderLock className="h-7 w-7" /><span>No approved social assets</span></div></article><article className="mos-surface-card"><div className="section-kicker"><AlertTriangle className="h-4 w-4" />Required before reuse</div><h2>Evidence boundary</h2><ul className="mos-evidence-list"><li><strong>Provenance</strong><span>Supplier or source identity and checksum.</span></li><li><strong>Rights</strong><span>Scope, territories, duration, withdrawal terms, and permitted uses.</span></li><li><strong>Claims</strong><span>Review for any customer, product, outcome, or realism claim.</span></li></ul></article></section>;
}

function Distribution() {
  return <section className="mos-surface-card"><div className="mos-table-header"><div><div className="section-kicker"><CircleOff className="h-4 w-4" />External state</div><h2>No external social operation is available</h2><p>The read model has no platform links, scheduled dates, published state, or verified-live evidence.</p></div><StatusChip>Publishing disabled</StatusChip></div><div className="mos-record-table"><div className="mos-row mos-row-head"><span>Platform</span><span>Publication</span><span>External state</span><span>Verification</span></div>{socialPublications.map((publication) => <div className="mos-row" key={publication.recordKey}><span>{publication.platform}</span><span>{publication.format}</span><StatusChip>{publication.verifiedExternalState.status}</StatusChip><span>{publication.verifiedExternalState.evidence}</span></div>)}</div></section>;
}

function Metric({ label, value, note, tone }: { label: string; value: string; note: string; tone: "blocked" | "fixture" }) {
  return <article className={`mos-metric mos-metric-${tone}`}><span>{label}</span><strong>{value}</strong><small>{note}</small></article>;
}
