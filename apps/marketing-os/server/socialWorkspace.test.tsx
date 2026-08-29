// @vitest-environment jsdom
import React from "react";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import SocialWorkspace, { type SocialSurface } from "../client/src/pages/SocialWorkspace";

vi.mock("../client/src/_core/hooks/useAuth", () => ({
  useAuth: () => ({ isAuthenticated: true, loading: false }),
}));

vi.mock("../client/src/const", () => ({ startLogin: vi.fn() }));

const surfaces: Array<[SocialSurface, RegExp]> = [
  ["overview", /social overview/i],
  ["campaigns", /social campaigns/i],
  ["concepts", /content concepts/i],
  ["calendar", /publication calendar/i],
  ["studio", /content studio/i],
  ["review", /review and gates/i],
  ["assets", /assets and rights/i],
  ["distribution", /distribution status/i],
];

function renderAtWidth(width: number, surface: SocialSurface) {
  Object.defineProperty(window, "innerWidth", { configurable: true, value: width });
  window.dispatchEvent(new Event("resize"));
  return render(<SocialWorkspace surface={surface} />);
}

afterEach(() => cleanup());

describe("Social Media OS Phase 1 surfaces", () => {
  it.each([1280, 375])("renders every social route at %ipx as source-backed fixture evidence", (width) => {
    for (const [surface, heading] of surfaces) {
      cleanup();
      renderAtWidth(width, surface);
      expect(screen.getByRole("heading", { name: heading })).toBeTruthy();
      expect(screen.getByText(/fixture source/i)).toBeTruthy();
      expect(screen.getAllByText(/read-only/i).length).toBeGreaterThan(0);
      expect(screen.queryByRole("button", { name: /publish|schedule|activate|send/i })).toBeNull();
    }
  });

  it("preserves the imported provenance fingerprint, fixture status, and blocked operation state", () => {
    renderAtWidth(1280, "overview");
    expect(screen.getByText(/Social Media OS Phase 1/i)).toBeTruthy();
    expect(screen.getByText(/SHA-256/i)).toBeTruthy();
    expect(screen.getByText(/no operation is authorized/i)).toBeTruthy();
    expect(screen.getByText(/Phase 1 fixture campaign/i)).toBeTruthy();
  });
});
