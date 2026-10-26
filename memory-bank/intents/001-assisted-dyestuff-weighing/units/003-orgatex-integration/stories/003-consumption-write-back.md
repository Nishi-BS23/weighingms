---
id: 003-consumption-write-back
unit: 003-orgatex-integration
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 003-orgatex-integration
implemented: true
---

# Story: 003-consumption-write-back

**Title**: Status and consumption write-back

## User Story

**As a** store and production planning (via OrgaTEX)
**I want** WeighingMS to report batch status and post actual consumption per component exactly once
**So that** OrgaTEX can reconcile actual against theoretical consumption

## Requirements

- FR-17 OrgaTEX write-back

## Acceptance Criteria

- [x] `OrgatexPort.set_batch_status(batchId, status)` sends `PATCH /api/batches/{id}/status` to the dummy
- [x] `OrgatexPort.post_consumption(payload)` sends `POST /api/batches/{id}/consumption` with idempotencyKey = sessionId and returns `{consumptionId, receivedAt, duplicate}`
- [x] **Given** the same payload is posted twice, **Then** the dummy holds one posting and the second call returns `duplicate: true`
- [x] **Given** the dummy is unavailable or times out, **Then** the adapter raises `OrgatexUnavailable` (no partial state in WeighingMS)
- [x] Request and response are logged (without personal data beyond operator ID)

## UI/UX Impact

None directly; Screen 3 shows the result via the session summary.

## API Dependencies

- Uses Dummy OrgaTEX `PATCH /api/batches/{batchId}/status`, `POST /api/batches/{batchId}/consumption`

## Test Expectations

- Adapter tests against the dummy: status, post, duplicate, unavailable

## Technical Notes

None

## Dependencies

### Requires
- 001-training-substitutes/003-dummy-orgatex-consumption-and-status

### Enables
- 002-weighing-station/009-batch-completion

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| OrgaTEX responds 5xx after storing | Retry with same key → duplicate=true treated as success |

## Out of Scope

- When to post (decided by weighing-station completion)
