import { router, adminProcedure, protectedProcedure } from "../_core/trpc";
import { getMarketingSyncHealth, requestMarketingReconciliation } from "../marketingSync";

export const marketingSyncRouter = router({
  health: protectedProcedure.query(async () => getMarketingSyncHealth()),
  run: adminProcedure.mutation(async ({ ctx }) => requestMarketingReconciliation(ctx.user.id)),
});
