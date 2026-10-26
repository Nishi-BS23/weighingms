---
id: 003-orgatex-integration
unit: 003-orgatex-integration
intent: 001-assisted-dyestuff-weighing
type: simple-construction-bolt
status: complete
stories:
  - 001-batch-queue-from-orgatex
  - 002-batch-detail-and-recipe-from-orgatex
  - 003-consumption-write-back
created: 2026-10-26T06:33:30.000Z
started: 2026-10-26T06:48:30.000Z
completed: "2026-10-26T06:54:18Z"
current_stage: null
stages_completed:
  - name: plan
    completed: 2026-10-26T06:48:57.000Z
    artifact: implementation-plan.md
  - name: implement
    completed: 2026-10-26T06:52:45.000Z
    artifact: implementation-walkthrough.md
  - name: test
    completed: 2026-10-26T06:54:18.000Z
    artifact: test-walkthrough.md
requires_bolts:
  - 001-training-substitutes
enables_bolts:
  - 005-weighing-station-ui
  - 006-weighing-station
  - 007-weighing-station
requires_units: []
blocks: false
complexity:
  avg_complexity: 2
  avg_uncertainty: 1
  max_dependencies: 2
  testing_scope: 2
---

# Bolt: 003-orgatex-integration

## Overview

Create the WeighingMS backend app (:8000) with configuration, error handling and logging conventions, the `OrgatexPort` and its HTTP adapter, and the batch endpoints used by the UI.

## Objective

Implement and test the stories below so that the expected outcome is demonstrable. Workbook steps covered: 18, 19 (backend).

## Stories Included

- **001-batch-queue-from-orgatex**
- **002-batch-detail-and-recipe-from-orgatex**
- **003-consumption-write-back**

## Bolt Type

**Type**: Simple Construction Bolt
**Definition**: `.specsmd/aidlc/templates/construction/bolt-types/simple-construction-bolt.md`

## Stages

- [x] **1. plan**: Complete → implementation-plan.md
- [x] **2. implement**: Complete → Source code + implementation-walkthrough.md
- [x] **3. test**: Complete → Tests + test-walkthrough.md

## Expected Outcome

- `src/weighingms/` app skeleton (config, error handler, request-ID logging)
- `OrgatexPort` + HTTP adapter
- WeighingMS `GET /api/batches`, `/api/batches/{id}`, `/api/batches/{id}/recipe`
- Scale-selection and tolerance-band policies needed by the recipe endpoint (minimal, completed in 006)

## Test Expectations

- Adapter tests against the dummy app via in-process ASGI transport
- API tests incl. OrgaTEX unavailable → 503
- Write-back idempotency test

## Dependencies

### Requires
- 001-training-substitutes

### Enables
- 005-weighing-station-ui
- 006-weighing-station
- 007-weighing-station

## Success Criteria

- [x] All stories implemented
- [x] All acceptance criteria met
- [x] Tests passing (`npm run check`)
- [x] Code reviewed (agent self-review at each stage checkpoint; delegated by the participant)

## Notes

Human validation is required at every stage checkpoint (delegated to the agent by the participant; each approval is recorded in the stage artifact).
