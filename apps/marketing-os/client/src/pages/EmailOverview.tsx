import React from "react";
import { AccessGate } from "@/components/AccessGate";
import { startLogin } from "@/const";
import { useAuth } from "@/_core/hooks/useAuth";
import { trpc } from "@/lib/trpc";
import { AlertTriangle, ArrowRight, CheckCircle2, Loader2, LockKeyhole, ShieldCheck } from "lucide-react";
import { Link } from "wouter";

function journeyCode(series: string) {
  return series.split("·")[0]?.trim() || series;
}

function journeyLabel(series: string) {
  const withoutCode = series.split("·").slice(1).join("·").trim();
  return withoutCode || series;
}

export default function EmailOverview() {
  const { isAuthenticated, loading } = useAuth();
  const portfolio = trpc.campaigns.portfolio.useQuery(undefined, { enabled: isAuthenticated });
  if (loading) return <div className="page-loader"><Loader2 className="h-5 w-5 animate-spin" />Checking Marketing OS access…</div>;
  if (!isAuthenticated) return <AccessGate onSignIn={() => startLogin()} />;
  if (portfolio.isLoading) return <div className="page-loader"><Loader2 className="h-5 w-5 animate-spin" />Loading canonical Email OS evidence…</div>;
  if (portfolio.isError) return <div className="page-loader page-error"><AlertTriangle className="h-5 w-5" />{portfolio.error.message}</div>;

  const emails = portfolio.data ?? [];
  const journeys = Array.from(new Map(emails.map(email => [email.series, emails.filter(item => item.series === email.series)])).entries());
  const ready = emails.filter(email => email.sourceStatus === "ready").length;
  const blocked = emails.length - ready;

  return <div className="marketing-page email-page">
    <header className="page-heading marketing-heading"><div><p>Email domain</p><h1>Email OS</h1><span>The production and release workspace for the canonical 53-email programme. Source completion, preview evidence, platform state, and owner authorization remain separate.</span></div><div className="heading-actions"><span className="surface-chip">Shopify Messaging + Flow</span><Link href="/email/review" className="quiet-button"><ShieldCheck className="h-4 w-4" />Open review queue</Link></div></header>
    <section className="marketing-metrics"><article><span>Canonical emails</span><strong>{emails.length}</strong><small>Across {journeys.length} lifecycle series</small></article><article className="email-accent"><span>Source-ready</span><strong>{ready}</strong><small>Eligible for editorial and QA review</small></article><article className="risk"><span>Source blockers</span><strong>{blocked}</strong><small>Unresolved source or real-data dependencies</small></article><article><span>Authorized sends</span><strong>0</strong><small>Owner release decision still required</small></article></section>
    <section className="email-overview-grid"><article className="journey-board"><div className="section-card-head"><div><h2>Journey portfolio</h2><p>Seven independent programmes. Campaign progress does not imply release readiness.</p></div><span className="state-pill">Source evidence</span></div><div className="journey-grid">{journeys.map(([series, items]) => <Link key={series} href="/email/campaigns" className="journey-card"><code>{journeyCode(series)}</code><span>{journeyLabel(series)}</span><small>{items.length} canonical email{items.length === 1 ? "" : "s"}</small></Link>)}</div></article><article className="preview-readiness"><div className="section-card-head"><div><h2>Preview readiness</h2><p>Truthful rendering requires source and real-data dependencies to be resolved.</p></div><span className="state-pill">{ready} / {emails.length}</span></div><div className="readiness-ring"><strong>{emails.length ? Math.round((ready / emails.length) * 100) : 0}%</strong><span>source ready</span></div><div className="progress-line"><i style={{ width: `${emails.length ? (ready / emails.length) * 100 : 0}%` }} /></div><p>{ready} records can proceed to editorial review. {blocked} remain deliberately blocked.</p></article></section>
    <section className="email-lower-grid"><article className="production-pulse"><div className="section-card-head"><div><h2>Production pulse</h2><p>What the team should inspect before opening raw source or Issue evidence.</p></div><Link href="/email/library">View all {emails.length}<ArrowRight className="h-3.5 w-3.5" /></Link></div><div className="pulse-table"><div className="pulse-head"><span>Email</span><span>Journey</span><span>Source</span><span>Next gate</span></div>{emails.slice(0, 6).map(email => <Link key={email.key} href="/email/review" className="pulse-row"><span><strong>{email.key} · {email.name.split("·").slice(1).join("·").trim()}</strong><small>Canonical source · {email.shopifySurface}</small></span><code>{email.series}</code><i className={email.sourceStatus === "ready" ? "evidence ready" : "evidence blocked"}>{email.sourceStatus === "ready" ? <CheckCircle2 className="h-3.5 w-3.5" /> : <LockKeyhole className="h-3.5 w-3.5" />}{email.sourceStatus === "ready" ? "Ready" : "Blocked"}</i><span>{email.sourceStatus === "ready" ? "Editorial review" : "Source authority"}</span></Link>)}</div></article><article className="release-gate-card"><div className="section-card-head"><div><h2>Release gate</h2><p>A merged record never becomes a marketing send.</p></div><span className="locked-chip">Locked</span></div><ul><li><CheckCircle2 />Canonical source and repository build</li><li><LockKeyhole />Audience and consent re-verification</li><li><LockKeyhole />Journey collision and exit rules</li><li><LockKeyhole />Owner schedule / send authorization</li></ul></article></section>
  </div>;
}
