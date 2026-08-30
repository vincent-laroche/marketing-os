// @vitest-environment jsdom
import React from "react";
import "@testing-library/jest-dom/vitest";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("../client/src/_core/hooks/useAuth", () => ({
  useAuth: () => ({ user: { name: "Vincent" }, loading: false, isAuthenticated: true, logout: vi.fn() }),
}));

vi.mock("../client/src/lib/trpc", () => ({
  trpc: {
    marketingSync: {
      health: {
        useQuery: () => ({
          data: { configured: true, latestRun: { status: "completed", recordCount: 192, blockedCount: 0, completedAt: "2026-08-27T02:58:46.000Z" } },
          isLoading: false,
          isError: false,
        }),
      },
      run: { useMutation: () => ({ mutate: vi.fn(), isPending: false, isError: false, data: null }) },
    },
    campaigns: {
      portfolio: {
        useQuery: () => ({
          data: [
            { key: "CR-1", name: "CR-1 · Your Cart's Still Here", series: "J2 · Cart recovery", sourceStatus: "ready", shopifySurface: "Shopify Messaging", subject: "Your cart is still here", latestRevision: { id: 1 }, latestHandoff: null, releaseStage: "in_review" },
            { key: "RO-4", name: "RO-4 · Same Spec or Change", series: "J4 · Reorder", sourceStatus: "blocked", shopifySurface: "Shopify Flow", subject: null, latestRevision: null, latestHandoff: null, releaseStage: "blocked" },
            { key: "NL-01", name: "NL-01 · Education", series: "N · Newsletter programme", sourceStatus: "ready", shopifySurface: "Shopify Messaging", subject: "Education", latestRevision: null, latestHandoff: null, releaseStage: "in_review" },
          ],
          isLoading: false,
          isError: false,
        }),
      },
      flow: {
        recipes: {
          useQuery: () => ({
            data: [{ journey: "J2 · Cart Recovery", target: "Shopify Flow", rule: "Manual-only journey configuration", collisionRule: "Exclude overlapping journeys", exitRule: "Exit after purchase", frequencyRule: "Respect frequency cap", steps: ["Review source", "Configure manually"], version: "1" }],
            isLoading: false,
          }),
        },
      },
    },
  },
}));

import GovernanceSurface from "../client/src/pages/GovernanceSurface";
import EmailSurface from "../client/src/pages/EmailSurface";
import ReadOnlySurface from "../client/src/pages/ReadOnlySurface";
import Home from "../client/src/pages/Home";
import EmailOverview from "../client/src/pages/EmailOverview";
import EmailReview from "../client/src/pages/EmailReview";
import FlowRecipes from "../client/src/pages/FlowRecipes";
import SyncHealth from "../client/src/pages/SyncHealth";

afterEach(cleanup);

function renderAtWidth(width: number, node: React.ReactElement) {
  Object.defineProperty(window, "innerWidth", { configurable: true, value: width });
  window.dispatchEvent(new Event("resize"));
  return render(node);
}

