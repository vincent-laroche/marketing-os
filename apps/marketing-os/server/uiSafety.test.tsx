// @vitest-environment jsdom
import React from "react";
import "@testing-library/jest-dom/vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ReleaseGate } from "../client/src/components/ReleaseGate";

afterEach(cleanup);

describe("visible release safety controls", () => {
  it("shows a fail-closed consent warning and prevents unauthenticated alert actions", () => {
    render(<ReleaseGate isAuthenticated={false} alertPending={false} onAlert={vi.fn()} />);
    expect(screen.getByText(/consent evidence remains segmented/i)).toBeVisible();
    expect(screen.getByText(/fail closed/i)).toBeVisible();
    expect(screen.getByRole("button", { name: /alert owner/i })).toBeDisabled();
  });

  it("allows an authenticated owner to invoke only the non-sending alert control", () => {
    const onAlert = vi.fn();
    render(<ReleaseGate isAuthenticated={true} alertPending={false} onAlert={onAlert} />);
    fireEvent.click(screen.getByRole("button", { name: /alert owner/i }));
    expect(onAlert).toHaveBeenCalledTimes(1);
    expect(screen.queryByRole("button", { name: /send|schedule|activate/i })).not.toBeInTheDocument();
  });
});
