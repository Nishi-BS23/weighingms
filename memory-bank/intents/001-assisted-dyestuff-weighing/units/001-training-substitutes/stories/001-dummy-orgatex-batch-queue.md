---
id: 001-dummy-orgatex-batch-queue
unit: 001-training-substitutes
intent: 001-assisted-dyestuff-weighing
status: complete
priority: must
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 001-training-substitutes
implemented: true
---

# Story: 001-dummy-orgatex-batch-queue

**Title**: Dummy OrgaTEX batch queue and batch detail

## User Story

**As a** trainer preparing a WeighingMS training session
**I want** a Dummy OrgaTEX that serves the training batch queue and batch details
**So that** WeighingMS can load real-looking batches through an API instead of hard-coded UI data

## Requirements

- FR-25 Dummy OrgaTEX
- FR-1 Batch queue (data source)

## Acceptance Criteria

- [x] **Given** the seed file, **When** `GET /api/batches` is called on the dummy service, **Then** it returns 200 with B-24187, B-24188, B-24190, B-24191 including batchId, orderRef, machineRef, fabricDesc, fabricWeightKg, shadeCode, recipeId, componentCount, status, releasedAt
- [x] **Given** a status filter, **When** `GET /api/batches?status=QUEUED` is called, **Then** only QUEUED batches are returned
- [x] **Given** B-24187 exists, **When** `GET /api/batches/B-24187` is called, **Then** it returns order SO-9931, machine JET-04, fabric "100% CTN knit", 480 kg, shade Teal 4C, 5 components, status QUEUED
- [x] **Given** an unknown ID, **When** `GET /api/batches/B-00000` is called, **Then** it returns 404 with `{"error": {"code": "BATCH_NOT_FOUND", ...}}`
- [x] **Given** the dummy service starts, **Then** the project skeleton exists: Poetry project, `src/dummy_systems` app on port 8100, root `package.json` whose `npm run dev` starts it

## UI/UX Impact

None directly. Supplies the rows of Screen 1 (Batch, Order, Machine, Fabric / lot, Shade, Comp., Status) through WeighingMS.

## API Dependencies

- Provides `GET /api/batches`, `GET /api/batches/{batchId}` (training contract, not the real OrgaTEX interface)

## Test Expectations

- pytest API tests with FastAPI TestClient for list, filter, detail, 404
- Seed file schema test (all batches have recipes; component counts match)

## Technical Notes

Seed file `data/seed/orgatex-seed.json`; quantities as decimal strings. Fabric/lot column in the UI is composed as "{fabricDesc} · {fabricWeightKg} kg". This story also creates the backend skeleton (pyproject, ruff/mypy/pytest config, package layout per coding standards).

## Dependencies

### Requires
- None (first story)

### Enables
- 002-dummy-orgatex-recipe
- 003-orgatex-integration/001-batch-queue-from-orgatex

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Empty queue (all WEIGHED) | 200 with empty list |
| Lower-case batch ID | 404 (IDs are exact) |

## Out of Scope

- Real OrgaTEX authentication and paging
