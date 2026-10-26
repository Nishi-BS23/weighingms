import { expect, type APIRequestContext, type Page } from "@playwright/test";

/** The training substitutes service, read here only to prove what reached the "external" systems. */
export const DUMMY = "http://127.0.0.1:8100";

export type System =
  "orgatex" | "scale-3kg" | "scale-32kg" | "scanner" | "printer";

export async function resetTraining(request: APIRequestContext): Promise<void> {
  const response = await request.post("/api/training/reset");
  expect(response.ok()).toBeTruthy();
}

export async function setAvailable(
  request: APIRequestContext,
  system: System,
  available: boolean,
): Promise<void> {
  const response = await request.put(`/api/training/availability/${system}`, {
    data: { available },
  });
  expect(response.ok()).toBeTruthy();
}

/** Put an exact net weight on a simulated scale (deterministic, no timing). */
export async function putWeight(
  request: APIRequestContext,
  scaleId: "scale-3kg" | "scale-32kg",
  value: string,
  unit: "g" | "kg",
): Promise<void> {
  const response = await request.post(
    `/api/training/scales/${scaleId}/simulate`,
    {
      data: { profile: "exact", net: { value, unit } },
    },
  );
  expect(response.ok()).toBeTruthy();
}

export const weighedNow = (page: Page) => page.getByTestId("weighed-now");
export const statusLine = (page: Page) => page.getByTestId("status-line");
export const confirmKey = (page: Page) =>
  page.getByRole("button", { name: /OK · Confirm/ });

export async function openBatch(page: Page, batchId: string): Promise<void> {
  await page.goto("/");
  await page.locator(`tr[data-batch="${batchId}"]`).click();
  await expect(page.locator(".rail-head .v")).toHaveText(batchId);
}

export async function activeIs(page: Page, componentId: string): Promise<void> {
  await expect(
    page.locator(`[data-component="${componentId}"]`),
  ).toHaveAttribute("data-state", "active");
}
