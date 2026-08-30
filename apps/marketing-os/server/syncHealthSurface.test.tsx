// @vitest-environment jsdom
import React from "react";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import SyncHealth from "../client/src/pages/SyncHealth";

const authState = { isAuthenticated: true, loading: false, user: { role: "admin" } };
const mutate = vi.fn();

vi.mock("../client/src/_core/hooks/useAuth", () => ({ useAuth: () => authState }));
vi.mock("../client/src/const", () => ({ startLogin: vi.fn() }));
vi.mock("../client/src/lib/trpc", () => ({
  trpc: {
    marketingSync: {
      health: { useQuery: () => ({ isLoading: false, isError: false, data: { configured: true, latestRun: { status: "completed", recordCount: 53, blockedCount: 0, completedAt: "2026-08-27T01:00:00.000Z" } }, refetch: vi.fn() }) },
      run: { useMutation: () => ({ mutate, isPending: false, isError: false, data: null }) },
    },
  },
}));

afterEach(() => { cleanup(); mutate.mockClear(); authState.user.role = "admin"; authState.isAuthenticated = true; });

describe("Marketing OS Sync Health", () => {
  it("shows aggregate synchronization evidence and the owner-only reconciliation control", () => {
    render(<SyncHealth />);
    expect(screen.getByRole("heading", { name: /sync health/i })).toBeTruthy();
    expect(screen.getByText(/aggregate only — no content shown/i)).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: /run reconciliation/i }));
    expect(mutate).toHaveBeenCalledTimes(1);
  });

  it("does not surface marketing operation controls", () => {
    render(<SyncHealth />);
    expect(screen.getByText(/operations disabled/i)).toBeTruthy();
    expect(screen.queryByRole("button", { name: /send|schedule|publish|activate|mutate audience/i })).toBeNull();
    expect(screen.getByText(/Shopify consent remains Shopify-authoritative/i)).toBeTruthy();
  });

  it("keeps aggregate health readable but hides manual reconciliation from non-admin users", () => {
    authState.user.role = "user";
    render(<SyncHealth />);
    expect(screen.getByRole("heading", { name: /sync health/i })).toBeTruthy();
    expect(screen.queryByRole("button", { name: /run reconciliation/i })).toBeNull();
    expect(screen.getByText(/only the marketing os owner may request a reconciliation/i)).toBeTruthy();
  });

  it("keeps synchronization evidence behind the sign-in gate for unauthenticated visitors", () => {
    authState.isAuthenticated = false;
    render(<SyncHealth />);
    expect(screen.getByRole("heading", { name: /campaign evidence requires a signed-in operator/i })).toBeTruthy();
    expect(screen.queryByRole("heading", { name: /sync health/i })).toBeNull();
    expect(screen.queryByText(/records observed/i)).toBeNull();
  });
});
