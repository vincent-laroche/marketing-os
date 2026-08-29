import { describe, expect, it } from "vitest";
import { activeEditorProvider, editorProviders } from "../client/src/lib/editorProvider";

describe("editor provider UI boundary", () => {
  it("keeps Beefree active while retaining migration descriptors for Topol and Unlayer", () => {
    expect(activeEditorProvider.id).toBe("beefree");
    expect(activeEditorProvider.supportsServerSession).toBe(true);
    expect(editorProviders.topol.preservesProviderDocument).toBe(true);
    expect(editorProviders.unlayer.preservesProviderDocument).toBe(true);
  });
});
