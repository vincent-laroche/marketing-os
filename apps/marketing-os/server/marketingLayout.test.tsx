// @vitest-environment jsdom
import React from "react";
import "@testing-library/jest-dom/vitest";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("../client/src/_core/hooks/useAuth", () => ({
  useAuth: () => ({ user: { name: "Vincent" }, loading: false, isAuthenticated: true, logout: vi.fn() }),
}));

import MarketingLayout from "../client/src/components/MarketingLayout";

afterEach(cleanup);

describe("Marketing OS navigation", () => {
  it("keeps the shared control plane and specialist Email boundary visible without execution controls", () => {
    window.history.pushState({}, "", "/");
    render(<MarketingLayout><article>Command center content</article></MarketingLayout>);

    expect(screen.getByRole("navigation", { name: /marketing os navigation/i })).toBeVisible();
    expect(screen.getByRole("link", { name: /command center/i })).toBeVisible();
    expect(screen.getByRole("link", { name: /email os/i })).toBeVisible();
    expect(screen.getByRole("link", { name: /social media os/i })).toBeVisible();
    expect(screen.getByText(/read-only control plane/i)).toBeVisible();
    expect(screen.queryByRole("button", { name: /send|schedule|publish|activate/i })).not.toBeInTheDocument();
  });

  it("keeps an Email child surface active rather than the Email overview root", () => {
    window.history.pushState({}, "", "/email/review");
    render(<MarketingLayout><article>Email review content</article></MarketingLayout>);

    expect(screen.getByText("Email OS", { selector: "p" })).toBeVisible();
    expect(screen.getByRole("link", { name: /review & qa/i })).toBeVisible();
    expect(screen.getByText("Review & QA", { selector: ".breadcrumbs strong" })).toBeVisible();
  });

  it("shows the dedicated Social Media OS navigation and context without surfacing operation controls", () => {
    window.history.pushState({}, "", "/social/review");
    render(<MarketingLayout><article>Social review content</article></MarketingLayout>);

    expect(screen.getByText("Social Media OS", { selector: "p" })).toBeVisible();
    expect(screen.getByRole("link", { name: /review & gates/i })).toBeVisible();
    expect(screen.getByRole("link", { name: /distribution status/i })).toBeVisible();
    expect(screen.getByText("Phase 1 fixture read model")).toBeVisible();
    expect(screen.getByText("Review & Gates", { selector: ".breadcrumbs strong" })).toBeVisible();
    expect(screen.queryByRole("button", { name: /send|schedule|publish|activate/i })).not.toBeInTheDocument();
  });
});
