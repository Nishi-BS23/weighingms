---
id: 001-live-weight-from-selected-scale
unit: 004-device-integration
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 004-device-integration
implemented: true
---

# Story: 001-live-weight-from-selected-scale

**Title**: Live weight from the selected scale

## User Story

**As a** weighing operator
**I want** to see the weight on the selected scale as I dispense
**So that** I can stop at the target

## Requirements

- FR-9 Live weight

## Acceptance Criteria

- [x] `ScalePort.read_weight(scaleId)` returns gross, tare, net as Decimal with unit, stable flag and readAt from the Dummy Scale `GET /api/scales/{id}/weight`
- [x] **Given** the dummy scale is unavailable (503/timeout) or the reading is older than 2 s, **Then** the port returns `ScaleUnavailable` — never a weight of 0
- [x] `ScalePort.list_scales()` and `status(scaleId)` return capacity, resolution, availability and calibration validity
- [x] Added latency per reading < 50 ms on localhost

## UI/UX Impact

"Weighed now" readout (through the session live endpoint).

## API Dependencies

- Uses Dummy Scale `GET /api/scales`, `GET /api/scales/{scaleId}/status`, `GET /api/scales/{scaleId}/weight`

## Test Expectations

- Adapter tests against the dummy (exact profile values)
- Unavailable and stale-reading tests
- Latency micro-benchmark

## Technical Notes

`ScalePort` in `weighingms.application.ports`; HTTP implementation in `weighingms.infrastructure.devices.scale_adapter`.

## Dependencies

### Requires
- 001-training-substitutes/004-dummy-scale-readings-and-tare

### Enables
- 002-weighing-station/010-activate-component-weighing-context

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Reading with unit different from component unit | Converted exactly (g ↔ kg) |

## Out of Scope

- Serial streaming implementation
