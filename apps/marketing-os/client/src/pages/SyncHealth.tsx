import { AccessGate } from "@/components/AccessGate";
import { startLogin } from "@/const";
import { useAuth } from "@/_core/hooks/useAuth";
import { trpc } from "@/lib/trpc";
import { AlertTriangle, CheckCircle2, Loader2, RefreshCw, ShieldCheck } from "lucide-react";
import React from "react";

function formatDate(value: Date | string | null | undefined) {
  if (!value) return "No successful Worker receipt yet";
  return new Date(value).toLocaleString();
}

export default function SyncHealth() {
  const { isAuthenticated, loading, user } = useAuth();
  const health = trpc.marketingSync.health.useQuery(undefined, { enabled: isAuthenticated });
  const reconcile = trpc.marketingSync.run.useMutation({ onSuccess: () => health.refetch() });
  if (loading) return <div className="page-loader"><Loader2 className="h-5 w-5 animate-spin" />Checking Marketing OS access…</div>;
  if (!isAuthenticated) return <AccessGate onSignIn={() => startLogin()} />;
  if (health.isLoading) return <div className="page-loader"><Loader2 className="h-5 w-5 animate-spin" />Loading synchronization evidence…</div>;
  if (health.isError) return <div className="page-loader page-error"><AlertTriangle className="h-5 w-5" />{health.error.message}</div>;
  const latestRun = health.data?.latestRun;

  return <div className="marketing-page email-page">
    <header className="page-heading marketing-heading"><div><p>Shared control plane</p><h1>Sync Health</h1><span>Evidence for the audited Notion reconciliation Worker. Canonical content, consent, rights, approval decisions, and live marketing operations stay outside this control.</span></div><span className="surface-chip">Cloudflare Worker · D1 mapping</span></header>
    <section className="marketing-metrics"><article><span>Worker binding</span><strong>{health.data?.configured ? "Ready" : "Blocked"}</strong><small>Server-side credential only</small></article><article className="email-accent"><span>Latest state</span><strong>{latestRun?.status ?? "Awaiting receipt"}</strong><small>{formatDate(latestRun?.completedAt)}</small></article><article><span>Records observed</span><strong>{latestRun?.recordCount ?? 0}</strong><small>Aggregate only — no content shown</small></article><article className={latestRun?.blockedCount ? "risk" : ""}><span>Blocked records</span><strong>{latestRun?.blockedCount ?? 0}</strong><small>Conflicts remain fail-closed</small></article></section>
    <section className="email-lower-grid"><article className="release-gate-card"><div className="section-card-head"><div><h2>Synchronization boundary</h2><p>Two-way metadata reconciliation is available; no marketing action is part of this worker.</p></div><span className="locked-chip">Operations disabled</span></div><ul><li><CheckCircle2 />Notion source and worker revisions are fingerprinted</li><li><CheckCircle2 />D1 mapping state is idempotent and conflict-preserving</li><li><ShieldCheck />Shopify consent remains Shopify-authoritative</li><li><ShieldCheck />No send, schedule, publish, activation, or audience mutation path</li></ul></article><article className="release-gate-card"><div className="section-card-head"><div><h2>Manual reconciliation</h2><p>Queues the approved Worker on demand. It reconciles source metadata only and records an audit event.</p></div></div>{user?.role === "admin" ? <button className="quiet-button" onClick={() => reconcile.mutate()} disabled={reconcile.isPending}><RefreshCw className={reconcile.isPending ? "h-4 w-4 animate-spin" : "h-4 w-4"} />{reconcile.isPending ? "Queuing…" : "Run reconciliation"}</button> : <p>Only the Marketing OS owner may request a reconciliation. All other authenticated users can read health evidence.</p>}{reconcile.isError && <p className="text-red-700">{reconcile.error.message}</p>}{reconcile.data && <p>Run {reconcile.data.runId} was accepted. Refresh this page after the Worker posts its aggregate receipt.</p>}</article></section>
  </div>;
}
