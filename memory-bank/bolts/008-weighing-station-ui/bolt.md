---
id: 008-weighing-station-ui
unit: 006-weighing-station-ui
intent: 001-assisted-dyestuff-weighing
type: simple-construction-bolt
status: complete
stories:
  - 004-recipe-rail
  - 005-live-weighing-panel
  - 006-weighing-actions
  - 007-overshoot-surplus-panel
created: 2026-10-26T06:33:30.000Z
started: 2026-10-26T08:59:22.000Z
completed: "2026-10-26T09:05:35Z"
current_stage: null
stages_completed:
  - name: plan
    completed: 2026-10-26T08:59:45.000Z
    artifact: implementation-plan.md
  - name: implement
    completed: 2026-10-26T09:03:43.000Z
    artifact: implementation-walkthrough.md
  - name: test
    completed: 2026-10-26T09:05:35.000Z
    artifact: test-walkthrough.md
requires_bolts:
  - 005-weighing-station-ui
  - 007-weighing-station
enables_bolts:
  - 010-weighing-station-ui
requires_units: []
blocks: false
complexity:
  avg_complexity: 2
  avg_uncertainty: 1
  max_dependencies: 2
  testing_scope: 2
---

# Bolt: 008-weighing-station-ui

## Overview

Deliver Screen 2: recipe rail, live weighing panel, actions and dialogs, surplus panel — all driven by the session API.

## Objective

Implement and test the stories below so that the expected outcome is demonstrable. Workbook steps covered: 20–25 (UI).

## Stories Included

- **004-recipe-rail**
- **005-live-weighing-panel**
- **006-weighing-actions**
- **007-overshoot-surplus-panel**

## Bolt Type

**Type**: Simple Construction Bolt
**Definition**: `.specsmd/aidlc/templates/construction/bolt-types/simple-construction-bolt.md`

## Stages

- [x] **1. plan**: Complete → implementation-plan.md
- [x] **2. implement**: Complete → Source code + implementation-walkthrough.md
- [x] **3. test**: Complete → Tests + test-walkthrough.md

## Expected Outcome

- Screen 2 components and dialogs
- Live polling hook

## Test Expectations

- Vitest: zones, Confirm enablement, dialogs, surplus panel
- Evidence screenshots for Steps 20–25

## Dependencies

### Requires
- 005-weighing-station-ui
- 007-weighing-station

### Enables
- 010-weighing-station-ui

## Success Criteria

- [x] All stories implemented
- [x] All acceptance criteria met
- [x] Tests passing (`npm run check`)
- [x] Code reviewed (agent self-review at each stage checkpoint; delegated by the participant)

## Notes

Human validation is required at every stage checkpoint (delegated to the agent by the participant; each approval is recorded in the stage artifact).
