import { afterEach, describe, expect, it, vi } from "vitest";
import { apiError, stubApi } from "../test-utils";
import { api, ApiError } from "./client";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("api client", () => {
  it("turns the standard error body into an ApiError with its code", async () => {
    stubApi({ "GET /api/batches": apiError(503, "ORGATEX_UNAVAILABLE", "OrgaTEX is down") });

    const error = await api.batches().catch((e: unknown) => e);

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 503, code: "ORGATEX_UNAVAILABLE" });
  });

  it("reports a network failure as NETWORK_ERROR", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.reject(new TypeError("Failed to fetch"))),
    );

    await expect(api.batches()).rejects.toMatchObject({ code: "NETWORK_ERROR" });
  });

  it("sends JSON bodies", async () => {
    const { fetchMock } = stubApi({
      "PUT /api/training/availability/printer": { body: { systems: {} } },
    });

    await api.training.setAvailability("printer", false);

    const init = fetchMock.mock.calls[0]?.[1];
    expect(init?.body).toBe(JSON.stringify({ available: false }));
  });
});
