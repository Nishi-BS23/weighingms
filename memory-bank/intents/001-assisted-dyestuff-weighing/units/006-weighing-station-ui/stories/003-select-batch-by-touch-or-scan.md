---
id: 003-select-batch-by-touch-or-scan
unit: 006-weighing-station-ui
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 005-weighing-station-ui
implemented: true
---

# Story: 003-select-batch-by-touch-or-scan

**Title**: Select a batch by touch or scan

## User Story

**As a** weighing operator
**I want** to start a batch by touching its row or scanning its card
**So that** I get to the weighing screen with one action

## Requirements

- FR-30 Screen 1
- FR-2 Batch selection

## Acceptance Criteria

- [x] Touching the B-24187 row requests `GET /api/batches/B-24187` and `GET /api/batches/B-24187/recipe`, then starts/resumes the session (`POST /api/sessions`) and shows Screen 2
- [x] A scan from the scanner (polled `GET /api/scanner/scans?after=`) or typed into the always-focused scan field + Enter (keyboard-wedge) selects the same way
- [x] Unknown or non-selectable codes show "Batch {code} cannot be weighed: {reason}" and stay on Screen 1
- [x] Scanner DOWN → scan prompt says "Scanner unavailable — touch a row"; touch still works

## UI/UX Impact

Prototype View 1 interactions (touch row, scan) → View 2.

## API Dependencies

- Uses `GET /api/batches/{batchId}`, `GET /api/batches/{batchId}/recipe`, `POST /api/sessions`, `GET /api/scanner/scans`

## Test Expectations

- Vitest: keyboard-wedge input triggers selection
- Playwright (in 012): touch and scan paths

## Technical Notes

Until bolt 006 delivers `POST /api/sessions`, selection loads batch + recipe and opens a read-only recipe view; the session call is wired in bolt 008.

## Dependencies

### Requires
- 002-batch-queue-screen
- 003-orgatex-integration/002-batch-detail-and-recipe-from-orgatex
- 004-device-integration/003-scanner-input

### Enables
- 004-recipe-rail

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Scan arrives while on Screen 2 | Ignored (only Screen 1 consumes scans) |

## Out of Scope

- Dyestuff identity scans (UQ-13)
