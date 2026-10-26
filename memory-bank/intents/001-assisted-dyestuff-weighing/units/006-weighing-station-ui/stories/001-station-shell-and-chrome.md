---
id: 001-station-shell-and-chrome
unit: 006-weighing-station-ui
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 005-weighing-station-ui
implemented: true
---

# Story: 001-station-shell-and-chrome

**Title**: Station shell, chrome and training panel

## User Story

**As a** weighing operator
**I want** the terminal to look and behave like the station I was shown — device frame, top bar, step indicator and live status strip
**So that** I recognise the station and always see who I am, what batch I am on and whether the devices work

## Requirements

- FR-33 Station chrome
- FR-24 Device status (display)
- FR-19 Operator traceability (display)
- FR-29 Training controls (panel)

## Acceptance Criteria

- [x] Frontend scaffold (Vite + React + TS strict, ESLint, Prettier, Vitest) exists; root `npm run dev` starts dummy service, WeighingMS API and Vite together and prints the UI URL
- [x] Device frame with bezel caption '15" INDUSTRIAL TOUCH TERMINAL'; dark HMI screen in both page themes, using the prototype's design tokens
- [x] Top bar: "WeighingMS" + "STATION 01"; crumb "BATCH {id} · ORDER {order} · MACHINE {machine}" when a batch is active; operator chip "Operator {name} · {shift}" from `GET /api/operators/current`; clicking the chip opens a badge sign-in dialog
- [x] Step indicator "1 · Select batch / 2 · Weigh / 3 · Confirm & print" highlights the current step and only allows going to reachable steps
- [x] Status strip polls `GET /api/devices/status` every 1 s and shows SCALE 3 kg, SCALE 32 kg, SCANNER, PRINTER, ORGATEX with green/amber/red dots and text, plus "EN" and a live clock
- [x] Training panel outside the device frame: Simulate dispense, Simulate overshoot, Reset weighing, Simulate scan (code input), availability toggles for the 5 systems, Reset training data

## UI/UX Impact

Reproduces prototype page controls (as training panel), `.device`, `.topbar`, `.strip` (ui-analysis §2).

## API Dependencies

- Uses `GET /api/operators/current`, `POST /api/operators/sign-in`, `GET /api/devices/status`, `/api/training/*`

## Test Expectations

- Vitest: strip renders states from API fixture; step indicator reachability
- Manual/visual check against prototype

## Technical Notes

Generate API types with openapi-typescript from `/openapi.json`. CSS ported from prototype tokens (not its JS).

## Dependencies

### Requires
- 004-device-integration/004-device-status-and-failure-detection

### Enables
- 002-batch-queue-screen

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Backend unreachable | Banner "Station service unavailable"; strip shows all unknown |

## Out of Scope

- Question pins and meeting notes (TA-20)
