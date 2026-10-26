import { defineConfig, devices } from "@playwright/test";

/**
 * End-to-end suites for WeighingMS (Workbook Steps 29–30). The tests share one station (one
 * database, one set of training substitutes), so they run serially and reset the training data
 * before each test.
 */
export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 90_000,
  expect: { timeout: 10_000 },
  reporter: [
    ["list"],
    ["html", { outputFolder: "playwright-report", open: "never" }],
  ],
  use: {
    baseURL: "http://127.0.0.1:5173",
    viewport: { width: 1240, height: 1100 },
    video: "on",
    screenshot: "on",
    trace: "retain-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 1240, height: 1100 },
      },
    },
  ],
  webServer: {
    command: "npm run dev",
    cwd: "..",
    url: "http://127.0.0.1:5173",
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
