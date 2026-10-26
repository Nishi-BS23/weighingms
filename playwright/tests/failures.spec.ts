import { expect, test } from "@playwright/test";
import {
  activeIs,
  confirmKey,
  DUMMY,
  openBatch,
  putWeight,
  resetTraining,
  setAvailable,
  statusLine,
  weighedNow,
} from "./support";

test.beforeEach(async ({ request }) => {
  await resetTraining(request);
});

test("Scale unavailable — safe failure", async ({ page, request }) => {
  await openBatch(page, "B-24187");
  await putWeight(request, "scale-3kg", "1242.0", "g");
  await expect(confirmKey(page)).toBeEnabled();

  await setAvailable(request, "scale-3kg", false);

  await expect(weighedNow(page)).toHaveText("—");
  await expect(statusLine(page)).toHaveText("SCALE OFFLINE — CHECK CONNECTION");
  await expect(confirmKey(page)).toBeDisabled();
  await expect(page.locator('[data-device="scale-3kg"]')).toHaveText(
    "SCALE 3 kg · OFFLINE",
  );

  await setAvailable(request, "scale-3kg", true);
  await expect(weighedNow(page)).toHaveText("1242.0");
  await expect(confirmKey(page)).toBeEnabled();
});

test("OrgaTEX unavailable — queue message with Retry; weighing in progress continues", async ({
  page,
  request,
}) => {
  await setAvailable(request, "orgatex", false);
  await page.goto("/");
  await expect(
    page.getByText("OrgaTEX is not reachable. Check the connection and retry."),
  ).toBeVisible();
  await expect(page.locator('[data-device="orgatex"]')).toHaveText(
    "ORGATEX · OFFLINE",
  );

  await setAvailable(request, "orgatex", true);
  await page.getByRole("button", { name: "Retry" }).click();
  await page.locator('tr[data-batch="B-24187"]').click();
  await activeIs(page, "B-24187-01");

  await setAvailable(request, "orgatex", false);
  await putWeight(request, "scale-3kg", "1240.0", "g");
  await confirmKey(page).click();
  await activeIs(page, "B-24187-02");
});

test("OrgaTEX unavailable at completion — PENDING, Retry posts exactly once", async ({
  page,
  request,
}) => {
  await openBatch(page, "B-24187");
  const plan: ["scale-3kg" | "scale-32kg", string, "g" | "kg"][] = [
    ["scale-3kg", "1240.0", "g"],
    ["scale-3kg", "386.0", "g"],
    ["scale-3kg", "94.0", "g"],
    ["scale-32kg", "24.000", "kg"],
    ["scale-32kg", "9.600", "kg"],
  ];
  for (const [index, [scale, value, unit]] of plan.entries()) {
    if (index === 4) await setAvailable(request, "orgatex", false);
    await putWeight(request, scale, value, unit);
    await expect(weighedNow(page)).toHaveText(value);
    await confirmKey(page).click();
    if (index < 4)
      await expect(
        page.getByText(`${index + 1} of 5 components weighed`),
      ).toBeVisible();
  }

  await expect(page.getByText("Batch B-24187 weighed")).toBeVisible();
  await expect(page.getByTestId("write-back")).toHaveText("PENDING");

  await setAvailable(request, "orgatex", true);
  await page.getByRole("button", { name: "Retry" }).click();
  await expect(page.getByTestId("write-back")).toHaveText(/^CONFIRMED/);
  const stored = await (
    await request.get(`${DUMMY}/api/batches/B-24187/consumption`)
  ).json();
  expect(stored).toHaveLength(1);
});

test("Printer unavailable — defined message, batch stays completed, print later", async ({
  page,
  request,
}) => {
  await openBatch(page, "B-24191");
  const plan: ["scale-3kg" | "scale-32kg", string, "g" | "kg"][] = [
    ["scale-3kg", "285.0", "g"],
    ["scale-3kg", "9.5", "g"],
    ["scale-32kg", "9.500", "kg"],
    ["scale-32kg", "3.800", "kg"],
  ];
  for (const [scale, value, unit] of plan) {
    await putWeight(request, scale, value, unit);
    await expect(weighedNow(page)).toHaveText(value);
    await confirmKey(page).click();
  }
  await expect(page.getByText("Batch B-24191 weighed")).toBeVisible();

  await setAvailable(request, "printer", false);
  await page.getByRole("button", { name: /Print ticket/ }).click();
  await expect(
    page.getByText("Printer not available. Check the printer and try again."),
  ).toBeVisible();
  await expect(page.getByText("Batch B-24191 weighed")).toBeVisible();

  await setAvailable(request, "printer", true);
  await page.getByRole("button", { name: /Print ticket/ }).click();
  await expect(page.getByText(/^Ticket printed · TKT-/)).toBeVisible();
});

