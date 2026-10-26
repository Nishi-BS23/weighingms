---
id: 005-overshoot-handling
unit: 002-weighing-station
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 007-weighing-station
implemented: true
---

# Story: 005-overshoot-handling

**Title**: Overshoot detection and defined response

## User Story

**As a** weighing operator
**I want** the station to detect an over-dose, show me the surplus and tell me exactly what I may do next
**So that** an over-dosed component never reaches production silently and the response is the agreed rule, not an ad-hoc one

## Requirements

- FR-14 Overshoot

## Acceptance Criteria

- [x] **Given** Yellow RGB net 96.4 g, **Then** zone OVER, surplus 2.4 g, surplusPct 2.6, canConfirm false, statusText "OVER TOLERANCE — SURPLUS +2.4 g"
- [x] **Given** the overshoot rule recorded at Workbook Step 24 (`STEP-24-overshoot-decision.md`), **Then** the evaluation exposes the allowed recovery actions for the operator exactly as decided
- [x] **Given** the weight is brought back into the band (excess removed), **Then** zone WITHIN and confirmation is allowed again
- [x] No automatic recalculation of other components happens unless the Step 24 decision explicitly selects it

## UI/UX Impact

Surplus panel on Screen 2 (heading "Surplus +x (+y%) — over tolerance" and the decided guidance).

## API Dependencies

- Exposed via `GET /api/sessions/{sessionId}/live` (`surplus`, `surplusPct`, `allowedActions`)

## Test Expectations

- Domain tests for surplus maths and allowed actions
- Workbook STEP-24-overshoot-test evidence

## Technical Notes

Decision gate: implement only after the Step 24 decision (options → impact → human decision).

## Dependencies

### Requires
- 003-tolerance-evaluation

### Enables
- 006-supervisor-override
- 006-weighing-station-ui/007-overshoot-surplus-panel

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Overshoot beyond scale capacity | Reading clamped; still OVER |

## Out of Scope

- Proportional recalculation of remaining components unless chosen at Step 24
