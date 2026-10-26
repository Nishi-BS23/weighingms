---
id: 008-quit-and-abandon
unit: 002-weighing-station
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 007-weighing-station
implemented: true
---

# Story: 008-quit-and-abandon

**Title**: Quit and abandon safely

## User Story

**As a** weighing operator
**I want** to abandon the component I am weighing and leave the batch safely
**So that** an interrupted weighing never produces a false record and I can resume later

## Requirements

- FR-22 Quit

## Acceptance Criteria

- [x] **When** `POST /api/sessions/{id}/quit` is called, **Then** no WeighingRecord is created for the active component, an ABANDON audit event (component, net weight at quit, operator) is stored, the component returns to PENDING and the session stays IN_PROGRESS
- [x] **Given** 2 components were DONE, **When** the batch is selected again, **Then** they are still DONE (resume)
- [x] **Given** the session is COMPLETED, **Then** 409 `SESSION_COMPLETED`

## UI/UX Impact

Quit (F4) with a confirmation dialog on Screen 2; returns to Screen 1.

## API Dependencies

- Provides `POST /api/sessions/{sessionId}/quit`

## Test Expectations

- API tests: quit leaves no record, audit stored, resume preserves DONE
- Workbook Step 30 "Quit → safe exit"

## Technical Notes

None

## Dependencies

### Requires
- 001-start-or-resume-weighing-session

### Enables
- 006-weighing-station-ui/006-weighing-actions

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Quit with weight within tolerance | Still no record (operator chose to quit) |

## Out of Scope

- Cancelling the batch in OrgaTEX
