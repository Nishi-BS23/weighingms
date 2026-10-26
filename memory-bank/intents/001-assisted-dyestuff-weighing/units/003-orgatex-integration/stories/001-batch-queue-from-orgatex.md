---
id: 001-batch-queue-from-orgatex
unit: 003-orgatex-integration
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 003-orgatex-integration
implemented: true
---

# Story: 001-batch-queue-from-orgatex

**Title**: Batch queue from OrgaTEX

## User Story

**As a** weighing operator
**I want** the batch screen to show the queue OrgaTEX released to my station
**So that** I work from OrgaTEX's queue, not a separately maintained list

## Requirements

- FR-1 Batch queue

## Acceptance Criteria

- [x] **When** the UI calls WeighingMS `GET /api/batches`, **Then** WeighingMS calls the OrgaTEX adapter, which calls Dummy OrgaTEX `GET /api/batches`, and returns `{receivedAt, batches[]}` with batchId, orderRef, machineRef, fabricLot ("100% CTN knit · 480 kg"), shadeCode, componentCount, status, selectable
- [x] **Given** QUEUED/WEIGHING, **Then** `selectable: true`; WEIGHED/CANCELLED/unknown → `selectable: false` with `notSelectableReason`
- [x] **Given** Dummy OrgaTEX is unavailable, **Then** 503 `ORGATEX_UNAVAILABLE` with message "OrgaTEX is not reachable. Check the connection and retry."
- [x] Every OrgaTEX call is logged with method, path, status and duration
- [x] The adapter records the last successful OrgaTEX contact time (for the status strip)

## UI/UX Impact

Screen 1 queue table and "Queue received from OrgaTEX at HH:MM".

## API Dependencies

- Provides WeighingMS `GET /api/batches`
- Uses Dummy OrgaTEX `GET /api/batches`

## Test Expectations

- Adapter tests against the dummy app (in-process ASGI transport)
- API test: OrgaTEX unavailable → 503
- Workbook STEP-18 curl evidence

## Technical Notes

`OrgatexPort` defined in `weighingms.application.ports`; implementation `weighingms.infrastructure.orgatex.http_adapter`. Base URL from config.

## Dependencies

### Requires
- 001-training-substitutes/001-dummy-orgatex-batch-queue

### Enables
- 006-weighing-station-ui/002-batch-queue-screen

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| OrgaTEX returns an unknown status | Row shown, not selectable, reason "Status not supported" |

## Out of Scope

- Caching the queue for offline start (TA-13)
