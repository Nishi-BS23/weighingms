---
id: 009-ticket-printing
unit: 005-ticket-printing
intent: 001-assisted-dyestuff-weighing
type: simple-construction-bolt
status: complete
stories:
  - 001-compose-weighing-ticket
  - 002-print-ticket
  - 003-reprint-ticket
created: 2026-10-26T06:33:30.000Z
started: 2026-10-26T09:06:01.000Z
completed: "2026-10-26T09:09:07Z"
current_stage: null
stages_completed:
  - name: plan
    completed: 2026-10-26T09:06:01.000Z
    artifact: implementation-plan.md
  - name: implement
    completed: 2026-10-26T09:08:23.000Z
    artifact: implementation-walkthrough.md
  - name: test
    completed: 2026-10-26T09:09:06.000Z
    artifact: test-walkthrough.md
requires_bolts:
  - 007-weighing-station
  - 002-training-substitutes
enables_bolts:
  - 010-weighing-station-ui
requires_units: []
blocks: false
complexity:
  avg_complexity: 1
  avg_uncertainty: 1
  max_dependencies: 2
  testing_scope: 2
---

# Bolt: 009-ticket-printing

## Overview

Compose the weighing ticket from the completed session, print it through the printer adapter, and mark reprints.

## Objective

Implement and test the stories below so that the expected outcome is demonstrable. Workbook steps covered: 27 (backend).

## Stories Included

- **001-compose-weighing-ticket**
- **002-print-ticket**
- **003-reprint-ticket**

## Bolt Type

**Type**: Simple Construction Bolt
**Definition**: `.specsmd/aidlc/templates/construction/bolt-types/simple-construction-bolt.md`

## Stages

- [x] **1. plan**: Complete → implementation-plan.md
- [x] **2. implement**: Complete → Source code + implementation-walkthrough.md
- [x] **3. test**: Complete → Tests + test-walkthrough.md

## Expected Outcome

- Ticket service, `PrinterPort` adapter
- `GET /api/sessions/{id}/ticket`, `POST /api/sessions/{id}/ticket/print`

## Test Expectations

- Unit test: ticket text for prototype actuals
- API tests: print stored in dummy, printer down → 503, reprint

## Dependencies

### Requires
- 007-weighing-station
- 002-training-substitutes

### Enables
- 010-weighing-station-ui

## Success Criteria

- [x] All stories implemented
- [x] All acceptance criteria met
- [x] Tests passing (`npm run check`)
- [x] Code reviewed (agent self-review at each stage checkpoint; delegated by the participant)

## Notes

Human validation is required at every stage checkpoint (delegated to the agent by the participant; each approval is recorded in the stage artifact).
