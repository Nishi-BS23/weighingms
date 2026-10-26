---
id: 006-weighing-actions
unit: 006-weighing-station-ui
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 008-weighing-station-ui
implemented: true
---

# Story: 006-weighing-actions

**Title**: Weighing actions: confirm, re-tare, quit, override

## User Story

**As a** weighing operator
**I want** large keys to confirm, re-tare, quit or call a supervisor
**So that** I can act quickly with gloves on

## Requirements

- FR-31 Screen 2
- FR-13 Confirmation
- FR-7 Tare (re-tare)
- FR-22 Quit
- FR-21 Supervisor override

## Acceptance Criteria

- [x] Keys ≥ 62 px high: "OK · Confirm F1" (green, enabled only when `canConfirm`), "Re-tare F2", "Quit F4", "Supervisor override" (right-aligned)
- [x] Confirm → `POST /api/sessions/{id}/confirm`; on success the rail shows ✓ actual and the next component activates; on 409 the message is shown
- [x] Re-tare → `POST /api/sessions/{id}/retare`; Weighed now returns to 0
- [x] Quit → confirmation dialog "Abandon {component}? Nothing will be recorded for it." → `POST /api/sessions/{id}/quit` → Screen 1
- [x] Supervisor override → status "OVERRIDE REQUESTED — AWAITING SUPERVISOR" and dialog (PIN masked, reason) → `POST /api/sessions/{id}/override`; errors shown in the dialog
- [x] After the last confirmation the UI moves to Screen 3

## UI/UX Impact

Prototype `.actions` keys (L556–561) and new dialogs (quit, override).

## API Dependencies

- Uses `POST /api/sessions/{sessionId}/confirm`, `/retare`, `/quit`, `/override`

## Test Expectations

- Vitest: Confirm disabled unless canConfirm; dialogs submit correct payloads
- Playwright (in 012/013): confirm flow, quit, override

## Technical Notes

None

## Dependencies

### Requires
- 005-live-weighing-panel
- 002-weighing-station/004-confirm-component-weighing
- 002-weighing-station/006-supervisor-override
- 002-weighing-station/008-quit-and-abandon

### Enables
- 008-completion-summary-screen

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Confirm pressed as weight leaves band | API 409 OUT_OF_TOLERANCE shown; component stays active |

## Out of Scope

- Physical 21-key terminal mapping beyond F1–F4
