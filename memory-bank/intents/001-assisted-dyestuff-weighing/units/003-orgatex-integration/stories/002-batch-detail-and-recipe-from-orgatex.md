---
id: 002-batch-detail-and-recipe-from-orgatex
unit: 003-orgatex-integration
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 003-orgatex-integration
implemented: true
---

# Story: 002-batch-detail-and-recipe-from-orgatex

**Title**: Batch detail and recipe from OrgaTEX

## User Story

**As a** weighing operator
**I want** selecting a batch to load its header and recipe with each component's identity, quantity, tolerance and lot
**So that** I see exactly what has to be weighed

## Requirements

- FR-3 Recipe loading
- FR-4 Component identification

## Acceptance Criteria

- [x] **When** `GET /api/batches/B-24187` is called on WeighingMS, **Then** the batch header is returned (order, machine, fabric, shade, component count, status)
- [x] **When** `GET /api/batches/B-24187/recipe` is called, **Then** the 5 components are returned in sequence with componentId, sequence, dyestuffCode, name, shortName, colourHex, target {value, unit}, tolerance band {min, max}, scale assignment (scaleId, label) and lotId
- [x] Quantities are decimal strings; units g/kg only; an invalid unit from OrgaTEX → 502 `ORGATEX_BAD_DATA`
- [x] Unknown batch → 404 `BATCH_NOT_FOUND`; OrgaTEX down → 503
- [x] Recipe returned in < 300 ms locally (supports NFR-2)

## UI/UX Impact

Recipe rail (name, code · scale, target), weigh header identity.

## API Dependencies

- Provides WeighingMS `GET /api/batches/{batchId}`, `GET /api/batches/{batchId}/recipe`
- Uses Dummy OrgaTEX `GET /api/batches/{batchId}`, `GET /api/batches/{batchId}/recipe`
- Uses domain policies: scale selection, tolerance band (002)

## Test Expectations

- Adapter mapping tests (exact Decimal values for B-24187)
- API tests: 404, 503, bad unit

## Technical Notes

Scale assignment and band come from domain policies so the UI shows them before a session starts. Short names from configuration.

## Dependencies

### Requires
- 001-batch-queue-from-orgatex
- 001-training-substitutes/002-dummy-orgatex-recipe

### Enables
- 002-weighing-station/001-start-or-resume-weighing-session
- 006-weighing-station-ui/003-select-batch-by-touch-or-scan

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Recipe component without tolerance | Default rule applied (TA-03), band marked `source: DEFAULT` |

## Out of Scope

- Recipe versions history
