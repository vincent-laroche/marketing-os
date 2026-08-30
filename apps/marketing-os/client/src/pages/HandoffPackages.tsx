import { AccessGate } from "@/components/AccessGate";
import { trpc } from "@/lib/trpc";
import { useAuth } from "@/_core/hooks/useAuth";
import { startLogin } from "@/const";
import { FileArchive, Loader2, LockKeyhole } from "lucide-react";

export default function HandoffPackages() {
  const { isAuthenticated, loading } = useAuth();
  const portfolio = trpc.campaigns.portfolio.useQuery(undefined, { enabled: isAuthenticated });
  if (loading) return <div className="page-loader"><Loader2 className="h-5 w-5 animate-spin" />Checking access…</div>;
  if (!isAuthenticated) return <AccessGate onSignIn={() => startLogin()} />;
  if (portfolio.isLoading) return <div className="page-loader"><Loader2 className="h-5 w-5 animate-spin" />Loading handoff state…</div>;
  const staged = (portfolio.data ?? []).filter(email => email.revisionCount > 0 || email.latestHandoff);
  return <div className="ops-page"><header className="page-heading"><p className="eyebrow">Shopify review boundary</p><h1>Evidence packages, not publish controls.</h1><p>Exported artifacts and manual draft read-back are retained here. Shopify sends and activation remain outside this application.</p></header><section className="handoff-guard"><LockKeyhole className="h-5 w-5" /><div><strong>Manual-only handoff</strong><p>This platform cannot send, schedule, activate, or change an audience.</p></div></section><section className="handoff-list"><div className="section-title"><div><p className="eyebrow">Package ledger</p><h2>Campaigns with retained evidence</h2></div><span>{staged.length}</span></div>{staged.length ? staged.map(email => <a href="/workspace" key={email.key}><FileArchive className="h-4 w-4" /><code>{email.key}</code><div><strong>{email.name.split("·")[1]?.trim() || email.name}</strong><small>Release stage: {email.releaseStage.replaceAll("_", " ")}</small></div><span>Open workspace</span></a>) : <div className="empty-state"><FileArchive className="h-6 w-6" /><h2>No review packages yet.</h2><p>Save a revision, run QA, then prepare an immutable package from the campaign workspace.</p><a href="/workspace">Open workspace</a></div>}</section></div>;
}
