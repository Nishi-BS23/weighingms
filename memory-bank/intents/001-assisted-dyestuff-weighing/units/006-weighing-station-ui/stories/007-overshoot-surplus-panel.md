---
id: 007-overshoot-surplus-panel
unit: 006-weighing-station-ui
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 008-weighing-station-ui
implemented: true
---

# Story: 007-overshoot-surplus-panel

**Title**: Overshoot surplus panel

## User Story

**As a** weighing operator
**I want** a clear red panel when I overshoot, telling me the surplus and what to do
**So that** I handle the over-dose by the agreed rule

## Requirements

- FR-31 Screen 2
- FR-14 Overshoot

## Acceptance Criteria

- [x] When zone is OVER, the surplus panel appears: "Surplus +{surplus} {unit} (+{pct}%) — over tolerance" with the guidance and allowed actions from the API (Step 24 decision)
- [x] Panel hides when the weight returns into or below the band
- [x] Status line "OVER TOLERANCE — SURPLUS +{x} {u}" in red

## UI/UX Impact

Prototype `.surplus` (L544–554) — recalculation table shown only if Step 24 selects compensation.

## API Dependencies

- Uses `GET /api/sessions/{sessionId}/live` (`surplus`, `surplusPct`, `allowedActions`, `guidance`)

## Test Expectations

- Vitest: panel visibility by zone; text formatting
- Workbook STEP-24-overshoot-ui evidence

## Technical Notes

None

## Dependencies

### Requires
- 005-live-weighing-panel
- 002-weighing-station/005-overshoot-handling

### Enables
- None

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Overshoot then remove excess | Panel disappears, Confirm enabled when within |

## Out of Scope

- Editing other components' targets
