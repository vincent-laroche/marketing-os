// @vitest-environment jsdom
import React from "react";
import "@testing-library/jest-dom/vitest";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import SocialWorkspace, { type SocialSurface } from "../client/src/pages/SocialWorkspace";

vi.mock("../client/src/_core/hooks/useAuth", () => ({
  useAuth: () => ({ isAuthenticated: false, loading: false }),
}));

vi.mock("../client/src/const", () => ({ startLogin: vi.fn() }));

const surfaces: SocialSurface[] = ["overview", "campaigns", "concepts", "calendar", "studio", "review", "assets", "distribution"];

afterEach(cleanup);

describe("Social Media OS unauthenticated access boundary", () => {
  it.each([1280, 375])("gates every Social surface at %ipx before fixture evidence is rendered", (width) => {
    Object.defineProperty(window, "innerWidth", { configurable: true, value: width });

    for (const surface of surfaces) {
      cleanup();
      render(<SocialWorkspace surface={surface} />);
      expect(screen.getByRole("heading", { name: /campaign evidence requires a signed-in operator/i })).toBeVisible();
      expect(screen.getByRole("button", { name: /sign in to campaign os/i })).toBeVisible();
      expect(screen.queryByText(/Social Media OS Phase 1/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/Phase 1 fixture campaign/i)).not.toBeInTheDocument();
      expect(screen.queryByRole("button", { name: /publish|schedule|activate|send/i })).not.toBeInTheDocument();
    }
  });
});
