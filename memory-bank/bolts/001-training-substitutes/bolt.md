---
id: 001-training-substitutes
unit: 001-training-substitutes
intent: 001-assisted-dyestuff-weighing
type: simple-construction-bolt
status: complete
stories:
  - 001-dummy-orgatex-batch-queue
  - 002-dummy-orgatex-recipe
  - 003-dummy-orgatex-consumption-and-status
created: 2026-10-26T06:33:30.000Z
started: 2026-10-26T06:34:24.000Z
completed: "2026-10-26T06:42:27Z"
current_stage: null
stages_completed:
  - name: plan
    completed: 2026-10-26T06:36:02.000Z
    artifact: implementation-plan.md
  - name: implement
    completed: 2026-10-26T06:40:36.000Z
    artifact: implementation-walkthrough.md
  - name: test
    completed: 2026-10-26T06:42:27.000Z
    artifact: test-walkthrough.md
requires_bolts: []
enables_bolts:
  - 002-training-substitutes
  - 003-orgatex-integration
requires_units: []
blocks: false
complexity:
  avg_complexity: 1
  avg_uncertainty: 1
  max_dependencies: 1
  testing_scope: 2
---

# Bolt: 001-training-substitutes

## Overview

Create the backend project skeleton (Poetry, ruff, mypy, pytest, root `package.json` with `npm run dev`) and the Dummy OrgaTEX service with the prototype seed data.

## Objective

Implement and test the stories below so that the expected outcome is demonstrable. Workbook steps covered: 16, 17, 18.

## Stories Included

- **001-dummy-orgatex-batch-queue**
- **002-dummy-orgatex-recipe**
- **003-dummy-orgatex-consumption-and-status**

## Bolt Type

**Type**: Simple Construction Bolt
**Definition**: `.specsmd/aidlc/templates/construction/bolt-types/simple-construction-bolt.md`

## Stages

- [x] **1. plan**: Complete → implementation-plan.md
- [x] **2. implement**: Complete → Source code + implementation-walkthrough.md
- [x] **3. test**: Complete → Tests + test-walkthrough.md

## Expected Outcome

- `pyproject.toml`, `package.json`, tooling config
- `src/dummy_systems/` FastAPI app on :8100 (OrgaTEX routes)
- `data/seed/orgatex-seed.json` (B-24187 + 3 labelled training batches)
- Consumption/status store (SQLite `data/dummy.db`)

## Test Expectations

- pytest API tests for every Dummy OrgaTEX endpoint (list, filter, detail, recipe, 404, consumption idempotency, status)
- curl evidence of `/api/batches`, `/api/batches/B-24187`, `/api/batches/B-24187/recipe` (Workbook STEP-18)

## Dependencies

### Requires
- None (first bolt)

### Enables
- 002-training-substitutes
- 003-orgatex-integration

## Success Criteria

- [x] All stories implemented
- [x] All acceptance criteria met
- [x] Tests passing (`npm run check`)
- [x] Code reviewed (agent self-review at each stage checkpoint; delegated by the participant)

## Notes

Human validation is required at every stage checkpoint (delegated to the agent by the participant; each approval is recorded in the stage artifact).
