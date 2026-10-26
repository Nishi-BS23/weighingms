---
id: 007-failure-injection-and-reset
unit: 001-training-substitutes
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 002-training-substitutes
implemented: true
---

# Story: 007-failure-injection-and-reset

**Title**: Failure injection and reset

## User Story

**As a** trainer or test runner
**I want** to make any external system unavailable and to reset all training data
**So that** failure scenarios can be demonstrated and tests start from a known state

## Requirements

- FR-29 Training controls
- FR-20 Scale/scanner/printer failure (simulation)

## Acceptance Criteria

- [x] **When** `PUT /api/control/availability/orgatex` with `{"available": false}` is called, **Then** every Dummy OrgaTEX endpoint returns 503 `SYSTEM_UNAVAILABLE` until set back to true
- [x] **Given** systems `scale-3kg`, `scale-32kg`, `scanner`, `printer`, **Then** each can be toggled the same way and only its endpoints are affected
- [x] **When** `GET /api/control/availability` is called, **Then** the state of all five systems is returned
- [x] **When** `POST /api/control/reset` is called, **Then** batch statuses, consumption postings, tickets, scans, scale states and availability return to the seed state
- [x] Control endpoints are never affected by availability toggles

## UI/UX Impact

Training panel toggles (FR-29) call these through WeighingMS; status strip turns red for unavailable systems.

## API Dependencies

- Provides `GET /api/control/availability`, `PUT /api/control/availability/{system}`, `POST /api/control/reset`

## Test Expectations

- pytest: each toggle → 503 on the right endpoints only; reset restores seed

## Technical Notes

None

## Dependencies

### Requires
- 003-dummy-orgatex-consumption-and-status
- 004-dummy-scale-readings-and-tare
- 005-dummy-scanner
- 006-dummy-printer

### Enables
- 004-device-integration/004-device-status-and-failure-detection
- 006-weighing-station-ui/013-failure-scenario-tests

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Unknown system name | 404 |
| Reset while a scale profile runs | Profile cleared |

## Out of Scope

- Latency/timeout injection (503 only in this build)
