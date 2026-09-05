import { describe, expect, it } from "vitest";
import { getCanonicalEmails, getJourneyRecipe } from "./canonical";
import { evaluateEmailQa } from "./qa";

describe("canonical campaign import and QA", () => {
  it("preserves the complete 53-email source portfolio", () => {
    const emails = getCanonicalEmails();
    expect(emails).toHaveLength(53);
    expect(emails.every(email => email.sourceDigest.length === 64)).toBe(true);
  });

  it("fails closed for known source-blocked input", () => {
    const blockedEmail = getCanonicalEmails().find(email => email.sourceStatus === "source_blocked");
    expect(blockedEmail).toBeDefined();
    const qa = evaluateEmailQa(blockedEmail!.key);
    expect(qa.status).toBe("qa_failed");
    expect(qa.checks.some(check => check.id === "module-order" && check.status === "fail")).toBe(true);
  });

  it("detects unsafe rendered HTML before a handoff package can be created", () => {
    const qa = evaluateEmailQa("BR-1", `
      <table style="background-color: #fff"><tr><td width="800">
        <a href="https://example.com/product">View product</a>
        <img src="data:image/png;base64,QUJD" />
        {{ unsupported_token }}
      </td></tr></table>
    `);
    const failedIds = qa.checks.filter(check => check.status === "fail").map(check => check.id);
    expect(failedIds).toEqual(expect.arrayContaining(["cta-utm", "liquid-support", "transparent-wrapper", "accessibility", "responsive-render"]));
  });

  it("provides versioned Flow setup rules with collision, exit, and frequency safeguards", () => {
    const recipe = getJourneyRecipe("J2 · Cart Recovery");
    expect(recipe.version).toMatch(/^2026\.08\.25$/);
    expect(recipe.steps.length).toBeGreaterThan(2);
    expect(recipe.collisionRule).toContain("newsletter");
    expect(recipe.exitRule).toContain("purchase");
    expect(recipe.frequencyRule).toContain("two-per-seven-day");
  });
});
