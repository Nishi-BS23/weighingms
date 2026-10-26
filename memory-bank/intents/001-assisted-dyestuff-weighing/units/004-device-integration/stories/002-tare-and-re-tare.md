---
id: 002-tare-and-re-tare
unit: 004-device-integration
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 004-device-integration
implemented: true
---

# Story: 002-tare-and-re-tare

**Title**: Tare and re-tare

## User Story

**As a** weighing operator
**I want** the scale to be zeroed with the empty container when I start a component and whenever I press Re-tare
**So that** "Weighed now" shows only the dyestuff I dispensed

## Requirements

- FR-7 Tare

## Acceptance Criteria

- [x] `ScalePort.tare(scaleId)` calls Dummy Scale `POST /api/scales/{id}/tare` and returns the post-tare reading with net 0
- [x] **Given** the scale is unavailable, **Then** `ScaleUnavailable` is raised and logged

## UI/UX Impact

Re-tare (F2) and component activation reset "Weighed now" to 0.0 g / 0.000 kg.

## API Dependencies

- Uses Dummy Scale `POST /api/scales/{scaleId}/tare`

## Test Expectations

- Adapter tests: tare → net 0; unavailable

## Technical Notes

None

## Dependencies

### Requires
- 001-live-weight-from-selected-scale

### Enables
- 002-weighing-station/010-activate-component-weighing-context

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Tare during dispense simulation | Net restarts from 0 relative to new tare |

## Out of Scope

- Weighing the empty container to capture tare (tare_source WEIGHED)
