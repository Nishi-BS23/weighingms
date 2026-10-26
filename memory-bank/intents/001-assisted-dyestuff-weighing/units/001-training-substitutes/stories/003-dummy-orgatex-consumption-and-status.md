---
id: 003-dummy-orgatex-consumption-and-status
unit: 001-training-substitutes
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 001-training-substitutes
implemented: true
---

# Story: 003-dummy-orgatex-consumption-and-status

**Title**: Dummy OrgaTEX consumption and status write-back

## User Story

**As a** trainer demonstrating the OrgaTEX write-back
**I want** the Dummy OrgaTEX to accept batch status updates and consumption postings and show what it stored
**So that** the write-back can be proven (request, 200 OK response, stored record)

## Requirements

- FR-25 Dummy OrgaTEX
- FR-17 OrgaTEX write-back (receiver)

## Acceptance Criteria

- [x] **Given** a valid payload, **When** `POST /api/batches/B-24187/consumption` is called, **Then** it returns 200 with consumptionId, receivedAt, `duplicate: false` and stores the posting
- [x] **Given** the same idempotencyKey is posted again, **Then** it returns 200 with the original consumptionId and `duplicate: true`, and only one posting is stored
- [x] **When** `GET /api/batches/B-24187/consumption` is called, **Then** the stored postings are returned with all lines
- [x] **When** `PATCH /api/batches/B-24187/status` with `{"status": "WEIGHING"}` or `WEIGHED` is called, **Then** the batch status changes and appears in `GET /api/batches`
- [x] **Given** an invalid status value, **Then** 422

## UI/UX Impact

None directly. The stored record is evidence for Workbook Step 26; Screen 3 shows "Written to OrgaTEX · CONFIRMED".

## API Dependencies

- Provides `POST /api/batches/{batchId}/consumption`, `GET /api/batches/{batchId}/consumption`, `PATCH /api/batches/{batchId}/status`

## Test Expectations

- pytest: post, duplicate post, get postings, status change, invalid status

## Technical Notes

Postings and statuses persisted in `data/dummy.db` (SQLite) so they survive restarts until reset.

## Dependencies

### Requires
- 001-dummy-orgatex-batch-queue

### Enables
- 003-orgatex-integration/003-consumption-write-back

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Posting for unknown batch | 404 |
| Posting with zero lines | 422 |

## Out of Scope

- Validation that consumption equals recipe (OrgaTEX-side business rules are unknown)
