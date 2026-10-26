---
stage: test
bolt: 005-weighing-station-ui
created: 2026-10-26T07:11:48Z
---

## Test Report: 006-weighing-station-ui (bolt 1 of 4)

### Summary

- **Tests**: frontend 14/14 passed (new); backend 112/112 still passing
- **Coverage**: logic and screens of this bolt covered by component tests; backend 98%
- **Static checks**: Prettier, ESLint (type-checked), `tsc --noEmit` clean; root `npm run check` green

### Test Files

- [x] `frontend/src/api/client.test.ts` - standard error body → `ApiError` with code, network failure → `NETWORK_ERROR`, JSON request bodies
- [x] `frontend/src/features/chrome/StatusStrip.test.tsx` - prototype strip texts, OrgaTEX "LINKED HH:MM", DOWN/DEGRADED shown with text, unknown status
- [x] `frontend/src/features/chrome/StepIndicator.test.tsx` - current step pressed, unreachable step disabled, selection callback
- [x] `frontend/src/features/batch-queue/BatchQueueScreen.test.tsx` - rows from `GET /api/batches`, touch selection calls batch + recipe, refusal reason, keyboard-wedge unknown code, barcode-scanner selection, OrgaTEX down → message + Retry recovers, scanner down → touch hint
- [x] `frontend/src/test-utils.ts`, `test-fixtures.ts` - route-table fetch stub and API-shaped fixtures

### Acceptance Criteria Validation

- ✅ **`npm run dev` prints the UI URL and serves Screen 1** — "Local: http://127.0.0.1:5173/"
- ✅ **Queue rows come from `GET /api/batches`; no batch literals in UI code** — component test + grep in evidence/STEP-19-network.txt
- ✅ **Selecting B-24187 calls `/api/batches/B-24187` and `/recipe` and shows the recipe** — component test + real-browser network log
- ✅ **Refusals explained; OrgaTEX down → message + Retry; scanner down → touch hint**
- ✅ **Frame, top bar, step indicator, status strip and training panel match the prototype** — screenshot comparison (evidence/STEP-19-batch-screen.png)
- ✅ **Root `npm run check` green**

### Issues Found

- Lint (react-hooks v7) rejected effect-triggered loads; solved with a `useResource` hook that only updates state in async callbacks.

### Notes

Operator chip shows "—" until the operator endpoint lands in bolt 006 (expected 404 in the browser console until then).

### Stage checkpoint (delegated, self-validated)

All tests pass; acceptance criteria verified in tests and in a real browser. **Approved** — bolt complete.
