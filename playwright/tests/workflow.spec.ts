import { expect, test } from "@playwright/test";
import {
  activeIs,
  confirmKey,
  DUMMY,
  openBatch,
  putWeight,
  resetTraining,
  statusLine,
  weighedNow,
} from "./support";

const COMPONENTS = [
  {
    id: "B-24187-01",
    name: "Remazol Brill. Blue RSPL",
    scale: "3 kg precision",
    landing: "1242.4",
    unit: "g",
  },
  {
    id: "B-24187-02",
    name: "Remazol Red RB",
    scale: "3 kg precision",
    landing: "386.8",
    unit: "g",
  },
  {
    id: "B-24187-03",
    name: "Remazol Yellow RGB",
    scale: "3 kg precision",
    landing: "94.2",
    unit: "g",
  },
  {
    id: "B-24187-04",
    name: "Sodium Sulphate",
    scale: "32 kg floor",
    landing: "24.048",
    unit: "kg",
  },
  {
    id: "B-24187-05",
    name: "Soda Ash",
    scale: "32 kg floor",
    landing: "9.619",
    unit: "kg",
  },
];

test.beforeEach(async ({ request }) => {
  await resetTraining(request);
});

test("B-24187: select, load recipe, weigh five components, write back, print ticket", async ({
  page,
  request,
}) => {
  const consoleErrors: string[] = [];
  page.on("console", (m) => {
    if (m.type() === "error") consoleErrors.push(m.text());
  });
  page.on("pageerror", (e) => consoleErrors.push(String(e)));
  const batchCalls: string[] = [];
  page.on("response", (response) => {
    const path = new URL(response.url()).pathname;
    if (path.startsWith("/api/batches"))
      batchCalls.push(
        `${response.request().method()} ${path} ${response.status()}`,
      );
  });

  await test.step("Open WeighingMS — batch queue from OrgaTEX", async () => {
    await page.goto("/");
    await expect(page.getByText("Scan a batch card to begin")).toBeVisible();
    for (const id of ["B-24187", "B-24188", "B-24190", "B-24191"]) {
      await expect(page.locator(`tr[data-batch="${id}"]`)).toBeVisible();
    }
  });

  await test.step("Select B-24187 and load its recipe", async () => {
    await page.locator('tr[data-batch="B-24187"]').click();
    await expect(page.getByText("Recipe · Teal 4C")).toBeVisible();
    await expect(page.locator(".comp")).toHaveCount(5);
    await expect(page.getByText("0 of 5 components weighed")).toBeVisible();
    expect(batchCalls).toEqual([
      "GET /api/batches 200",
      "GET /api/batches/B-24187 200",
      "GET /api/batches/B-24187/recipe 200",
    ]);
  });

  for (const [index, component] of COMPONENTS.entries()) {
    await test.step(`Weigh ${component.name} on the ${component.scale} scale and confirm`, async () => {
      await activeIs(page, component.id);
      await expect(page.locator(".weigh-head .nm")).toHaveText(component.name);
      await expect(page.getByTestId("scale-selected")).toHaveText(
        component.scale,
      );
      await expect(weighedNow(page)).toHaveText(
        component.unit === "g" ? "0.0" : "0.000",
      );
      await page.getByRole("button", { name: /Simulate dispense/ }).click();
      await expect(weighedNow(page)).toHaveText(component.landing, {
        timeout: 20_000,
      });
      await expect(statusLine(page)).toHaveText(
        "WITHIN TOLERANCE — PRESS OK TO CONFIRM",
      );
      await expect(confirmKey(page)).toBeEnabled();
      await confirmKey(page).click();
      if (index < COMPONENTS.length - 1) {
        await expect(
          page.getByText(`${index + 1} of 5 components weighed`),
        ).toBeVisible();
        await expect(
          page.locator(`[data-component="${component.id}"] .st`),
        ).toHaveText(`✓ ${component.landing}`);
      }
    });
  }

  await test.step("Batch complete — OrgaTEX write-back confirmed", async () => {
    await expect(page.getByText("Batch B-24187 weighed")).toBeVisible();
    await expect(page.getByText("5 of 5")).toBeVisible();
    await expect(page.getByText("YES")).toBeVisible();
    await expect(page.getByTestId("write-back")).toHaveText(
      /^CONFIRMED \d{2}:\d{2}:\d{2}$/,
    );
    const stored = await (
      await request.get(`${DUMMY}/api/batches/B-24187/consumption`)
    ).json();
    expect(stored).toHaveLength(1);
    expect(
      stored[0].posting.lines.map(
        (l: { actual: { value: string } }) => l.actual.value,
      ),
    ).toEqual(COMPONENTS.map((c) => c.landing));
    const batch = await (
      await request.get(`${DUMMY}/api/batches/B-24187`)
    ).json();
    expect(batch.status).toBe("WEIGHED");
  });

  await test.step("Print the weighing ticket", async () => {
    await expect(page.getByTestId("ticket")).toContainText(
      "FCI DYEING — WEIGHING TICKET",
    );
    await expect(page.getByTestId("ticket")).toContainText(
      "ALL WITHIN TOLERANCE",
    );
    await page.getByRole("button", { name: /Print ticket/ }).click();
    await expect(page.getByText(/^Ticket printed · TKT-/)).toBeVisible();
    const printed = await (await request.get(`${DUMMY}/api/tickets`)).json();
    expect(printed).toHaveLength(1);
    expect(printed[0].batchId).toBe("B-24187");
    expect(printed[0].reprint).toBe(false);
  });

  await test.step("Next batch — back to the queue, B-24187 is WEIGHED", async () => {
    await page.getByRole("button", { name: /Next batch/ }).click();
    await expect(page.locator('tr[data-batch="B-24187"] .tag')).toHaveText(
      "WEIGHED",
    );
    expect(consoleErrors).toEqual([]);
  });
});

test("Yellow RGB tolerance boundaries and the switch to the 32 kg floor scale", async ({
  page,
  request,
}) => {
  await openBatch(page, "B-24187");
  await page.locator('[data-component="B-24187-03"]').click();
  await activeIs(page, "B-24187-03");
  await expect(page.getByTestId("tolerance-caption")).toHaveText(
    "TOLERANCE ±0.5 g (93.5 – 94.5)",
  );

  const cases: [string, boolean][] = [
    ["93.4", false],
    ["93.5", true],
    ["94.0", true],
    ["94.5", true],
    ["94.6", false],
  ];
  for (const [weight, confirmable] of cases) {
    await putWeight(request, "scale-3kg", weight, "g");
    await expect(weighedNow(page)).toHaveText(weight);
    if (confirmable) await expect(confirmKey(page)).toBeEnabled();
    else await expect(confirmKey(page)).toBeDisabled();
  }
  await expect(page.locator(".surplus")).toContainText("Surplus +0.6 g");

  await page.locator('[data-component="B-24187-04"]').click();
  await activeIs(page, "B-24187-04");
  await expect(page.getByTestId("scale-selected")).toHaveText("32 kg floor");
  await expect(page.locator(".weigh-head .meta")).toHaveText(
    "AUX-0101 · LOT 2026-0112 · CONTAINER D-03 · TARE 1.850 kg",
  );
  await expect(weighedNow(page)).toHaveText("0.000");
});
