import phaseOneModel from "@/data/social/social-read-model.phase1.json";

export type SocialGate = {
  gate: string;
  status: "met" | "blocked";
  evidence: string;
};

export type SocialPublication = {
  recordKey: string;
  platform: "Instagram" | "TikTok" | "Facebook";
  format: string;
  safeArea: string;
  stage: string;
  fixture: boolean;
  plannedDate: string | null;
  readinessGates: SocialGate[];
  verifiedExternalState: { status: string; verified: boolean; evidence: string };
};

export const socialReadModel = phaseOneModel;
export const socialCampaign = phaseOneModel.campaigns[0];
export const socialConcept = phaseOneModel.concepts[0];
export const socialPublications = phaseOneModel.publications as SocialPublication[];

export function humanizeGate(gate: string) {
  return gate === "explicitOperationApproval" ? "explicit operation approval" : gate;
}
