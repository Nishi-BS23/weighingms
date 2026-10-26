---
id: 007-component-progression
unit: 002-weighing-station
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 006-weighing-station
implemented: true
---

# Story: 007-component-progression

**Title**: Component progression

## User Story

**As a** weighing operator
**I want** the station to move me through the recipe component by component and let me pick another pending component when needed
**So that** I always know what to weigh next and nothing is weighed twice or skipped

## Requirements

- FR-15 Component progression

## Acceptance Criteria

- [x] **Given** a fresh session, **Then** Blue RSPL is ACTIVE and the other four PENDING
- [x] **When** the active component is confirmed, **Then** it becomes DONE and the next PENDING component in sequence becomes ACTIVE: Blue RSPL → Red RB → Yellow RGB → Sodium Sulphate → Soda Ash
- [x] **When** a PENDING component is activated, **Then** it becomes ACTIVE and the previously ACTIVE (unconfirmed) one returns to PENDING
- [x] **When** a DONE component is activated, **Then** 409 `COMPONENT_ALREADY_DONE`
- [x] **Then** progress reports `{done, total}` (e.g. "2 of 5")

## UI/UX Impact

Recipe rail states (done ✓ actual / WEIGHING / PENDING) and "n of 5 components weighed".

## API Dependencies

- Exposed via session endpoints (`GET /api/sessions/{id}`, activate, confirm)

## Test Expectations

- Domain tests for all transitions; Workbook Step 23 five-component sequence

## Technical Notes

None

## Dependencies

### Requires
- None

### Enables
- 009-batch-completion
- 001-start-or-resume-weighing-session

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Last pending confirmed | No ACTIVE component; session ready to complete |

## Out of Scope

- Parallel weighing of several components
