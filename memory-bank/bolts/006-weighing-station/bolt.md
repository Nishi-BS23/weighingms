---
id: 006-weighing-station
unit: 002-weighing-station
intent: 001-assisted-dyestuff-weighing
type: ddd-construction-bolt
status: complete
stories:
  - 001-start-or-resume-weighing-session
  - 002-automatic-scale-selection
  - 003-tolerance-evaluation
  - 007-component-progression
  - 010-activate-component-weighing-context
created: 2026-10-26T06:33:30.000Z
started: 2026-10-26T07:11:54.000Z
completed: "2026-10-26T08:49:58Z"
current_stage: null
stages_completed:
  - name: model
    completed: 2026-10-26T07:13:05.000Z
    artifact: ddd-01-domain-model.md
  - name: design
    completed: 2026-10-26T07:13:36.000Z
    artifact: ddd-02-technical-design.md
  - name: adr
    completed: 2026-10-26T07:14:08.000Z
    artifact: adr-001-live-weight-by-polling.md,adr-002-recipe-snapshot-per-session.md,adr-003-training-mode-flag.md
  - name: implement
    completed: 2026-10-26T08:45:12.000Z
    artifact: src/weighingms (domain/weighing, application/sessions|operators|training, infrastructure/persistence, api/sessions|operators)
  - name: test
    completed: 2026-10-26T08:49:58.000Z
    artifact: ddd-03-test-report.md
requires_bolts:
  - 003-orgatex-integration
  - 004-device-integration
enables_bolts:
  - 007-weighing-station
  - 008-weighing-station-ui
requires_units: []
blocks: false
complexity:
  avg_complexity: 3
  avg_uncertainty: 2
  max_dependencies: 2
  testing_scope: 2
---

# Bolt: 006-weighing-station

## Overview

Model the weighing domain and deliver the core session slice: start/resume, scale rule, tolerance evaluation, progression, component activation with context, live evaluation and re-tare, with SQLAlchemy persistence and Alembic.

## Objective

Implement and test the stories below so that the expected outcome is demonstrable. Workbook steps covered: 20–23 (backend), 22 tolerance tests.

## Stories Included

- **001-start-or-resume-weighing-session**
- **002-automatic-scale-selection**
- **003-tolerance-evaluation**
- **007-component-progression**
- **010-activate-component-weighing-context**

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

- Domain model (session aggregate, value objects, policies)
- Application services + persistence (`weighingms.db`)
- `POST /api/sessions`, `GET /api/sessions/{id}`, activate, `GET .../live`, `POST .../retare`, operator endpoints

## Test Expectations

- Domain unit tests incl. Workbook Step 22 boundaries (STEP-22-tolerance-tests.txt)
- API tests against the dummy (start, resume, scale switch, live, re-tare)
- Persistence/resume test

## Dependencies

### Requires
- 003-orgatex-integration
- 004-device-integration

### Enables
- 007-weighing-station
- 008-weighing-station-ui

## Success Criteria

- [x] All stories implemented
- [x] All acceptance criteria met
- [x] Tests passing (`npm run check`)
- [x] Code reviewed (agent self-review at each stage checkpoint; delegated by the participant)

## Notes

Human validation is required at every stage checkpoint (delegated to the agent by the participant; each approval is recorded in the stage artifact).
