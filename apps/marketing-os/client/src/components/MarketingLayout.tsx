import { startLogin } from "@/const";
import { useAuth } from "@/_core/hooks/useAuth";
import { Activity, BarChart3, CalendarDays, CheckCircle2, ChevronRight, Clapperboard, Command, FileCheck2, FolderOpen, LayoutDashboard, Layers3, ListChecks, Mail, PanelLeft, Radio, Search, ShieldCheck, Workflow } from "lucide-react";
import React from "react";
import { useState } from "react";
import { Link, useLocation } from "wouter";

type NavigationItem = { label: string; href: string; icon: typeof Command };

const sharedItems: NavigationItem[] = [
  { label: "Command Center", href: "/", icon: Command },
  { label: "Initiatives", href: "/initiatives", icon: Layers3 },
  { label: "Master Calendar", href: "/calendar", icon: CalendarDays },
  { label: "Approvals & Decisions", href: "/decisions", icon: CheckCircle2 },
  { label: "Assets, Claims & Rights", href: "/assets", icon: FolderOpen },
  { label: "Insights & Learnings", href: "/insights", icon: BarChart3 },
  { label: "Sync Health", href: "/sync", icon: Activity },
];

const emailItems: NavigationItem[] = [
  { label: "Overview", href: "/email", icon: LayoutDashboard },
  { label: "Campaigns & Journeys", href: "/email/campaigns", icon: Layers3 },
  { label: "Email Library", href: "/email/library", icon: Mail },
  { label: "Production Queue", href: "/email/production", icon: ListChecks },
  { label: "Review & QA", href: "/email/review", icon: FileCheck2 },
  { label: "Preview Gallery", href: "/email/previews", icon: LayoutDashboard },
  { label: "Messaging & Flow", href: "/email/flow", icon: Workflow },
  { label: "Audience & Consent", href: "/email/audience", icon: ShieldCheck },
  { label: "Performance", href: "/email/performance", icon: BarChart3 },
];

const socialItems: NavigationItem[] = [
  { label: "Overview", href: "/social", icon: LayoutDashboard },
  { label: "Campaigns", href: "/social/campaigns", icon: Layers3 },
  { label: "Content Concepts", href: "/social/concepts", icon: Clapperboard },
  { label: "Publication Calendar", href: "/social/calendar", icon: CalendarDays },
  { label: "Content Studio", href: "/social/studio", icon: FileCheck2 },
  { label: "Review & Gates", href: "/social/review", icon: CheckCircle2 },
  { label: "Assets & Rights", href: "/social/assets", icon: FolderOpen },
  { label: "Distribution Status", href: "/social/distribution", icon: Radio },
];

function activePath(location: string, href: string) {
  if (href === "/" || href === "/email" || href === "/social") return location === href;
  return location === href || location.startsWith(`${href}/`);
}

function SectionNav({ label, items, location, compact }: { label: string; items: NavigationItem[]; location: string; compact: boolean }) {
  return <section className="marketing-nav-section"><p>{label}</p>{items.map(item => {
    const Icon = item.icon;
    return <Link key={item.href} href={item.href} className={activePath(location, item.href) ? "marketing-nav-item active" : "marketing-nav-item"} title={item.label} aria-label={item.label}><Icon className="h-4 w-4" />{!compact && <span>{item.label}</span>}</Link>;
  })}</section>;
}

export default function MarketingLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const [compact, setCompact] = useState(false);
  const [location] = useLocation();
  const emailContext = location.startsWith("/email");
  const socialContext = location.startsWith("/social");
  const current = (emailContext ? emailItems : socialContext ? socialItems : sharedItems).find(item => activePath(location, item.href));
  const domainLabel = emailContext ? "Email OS" : socialContext ? "Social Media OS" : "Marketing OS";

  return <div className={`marketing-shell ${compact ? "marketing-shell-compact" : ""}`}>
    <aside className="marketing-sidebar">
        <div className="marketing-brand">
        <button className="marketing-mark" onClick={() => setCompact(value => !value)} aria-label="Toggle navigation"><PanelLeft className="h-4 w-4" /></button>
        {!compact && <div><strong>Marketing OS</strong><small>Hair Solutions Co.</small></div>}
      </div>
        <nav aria-label="Marketing OS navigation">
          <SectionNav label="Shared control plane" items={sharedItems} location={location} compact={compact} />
          {emailContext && <SectionNav label="Email OS" items={emailItems} location={location} compact={compact} />}
          {socialContext && <SectionNav label="Social Media OS" items={socialItems} location={location} compact={compact} />}
      </nav>
      <div className="marketing-sidebar-footer">
        <Link href="/email" className={emailContext ? "domain-switch active" : "domain-switch"}><Mail className="h-4 w-4" />{!compact && <span><strong>Email OS</strong><small>53 canonical emails · 7 journeys</small></span>}</Link>
        <Link href="/social" className={socialContext ? "domain-switch social active" : "domain-switch social"}><Layers3 className="h-4 w-4" />{!compact && <span><strong>Social Media OS</strong><small>Phase 1 fixture read model</small></span>}</Link>
        {!compact && <div className="read-only-note"><ShieldCheck className="h-3.5 w-3.5" /><span>Read-only control plane</span></div>}
      </div>
    </aside>
    <div className="marketing-workspace">
      <header className="marketing-topbar">
        <div className="breadcrumbs"><span>Hair Solutions Co.</span><ChevronRight className="h-3 w-3" /><span>{domainLabel}</span><ChevronRight className="h-3 w-3" /><strong>{current?.label ?? "Command Center"}</strong></div>
        <div className="topbar-actions"><label className="global-search"><Search className="h-3.5 w-3.5" /><input disabled aria-label="Search source-backed records" placeholder="Search records after compiled read models are connected" /><kbd>⌘ K</kbd></label><span className="source-health"><i />Source health</span><span className="readonly-pill">Read-only</span>{isAuthenticated ? <button className="account-button" onClick={logout} title="Sign out">{user?.name?.slice(0, 1).toUpperCase() || "V"}</button> : loading ? <span className="account-button muted">…</span> : <button className="account-button" onClick={() => startLogin()} title="Sign in">↗</button>}</div>
      </header>
      <main className="marketing-main">{children}</main>
    </div>
  </div>;
}
