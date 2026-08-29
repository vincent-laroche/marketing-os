import React from "react";
import { AccessGate } from "@/components/AccessGate";
import { startLogin } from "@/const";
import { useAuth } from "@/_core/hooks/useAuth";
import { FolderLock, Loader2, ShieldCheck } from "lucide-react";

const copy: Record<string, { eyebrow: string; title: string; description: string; note: string }> = {
  initiatives: { eyebrow: "Shared control plane", title: "Initiatives", description: "Cross-channel relationships remain a decision and evidence layer. They do not merge Email OS and Social Media OS production rules.", note: "No source-backed shared initiative has been created yet." },
  calendar: { eyebrow: "Shared control plane", title: "Master calendar", description: "Dates will appear only when canonical records carry approved planning evidence. A blank calendar is safer than invented schedule pressure.", note: "No authorized shared marketing dates are recorded." },
  decisions: { eyebrow: "Shared control plane", title: "Approvals & decisions", description: "Owner decisions are retained as explicit evidence. They never trigger sending, publishing, scheduling, or audience changes.", note: "Consent and release authorization remain separate gates in Email OS." },
  assets: { eyebrow: "Shared control plane", title: "Assets, claims & rights", description: "Asset provenance, claims boundaries, and rights evidence remain source-backed and channel-specific.", note: "The shared read layer has no approved cross-channel asset registry yet." },
  insights: { eyebrow: "Shared control plane", title: "Insights & learnings", description: "Combined learning is shown only after channel-level evidence exists. This interface does not manufacture attribution.", note: "No cross-channel learning evidence is available yet." },
  social: { eyebrow: "Social Media OS", title: "Social workspace boundary", description: "Social Media OS is being implemented in its own source-backed branch. The shared shell reserves this domain without promoting fixture data into production work.", note: "No social publishing, scheduling, or platform action is available from this application." },
  performance: { eyebrow: "Email OS", title: "Performance", description: "Measurement begins only after an approved Shopify send and separately verified data becomes available.", note: "No performance data is available because this application has no marketing execution authority." },
};

export default function ReadOnlySurface({ kind }: { kind: keyof typeof copy }) {
  const { isAuthenticated, loading } = useAuth();
  const page = copy[kind];
  if (loading) return <div className="page-loader"><Loader2 className="h-5 w-5 animate-spin" />Checking Marketing OS access…</div>;
  if (!isAuthenticated) return <AccessGate onSignIn={() => startLogin()} />;
  return <div className="marketing-page empty-surface"><header className="page-heading marketing-heading"><div><p>{page.eyebrow}</p><h1>{page.title}</h1><span>{page.description}</span></div><span className="readonly-pill"><ShieldCheck className="h-3.5 w-3.5" />Read-only</span></header><section><FolderLock className="h-8 w-8" /><h2>Evidence before interface density.</h2><p>{page.note}</p><small>This intentional empty state keeps missing source truth visible rather than filling the surface with simulated marketing work.</small></section></div>;
}
