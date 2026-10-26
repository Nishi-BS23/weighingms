---
id: 002-training-substitutes
unit: 001-training-substitutes
intent: 001-assisted-dyestuff-weighing
type: simple-construction-bolt
status: complete
stories:
  - 004-dummy-scale-readings-and-tare
  - 005-dummy-scanner
  - 006-dummy-printer
  - 007-failure-injection-and-reset
created: 2026-10-26T06:33:30.000Z
started: 2026-10-26T06:42:40.000Z
completed: "2026-10-26T06:47:56Z"
current_stage: null
stages_completed:
  - name: plan
    completed: 2026-10-26T06:43:43.000Z
    artifact: implementation-plan.md
  - name: implement
    completed: 2026-10-26T06:46:22.000Z
    artifact: implementation-walkthrough.md
  - name: test
    completed: 2026-10-26T06:47:56.000Z
    artifact: test-walkthrough.md
requires_bolts:
  - 001-training-substitutes
enables_bolts:
  - 004-device-integration
  - 009-ticket-printing
requires_units: []
blocks: false
complexity:
  avg_complexity: 2
  avg_uncertainty: 1
  max_dependencies: 1
  testing_scope: 2
---

# Bolt: 002-training-substitutes

## Overview

Add the Dummy Scale (two scales, simulation profiles, tare, calibration), Dummy Scanner, Dummy Printer, failure injection and reset.

## Objective

Implement and test the stories below so that the expected outcome is demonstrable. Workbook steps covered: 16, 18.

## Stories Included

- **004-dummy-scale-readings-and-tare**
- **005-dummy-scanner**
- **006-dummy-printer**
- **007-failure-injection-and-reset**

## Bolt Type

**Type**: Simple Construction Bolt
**Definition**: `.specsmd/aidlc/templates/construction/bolt-types/simple-construction-bolt.md`

## Stages

- [x] **1. plan**: Complete → implementation-plan.md
- [x] **2. implement**: Complete → Source code + implementation-walkthrough.md
- [x] **3. test**: Complete → Tests + test-walkthrough.md

## Expected Outcome

- Scale, scanner, printer and control routers in `src/dummy_systems/`
- Injectable clock for deterministic simulation

## Test Expectations

- pytest: simulation profiles with fake clock, exact weight, tare, capacity clamp
- pytest: scanner order/cursor, printer store, availability toggles → 503, reset

## Dependencies

### Requires
- 001-training-substitutes

### Enables
- 004-device-integration
- 009-ticket-printing

## Success Criteria

- [x] All stories implemented
- [x] All acceptance criteria met
- [x] Tests passing (`npm run check`)
- [x] Code reviewed (agent self-review at each stage checkpoint; delegated by the participant)

## Notes

Human validation is required at every stage checkpoint (delegated to the agent by the participant; each approval is recorded in the stage artifact).
