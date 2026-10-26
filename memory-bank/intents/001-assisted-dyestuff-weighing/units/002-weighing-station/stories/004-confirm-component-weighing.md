---
id: 004-confirm-component-weighing
unit: 002-weighing-station
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 007-weighing-station
implemented: true
---

# Story: 004-confirm-component-weighing

**Title**: Confirm a component weighing

## User Story

**As a** weighing operator
**I want** to confirm a component when it is within tolerance and have the weighing recorded permanently
**So that** the batch has a complete, trustworthy record of what was dispensed

## Requirements

- FR-13 Confirmation
- FR-5 Dyestuff lot
- FR-6 Container
- FR-19 Operator traceability

## Acceptance Criteria

- [x] **Given** the active component's live net weight is within tolerance, **When** `POST /api/sessions/{id}/confirm` is called, **Then** the backend re-reads the scale, re-evaluates and stores a WeighingRecord with batch, component, dyestuff code/name, target, actual, unit, tolerance min/max, result IN_TOLERANCE, operator, lot, container, tare, scale, confirmedAt
- [x] **Given** the re-read weight is outside tolerance, **Then** 409 `OUT_OF_TOLERANCE` and nothing is stored
- [x] **Given** the scale is unavailable or its calibration expired, **Then** 409 `SCALE_UNAVAILABLE` / `SCALE_CALIBRATION_EXPIRED` and nothing is stored
- [x] **Given** a successful confirm, **Then** the record is committed before the response and cannot be updated or deleted through any API
- [x] **Then** the response contains the updated session (component DONE with actual, next component ACTIVE or session ready to complete)

## UI/UX Impact

OK · Confirm (F1) on Screen 2; rail item shows "✓ {actual}".

## API Dependencies

- Provides `POST /api/sessions/{sessionId}/confirm`
- Uses `ScalePort.read_weight`, `ScalePort.status` (004)

## Test Expectations

- API test producing the transaction JSON (Workbook STEP-25-transaction.json)
- Rejection tests: out of tolerance, scale down, calibration expired
- Durability test: record present after engine restart

## Technical Notes

Decimal-as-text columns; insert-only repository for records.

## Dependencies

### Requires
- 003-tolerance-evaluation
- 010-activate-component-weighing-context

### Enables
- 007-component-progression
- 009-batch-completion
- 005-ticket-printing/001-compose-weighing-ticket

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Double-click Confirm | Second call finds component DONE → 409 `COMPONENT_ALREADY_DONE`, no duplicate record |

## Out of Scope

- Corrections of confirmed records (new record referencing original — not in this build)
