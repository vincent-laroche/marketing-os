import React from "react";
import { Link2, PackageCheck } from "lucide-react";
import { Button } from "@/components/ui/button";

export function PreparePackageControl({ isAuthenticated, hasRenderedHtml, pending, onPrepare }: { isAuthenticated: boolean; hasRenderedHtml: boolean; pending: boolean; onPrepare: () => void }) {
  return <Button className="w-full" disabled={!isAuthenticated || !hasRenderedHtml || pending} onClick={onPrepare}><PackageCheck className="mr-2 h-4 w-4" />Prepare review package</Button>;
}

export function DraftEvidenceControl({ isAuthenticated, draftUrl, evidenceNote, pending, onRecord }: { isAuthenticated: boolean; draftUrl: string; evidenceNote: string; pending: boolean; onRecord: () => void }) {
  return <Button variant="outline" disabled={!isAuthenticated || !draftUrl || evidenceNote.length < 8 || pending} onClick={onRecord}><Link2 className="mr-2 h-4 w-4" />Record draft evidence</Button>;
}

export function ScreenshotPrerequisite({ hasExportPackage }: { hasExportPackage: boolean }) {
  return hasExportPackage ? null : <p className="empty-note">Responsive screenshot evidence unlocks only after an immutable review package is prepared.</p>;
}

export function ScreenshotUploadGate({ hasExportPackage, children }: { hasExportPackage: boolean; children: React.ReactNode }) {
  return hasExportPackage ? <>{children}</> : <ScreenshotPrerequisite hasExportPackage={false} />;
}
