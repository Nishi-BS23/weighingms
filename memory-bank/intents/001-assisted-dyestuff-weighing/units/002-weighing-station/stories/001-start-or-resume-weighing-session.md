---
id: 001-start-or-resume-weighing-session
unit: 002-weighing-station
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 006-weighing-station
implemented: true
---

# Story: 001-start-or-resume-weighing-session

**Title**: Start or resume a weighing session as the signed-in operator

## User Story

**As a** weighing operator
**I want** selecting a batch to start its weighing session under my name, or resume it if it is already in progress
**So that** I never weigh against a batch that is not released and my work is always attributed to me

## Requirements

- FR-2 Batch selection
- FR-19 Operator traceability

## Acceptance Criteria

- [x] **Given** B-24187 is QUEUED, **When** `POST /api/sessions {batchId: "B-24187"}` is called, **Then** a session IN_PROGRESS is created with the recipe snapshot, the signed-in operator, all components PENDING except sequence 1 ACTIVE, and OrgaTEX status is set to WEIGHING
- [x] **Given** a session for B-24187 is IN_PROGRESS with 2 components DONE, **When** the batch is selected again, **Then** the same session is returned with those 2 DONE and the next pending component ACTIVE
- [x] **Given** a batch with status WEIGHED or CANCELLED, **Then** 409 `BATCH_NOT_SELECTABLE` with the reason
- [x] **Given** an unknown batch, **Then** 404 `BATCH_NOT_FOUND`; **Given** OrgaTEX unavailable and no session exists, **Then** 503 `ORGATEX_UNAVAILABLE`
- [x] **When** `GET /api/operators/current` is called, **Then** R. Karim, Shift A is returned by default; **When** `POST /api/operators/sign-in {badgeId}` with a known badge is called, **Then** that operator becomes current and an OPERATOR_CHANGE audit event is stored; unknown badge → 404 `OPERATOR_NOT_FOUND`

## UI/UX Impact

Screen 1 → Screen 2 transition; top bar operator chip and crumb.

## API Dependencies

- Provides `POST /api/sessions`, `GET /api/sessions/{sessionId}`, `GET /api/operators/current`, `POST /api/operators/sign-in`
- Uses `OrgatexPort.get_batch`, `get_recipe`, `set_batch_status` (003)

## Test Expectations

- Domain unit tests: selectable statuses, first active component
- API tests against the dummy: start, resume, not selectable, not found, OrgaTEX down
- Persistence test: session survives app restart (NFR-4)

## Technical Notes

Selectable statuses configurable (TA-02). Recipe snapshot stored with the session (TA-13).

## Dependencies

### Requires
- 003-orgatex-integration/002-batch-detail-and-recipe-from-orgatex
- 007-component-progression

### Enables
- 010-activate-component-weighing-context
- 004-confirm-component-weighing

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Two sessions requested concurrently for the same batch | One session (unique open session per batch) |
| Operator changed mid-session | Records carry the operator at confirm time |

## Out of Scope

- Multi-station locking
