---
id: 003-tolerance-evaluation
unit: 002-weighing-station
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 006-weighing-station
implemented: true
---

# Story: 003-tolerance-evaluation

**Title**: Tolerance evaluation, target and remaining

## User Story

**As a** weighing operator
**I want** the station to tell me at every moment whether I am under, within or over tolerance and how much is still to weigh
**So that** I can dispense accurately without calculating anything

## Requirements

- FR-12 Tolerance
- FR-10 Target quantity
- FR-11 Remaining quantity

## Acceptance Criteria

- [x] **Given** Yellow RGB 94.0 g ±0.5 g, **Then** 93.4 → UNDER (canConfirm false); 93.5 → WITHIN (true); 94.0 → WITHIN (true); 94.5 → WITHIN (true); 94.6 → OVER (false)
- [x] **Given** net ≥ 0.9 × target and below the band, **Then** zone NEAR (visual cue), canConfirm false
- [x] **Given** net 60.0 g, **Then** remaining 34.0 g; **Given** net 96.4 g, **Then** remaining 0.0 g, surplus 2.4 g, surplusPct 2.6
- [x] **Given** a component without tolerance, **Then** the default rule applies: 0.5% of target, minimum 0.2 g (precision) / 0.010 kg (floor)
- [x] Evaluation returns statusText: "DISPENSE — 34.0 g REMAINING" / "WITHIN TOLERANCE — PRESS OK TO CONFIRM" / "OVER TOLERANCE — SURPLUS +2.4 g"; quantities formatted g 1 dp, kg 3 dp

## UI/UX Impact

Readout colour, "Still to weigh", "Target", tolerance caption, bar band, status line, Confirm enabled state.

## API Dependencies

- Exposed via `GET /api/sessions/{sessionId}/live` (story 010, same bolt)

## Test Expectations

- Workbook Step 22 boundary tests (automated, output saved as STEP-22-tolerance-tests.txt)
- Property test: within ⇔ min ≤ net ≤ max
- Decimal-only arithmetic test (no float)

## Technical Notes

Bounds inclusive. Default tolerance rule configurable (TA-03). Formatting helpers in domain so UI never formats rules.

## Dependencies

### Requires
- None

### Enables
- 004-confirm-component-weighing
- 005-overshoot-handling

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Net weight negative (container removed after tare) | UNDER, remaining = target |
| Scale unavailable | Evaluation with scaleAvailable=false, canConfirm false, statusText "SCALE OFFLINE — CHECK CONNECTION" |

## Out of Scope

- Banded tolerance rules (UQ-06)
