---
id: 009-ticket-preview-and-print
unit: 006-weighing-station-ui
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 010-weighing-station-ui
implemented: true
---

# Story: 009-ticket-preview-and-print

**Title**: Ticket preview and print

## User Story

**As a** weighing operator
**I want** to see the ticket and print it
**So that** the container leaves with its ticket

## Requirements

- FR-32 Screen 3
- FR-18 Ticket generation

## Acceptance Criteria

- [x] Paper-style ticket preview from `GET /api/sessions/{id}/ticket` with all fields, component lines, result line, barcode bars generated from the barcode value and the batch ID
- [x] "Print ticket F1" → `POST /api/sessions/{id}/ticket/print` → "Ticket printed · {ticketId}"; reprints show REPRINT
- [x] Printer unavailable → "Printer not available. Check the printer and try again." with the key still available

## UI/UX Impact

Prototype `.ticket` (L590–613).

## API Dependencies

- Uses `GET /api/sessions/{sessionId}/ticket`, `POST /api/sessions/{sessionId}/ticket/print`

## Test Expectations

- Vitest: ticket rendering from fixture
- Workbook STEP-27 evidence

## Technical Notes

None

## Dependencies

### Requires
- 008-completion-summary-screen
- 005-ticket-printing/002-print-ticket

### Enables
- 012-end-to-end-workflow-test

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Long component names | Short names from API |

## Out of Scope

- Browser print dialog styling beyond a print stylesheet
