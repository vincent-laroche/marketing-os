import { createBeefreeSession, type BeefreeSession } from "./beefree";

export type EditorProviderId = "beefree" | "topol" | "unlayer";

export type EditorProviderSession = {
  provider: EditorProviderId;
  configured: boolean;
  accessToken?: string;
  message: string;
};

export interface EditorProviderAdapter {
  id: EditorProviderId;
  displayName: string;
  createSession(uid: string): Promise<EditorProviderSession>;
}

const beefreeAdapter: EditorProviderAdapter = {
  id: "beefree",
  displayName: "Beefree",
  async createSession(uid) {
    const session: BeefreeSession = await createBeefreeSession(uid);
    return { provider: "beefree", ...session };
  },
};

const adapters: Record<EditorProviderId, EditorProviderAdapter | null> = {
  beefree: beefreeAdapter,
  topol: null,
  unlayer: null,
};

export function getEditorProvider(provider: EditorProviderId = "beefree") {
  const adapter = adapters[provider];
  if (!adapter) throw new Error(`${provider} is not configured as an editor provider in this deployment.`);
  return adapter;
}
