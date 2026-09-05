import { startLogin } from "@/const";
import { useAuth } from "@/_core/hooks/useAuth";
import { Activity, BookOpen, ClipboardCheck, FileArchive, LogOut, Network, PanelLeft, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { Link, useLocation } from "wouter";

const menuItems = [
  { icon: Activity, label: "Portfolio", href: "/" },
  { icon: ClipboardCheck, label: "Release readiness", href: "/readiness" },
  { icon: Network, label: "Flow recipes", href: "/flows" },
  { icon: FileArchive, label: "Handoff packages", href: "/handoff" },
  { icon: BookOpen, label: "Audit ledger", href: "/audit" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const [compact, setCompact] = useState(false);
  const [location] = useLocation();

  return (
    <div className={`campaign-shell ${compact ? "campaign-shell-compact" : ""}`}>
      <aside className="campaign-sidebar">
        <div className="sidebar-brand">
          <button onClick={() => setCompact(value => !value)} className="brand-mark" aria-label="Toggle navigation"><PanelLeft className="h-4 w-4" /></button>
          {!compact ? <div><p className="brand-kicker">Hair Solutions Co.</p><p className="brand-title">Campaign OS</p></div> : null}
        </div>
        <nav className="sidebar-nav" aria-label="Campaign OS sections">
          {menuItems.map(item => (
            <Link key={item.href} href={item.href} className={location === item.href ? "nav-item nav-item-active" : "nav-item"} title={item.label} aria-label={item.label}>
              <item.icon className="h-4 w-4" />
              {!compact ? <span>{item.label}</span> : null}
            </Link>
          ))}
        </nav>
        <div className="sidebar-safety">
          <ShieldCheck className="h-4 w-4" />
          {!compact ? <span>No sending authority</span> : null}
        </div>
        <div className="sidebar-account">
          {loading ? <span>Loading workspace…</span> : isAuthenticated ? (
            <><span className="account-dot">{user?.name?.slice(0, 1).toUpperCase() || "V"}</span>{!compact ? <span className="account-name">{user?.name || "Operations"}</span> : null}<button className="account-logout" onClick={logout} aria-label="Sign out"><LogOut className="h-4 w-4" /></button></>
          ) : (
            <button className="signin-link" onClick={() => startLogin()}>{compact ? "↗" : "Sign in for editing"}</button>
          )}
        </div>
      </aside>
      <main className="campaign-main">{children}</main>
    </div>
  );
}
