---
id: 002-batch-queue-screen
unit: 006-weighing-station-ui
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 005-weighing-station-ui
implemented: true
---

# Story: 002-batch-queue-screen

**Title**: Batch queue screen

## User Story

**As a** weighing operator
**I want** to see the batches waiting for me with their order, machine, fabric, shade, component count and status
**So that** I can pick the right batch

## Requirements

- FR-30 Screen 1
- FR-1 Batch queue

## Acceptance Criteria

- [x] Screen 1 obtains its rows from `GET /api/batches` — no `const batches = [...]` in UI code
- [x] Scan prompt with animated beam: "Scan a batch card to begin" / "Or touch a row below. Queue received from OrgaTEX at HH:MM." (beam animation off for reduced motion)
- [x] Table columns Batch, Order, Machine, Fabric / lot, Shade, Comp., Status; status tags QUEUED neutral, WEIGHING amber
- [x] Non-selectable rows are dimmed and show their reason on touch
- [x] OrgaTEX unavailable → message with Retry button; no stale rows

## UI/UX Impact

Prototype View 1 (L448–487).

## API Dependencies

- Uses WeighingMS `GET /api/batches`

## Test Expectations

- Vitest: renders rows from mocked API module; error state
- Workbook STEP-19 network evidence (Playwright request log)

## Technical Notes

None

## Dependencies

### Requires
- 001-station-shell-and-chrome
- 003-orgatex-integration/001-batch-queue-from-orgatex

### Enables
- 003-select-batch-by-touch-or-scan

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Empty queue | "No batches released to this station" |

## Out of Scope

- Sorting/filtering the queue
