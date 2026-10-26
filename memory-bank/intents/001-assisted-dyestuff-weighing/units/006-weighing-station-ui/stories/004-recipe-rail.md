---
id: 004-recipe-rail
unit: 006-weighing-station-ui
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 008-weighing-station-ui
implemented: true
---

# Story: 004-recipe-rail

**Title**: Recipe rail with component states

## User Story

**As a** weighing operator
**I want** to see every component of the recipe with what is done, what I am weighing and what is pending
**So that** I always know my progress

## Requirements

- FR-31 Screen 2
- FR-3 Recipe loading
- FR-15 Component progression

## Acceptance Criteria

- [x] Rail header "Recipe · {shade}", batch ID, "{done} of {total} components weighed"
- [x] Each item: colour swatch, name, "{code} · {scale class}", target with unit, state "✓ {actual}" (green) / "WEIGHING" (amber, left border) / "PENDING"
- [x] Touching a pending item calls activate and makes it the weighing component; touching a done item does nothing
- [x] After a confirmation the rail updates and the next pending component becomes active automatically

## UI/UX Impact

Prototype `.rail`, `.comp` states (L493–500, L696–716).

## API Dependencies

- Uses `GET /api/sessions/{sessionId}`, `POST /api/sessions/{sessionId}/components/{componentId}/activate`

## Test Expectations

- Vitest: states rendering; click pending → activate called; click done → no call

## Technical Notes

None

## Dependencies

### Requires
- 003-select-batch-by-touch-or-scan
- 002-weighing-station/007-component-progression
- 002-weighing-station/010-activate-component-weighing-context

### Enables
- 005-live-weighing-panel

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Activate fails (scale down) | Item becomes active; panel shows scale offline |

## Out of Scope

- Re-ordering components
