import { z } from "zod";
import { createBeefreeSession } from "../beefree";
import { getCanonicalEmail, getCanonicalEmails, getJourneyRecipe } from "../canonical";
import { attachExportPackageScreenshot, captureProductSnapshot, createExportPackage, getCampaignDetail, getCampaignPortfolio, getRecentAuditEvents, listFlowRecipes, notifySourceBlockers, recordHandoffEvidence, saveQaRun, saveRevision } from "../db";
import { getEditorProvider } from "../editorProvider";
import { evaluateEmailQa } from "../qa";
import { searchCatalog } from "../shopify";
import { protectedProcedure, publicProcedure, router } from "../_core/trpc";

const revisionInput = z.object({
  emailKey: z.string().min(2),
  providerDocument: z.string().min(2),
  renderedHtml: z.string().optional(),
  subject: z.string().optional(),
  previewText: z.string().optional(),
});

export const campaignsRouter = router({
  portfolio: protectedProcedure.query(async () => getCampaignPortfolio()),
  detail: protectedProcedure.input(z.object({ emailKey: z.string().min(2) })).query(async ({ input }) => getCampaignDetail(input.emailKey)),
  catalog: router({
    search: protectedProcedure.input(z.object({ query: z.string().max(120).default("") })).query(async ({ input }) => searchCatalog(input.query)),
    snapshot: protectedProcedure.input(z.object({
      emailKey: z.string().min(2),
      product: z.object({
        id: z.string().min(1),
        title: z.string().min(1),
        handle: z.string().min(1),
        status: z.string().min(1),
        featuredImageUrl: z.string().nullable(),
        price: z.string().nullable(),
      }),
    })).mutation(async ({ ctx, input }) => captureProductSnapshot({ ...input, userId: ctx.user.id })),
  }),
  beefree: router({
    session: protectedProcedure.input(z.object({ uid: z.string().min(2).max(128) })).query(async ({ input }) => getEditorProvider("beefree").createSession(input.uid)),
  }),
  revisions: router({
    save: protectedProcedure.input(revisionInput).mutation(async ({ ctx, input }) => {
      const canonical = getCanonicalEmail(input.emailKey);
      if (!canonical) throw new Error("Canonical email not found.");
      return saveRevision({ ...input, sourceDigest: canonical.sourceDigest, userId: ctx.user.id });
    }),
  }),
  qa: router({
    run: protectedProcedure.input(z.object({ emailKey: z.string().min(2), renderedHtml: z.string().optional() })).mutation(async ({ ctx, input }) => {
      const result = evaluateEmailQa(input.emailKey, input.renderedHtml);
      await saveQaRun({ emailKey: input.emailKey, result, userId: ctx.user.id });
      return result;
    }),
  }),
  handoff: router({
    prepare: protectedProcedure.input(z.object({ emailKey: z.string().min(2), renderedHtml: z.string().min(1) })).mutation(async ({ ctx, input }) => {
      const qa = evaluateEmailQa(input.emailKey, input.renderedHtml);
      if (qa.status !== "qa_passed") throw new Error("Handoff is blocked until deterministic QA passes.");
      const canonical = getCanonicalEmail(input.emailKey);
      if (!canonical) throw new Error("Canonical email not found.");
      return createExportPackage({ email: canonical, renderedHtml: input.renderedHtml, qa, userId: ctx.user.id });
    }),
    recordEvidence: protectedProcedure.input(z.object({
      emailKey: z.string().min(2),
      shopifyDraftUrl: z.string().url(),
      evidenceNote: z.string().min(8).max(2000),
    })).mutation(async ({ ctx, input }) => recordHandoffEvidence({ ...input, userId: ctx.user.id })),
    uploadScreenshot: protectedProcedure.input(z.object({
      exportPackageId: z.number().int().positive(),
      viewport: z.enum(["320px", "375px", "430px", "desktop", "gmail-dark-mode"]),
      dataUrl: z.string().min(32).max(6_000_000),
    })).mutation(async ({ ctx, input }) => attachExportPackageScreenshot({ ...input, userId: ctx.user.id })),
  }),
  flow: router({
    recipes: protectedProcedure.query(async () => {
      const recipes = await listFlowRecipes();
      return recipes;
    }),
    preview: protectedProcedure.input(z.object({ journey: z.string().min(2) })).query(({ input }) => getJourneyRecipe(input.journey)),
  }),
  alerts: router({
    notifySourceBlockers: protectedProcedure.mutation(async ({ ctx }) => notifySourceBlockers(ctx.user.id)),
  }),
  audit: protectedProcedure.query(async () => getRecentAuditEvents()),
  source: protectedProcedure.query(() => ({ total: getCanonicalEmails().length })),
});
