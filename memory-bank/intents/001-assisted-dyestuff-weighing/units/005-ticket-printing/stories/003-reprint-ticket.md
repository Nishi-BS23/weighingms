---
id: 003-reprint-ticket
unit: 005-ticket-printing
intent: 001-assisted-dyestuff-weighing
status: complete
priority: could
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 009-ticket-printing
implemented: true
---

# Story: 003-reprint-ticket

**Title**: Reprint marked as reprint

## User Story

**As a** weighing operator
**I want** a second print to be clearly marked as a reprint
**So that** nobody mistakes a copy for a second batch

## Requirements

- FR-18 Ticket generation (reprint)

## Acceptance Criteria

- [x] **Given** a ticket was printed, **When** print is called again, **Then** the ticket carries `reprint: true` and the text line "*** REPRINT ***"
- [x] A REPRINT audit event is stored

## UI/UX Impact

Preview shows REPRINT after the first print.

## API Dependencies

- Same endpoints as 002

## Test Expectations

- API test: second print → reprint true, audit stored

## Technical Notes

None

## Dependencies

### Requires
- 002-print-ticket

### Enables
- None

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| First print failed (printer down) | Next successful print is the original, not a reprint |

## Out of Scope

- Reprint authorisation
