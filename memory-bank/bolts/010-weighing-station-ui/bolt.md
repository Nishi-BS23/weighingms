---
id: 010-weighing-station-ui
unit: 006-weighing-station-ui
intent: 001-assisted-dyestuff-weighing
type: simple-construction-bolt
status: complete
stories:
  - 008-completion-summary-screen
  - 009-ticket-preview-and-print
  - 010-operator-facing-failure-messages
  - 011-function-keys
created: 2026-10-26T06:33:30.000Z
started: 2026-10-26T09:09:36.000Z
completed: "2026-10-26T09:14:43Z"
current_stage: null
stages_completed:
  - name: plan
    completed: 2026-10-26T09:09:38.000Z
    artifact: implementation-plan.md
  - name: implement
    completed: 2026-10-26T09:12:27.000Z
    artifact: implementation-walkthrough.md
  - name: test
    completed: 2026-10-26T09:14:43.000Z
    artifact: test-walkthrough.md
requires_bolts:
  - 008-weighing-station-ui
  - 009-ticket-printing
enables_bolts:
  - 011-weighing-station-ui
requires_units: []
blocks: false
complexity:
  avg_complexity: 2
  avg_uncertainty: 1
  max_dependencies: 2
  testing_scope: 2
---

# Bolt: 010-weighing-station-ui

## Overview

Deliver Screen 3 (summary, per-component results, write-back status + retry, ticket preview and print, next batch), operator-facing error messages and function keys.

## Objective

Implement and test the stories below so that the expected outcome is demonstrable. Workbook steps covered: 26, 27 (UI).

## Stories Included

- **008-completion-summary-screen**
- **009-ticket-preview-and-print**
- **010-operator-facing-failure-messages**
- **011-function-keys**

## Bolt Type

**Type**: Simple Construction Bolt
**Definition**: `.specsmd/aidlc/templates/construction/bolt-types/simple-construction-bolt.md`

## Stages

- [x] **1. plan**: Complete → implementation-plan.md
- [x] **2. implement**: Complete → Source code + implementation-walkthrough.md
- [x] **3. test**: Complete → Tests + test-walkthrough.md

## Expected Outcome

- Screen 3
- Error message mapping and error boundaries
- F-key handling

## Test Expectations

- Vitest: summary variants, ticket rendering, error mapping, key dispatch

## Dependencies

### Requires
- 008-weighing-station-ui
- 009-ticket-printing

### Enables
- 011-weighing-station-ui

## Success Criteria

- [x] All stories implemented
- [x] All acceptance criteria met
- [x] Tests passing (`npm run check`)
- [x] Code reviewed (agent self-review at each stage checkpoint; delegated by the participant)

## Notes

Human validation is required at every stage checkpoint (delegated to the agent by the participant; each approval is recorded in the stage artifact).
