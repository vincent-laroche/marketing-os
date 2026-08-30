import React from "react";
import { LockKeyhole } from "lucide-react";
import { Button } from "@/components/ui/button";

export function AccessGate({ onSignIn }: { onSignIn: () => void }) {
  return <section className="access-gate"><p className="eyebrow">Restricted marketing operations workspace</p><h1>Campaign evidence requires a signed-in operator.</h1><p>Canonical copy, audience rules, QA evidence, and Shopify draft records are protected. Sign in to review the 53-email portfolio and use the controlled handoff workflow.</p><Button onClick={onSignIn}><LockKeyhole className="mr-2 h-4 w-4" />Sign in to Campaign OS</Button><span>Campaign OS does not send, schedule, activate, or change audiences.</span></section>;
}