test("Invalid weight — shown but refused by the server even if the UI is bypassed", async ({
  page,
  request,
}) => {
  await openBatch(page, "B-24187");
  await putWeight(request, "scale-3kg", "1250.0", "g");
  await expect(weighedNow(page)).toHaveText("1250.0");
  await expect(confirmKey(page)).toBeDisabled();

  const session = await (
    await request.post("/api/sessions", { data: { batchId: "B-24187" } })
  ).json();
  const confirm = await request.post(
    `/api/sessions/${session.sessionId}/confirm`,
  );
  expect(confirm.status()).toBe(409);
  expect((await confirm.json()).error.code).toBe("OUT_OF_TOLERANCE");

  for (const value of ["-5", "abc"]) {
    const injected = await request.post(
      "/api/training/scales/scale-3kg/simulate",
      { data: { profile: "exact", net: { value, unit: "g" } } },
    );
    expect(injected.status()).toBe(422);
  }

  const records = await (
    await request.get("/api/weighing-records?batchId=B-24187")
  ).json();
  expect(records).toEqual([]);
  await activeIs(page, "B-24187-01");
});

test("Over tolerance and under tolerance — cannot confirm, nothing recorded", async ({
  page,
  request,
}) => {
  await openBatch(page, "B-24187");
  await putWeight(request, "scale-3kg", "1250.0", "g");
  await expect(statusLine(page)).toHaveText("OVER TOLERANCE — SURPLUS +10.0 g");
  await expect(confirmKey(page)).toBeDisabled();
  await expect(page.locator(".surplus")).toContainText("over tolerance");

  await putWeight(request, "scale-3kg", "1200.0", "g");
  await expect(statusLine(page)).toHaveText("DISPENSE — 40.0 g REMAINING");
  await expect(confirmKey(page)).toBeDisabled();

  const records = await (
    await request.get("/api/weighing-records?batchId=B-24187")
  ).json();
  expect(records).toEqual([]);
});

test("Re-tare — weight reset to zero", async ({ page, request }) => {
  await openBatch(page, "B-24187");
  await putWeight(request, "scale-3kg", "500.0", "g");
  await expect(weighedNow(page)).toHaveText("500.0");

  await page.getByRole("button", { name: /Re-tare/ }).click();

  await expect(weighedNow(page)).toHaveText("0.0");
});

test("Quit — safe exit: nothing recorded, batch resumes where it was", async ({
  page,
  request,
}) => {
  await openBatch(page, "B-24187");
  await putWeight(request, "scale-3kg", "1240.0", "g");
  await confirmKey(page).click();
  await activeIs(page, "B-24187-02");
  await putWeight(request, "scale-3kg", "200.0", "g");

  await page.getByRole("button", { name: /Quit/ }).click();
  await page.getByRole("button", { name: "Quit", exact: true }).click();

  await expect(page.getByText("Scan a batch card to begin")).toBeVisible();
  const records = await (
    await request.get("/api/weighing-records?batchId=B-24187")
  ).json();
  expect(records).toHaveLength(1);
  await page.locator('tr[data-batch="B-24187"]').click();
  await expect(page.getByText("1 of 5 components weighed")).toBeVisible();
  await activeIs(page, "B-24187-02");
});

test("Incomplete batch — cannot complete", async ({ page, request }) => {
  await openBatch(page, "B-24187");
  const session = await (
    await request.post("/api/sessions", { data: { batchId: "B-24187" } })
  ).json();

  const response = await request.post(
    `/api/sessions/${session.sessionId}/complete`,
  );

  expect(response.status()).toBe(409);
  expect((await response.json()).error.code).toBe("BATCH_INCOMPLETE");
  await expect(
    page.getByRole("button", { name: "3 · Confirm & print" }),
  ).toBeDisabled();
});
