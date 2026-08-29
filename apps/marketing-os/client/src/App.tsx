import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import MarketingLayout from "./components/MarketingLayout";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";
import EmailOverview from "./pages/EmailOverview";
import EmailReview from "./pages/EmailReview";
import EmailSurface from "./pages/EmailSurface";
import GovernanceSurface from "./pages/GovernanceSurface";
import ReadOnlySurface from "./pages/ReadOnlySurface";
import SocialWorkspace from "./pages/SocialWorkspace";
import Readiness from "./pages/Readiness";
import FlowRecipes from "./pages/FlowRecipes";
import HandoffPackages from "./pages/HandoffPackages";
import AuditLedger from "./pages/AuditLedger";
import Workspace from "./pages/Workspace";
import SyncHealth from "./pages/SyncHealth";

function Router() {
  // make sure to consider if you need authentication for certain routes
  return (
    <Switch>
      <Route path={"/"}>{() => <MarketingLayout><Home /></MarketingLayout>}</Route>
      <Route path={"/initiatives"}>{() => <MarketingLayout><ReadOnlySurface kind="initiatives" /></MarketingLayout>}</Route>
      <Route path={"/calendar"}>{() => <MarketingLayout><ReadOnlySurface kind="calendar" /></MarketingLayout>}</Route>
      <Route path={"/decisions"}>{() => <MarketingLayout><GovernanceSurface kind="decisions" /></MarketingLayout>}</Route>
      <Route path={"/assets"}>{() => <MarketingLayout><GovernanceSurface kind="assets" /></MarketingLayout>}</Route>
      <Route path={"/insights"}>{() => <MarketingLayout><GovernanceSurface kind="insights" /></MarketingLayout>}</Route>
      <Route path={"/sync"}>{() => <MarketingLayout><SyncHealth /></MarketingLayout>}</Route>
      <Route path={"/social"}>{() => <MarketingLayout><SocialWorkspace /></MarketingLayout>}</Route>
      <Route path={"/social/campaigns"}>{() => <MarketingLayout><SocialWorkspace surface="campaigns" /></MarketingLayout>}</Route>
      <Route path={"/social/concepts"}>{() => <MarketingLayout><SocialWorkspace surface="concepts" /></MarketingLayout>}</Route>
      <Route path={"/social/calendar"}>{() => <MarketingLayout><SocialWorkspace surface="calendar" /></MarketingLayout>}</Route>
      <Route path={"/social/studio"}>{() => <MarketingLayout><SocialWorkspace surface="studio" /></MarketingLayout>}</Route>
      <Route path={"/social/review"}>{() => <MarketingLayout><SocialWorkspace surface="review" /></MarketingLayout>}</Route>
      <Route path={"/social/assets"}>{() => <MarketingLayout><SocialWorkspace surface="assets" /></MarketingLayout>}</Route>
      <Route path={"/social/distribution"}>{() => <MarketingLayout><SocialWorkspace surface="distribution" /></MarketingLayout>}</Route>
      <Route path={"/email"}>{() => <MarketingLayout><EmailOverview /></MarketingLayout>}</Route>
      <Route path={"/email/review"}>{() => <MarketingLayout><EmailReview /></MarketingLayout>}</Route>
      <Route path={"/email/campaigns"}>{() => <MarketingLayout><EmailSurface surface="campaigns" /></MarketingLayout>}</Route>
      <Route path={"/email/library"}>{() => <MarketingLayout><EmailSurface surface="library" /></MarketingLayout>}</Route>
      <Route path={"/email/production"}>{() => <MarketingLayout><EmailSurface surface="production" /></MarketingLayout>}</Route>
      <Route path={"/email/previews"}>{() => <MarketingLayout><EmailSurface surface="previews" /></MarketingLayout>}</Route>
      <Route path={"/email/flow"}>{() => <MarketingLayout><FlowRecipes /></MarketingLayout>}</Route>
      <Route path={"/email/audience"}>{() => <MarketingLayout><EmailSurface surface="audience" /></MarketingLayout>}</Route>
      <Route path={"/email/performance"}>{() => <MarketingLayout><ReadOnlySurface kind="performance" /></MarketingLayout>}</Route>
      <Route path={"/readiness"}>{() => <MarketingLayout><Readiness /></MarketingLayout>}</Route>
      <Route path={"/flows"}>{() => <MarketingLayout><FlowRecipes /></MarketingLayout>}</Route>
      <Route path={"/handoff"}>{() => <MarketingLayout><HandoffPackages /></MarketingLayout>}</Route>
      <Route path={"/audit"}>{() => <MarketingLayout><AuditLedger /></MarketingLayout>}</Route>
      <Route path={"/workspace"}>{() => <MarketingLayout><Workspace /></MarketingLayout>}</Route>
      <Route path={"/404"} component={NotFound} />
      {/* Final fallback route */}
      <Route component={NotFound} />
    </Switch>
  );
}

// NOTE: About Theme
// - First choose a default theme according to your design style (dark or light bg), than change color palette in index.css
//   to keep consistent foreground/background color across components
// - If you want to make theme switchable, pass `switchable` ThemeProvider and use `useTheme` hook

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="light">
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
