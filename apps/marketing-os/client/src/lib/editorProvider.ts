export type EditorProviderId = "beefree" | "topol" | "unlayer";

export type EditorProviderDescriptor = {
  id: EditorProviderId;
  label: string;
  supportsServerSession: boolean;
  preservesProviderDocument: boolean;
};

export const editorProviders: Record<EditorProviderId, EditorProviderDescriptor> = {
  beefree: { id: "beefree", label: "Beefree", supportsServerSession: true, preservesProviderDocument: true },
  topol: { id: "topol", label: "Topol", supportsServerSession: false, preservesProviderDocument: true },
  unlayer: { id: "unlayer", label: "Unlayer", supportsServerSession: false, preservesProviderDocument: true },
};

export const activeEditorProvider = editorProviders.beefree;
