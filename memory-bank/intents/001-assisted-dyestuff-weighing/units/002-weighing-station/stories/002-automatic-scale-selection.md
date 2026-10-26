---
id: 002-automatic-scale-selection
unit: 002-weighing-station
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 006-weighing-station
implemented: true
---

# Story: 002-automatic-scale-selection

**Title**: Automatic scale selection

## User Story

**As a** weighing operator
**I want** the station to pick the right scale for each component automatically
**So that** small quantities are weighed precisely and I never choose the wrong scale

## Requirements

- FR-8 Scale selection

## Acceptance Criteria

- [x] **Given** targets 1240.0 g, 386.0 g, 94.0 g, **Then** the policy returns scale-3kg "3 kg precision"
- [x] **Given** targets 24.000 kg, 9.600 kg, **Then** the policy returns scale-32kg "32 kg floor"
- [x] **Given** 3.000 kg (and 3000.0 g), **Then** precision; **Given** 3.001 kg, **Then** floor
- [x] **Given** the configured threshold is changed to 2 kg, **Then** 2.5 kg selects floor — without code changes

## UI/UX Impact

Scale badge "Scale selected / {label} / automatic" and the rail sub-line "{code} · {scale class}".

## API Dependencies

- None (pure domain policy); used by recipe and session endpoints

## Test Expectations

- Parametrised pytest over all prototype components and boundary values
- Config test for changed threshold

## Technical Notes

Compare in a common unit using Decimal (g → kg ÷ 1000). Threshold and scale definitions from configuration.

## Dependencies

### Requires
- None

### Enables
- 010-activate-component-weighing-context
- 006-weighing-station-ui/005-live-weighing-panel

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Unit other than g/kg | Rejected at recipe mapping (validation error) |

## Out of Scope

- Supervisor manual reselection (TA-04)