describe("authenticated Marketing OS route surfaces", () => {
  it("renders every shared route surface with authenticated evidence language at desktop width", () => {
    renderAtWidth(1440, <GovernanceSurface kind="decisions" />);
    expect(screen.getByRole("heading", { name: /approvals & decisions/i })).toBeVisible();
    expect(screen.getByText(/owner decision inbox/i)).toBeVisible();
    cleanup();

    renderAtWidth(1440, <GovernanceSurface kind="assets" />);
    expect(screen.getByRole("heading", { name: /assets, claims & rights/i })).toBeVisible();
    expect(screen.getByText(/no governed email asset records/i)).toBeVisible();
    cleanup();

    renderAtWidth(1440, <GovernanceSurface kind="insights" />);
    expect(screen.getByRole("heading", { name: /insights & learnings/i })).toBeVisible();
    expect(screen.getAllByText(/evidence maturity/i)[0]).toBeVisible();
    cleanup();

    renderAtWidth(1440, <ReadOnlySurface kind="initiatives" />);
    expect(screen.getByRole("heading", { name: /initiatives/i })).toBeVisible();
    cleanup();
    renderAtWidth(1440, <ReadOnlySurface kind="calendar" />);
    expect(screen.getByRole("heading", { name: /master calendar/i })).toBeVisible();
    cleanup();
    renderAtWidth(1440, <ReadOnlySurface kind="social" />);
    expect(screen.getByRole("heading", { name: /social workspace boundary/i })).toBeVisible();
    cleanup();
    renderAtWidth(1440, <SyncHealth />);
    expect(screen.getByRole("heading", { name: /sync health/i })).toBeVisible();
    expect(screen.getByText(/aggregate only — no content shown/i)).toBeVisible();
  });

  it("renders every Email route surface with canonical evidence at desktop width", () => {
    renderAtWidth(1440, <EmailSurface surface="campaigns" />);
    expect(screen.getByRole("heading", { name: /campaigns & journeys/i })).toBeVisible();
    expect(screen.getByText(/journey portfolio/i)).toBeVisible();
    cleanup();
    renderAtWidth(1440, <EmailSurface surface="library" />);
    expect(screen.getByRole("heading", { name: /email library/i })).toBeVisible();
    expect(screen.getByText(/canonical email inventory/i)).toBeVisible();
    cleanup();
    renderAtWidth(1440, <EmailSurface surface="production" />);
    expect(screen.getByRole("heading", { name: /production queue/i })).toBeVisible();
    cleanup();
    renderAtWidth(1440, <EmailSurface surface="previews" />);
    expect(screen.getByRole("heading", { name: /preview gallery/i })).toBeVisible();
    cleanup();
    renderAtWidth(1440, <EmailSurface surface="audience" />);
    expect(screen.getByRole("heading", { name: /audience & consent/i })).toBeVisible();
    cleanup();
    renderAtWidth(1440, <ReadOnlySurface kind="performance" />);
    expect(screen.getByRole("heading", { name: /performance/i })).toBeVisible();
  });

  it("retains the shared and Email evidence surfaces at mobile width without rendering execution controls", () => {
    renderAtWidth(375, <GovernanceSurface kind="decisions" />);
    expect(screen.getByText(/owner decision inbox/i)).toBeVisible();
    expect(screen.queryByRole("button", { name: /send|schedule|activate|publish/i })).not.toBeInTheDocument();
    cleanup();
    renderAtWidth(375, <GovernanceSurface kind="assets" />);
    expect(screen.getByText(/visual availability is not permitted use/i)).toBeVisible();
    cleanup();
    renderAtWidth(375, <GovernanceSurface kind="insights" />);
    expect(screen.getByText(/measurement boundary/i)).toBeVisible();
    cleanup();
    renderAtWidth(375, <EmailSurface surface="campaigns" />);
    expect(screen.getByText(/activation locked/i)).toBeVisible();
    cleanup();
    renderAtWidth(375, <EmailSurface surface="library" />);
    expect(screen.getByText(/library rule/i)).toBeVisible();
    cleanup();
    renderAtWidth(375, <ReadOnlySurface kind="initiatives" />);
    expect(screen.getByRole("heading", { name: /initiatives/i })).toBeVisible();
    cleanup();
    renderAtWidth(375, <ReadOnlySurface kind="calendar" />);
    expect(screen.getByRole("heading", { name: /master calendar/i })).toBeVisible();
    cleanup();
    renderAtWidth(375, <ReadOnlySurface kind="social" />);
    expect(screen.getByRole("heading", { name: /social workspace boundary/i })).toBeVisible();
    cleanup();
    renderAtWidth(375, <SyncHealth />);
    expect(screen.getByRole("heading", { name: /sync health/i })).toBeVisible();
    expect(screen.queryByRole("button", { name: /send|schedule|activate|publish|mutate audience/i })).not.toBeInTheDocument();
    cleanup();
    renderAtWidth(375, <EmailSurface surface="production" />);
    expect(screen.getByRole("heading", { name: /production queue/i })).toBeVisible();
    cleanup();
    renderAtWidth(375, <EmailSurface surface="previews" />);
    expect(screen.getByRole("heading", { name: /preview gallery/i })).toBeVisible();
    cleanup();
    renderAtWidth(375, <EmailSurface surface="audience" />);
    expect(screen.getByRole("heading", { name: /audience & consent/i })).toBeVisible();
    cleanup();
    renderAtWidth(375, <ReadOnlySurface kind="performance" />);
    expect(screen.getByRole("heading", { name: /performance/i })).toBeVisible();
  });

  it("renders the previously uncovered Command Center and Email routes with authenticated text at desktop and mobile widths", () => {
    renderAtWidth(1440, <Home />);
    expect(screen.getByRole("heading", { name: /^marketing os$/i })).toBeVisible();
    expect(screen.getByText(/needs vincent/i)).toBeVisible();
    cleanup();
    renderAtWidth(1440, <EmailOverview />);
    expect(screen.getByRole("heading", { name: /^email os$/i })).toBeVisible();
    expect(screen.getByText(/production pulse/i)).toBeVisible();
    cleanup();
    renderAtWidth(1440, <EmailReview />);
    expect(screen.getByRole("heading", { name: /review & qa/i })).toBeVisible();
    expect(screen.getByText(/deterministic qa only/i)).toBeVisible();
    cleanup();
    renderAtWidth(1440, <FlowRecipes />);
    expect(screen.getByRole("heading", { name: /flow recipes, versioned and deliberate/i })).toBeVisible();
    expect(screen.getByText(/manual-only journey configuration/i)).toBeVisible();
    cleanup();
    renderAtWidth(375, <Home />);
    expect(screen.getByText(/open owner decisions/i)).toBeVisible();
    cleanup();
    renderAtWidth(375, <EmailOverview />);
    expect(screen.getByText(/release gate/i)).toBeVisible();
    cleanup();
    renderAtWidth(375, <EmailReview />);
    expect(screen.getByText(/no draft, schedule, or sending action/i)).toBeVisible();
    cleanup();
    renderAtWidth(375, <FlowRecipes />);
    expect(screen.getByText(/view manual setup sequence/i)).toBeVisible();
  });
});
