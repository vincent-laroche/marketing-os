import { afterEach, describe, expect, it, vi } from "vitest";

const originalClientId = process.env.BEE_CLIENT_ID;
const originalClientSecret = process.env.BEE_CLIENT_SECRET;

afterEach(() => {
  if (originalClientId === undefined) delete process.env.BEE_CLIENT_ID;
  else process.env.BEE_CLIENT_ID = originalClientId;
  if (originalClientSecret === undefined) delete process.env.BEE_CLIENT_SECRET;
  else process.env.BEE_CLIENT_SECRET = originalClientSecret;
  vi.restoreAllMocks();
});

describe("Beefree provider boundary", () => {
  it("returns a safe unconfigured state without calling the vendor when credentials are absent", async () => {
    delete process.env.BEE_CLIENT_ID;
    delete process.env.BEE_CLIENT_SECRET;
    const fetchSpy = vi.spyOn(globalThis, "fetch");
    const { createBeefreeSession } = await import("./beefree");

    await expect(createBeefreeSession("campaign-os-test")).resolves.toMatchObject({
      configured: false,
      message: expect.stringContaining("not been configured"),
    });
    expect(fetchSpy).not.toHaveBeenCalled();
  });
});
