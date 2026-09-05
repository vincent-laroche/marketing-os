import { AccessGate } from "@/components/AccessGate";
import { ReleaseGate } from "@/components/ReleaseGate";
import { trpc } from "@/lib/trpc";
import { useAuth } from "@/_core/hooks/useAuth";
import { startLogin } from "@/const";
import { AlertTriangle, CheckCircle2, Loader2 } from "lucide-react";

export default function Readiness() {
  const { isAuthenticated, loading } = useAuth();
  const portfolio = trpc.campaigns.portfolio.useQuery(undefined, { enabled: isAuthenticated });
  const notify = trpc.campaigns.alerts.notifySourceBlockers.useMutation();
  if (loading) return <div className="page-loader"><Loader2 className="h-5 w-5 animate-spin" />Checking access…</div>;
  if (!isAuthenticated) return <AccessGate onSignIn={() => startLogin()} />;
  if (portfolio.isLoading) return <div className="page-loader"><Loader2 className="h-5 w-5 animate-spin" />Loading readiness…</div>;
  const emails = portfolio.data ?? [];
  const ready = emails.filter(email => email.sourceStatus === "ready");
  const blocked = emails.filter(email => email.sourceStatus !== "ready");
  return <div className="ops-page"><header className="page-heading"><p className="eyebrow">Release control</p><h1>Readiness, without false green lights.</h1><p>Creative, QA, Shopify draft verification, and activation evidence remain distinct stages.</p></header><ReleaseGate isAuthenticated={isAuthenticated} alertPending={notify.isPending} onAlert={() => notify.mutate()} /><section className="readiness-summary"><article><CheckCircle2 className="h-5 w-5" /><strong>{ready.length}</strong><span>source-ready records</span></article><article><AlertTriangle className="h-5 w-5" /><strong>{blocked.length}</strong><span>records requiring input</span></article><article><strong>{emails.filter(email => email.releaseStage === "shopify_draft_verified").length}</strong><span>Shopify drafts read back</span></article></section><section className="split-ledger"><article><div className="section-title"><div><p className="eyebrow">Reviewable now</p><h2>Source ready</h2></div><span>{ready.length}</span></div><div className="record-list">{ready.map(email => <a href="/workspace" key={email.key}><code>{email.key}</code><div><strong>{email.name.split("·")[1]?.trim() || email.name}</strong><small>{email.shopifySurface} · {email.series}</small></div><span>Review</span></a>)}</div></article><article><div className="section-title"><div><p className="eyebrow">Fail closed</p><h2>Blocked or incomplete</h2></div><span>{blocked.length}</span></div><div className="record-list">{blocked.map(email => <a href="/workspace" key={email.key}><code>{email.key}</code><div><strong>{email.name.split("·")[1]?.trim() || email.name}</strong><small>{email.blockers?.[0] || email.dependencies?.[0] || "Source dependency remains"}</small></div><span className="danger-text">Blocked</span></a>)}</div></article></section></div>;
}
