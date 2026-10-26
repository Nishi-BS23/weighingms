---
id: 007-weighing-station
unit: 002-weighing-station
intent: 001-assisted-dyestuff-weighing
type: ddd-construction-bolt
status: complete
stories:
  - 004-confirm-component-weighing
  - 005-overshoot-handling
  - 006-supervisor-override
  - 008-quit-and-abandon
  - 009-batch-completion
  - 011-weighing-summary-and-records
created: 2026-10-26T06:33:30.000Z
started: 2026-10-26T08:50:36.000Z
completed: "2026-10-26T08:59:03Z"
current_stage: null
stages_completed:
  - name: model
    completed: 2026-10-26T08:51:20.000Z
    artifact: ddd-01-domain-model.md
  - name: design
    completed: 2026-10-26T08:51:49.000Z
    artifact: ddd-02-technical-design.md
  - name: adr
    completed: 2026-10-26T08:51:49.000Z
    artifact: adr-004-overshoot-block-and-recover.md
  - name: implement
    completed: 2026-10-26T08:56:12.000Z
    artifact: src/weighingms (session confirm/override/quit/complete, records, summary, migration 0002); src/dummy_systems scale load control
  - name: test
    completed: 2026-10-26T08:59:03.000Z
    artifact: ddd-03-test-report.md
requires_bolts:
  - 006-weighing-station
enables_bolts:
  - 008-weighing-station-ui
  - 009-ticket-printing
requires_units: []
blocks: false
complexity:
  avg_complexity: 3
  avg_uncertainty: 3
  max_dependencies: 2
  testing_scope: 2
---

# Bolt: 007-weighing-station

## Overview

Deliver confirmation with immutable records, the overshoot rule decided at Workbook Step 24, supervisor override, quit/abandon, batch completion with idempotent write-back and retry, and the summary/records queries.

## Objective

Implement and test the stories below so that the expected outcome is demonstrable. Workbook steps covered: 24 (decision), 25, 26 (backend).

## Stories Included

- **004-confirm-component-weighing**
- **005-overshoot-handling**
- **006-supervisor-override**
- **008-quit-and-abandon**
- **009-batch-completion**
- **011-weighing-summary-and-records**

## Bolt Type

**Type**: DDD Construction Bolt
**Definition**: `.specsmd/aidlc/templates/construction/bolt-types/ddd-construction-bolt.md`

## Stages

- [x] **1. model**: Complete → ddd-01-domain-model.md
- [x] **2. design**: Complete → ddd-02-technical-design.md
- [x] **3. adr**: Complete → adr-*.md (optional)
- [x] **4. implement**: Complete → Source code
- [x] **5. test**: Complete → ddd-03-test-report.md

## Expected Outcome

- Overshoot decision record (Step 24) + ADR
- Confirm, override, quit, complete, sync, summary, records endpoints
- Audit events

## Test Expectations

- Domain tests: overshoot rule, override policy
- API tests: confirm transaction JSON (STEP-25), write-back stored in dummy (STEP-26), PENDING → retry exactly once, BATCH_INCOMPLETE

## Dependencies

### Requires
- 006-weighing-station

### Enables
- 008-weighing-station-ui
- 009-ticket-printing

## Success Criteria

- [x] All stories implemented
- [x] All acceptance criteria met
- [x] Tests passing (`npm run check`)
- [x] Code reviewed (agent self-review at each stage checkpoint; delegated by the participant)

## Notes

Human validation is required at every stage checkpoint (delegated to the agent by the participant; each approval is recorded in the stage artifact).
