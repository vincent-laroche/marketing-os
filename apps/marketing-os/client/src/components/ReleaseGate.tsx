import React from "react";
import { BellRing, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/button";

export function ReleaseGate({ isAuthenticated, alertPending, onAlert }: { isAuthenticated: boolean; alertPending: boolean; onAlert: () => void }) {
  return <section className="consent-gate"><ShieldAlert className="h-5 w-5" /><div><strong>Release gate: consent evidence remains segmented.</strong><p>The broad subscribed audience is intentionally marked unsafe. Only owner-attested, consented cohorts may appear in a future Shopify review package.</p></div><Button size="sm" variant="outline" disabled={!isAuthenticated || alertPending} onClick={onAlert}><BellRing className="mr-2 h-3.5 w-3.5" />Alert owner</Button><span>Fail closed</span></section>;
}
