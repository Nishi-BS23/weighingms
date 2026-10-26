---
id: 006-dummy-printer
unit: 001-training-substitutes
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 002-training-substitutes
implemented: true
---

# Story: 006-dummy-printer

**Title**: Dummy printer

## User Story

**As a** trainer demonstrating ticket printing
**I want** a dummy printer that accepts and keeps weighing tickets
**So that** printing can be demonstrated and the printed ticket inspected

## Requirements

- FR-28 Dummy Printer
- FR-18 Ticket generation (receiver)

## Acceptance Criteria

- [x] **When** `POST /api/tickets` with a ticket (fields + text lines + barcode value + reprint flag) is called, **Then** it returns 200 `{ticketId, status: "PRINTED", printedAt}`
- [x] **When** `GET /api/tickets` / `GET /api/tickets/{ticketId}` is called, **Then** the stored tickets are returned
- [x] **When** `GET /api/printer/status` is called, **Then** it returns `{available: true}`

## UI/UX Impact

None directly. Supports "Print ticket" on Screen 3.

## API Dependencies

- Provides `POST /api/tickets`, `GET /api/tickets`, `GET /api/tickets/{ticketId}`, `GET /api/printer/status`

## Test Expectations

- pytest: print, list, get, unknown ticket 404

## Technical Notes

None

## Dependencies

### Requires
- 001-dummy-orgatex-batch-queue (skeleton)

### Enables
- 005-ticket-printing/002-print-ticket

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Ticket without lines | 422 |

## Out of Scope

- Printer languages (ZPL etc.)
