---
id: 010-operator-facing-failure-messages
unit: 006-weighing-station-ui
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 010-weighing-station-ui
implemented: true
---

# Story: 010-operator-facing-failure-messages

**Title**: Operator-facing failure messages

## User Story

**As a** weighing operator with limited computer experience
**I want** every failure explained in plain words with what I can do
**So that** I am never stuck or confused

## Requirements

- FR-20 Scale, scanner and printer failure
- FR-1 (OrgaTEX unavailable)
- NFR-10 Plain language

## Acceptance Criteria

- [x] API error codes map to plain messages (ORGATEX_UNAVAILABLE, SCALE_UNAVAILABLE, SCALE_CALIBRATION_EXPIRED, PRINTER_UNAVAILABLE, SCANNER_UNAVAILABLE, OUT_OF_TOLERANCE, BATCH_NOT_SELECTABLE, BATCH_INCOMPLETE, OVERRIDE_NOT_AUTHORISED, network failure)
- [x] No codes, stack traces or JSON shown to the operator; colour is never the only signal
- [x] Error boundary per screen shows "Something went wrong on this screen" with a Back to batch queue action

## UI/UX Impact

Message areas on all three screens; banner for backend unreachable.

## API Dependencies

- Consumes the standard error body `{error: {code, message, details}}`

## Test Expectations

- Vitest: mapping table complete for all codes

## Technical Notes

None

## Dependencies

### Requires
- 001-station-shell-and-chrome

### Enables
- 013-failure-scenario-tests

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Unknown error code | Generic plain message + code logged to console only in dev |

## Out of Scope

- Localisation
