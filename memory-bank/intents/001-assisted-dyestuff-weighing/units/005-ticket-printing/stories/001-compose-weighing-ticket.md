---
id: 001-compose-weighing-ticket
unit: 005-ticket-printing
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 009-ticket-printing
implemented: true
---

# Story: 001-compose-weighing-ticket

**Title**: Compose the weighing ticket

## User Story

**As a** worker carrying the container to the dyeing machine
**I want** a ticket listing the batch and every component's target and actual
**So that** the machine operator receives a physical record with the container

## Requirements

- FR-18 Ticket generation

## Acceptance Criteria

- [x] **When** `GET /api/sessions/{id}/ticket` is called for a completed session, **Then** it returns header "FCI DYEING — WEIGHING TICKET", batch, order, machine, shade, date (YYYY-MM-DD HH:MM), operator, lines (shortName, target, actual, unit) e.g. "Blue RSPL 1240.0 1241.5 g", result line "ALL WITHIN TOLERANCE" or "{n} OVERRIDDEN", barcodeValue "B-24187", reprint false
- [x] **Given** the session is not completed, **Then** 409 `SESSION_NOT_COMPLETED`
- [x] Header and short names come from configuration

## UI/UX Impact

Ticket preview on Screen 3.

## API Dependencies

- Provides `GET /api/sessions/{sessionId}/ticket`

## Test Expectations

- Unit test: composition for the prototype actuals matches the prototype ticket text
- API test: not completed → 409

## Technical Notes

None

## Dependencies

### Requires
- 002-weighing-station/011-weighing-summary-and-records

### Enables
- 002-print-ticket
- 006-weighing-station-ui/009-ticket-preview-and-print

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Overridden component | Result line shows "1 OVERRIDDEN"; line marked "*" |

## Out of Scope

- Graphical label layout
