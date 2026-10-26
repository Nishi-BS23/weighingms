---
id: 012-end-to-end-workflow-test
unit: 006-weighing-station-ui
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 011-weighing-station-ui
implemented: true
---

# Story: 012-end-to-end-workflow-test

**Title**: End-to-end workflow test (B-24187)

## User Story

**As a** trainer and assessor
**I want** an automated end-to-end test of the complete B-24187 workflow with report and video
**So that** the product is proven to work, not just shown

## Requirements

- FR-30
- FR-31
- FR-32
- NFR-17 E2E

## Acceptance Criteria

- [x] Playwright suite (TypeScript) in `playwright/` starts the stack (or reuses `npm run dev`), resets training data, then: open app → select B-24187 → recipe with 5 components → for each component drive the dummy scale into tolerance and Confirm → batch complete → OrgaTEX write-back CONFIRMED (verified also via dummy `GET /api/batches/B-24187/consumption`) → print ticket (verified via dummy `GET /api/tickets`)
- [x] Asserts scale switch (3 kg precision → 32 kg floor) and Yellow RGB tolerance boundary behaviour in the UI (93.4 blocked, 93.5/94.0/94.5 allowed, 94.6 blocked)
- [x] Records network requests for `/api/batches`, `/api/batches/B-24187`, `/api/batches/B-24187/recipe`
- [x] HTML report and video are produced (`playwright-report/`, `test-results/`)
- [x] `npm run test:e2e` runs it

## UI/UX Impact

Exercises all screens.

## API Dependencies

- Uses WeighingMS API and training endpoints

## Test Expectations

- This story is the test

## Technical Notes

None

## Dependencies

### Requires
- 009-ticket-preview-and-print

### Enables
- 013-failure-scenario-tests

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Slow machine | Assertions wait on UI state, not fixed sleeps |

## Out of Scope

- Cross-browser matrix (Chromium only)
