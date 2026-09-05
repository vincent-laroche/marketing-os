import React from "react";
import { AccessGate } from "@/components/AccessGate";
import { startLogin } from "@/const";
import { useAuth } from "@/_core/hooks/useAuth";
import { trpc } from "@/lib/trpc";
import { AlertTriangle, CheckCircle2, Eye, Loader2, LockKeyhole } from "lucide-react";

export default function EmailReview() {
  const { isAuthenticated, loading } = useAuth();
  const portfolio = trpc.campaigns.portfolio.useQuery(undefined, { enabled: isAuthenticated });
  if (loading) return <div className="page-loader"><Loader2 className="h-5 w-5 animate-spin" />Checking Marketing OS access…</div>;
  if (!isAuthenticated) return <AccessGate onSignIn={() => startLogin()} />;
  if (portfolio.isLoading) return <div className="page-loader"><Loader2 className="h-5 w-5 animate-spin" />Loading review evidence…</div>;
  if (portfolio.isError) return <div className="page-loader page-error"><AlertTriangle className="h-5 w-5" />{portfolio.error.message}</div>;
  const emails = portfolio.data ?? [];
  const selected = emails.find(email => email.sourceStatus === "ready") ?? emails[0];
  return <div className="marketing-page review-page"><header className="page-heading marketing-heading"><div><p>Email OS · production</p><h1>Review &amp; QA</h1><span>One evidence queue for source completion, rendering, consent, links, claims, and release readiness. No source values are invented here.</span></div><div className="heading-actions"><span className="warning-chip">Deterministic QA only</span><a href="/workspace" className="quiet-button"><Eye className="h-4 w-4" />Open campaign workspace</a></div></header><section className="review-grid"><article className="review-queue"><div className="filter-strip"><span>Status: Source evidence</span><span>Journey: All</span><span>Platform: Any</span><small>{emails.length} canonical emails · sorted by source state</small></div><div className="review-table"><div className="review-head"><span>Email</span><span>Journey</span><span>Source</span><span>Revision</span><span>QA</span><span>Gate</span></div>{emails.map(email => <a key={email.key} href="/workspace" className="review-row"><span><strong>{email.key} · {email.name.split("·").slice(1).join("·").trim()}</strong><small>Canonical source · {email.shopifySurface}</small></span><code>{email.series}</code><i className={email.sourceStatus === "ready" ? "evidence ready" : "evidence blocked"}>{email.sourceStatus === "ready" ? <CheckCircle2 className="h-3.5 w-3.5" /> : <LockKeyhole className="h-3.5 w-3.5" />}{email.sourceStatus === "ready" ? "Ready" : "Blocked"}</i><span>{email.latestRevision ? "Saved" : "None"}</span><span>{email.latestQa?.status?.replaceAll("_", " ") ?? "Not run"}</span><span>{email.releaseStage.replaceAll("_", " ")}</span></a>)}</div></article><aside className="review-preview"><div className="section-card-head"><div><h2>{selected?.key ?? "No source selected"} · Review state</h2><p>Preview evidence is intentionally absent until a source-backed revision and QA run exist.</p></div><span className="state-pill">Evidence</span></div><div className="preview-paper"><p>Email OS review</p><h3>{selected?.subject || "No canonical subject available"}</h3><span>Rendered desktop and mobile screenshots attach only to immutable export packages. This panel does not fabricate a preview.</span></div><div className="preview-foot"><LockKeyhole className="h-4 w-4" />No draft, schedule, or sending action is available here.</div></aside></section></div>;
}
