---
stage: implement
bolt: 011-weighing-station-ui
created: 2026-10-26T09:37:51Z
---

## Implementation Walkthrough: 006-weighing-station-ui (bolt 4 of 4) — end-to-end and failure-scenario suites, UI validation

### Summary

The product is now proven end to end. A Playwright suite runs the whole B-24187 workflow through the real UI. It checks what reached the external systems by reading the training substitutes directly: OrgaTEX consumption, batch status and printed tickets. A second suite drives each failure scenario from Workbook Step 30 through the training controls. The implementation was also compared with the prototype screen by screen. That comparison, the new suites and a rehearsal of the demonstration found four small defects, all fixed here.

### Structure Overview

`playwright/playwright.config.ts` targets the Vite UI at 127.0.0.1:5173. Its `webServer` is the root `npm run dev`, and it reuses a stack that is already running. The tests share one station, so they run serially, and every test resets the training data first. `tests/support.ts` holds the training helpers (reset, availability, exact weight) and the selectors. `workflow.spec.ts` covers story 012 and `failures.spec.ts` covers story 013.

### Completed Work

- [x] `playwright/playwright.config.ts` - Chromium, 1 worker, HTML and list reporters, video, screenshots, `webServer` = `npm run dev` (reused)
- [x] `playwright/tsconfig.json`, `playwright/package.json` (`typecheck` script) - strict TypeScript for the suites
- [x] `playwright/tests/support.ts` - `resetTraining`, `setAvailable`, `putWeight` (exact, deterministic), `openBatch`, `activeIs`
- [x] `playwright/tests/workflow.spec.ts`
  - B-24187 from queue to ticket: five components with *Simulate dispense* then Confirm.
  - Write-back verified on the dummy OrgaTEX: one posting, the actual weights in recipe order, and the batch WEIGHED.
  - Ticket verified on the dummy printer.
  - Network log of the three batch calls.
  - No browser console errors.
  - A second test covers the Yellow RGB boundaries and the switch to the 32 kg scale.
- [x] `playwright/tests/failures.spec.ts` - scale, OrgaTEX (queue, mid-weighing, write-back), printer, invalid weight, over/under tolerance, re-tare, quit and incomplete batch
- [x] `package.json` (root) - `test:e2e`; `setup` also installs the Playwright package and Chromium
- [x] `frontend/src/features/weighing/WeighScreen.tsx` - live polling paused while an action runs
- [x] `frontend/src/styles/station.css` - rail row line height matched to the prototype
- [x] `frontend/src/App.tsx` - **Reset training data** now reloads the queue and the operator (`App.test.tsx`)
- [x] `src/weighingms/api/training.py` - `QuantityIn.value` validated as a non-negative decimal string; `frontend/src/api/schema.d.ts` regenerated
- [x] Evidence:
  - `evidence/STEP-28-ui-validation/`: three comparison sheets plus `validation.md`.
  - `evidence/STEP-29-playwright-report/`, `STEP-29-e2e-video.mp4`, `STEP-29-e2e-final.png`, `STEP-29-check.txt`.
  - `evidence/STEP-30-failure-tests.md`, `STEP-30-failure-videos/`, `STEP-29-30-playwright-run.txt`.

### Key Decisions

- **Check the external systems, not only the screen.** The workflow test reads the dummy OrgaTEX and the dummy printer on port 8100 directly, so "CONFIRMED" on screen is backed by a stored posting.
- **Exact weights for failure tests; the real dispense ramp for the main workflow.** The workflow uses *Simulate dispense* (eased ramp, 120 ms polling), as an operator would. The failure tests set exact weights so they never depend on timing (NFR-15).
- **"Invalid weight" is enforced by the server.** The test bypasses the disabled button and calls `/confirm` directly, which returns 409 OUT_OF_TOLERANCE. It also injects malformed weights, which return 422.

### Deviations from Plan

- An "Invalid weight" scenario was added to the failure suite, because Workbook Step 30 lists it separately from over and under tolerance.
- Four defects were found and fixed (see Developer Notes).

### Dependencies Added

None. `@playwright/test` was added to `playwright/package.json` during the plan stage.

### Developer Notes

Defects found by this bolt, each fixed:
1. **Spurious `409 SESSION_COMPLETED` in the console after the last confirm.** A live poll could race the final confirm. Polling now pauses while an action runs. The workflow test now checks that the console has no errors.
2. **Training simulate with `"abc"` returned 500, and `"-5"` returned 503.** Both now return 422 VALIDATION_ERROR, with a regression test in `tests/api/weighingms/test_devices_api.py`.
3. **Rail rows were 71 px against the prototype's 61 px.** The prototype renders in quirks mode, so its two-line cells are shorter. One CSS rule now gives 61.6 px.
4. **Reset training data left a stale queue.** Pressed on Screen 1, it reset the backend, but the queue still showed B-24187 as WEIGHED, and the operator chip was not refreshed. Found while rehearsing the Step 35 demonstration. The queue screen is now remounted, and the operator is reloaded.

### Stage checkpoint (delegated, self-validated)

Suites written; type check and format are clean. Run against the live stack: 11/11 passed, three times in a row. **Approved**; proceed to Test.
