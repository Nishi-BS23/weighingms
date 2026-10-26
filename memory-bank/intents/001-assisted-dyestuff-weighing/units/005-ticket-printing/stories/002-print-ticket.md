---
id: 002-print-ticket
unit: 005-ticket-printing
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 009-ticket-printing
implemented: true
---

# Story: 002-print-ticket

**Title**: Print the ticket on the printer

## User Story

**As a** weighing operator
**I want** to print the ticket with one key
**So that** it can travel with the container

## Requirements

- FR-18 Ticket generation
- FR-20 Printer failure

## Acceptance Criteria

- [x] **When** `POST /api/sessions/{id}/ticket/print` is called, **Then** the printer adapter sends `POST /api/tickets` to the Dummy Printer and WeighingMS returns `{ticketId, printedAt, reprint}`
- [x] The print is recorded in WeighingMS print history
- [x] **Given** the printer is unavailable, **Then** 503 `PRINTER_UNAVAILABLE` with message "Printer not available. Check the printer and try again."; the session stays COMPLETED

## UI/UX Impact

Print ticket (F1) on Screen 3, "Ticket printed · {ticketId}" confirmation.

## API Dependencies

- Provides `POST /api/sessions/{sessionId}/ticket/print`
- Uses Dummy Printer `POST /api/tickets`

## Test Expectations

- API tests: print stored in dummy; printer down → 503; retry succeeds

## Technical Notes

None

## Dependencies

### Requires
- 001-compose-weighing-ticket
- 001-training-substitutes/006-dummy-printer

### Enables
- 003-reprint-ticket

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Double press | Second print is a reprint |

## Out of Scope

- Automatic printing on completion (TA-14)
