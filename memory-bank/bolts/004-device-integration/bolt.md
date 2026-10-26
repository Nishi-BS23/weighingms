---
id: 004-device-integration
unit: 004-device-integration
intent: 001-assisted-dyestuff-weighing
type: simple-construction-bolt
status: complete
stories:
  - 001-live-weight-from-selected-scale
  - 002-tare-and-re-tare
  - 003-scanner-input
  - 004-device-status-and-failure-detection
created: 2026-10-26T06:33:30.000Z
started: 2026-10-26T06:55:01.000Z
completed: "2026-10-26T07:00:00Z"
current_stage: null
stages_completed:
  - name: plan
    completed: 2026-10-26T06:55:25.000Z
    artifact: implementation-plan.md
  - name: implement
    completed: 2026-10-26T06:58:25.000Z
    artifact: implementation-walkthrough.md
  - name: test
    completed: 2026-10-26T07:00:00.000Z
    artifact: test-walkthrough.md
requires_bolts:
  - 002-training-substitutes
  - 003-orgatex-integration
enables_bolts:
  - 005-weighing-station-ui
  - 006-weighing-station
requires_units: []
blocks: false
complexity:
  avg_complexity: 2
  avg_uncertainty: 1
  max_dependencies: 2
  testing_scope: 2
---

# Bolt: 004-device-integration

## Overview

Implement `ScalePort` and `ScannerPort` adapters, device status aggregation and the training passthrough endpoints.

## Objective

Implement and test the stories below so that the expected outcome is demonstrable. Workbook steps covered: 21 (backend).

## Stories Included

- **001-live-weight-from-selected-scale**
- **002-tare-and-re-tare**
- **003-scanner-input**
- **004-device-status-and-failure-detection**

## Bolt Type

**Type**: Simple Construction Bolt
**Definition**: `.specsmd/aidlc/templates/construction/bolt-types/simple-construction-bolt.md`

## Stages

- [x] **1. plan**: Complete → implementation-plan.md
- [x] **2. implement**: Complete → Source code + implementation-walkthrough.md
- [x] **3. test**: Complete → Tests + test-walkthrough.md

## Expected Outcome

- Scale and scanner adapters
- `GET /api/devices/status`, `GET /api/scanner/scans`, `/api/training/*`

## Test Expectations

- Adapter tests against the dummy: readings, tare, staleness, unavailable
- API tests: status transitions within 2 s, calibration expired

## Dependencies

### Requires
- 002-training-substitutes
- 003-orgatex-integration

### Enables
- 005-weighing-station-ui
- 006-weighing-station

## Success Criteria

- [x] All stories implemented
- [x] All acceptance criteria met
- [x] Tests passing (`npm run check`)
- [x] Code reviewed (agent self-review at each stage checkpoint; delegated by the participant)

## Notes

Human validation is required at every stage checkpoint (delegated to the agent by the participant; each approval is recorded in the stage artifact).
