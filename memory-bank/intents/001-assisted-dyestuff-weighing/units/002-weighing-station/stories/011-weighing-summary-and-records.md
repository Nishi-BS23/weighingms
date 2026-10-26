---
id: 011-weighing-summary-and-records
unit: 002-weighing-station
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 007-weighing-station
implemented: true
---

# Story: 011-weighing-summary-and-records

**Title**: Weighing summary and record review

## User Story

**As a** operator or lab/QA reviewer
**I want** a summary of the completed batch and access to its weighing records
**So that** I can see what was required, what was weighed and whether it was accepted

## Requirements

- FR-23 Summary and record review
- FR-16 Batch completion (summary)

## Acceptance Criteria

- [x] **When** `GET /api/sessions/{id}/summary` is called for a completed session, **Then** it returns components weighed "5 of 5", allWithinTolerance (true/false + overridden count), totalDispensed in kg (3 dp; e.g. 35.322 kg for the prototype actuals), elapsed ("6 min 41 s" format), operator name, write-back status + time, and per-component target/actual/unit/result
- [x] **When** `GET /api/weighing-records?batchId=B-24187` is called, **Then** all records with the full traceability set are returned
- [x] **Given** an in-progress session, **Then** the summary reflects done components only and `completed: false`

## UI/UX Impact

Screen 3 summary rows and per-component results table.

## API Dependencies

- Provides `GET /api/sessions/{sessionId}/summary`, `GET /api/weighing-records`

## Test Expectations

- API tests: totals with Decimal (no float drift), elapsed formatting, records query

## Technical Notes

None

## Dependencies

### Requires
- 009-batch-completion

### Enables
- 006-weighing-station-ui/008-completion-summary-screen
- 005-ticket-printing/001-compose-weighing-ticket

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Mixed units | Total converted to kg exactly (g ÷ 1000) |

## Out of Scope

- Period reports (Brief BR-23)
