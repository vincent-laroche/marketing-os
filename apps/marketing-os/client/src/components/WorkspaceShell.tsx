import React from "react";
import { AccessGate } from "./AccessGate";

export function WorkspaceShell({ isAuthenticated, onSignIn, children }: { isAuthenticated: boolean; onSignIn: () => void; children: React.ReactNode }) {
  return isAuthenticated ? <>{children}</> : <AccessGate onSignIn={onSignIn} />;
}
