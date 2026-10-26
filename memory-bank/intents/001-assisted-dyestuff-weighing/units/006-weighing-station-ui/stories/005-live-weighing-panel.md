---
id: 005-live-weighing-panel
unit: 006-weighing-station-ui
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 008-weighing-station-ui
implemented: true
---

# Story: 005-live-weighing-panel

**Title**: Live weighing panel

## User Story

**As a** weighing operator
**I want** a big live weight, what is still to weigh, the target, a progress bar with the tolerance band and a plain status line
**So that** I can dispense to target without calculating

## Requirements

- FR-31 Screen 2
- FR-4
- FR-5
- FR-6
- FR-7
- FR-8
- FR-9
- FR-10
- FR-11
- FR-12

## Acceptance Criteria

- [x] Header: component name; meta "{code} · LOT {lot} · CONTAINER {container} · TARE {tare} {unit}"; scale badge "Scale selected / {label} / automatic"
- [x] Readout cells Weighed now (≥ 52 px, colour by zone), Still to weigh, Target — values and units from the live evaluation (`GET /api/sessions/{id}/live` polled every ~120 ms); g 1 dp, kg 3 dp
- [x] Progress bar: fill width = net / displayMax, band from min to max, target line; fill colour by zone; `role=progressbar` with aria values
- [x] Caption "0 · TOLERANCE ±{tol} {unit} ({min} – {max}) · {displayMax} {unit}"; status line text and colour from the evaluation
- [x] Switching from Yellow RGB to Sodium Sulphate changes the badge to "32 kg floor" and units to kg (Workbook Step 21)
- [x] The UI computes only bar geometry; zone, remaining, canConfirm, statusText come from the API

## UI/UX Impact

Prototype `.weigh-head`, `.readout`, `.bar-block`, `.status-line` (L503–542).

## API Dependencies

- Uses `GET /api/sessions/{sessionId}/live`

## Test Expectations

- Vitest: renders each zone from fixtures; geometry maths
- Playwright (in 012): tolerance boundary values visible (Workbook Step 22 UI)

## Technical Notes

None

## Dependencies

### Requires
- 004-recipe-rail

### Enables
- 006-weighing-actions
- 007-overshoot-surplus-panel

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Scale offline | Readout "—", status "SCALE OFFLINE — CHECK CONNECTION", bar frozen |

## Out of Scope

- Sound signals
