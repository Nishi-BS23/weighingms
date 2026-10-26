---
stage: plan
bolt: 011-weighing-station-ui
created: 2026-10-26T09:15:06Z
---

## Implementation Plan: 006-weighing-station-ui (bolt 4 of 4) — prove the product

### Objective
Automate the complete B-24187 workflow and the failure scenarios with Playwright (HTML report + video), and validate the implementation screen by screen against the prototype (Workbook Steps 28–30).

### 1. What will change
A Playwright project in `playwright/`, a root `npm run test:e2e` script, and validation evidence.

### 2. Files to be created / modified
- `playwright/playwright.config.ts` — Chromium, base URL `http://127.0.0.1:5173`, one worker (shared station state), HTML report, video on, `webServer` = root `npm run dev` (reused when already running)
- `playwright/tests/support.ts` — training helpers (reset, exact weight, availability) and dummy-service checks
- `playwright/tests/workflow.spec.ts` — Step 29 end-to-end scenario
- `playwright/tests/failures.spec.ts` — Step 30 scenarios
- `playwright/tsconfig.json`
- `package.json` (root) — `test:e2e` (modified)
- Evidence: `evidence/STEP-29-playwright-report/`, `STEP-29-e2e-video.webm`, `STEP-30-failure-tests.md`, `STEP-28-ui-validation/` (comparisons + validation.md)

### 3. Requirements and stories implemented
| Story | Requirements |
|-------|--------------|
| 012-end-to-end-workflow-test | FR-30, FR-31, FR-32, NFR-17 |
| 013-failure-scenario-tests | FR-20, FR-17, FR-13, FR-16, FR-22, FR-7 |

### 4. APIs involved
UI only for the operator path; WeighingMS `/api/training/*` to drive the simulated scale and inject failures; Dummy service (`:8100`) read-only checks for the stored consumption and printed tickets.

### 5. How it will be tested
The suites are the tests: workflow (open → select B-24187 → recipe → five components with Simulate dispense + Confirm → completion → write-back confirmed and stored → ticket printed and stored; plus Yellow RGB boundary values and the scale switch) and failures (scale unavailable, OrgaTEX unavailable, printer unavailable, over/under tolerance, re-tare, quit, incomplete batch). Run headless, report and video archived as evidence.

### Acceptance Criteria
- [ ] `npm run test:e2e` runs both suites green with an HTML report and video
- [ ] Network log of the batch calls captured in the workflow test
- [ ] Failure table (Scenario | Expected | Actual | Pass) filled from the run
- [ ] Prototype vs implementation comparison for all three screens with validation notes

### Checkpoint — plan review (delegated, self-validated)
Covers both stories and Workbook Steps 28–30; deterministic (training reset before each test, exact weights). **APPROVE PLAN.**
