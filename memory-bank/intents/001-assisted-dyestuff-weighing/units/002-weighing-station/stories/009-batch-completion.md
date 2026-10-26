---
id: 009-batch-completion
unit: 002-weighing-station
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 007-weighing-station
implemented: true
---

# Story: 009-batch-completion

**Title**: Batch completion and write-back trigger

## User Story

**As a** weighing operator
**I want** the batch to complete automatically when the last component is confirmed, with consumption sent to OrgaTEX
**So that** OrgaTEX gets actual consumption without re-keying and I can move on

## Requirements

- FR-16 Batch completion
- FR-17 OrgaTEX write-back (trigger)

## Acceptance Criteria

- [x] **Given** 4 of 5 DONE, **When** `POST /api/sessions/{id}/complete` is called, **Then** 409 `BATCH_INCOMPLETE`
- [x] **When** the 5th component is confirmed, **Then** the session becomes COMPLETED with completedAt, and write-back is attempted via `OrgatexPort.post_consumption` with idempotency key = sessionId, then status WEIGHED
- [x] **Given** write-back succeeds, **Then** syncStatus SYNCED and syncedAt set; **Given** OrgaTEX is unavailable, **Then** syncStatus PENDING, completion still succeeds
- [x] **When** `POST /api/sessions/{id}/sync` is called after OrgaTEX returns, **Then** posting happens and syncStatus becomes SYNCED; repeated calls never create a second posting

## UI/UX Impact

Transition to Screen 3; "Written to OrgaTEX · CONFIRMED HH:MM:SS" or "PENDING — Retry".

## API Dependencies

- Provides `POST /api/sessions/{sessionId}/complete`, `POST /api/sessions/{sessionId}/sync`
- Uses `OrgatexPort.post_consumption`, `set_batch_status` (003)

## Test Expectations

- API tests against the dummy: complete → stored consumption (Workbook Step 26 evidence)
- OrgaTEX down → PENDING → retry → exactly one posting
- Incomplete → BATCH_INCOMPLETE

## Technical Notes

None

## Dependencies

### Requires
- 004-confirm-component-weighing
- 007-component-progression
- 003-orgatex-integration/003-consumption-write-back

### Enables
- 011-weighing-summary-and-records
- 005-ticket-printing/001-compose-weighing-ticket

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Ambiguous failure (timeout after OrgaTEX stored it) | Retry with same key returns duplicate=true → SYNCED, no double post |

## Out of Scope

- Background automatic retry scheduler (retry is operator-triggered in this build)
