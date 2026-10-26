---
id: 006-supervisor-override
unit: 002-weighing-station
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 007-weighing-station
implemented: true
---

# Story: 006-supervisor-override

**Title**: Supervisor override

## User Story

**As a** dyehouse supervisor
**I want** to authorise confirmation of an out-of-tolerance weighing with my PIN and a reason
**So that** exceptions are possible but always attributable and justified

## Requirements

- FR-21 Supervisor override

## Acceptance Criteria

- [x] **Given** the weight is outside tolerance and > 0, **When** `POST /api/sessions/{id}/override {supervisorPin, reason}` with a valid supervisor PIN and non-empty reason is called, **Then** a WeighingRecord with result OVERRIDDEN, an Override (supervisor, reason, time) and an OVERRIDE audit event are stored and the component becomes DONE
- [x] **Given** a wrong PIN, **Then** 403 `OVERRIDE_NOT_AUTHORISED`; **Given** an empty reason, **Then** 422; nothing is stored
- [x] **Given** the weight is within tolerance, **Then** 409 `OVERRIDE_NOT_NEEDED`
- [x] **Given** an operator (non-supervisor) PIN, **Then** 403
- [x] The PIN is compared against a salted hash and never logged

## UI/UX Impact

"Supervisor override" key and dialog (PIN, reason); status line "OVERRIDE REQUESTED — AWAITING SUPERVISOR" while open.

## API Dependencies

- Provides `POST /api/sessions/{sessionId}/override`

## Test Expectations

- Domain tests: policy (outside tolerance, > 0)
- API tests: valid, wrong PIN, empty reason, not needed, log contains no PIN

## Technical Notes

Seeded supervisor: S. Ahmed, badge SV-2001, training PIN documented in README (training only). Step 24 may narrow when override is allowed.

## Dependencies

### Requires
- 003-tolerance-evaluation
- 005-overshoot-handling

### Enables
- 006-weighing-station-ui/006-weighing-actions

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Scale unavailable during override | 409 `SCALE_UNAVAILABLE` (actual weight unknown) |

## Out of Scope

- Remote approval workflow (UQ-08)
