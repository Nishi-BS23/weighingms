---
id: 005-weighing-station-ui
unit: 006-weighing-station-ui
intent: 001-assisted-dyestuff-weighing
type: simple-construction-bolt
status: complete
stories:
  - 001-station-shell-and-chrome
  - 002-batch-queue-screen
  - 003-select-batch-by-touch-or-scan
created: 2026-10-26T06:33:30.000Z
started: 2026-10-26T07:00:34.000Z
completed: "2026-10-26T07:11:48Z"
current_stage: null
stages_completed:
  - name: plan
    completed: 2026-10-26T07:01:21.000Z
    artifact: implementation-plan.md
  - name: implement
    completed: 2026-10-26T07:09:59.000Z
    artifact: implementation-walkthrough.md
  - name: test
    completed: 2026-10-26T07:11:48.000Z
    artifact: test-walkthrough.md
requires_bolts:
  - 003-orgatex-integration
  - 004-device-integration
enables_bolts:
  - 008-weighing-station-ui
requires_units: []
blocks: false
complexity:
  avg_complexity: 2
  avg_uncertainty: 1
  max_dependencies: 2
  testing_scope: 2
---

# Bolt: 005-weighing-station-ui

## Overview

Scaffold the React frontend, reproduce the device chrome and training panel, and deliver Screen 1 (batch queue, touch and scan selection) wired to the API; `npm run dev` starts all three processes.

## Objective

Implement and test the stories below so that the expected outcome is demonstrable. Workbook steps covered: 19.

## Stories Included

- **001-station-shell-and-chrome**
- **002-batch-queue-screen**
- **003-select-batch-by-touch-or-scan**

## Bolt Type

**Type**: Simple Construction Bolt
**Definition**: `.specsmd/aidlc/templates/construction/bolt-types/simple-construction-bolt.md`

## Stages

- [x] **1. plan**: Complete → implementation-plan.md
- [x] **2. implement**: Complete → Source code + implementation-walkthrough.md
- [x] **3. test**: Complete → Tests + test-walkthrough.md

## Expected Outcome

- `frontend/` (Vite, React, TS strict, ESLint, Prettier, Vitest)
- Generated API types
- Shell, top bar, step indicator, status strip, training panel
- Screen 1

## Test Expectations

- Vitest component tests
- Network evidence: `GET /api/batches`, `/api/batches/B-24187`, `/api/batches/B-24187/recipe` on selection (STEP-19)

## Dependencies

### Requires
- 003-orgatex-integration
- 004-device-integration

### Enables
- 008-weighing-station-ui

## Success Criteria

- [x] All stories implemented
- [x] All acceptance criteria met
- [x] Tests passing (`npm run check`)
- [x] Code reviewed (agent self-review at each stage checkpoint; delegated by the participant)

## Notes

Human validation is required at every stage checkpoint (delegated to the agent by the participant; each approval is recorded in the stage artifact).
