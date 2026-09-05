import { AccessGate } from "@/components/AccessGate";
import { trpc } from "@/lib/trpc";
import { useAuth } from "@/_core/hooks/useAuth";
import { startLogin } from "@/const";
import { BookOpen, Loader2 } from "lucide-react";

function date(value: Date | string | null) { return value ? new Date(value).toLocaleString(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }) : "No timestamp"; }

export default function AuditLedger() {
  const { isAuthenticated, loading } = useAuth();
  const audit = trpc.campaigns.audit.useQuery(undefined, { enabled: isAuthenticated });
  if (loading) return <div className="page-loader"><Loader2 className="h-5 w-5 animate-spin" />Checking access…</div>;
  if (!isAuthenticated) return <AccessGate onSignIn={() => startLogin()} />;
  if (audit.isLoading) return <div className="page-loader"><Loader2 className="h-5 w-5 animate-spin" />Loading audit ledger…</div>;
  return <div className="ops-page"><header className="page-heading"><p className="eyebrow">Evidence trail</p><h1>Audit ledger.</h1><p>Every retained action is recorded; this system does not execute marketing actions.</p></header><section className="ledger"><div className="section-title"><div><p className="eyebrow">Operator evidence</p><h2>Recent recorded events</h2></div><BookOpen className="h-5 w-5" /></div>{audit.data?.length ? audit.data.map(event => <div className="ledger-row" key={event.id}><span className="audit-marker" /><div><strong>{event.eventType.replaceAll("_", " ")}</strong><p>{event.emailKey || "Campaign OS"}</p></div><time>{date(event.createdAt)}</time></div>) : <div className="empty-state"><BookOpen className="h-6 w-6" /><h2>No recorded activity.</h2><p>The ledger will begin when an operator saves a revision, runs QA, prepares a package, or records a Shopify draft read-back.</p></div>}</section></div>;
}
