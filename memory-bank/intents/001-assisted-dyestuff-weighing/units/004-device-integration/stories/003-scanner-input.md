---
id: 003-scanner-input
unit: 004-device-integration
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 004-device-integration
implemented: true
---

# Story: 003-scanner-input

**Title**: Scanner input

## User Story

**As a** weighing operator
**I want** scanned batch cards to reach the station once and in order
**So that** scanning a card reliably selects that batch

## Requirements

- FR-2 Batch selection (scan path)
- FR-27 Dummy Scanner (consumer)

## Acceptance Criteria

- [x] **When** the UI calls WeighingMS `GET /api/scanner/scans?after={seq}`, **Then** new scans from the Dummy Scanner are returned in order with `lastSeq`
- [x] Training passthrough `POST /api/training/scan {code}` forwards to the Dummy Scanner
- [x] **Given** the scanner is unavailable, **Then** 503 `SCANNER_UNAVAILABLE`

## UI/UX Impact

Screen 1 reacts to scans; training panel "Simulate scan".

## API Dependencies

- Provides WeighingMS `GET /api/scanner/scans`, `POST /api/training/scan`
- Uses Dummy Scanner `GET /api/scanner/scans`, `POST /api/scanner/scans`

## Test Expectations

- Adapter + API tests: order, cursor, unavailable

## Technical Notes

None

## Dependencies

### Requires
- 001-training-substitutes/005-dummy-scanner

### Enables
- 006-weighing-station-ui/003-select-batch-by-touch-or-scan

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Cursor ahead of dummy after reset | Returns scans with seq > 0 once lastSeq resets (cursor reset handled) |

## Out of Scope

- Keyboard-wedge handling (done in the UI)
