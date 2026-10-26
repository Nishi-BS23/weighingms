---
id: 004-dummy-scale-readings-and-tare
unit: 001-training-substitutes
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 002-training-substitutes
implemented: true
---

# Story: 004-dummy-scale-readings-and-tare

**Title**: Dummy scales with simulation and tare

## User Story

**As a** trainer or automated test
**I want** two simulated scales that produce continuous readings, accept tare and can be driven to precise scenarios
**So that** live weighing, tolerance and scale switching can be demonstrated without hardware

## Requirements

- FR-26 Dummy Scale
- FR-9 Live weight (source)
- FR-7 Tare (receiver)

## Acceptance Criteria

- [x] **When** `GET /api/scales` is called, **Then** it lists `scale-3kg` (PRECISION, "3 kg precision", capacity 3 kg, resolution 0.1 g) and `scale-32kg` (FLOOR, "32 kg floor", capacity 32 kg, resolution 0.001 kg)
- [x] **When** `GET /api/scales/scale-3kg/weight` is called, **Then** it returns gross, tare and net as {value, unit}, `stable`, `readAt`, rounded to the scale resolution
- [x] **When** `POST /api/scales/scale-3kg/tare` is called, **Then** tare = current gross and net becomes 0.0
- [x] **Given** control `POST /api/control/scales/scale-3kg/simulate` with profile `dispense` and landing 94.2 g, **Then** net rises fast then eases (step = max(0.4% of landing, 5.5% of remaining) per 34 ms) and settles exactly at 94.2 g; `stable` is true once settled
- [x] **Given** profile `exact` with net 93.4 g, **Then** the next reading is exactly 93.4 g (deterministic for tests)
- [x] **Given** a landing above capacity, **Then** readings are clamped to capacity
- [x] **When** `GET /api/scales/{id}/status` is called, **Then** it returns available, calibrationDue, calibrationValid

## UI/UX Impact

None directly. Drives "Weighed now", the progress bar and the scale strip items.

## API Dependencies

- Provides `GET /api/scales`, `GET /api/scales/{scaleId}/status`, `GET /api/scales/{scaleId}/weight`, `POST /api/scales/{scaleId}/tare`
- Provides control `POST /api/control/scales/{scaleId}/simulate` (profiles: dispense, overshoot, below, exact)

## Test Expectations

- pytest with an injectable clock: dispense profile reaches landing, monotonic, eased
- pytest: exact, tare, rounding, capacity clamp, unknown scale 404

## Technical Notes

Profiles are computed from elapsed time on read (no background thread), using an injectable clock so tests are deterministic.

## Dependencies

### Requires
- 001-dummy-orgatex-batch-queue (skeleton)

### Enables
- 004-device-integration/001-live-weight-from-selected-scale
- 004-device-integration/002-tare-and-re-tare

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Tare while a profile is running | Profile continues relative to the new tare |
| Negative exact weight | 422 |

## Out of Scope

- Serial protocol emulation
