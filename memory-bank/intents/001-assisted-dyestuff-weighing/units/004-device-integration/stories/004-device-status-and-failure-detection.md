---
id: 004-device-status-and-failure-detection
unit: 004-device-integration
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 004-device-integration
implemented: true
---

# Story: 004-device-status-and-failure-detection

**Title**: Device status and failure detection

## User Story

**As a** weighing operator
**I want** to see at a glance whether scales, scanner, printer and OrgaTEX are working
**So that** I know immediately why something is blocked

## Requirements

- FR-24 Device and connection status visibility
- FR-20 Scale, scanner and printer failure

## Acceptance Criteria

- [x] **When** `GET /api/devices/status` is called, **Then** it returns entries for scale-3kg ("SCALE 3 kg"), scale-32kg ("SCALE 32 kg"), scanner, printer, orgatex with state UP/DOWN/DEGRADED and a text (READY, OFFLINE, CAL EXPIRED, LINKED HH:MM)
- [x] **Given** a device is made unavailable in the dummy, **Then** its state is DOWN within 2 s
- [x] **Given** a scale's calibration is expired, **Then** state DEGRADED with text "CAL EXPIRED"
- [x] Training passthroughs: `GET/PUT /api/training/availability`, `POST /api/training/reset`, `POST /api/training/simulate` forward to Dummy control (simulate computes landing from the active component: dispense = target + 0.4·tol, overshoot = target + 4.8·tol, below = 0.8·target)
- [x] Every device failure is logged at WARNING with device and error

## UI/UX Impact

Status strip on all screens; training panel toggles.

## API Dependencies

- Provides WeighingMS `GET /api/devices/status`, `/api/training/*` passthroughs
- Uses Dummy status + control endpoints

## Test Expectations

- API tests toggling each system
- Calibration expired test

## Technical Notes

None

## Dependencies

### Requires
- 001-live-weight-from-selected-scale
- 001-training-substitutes/007-failure-injection-and-reset

### Enables
- 006-weighing-station-ui/001-station-shell-and-chrome
- 006-weighing-station-ui/013-failure-scenario-tests

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Dummy service completely down | All devices DOWN, OrgaTEX DOWN |

## Out of Scope

- Historical device logs UI
