---
id: 002-dummy-orgatex-recipe
unit: 001-training-substitutes
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 001-training-substitutes
implemented: true
---

# Story: 002-dummy-orgatex-recipe

**Title**: Dummy OrgaTEX recipe

## User Story

**As a** trainer
**I want** the Dummy OrgaTEX to return each batch's recipe with components, targets, tolerances, dyestuff identity and lots
**So that** WeighingMS can guide weighing from recipe data rather than hard-coded values

## Requirements

- FR-25 Dummy OrgaTEX
- FR-3 Recipe loading (data source)
- FR-4 Component identification (data source)
- FR-5 Dyestuff lot (data source)

## Acceptance Criteria

- [x] **Given** B-24187, **When** `GET /api/batches/B-24187/recipe` is called, **Then** it returns shade Teal 4C and 5 components in sequence: Blue RSPL 1240.0 g ±6.0 g lot 2026-0341; Red RB 386.0 g ±2.0 g lot 2026-0298; Yellow RGB 94.0 g ±0.5 g lot 2026-0387; Sodium Sulphate 24.000 kg ±0.120 kg lot 2026-0112; Soda Ash 9.600 kg ±0.048 kg lot 2026-0155
- [x] **Given** any component, **Then** it includes componentId, sequence, dyestuffCode, name, dyestuffType, colourHex, targetQty {value, unit}, tolerance {value, unit}, lotId
- [x] **Given** B-24188, B-24190, B-24191, **Then** recipes exist with 5, 7 and 4 components and the seed marks them `"trainingDataNote": "invented training data"`
- [x] **Given** an unknown batch, **Then** 404 `BATCH_NOT_FOUND`

## UI/UX Impact

None directly. Feeds the recipe rail, weigh header (name, code, LOT) and tolerance caption on Screen 2.

## API Dependencies

- Provides `GET /api/batches/{batchId}/recipe`

## Test Expectations

- pytest: B-24187 recipe values exactly as the prototype
- pytest: quantities serialised as strings, never JSON numbers

## Technical Notes

B-24188 recipe = B-24187 targets × 520/480 (TA-19), tolerance 0.5% rounded to the unit's display precision.

## Dependencies

### Requires
- 001-dummy-orgatex-batch-queue

### Enables
- 003-orgatex-integration/002-batch-detail-and-recipe-from-orgatex

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Recipe component without tolerance (B-24190 one line) | `tolerance` omitted → WeighingMS default rule applies (TA-03) |

## Out of Scope

- Recipe versioning beyond a version string
