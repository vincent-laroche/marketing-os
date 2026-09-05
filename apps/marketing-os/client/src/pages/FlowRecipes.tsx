import React from "react";
import { AccessGate } from "@/components/AccessGate";
import { trpc } from "@/lib/trpc";
import { useAuth } from "@/_core/hooks/useAuth";
import { startLogin } from "@/const";
import { Loader2, Network, ShieldCheck } from "lucide-react";

export default function FlowRecipes() {
  const { isAuthenticated, loading } = useAuth();
  const recipes = trpc.campaigns.flow.recipes.useQuery(undefined, { enabled: isAuthenticated });
  if (loading) return <div className="page-loader"><Loader2 className="h-5 w-5 animate-spin" />Checking access…</div>;
  if (!isAuthenticated) return <AccessGate onSignIn={() => startLogin()} />;
  if (recipes.isLoading) return <div className="page-loader"><Loader2 className="h-5 w-5 animate-spin" />Loading Flow recipes…</div>;
  return <div className="ops-page"><header className="page-heading"><p className="eyebrow">Lifecycle control</p><h1>Flow recipes, versioned and deliberate.</h1><p>These are implementation records for manual Shopify configuration, not executable automations.</p></header><section className="recipe-grid">{recipes.data?.map(recipe => <article key={recipe.journey} className="recipe-card"><div className="recipe-card-head"><Network className="h-5 w-5" /><span>{recipe.target}</span></div><h2>{recipe.journey}</h2><p>{recipe.rule}</p><div className="recipe-rules"><p><ShieldCheck className="h-4 w-4" /><span><strong>Collision</strong>{recipe.collisionRule}</span></p><p><ShieldCheck className="h-4 w-4" /><span><strong>Exit</strong>{recipe.exitRule}</span></p><p><ShieldCheck className="h-4 w-4" /><span><strong>Frequency</strong>{recipe.frequencyRule}</span></p></div><details><summary>View manual setup sequence</summary><ol>{recipe.steps.map(step => <li key={step}>{step}</li>)}</ol></details><small>Recipe version {recipe.version}</small></article>)}</section></div>;
}
