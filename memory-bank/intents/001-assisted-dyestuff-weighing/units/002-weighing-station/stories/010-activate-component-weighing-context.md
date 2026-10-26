---
id: 010-activate-component-weighing-context
unit: 002-weighing-station
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 006-weighing-station
implemented: true
---

# Story: 010-activate-component-weighing-context

**Title**: Activate a component with its weighing context

## User Story

**As a** weighing operator
**I want** the active component to come with everything I need — scale, lot, container, tare, target and tolerance — and the scale ready at zero
**So that** I can start dispensing immediately and the record captures the right context

## Requirements

- FR-5 Dyestuff lot
- FR-6 Container
- FR-7 Tare (context)
- FR-10 Target quantity
- FR-8 Scale selection (applied)

## Acceptance Criteria

- [x] **When** `POST /api/sessions/{id}/components/{componentId}/activate` is called for Yellow RGB, **Then** the context returns name, code DYE-4471, lot 2026-0387, container C-12, tare 214 g, scale scale-3kg "3 kg precision", target 94.0 g, band 93.5–94.5 g, display max 125 g
- [x] **Then** the selected scale is tared (`ScalePort.tare`) so net starts at 0
- [x] **Given** Sodium Sulphate, **Then** container D-03, tare 1.850 kg, scale scale-32kg, unit kg
- [x] **When** `GET /api/sessions/{id}/live` is called, **Then** it returns the live evaluation for the active component (net, unit, zone, remaining, surplus, surplusPct, canConfirm, scaleAvailable, statusText, allowedActions)
- [x] **When** `POST /api/sessions/{id}/retare` is called, **Then** the scale is tared again and net returns to 0

## UI/UX Impact

Weigh header meta line, scale badge, readout, bar (display max), tolerance caption.

## API Dependencies

- Provides `POST /api/sessions/{sessionId}/components/{componentId}/activate`, `GET /api/sessions/{sessionId}/live`, `POST /api/sessions/{sessionId}/retare`
- Uses `ScalePort.tare`, `read_weight`, `status` (004)

## Test Expectations

- API tests for Yellow RGB and Sodium Sulphate contexts (Workbook Step 21 scale switch)
- Live endpoint latency < 50 ms locally

## Technical Notes

Container master seeded in WeighingMS (TA-08). Display max = target × 4/3 rounded up to a tidy value (ui-analysis R12).

## Dependencies

### Requires
- 002-automatic-scale-selection
- 003-tolerance-evaluation
- 004-device-integration/002-tare-and-re-tare

### Enables
- 004-confirm-component-weighing
- 006-weighing-station-ui/005-live-weighing-panel

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Scale unavailable on activation | Context returned; live shows scaleAvailable=false; tare retried on Re-tare |

## Out of Scope

- Container scanning
