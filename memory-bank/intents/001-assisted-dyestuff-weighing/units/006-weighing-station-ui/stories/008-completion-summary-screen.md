---
id: 008-completion-summary-screen
unit: 006-weighing-station-ui
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 010-weighing-station-ui
implemented: true
---

# Story: 008-completion-summary-screen

**Title**: Completion summary and write-back status

## User Story

**As a** weighing operator
**I want** a completion screen showing the batch summary, every component's result and whether OrgaTEX received the consumption
**So that** I know the batch is done and recorded

## Requirements

- FR-32 Screen 3
- FR-16 Batch completion
- FR-17 OrgaTEX write-back (display)
- FR-23 Summary

## Acceptance Criteria

- [x] Heading "Batch {id} weighed" (green); summary rows Components weighed, All within tolerance, Total dispensed, Elapsed, Operator, Written to OrgaTEX — from `GET /api/sessions/{id}/summary`
- [x] Per-component results table: component, target, actual, unit, result
- [x] Write-back CONFIRMED shows "CONFIRMED HH:MM:SS" (green); PENDING shows amber "PENDING" with a Retry button calling `POST /api/sessions/{id}/sync`
- [x] Note "Actual consumption posted against the batch. Container released for transport to {machine}." (or pending variant)
- [x] Next batch (F3) → Screen 1 with refreshed queue

## UI/UX Impact

Prototype View 3 left column (L569–587) + per-component results (PDF §6 Step 9).

## API Dependencies

- Uses `GET /api/sessions/{sessionId}/summary`, `POST /api/sessions/{sessionId}/sync`

## Test Expectations

- Vitest: confirmed/pending variants
- Workbook STEP-26-ui evidence (Playwright screenshot)

## Technical Notes

None

## Dependencies

### Requires
- 006-weighing-actions
- 002-weighing-station/009-batch-completion
- 002-weighing-station/011-weighing-summary-and-records

### Enables
- 009-ticket-preview-and-print

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Retry while OrgaTEX still down | Still PENDING with message |

## Out of Scope

- Historical batch browser
