---
id: 013-failure-scenario-tests
unit: 006-weighing-station-ui
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 011-weighing-station-ui
implemented: true
---

# Story: 013-failure-scenario-tests

**Title**: Failure scenario tests

## User Story

**As a** trainer and assessor
**I want** automated tests of the failure and boundary scenarios
**So that** the station is proven to fail safely

## Requirements

- FR-20
- FR-17
- FR-13
- FR-16
- FR-22
- FR-7

## Acceptance Criteria

- [x] Scale unavailable → readout "—", SCALE OFFLINE, Confirm disabled; restored → works
- [x] OrgaTEX unavailable → queue error with Retry; at completion → PENDING, retry after restore → CONFIRMED with exactly one posting
- [x] Printer unavailable → message, completion intact; restored → print works
- [x] Over tolerance / under tolerance → Confirm disabled
- [x] Re-tare → weight reset to 0
- [x] Quit → back to queue, no record, resume keeps confirmed components
- [x] Incomplete batch → completion API returns 409 BATCH_INCOMPLETE
- [x] Results tabulated in `STEP-30-failure-tests.md` (Scenario | Expected | Actual | Pass)

## UI/UX Impact

Exercises error states on all screens.

## API Dependencies

- Uses training availability toggles and WeighingMS API

## Test Expectations

- This story is the test

## Technical Notes

None

## Dependencies

### Requires
- 012-end-to-end-workflow-test
- 010-operator-facing-failure-messages

### Enables
- None

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Toggle left off by a failed test | Each test resets training data in beforeEach |

## Out of Scope

- Network latency simulation
