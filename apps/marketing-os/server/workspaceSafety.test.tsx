// @vitest-environment jsdom
import React from "react";
import "@testing-library/jest-dom/vitest";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AccessGate } from "../client/src/components/AccessGate";
import { DraftEvidenceControl, PreparePackageControl, ScreenshotUploadGate } from "../client/src/components/HandoffSafetyControls";
import { WorkspaceShell } from "../client/src/components/WorkspaceShell";

afterEach(cleanup);

describe("protected workspace and handoff controls", () => {
  it("keeps canonical content behind the deliberate sign-in gate", () => {
    render(<WorkspaceShell isAuthenticated={false} onSignIn={vi.fn()}><article>Canonical campaign detail</article></WorkspaceShell>);
    expect(screen.getByRole("heading", { name: /campaign evidence requires a signed-in operator/i })).toBeVisible();
    expect(screen.getByRole("button", { name: /sign in to campaign os/i })).toBeEnabled();
    expect(screen.getByText(/does not send, schedule, activate/i)).toBeVisible();
    expect(screen.queryByText(/canonical campaign detail/i)).not.toBeInTheDocument();
  });

  it("disables package, evidence, and screenshot steps when safe prerequisites are absent", () => {
    render(<><PreparePackageControl isAuthenticated={false} hasRenderedHtml={false} pending={false} onPrepare={vi.fn()} /><DraftEvidenceControl isAuthenticated={true} draftUrl="" evidenceNote="short" pending={false} onRecord={vi.fn()} /><ScreenshotUploadGate hasExportPackage={false}><input aria-label="Upload screenshot evidence" type="file" /></ScreenshotUploadGate></>);
    expect(screen.getByRole("button", { name: /prepare review package/i })).toBeDisabled();
    expect(screen.getByRole("button", { name: /record draft evidence/i })).toBeDisabled();
    expect(screen.getByText(/screenshot evidence unlocks only after/i)).toBeVisible();
    expect(screen.queryByLabelText(/upload screenshot evidence/i)).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /send|schedule|activate/i })).not.toBeInTheDocument();
  });
});
