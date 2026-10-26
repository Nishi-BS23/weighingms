---
stage: test
bolt: 011-weighing-station-ui
created: 2026-10-26T09:39:13Z
---

## Test Report: 006-weighing-station-ui (bolt 4 of 4) — end-to-end and failure-scenario suites, UI validation

### Summary

- **End-to-end (Playwright, Chromium):** 11/11 passed (2 workflow, 9 failure scenarios). Run three times in a row on the final code with no flakes, about 29 s per run, via `npm run test:e2e`.
- **Project check (`npm run check`):**
  - Backend: 214/214 passed (1 new), coverage 97.86 %, with ruff format, ruff lint and `mypy --strict` clean.
  - Frontend: 50/50 passed (1 new), with Prettier, ESLint (type-checked) and `tsc` clean.
- **Browser console:** no errors during the full B-24187 workflow; the test asserts this.

### Test Files

- [x] `playwright/tests/workflow.spec.ts`
  - **B-24187 workflow:**
    - The queue shows 4 batches.
    - Selecting B-24187 makes exactly `GET /api/batches`, `/api/batches/B-24187` and `/api/batches/B-24187/recipe`.
    - The rail shows 5 components.
    - For each component: name, selected scale and zero readout; dispense lands within tolerance (1242.4 g, 386.8 g, 94.2 g, 24.048 kg, 9.619 kg); the status reads WITHIN TOLERANCE; Confirm; the counter advances.
    - The done screen shows 5 of 5, YES and `CONFIRMED hh:mm:ss`.
    - The dummy OrgaTEX holds one posting with those actuals in recipe order, and the batch is WEIGHED.
    - The ticket preview is checked, then printed; the dummy printer holds one non-reprint ticket for B-24187.
    - Next batch shows B-24187 as WEIGHED.
  - **Yellow RGB boundaries:** 93.4 blocked; 93.5, 94.0 and 94.5 allowed; 94.6 blocked with surplus +0.6 g. Sodium Sulphate switches to the `32 kg floor` scale with D-03 / 1.850 kg and a `0.000` readout.
- [x] `playwright/tests/failures.spec.ts`: scale unavailable; OrgaTEX unavailable (queue, mid-weighing, write-back PENDING then Retry, exactly one posting); printer unavailable; invalid weight (direct `/confirm` returns 409, malformed weight returns 422, nothing recorded); over and under tolerance; re-tare; quit; incomplete batch (409 BATCH_INCOMPLETE, step 3 disabled).
- [x] `frontend/src/App.test.tsx`: after **Reset training data**, the queue is fetched again (WEIGHED becomes QUEUED) and the operator is reloaded. It fails without the fix.
- [x] `tests/api/weighingms/test_devices_api.py::test_invalid_simulated_weight_is_rejected`: `-5`, `abc`, `1e3` and an empty value each return 422 VALIDATION_ERROR.

### Acceptance Criteria Validation

- ✅ **012-end-to-end-workflow-test**:
  - The suite reuses `npm run dev` and resets training data.
  - Full workflow, with write-back and ticket verified on the dummies.
  - Scale switch and Yellow boundaries asserted.
  - Network requests recorded.
  - HTML report and video produced (`evidence/STEP-29-playwright-report/`, `evidence/STEP-29-e2e-video.mp4`).
  - `npm run test:e2e` runs it.
- ✅ **013-failure-scenario-tests**:
  - Every listed scenario is automated and passes.
  - Results are tabulated in `evidence/STEP-30-failure-tests.md` (Scenario | Expected | Actual | Pass), with a video per scenario in `evidence/STEP-30-failure-videos/`.

### Issues Found

1. A race between a live poll and the final confirm caused a `409 SESSION_COMPLETED` console error. Fixed: polling pauses during actions.
2. Malformed training weights gave 500 and 503. Fixed: 422 validation at the API boundary.
3. Rail rows were 10 px taller than in the prototype, because the prototype renders in quirks mode. Matched with a CSS rule.
4. **Reset training data** on Screen 1 left a stale queue and operator. Fixed: the queue screen is remounted and the operator reloaded.

The remaining visual differences are intentional and listed in `evidence/STEP-28-ui-validation/validation.md`.

### Notes

The tests share one station database and one set of training substitutes, so they run with one worker. Each test starts from `POST /api/training/reset`.

### Stage checkpoint (delegated, self-validated)

All tests pass and every acceptance criterion is verified. **Approved**; bolt complete.
