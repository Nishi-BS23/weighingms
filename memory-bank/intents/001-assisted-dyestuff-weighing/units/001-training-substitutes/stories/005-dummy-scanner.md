---
id: 005-dummy-scanner
unit: 001-training-substitutes
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 002-training-substitutes
implemented: true
---

# Story: 005-dummy-scanner

**Title**: Dummy scanner

## User Story

**As a** trainer
**I want** to simulate scanning a batch card
**So that** the "Scan a batch card to begin" interaction works without a physical scanner

## Requirements

- FR-27 Dummy Scanner
- FR-2 Batch selection (scan source)

## Acceptance Criteria

- [x] **When** `POST /api/scanner/scans` with `{"code": "B-24187"}` is called, **Then** it returns `{seq, code, scannedAt}` with seq increasing by 1
- [x] **When** `GET /api/scanner/scans?after=0` is called, **Then** all scans with seq > 0 are returned in order with `lastSeq`
- [x] **When** `GET /api/scanner/status` is called, **Then** it returns `{available: true}`

## UI/UX Impact

None directly. Scans arrive on Screen 1 via WeighingMS.

## API Dependencies

- Provides `POST /api/scanner/scans`, `GET /api/scanner/scans?after=`, `GET /api/scanner/status`

## Test Expectations

- pytest: ordering, cursor, empty code → 422

## Technical Notes

None

## Dependencies

### Requires
- 001-dummy-orgatex-batch-queue (skeleton)

### Enables
- 004-device-integration/003-scanner-input

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Same code scanned twice | Two scan events (seq differ) |

## Out of Scope

- Serial or HID emulation
