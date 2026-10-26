---
stage: test
bolt: 007-weighing-station
created: 2026-10-26T08:59:03Z
---

## Test Report: 002-weighing-station (confirmation, exceptions, completion)

### Summary

- **Unit Tests**: 17 new passed (confirm traceability set, out-of-tolerance/calibration/no-reading rejections, override with/without surplus, override not needed, Step 24 guidance, recovery by removing excess, abandon, completion rules, sync, supervisor PIN verification)
- **Integration/API Tests**: 15 new passed (confirm + advance + record, re-read rejection, scale down 503, calibration expired, overshoot block → recovery, supervisor override incl. wrong PIN 403 / empty reason 422 / audit / override row, override not needed, PIN never logged, quit + resume, BATCH_INCOMPLETE, full batch write-back once + WEIGHED, OrgaTEX down → PENDING → retry once, summary = prototype Screen 3, completed session rejects further weighing; dummy scale load)
- **Security Tests**: wrong PIN refused; PIN absent from all log output; supervisor recorded as actor
- **Whole backend**: 205/205 passed, coverage 97.7%; ruff + mypy --strict clean

### Acceptance Criteria Validation

- ✅ **004-confirm-component-weighing**: backend re-reads the scale; record has batch, component, dyestuff, target, actual, unit, band, result, operator, lot, container, tare, scale, timestamp (evidence/STEP-25-transaction.json); rejected when out of tolerance / scale down / calibration expired; durable in one transaction; immutable (unique per component)
- ✅ **005-overshoot-handling**: OVER → Confirm blocked, surplus +2.4 g (+2.6%), guidance per Step 24 decision (evidence/STEP-24-overshoot-decision.md, ADR-004); removing excess re-enables confirm; no recalculation
- ✅ **006-supervisor-override**: valid PIN + reason → OVERRIDDEN record with surplus, override row, OVERRIDE audit (actor supervisor); wrong PIN 403; empty reason 422; within tolerance → OVERRIDE_NOT_NEEDED; PIN never logged
- ✅ **008-quit-and-abandon**: no record, ABANDON audit with net at quit, session stays in progress, resume keeps DONE components
- ✅ **009-batch-completion**: 4/5 → BATCH_INCOMPLETE; 5/5 → COMPLETED + write-back (POST consumption 200, idempotency key = session ID) + WEIGHED; OrgaTEX down → PENDING, retry → SYNCED exactly once (evidence/STEP-26-writeback.json, STEP-26-request-log.txt)
- ✅ **011-weighing-summary-and-records**: 5 of 5, all within tolerance, total 35.322 kg, operator, write-back status, per-component results; records query by batch

### Issues Found

- Training simulation defect fixed: the floor scale still held the previous drum when the next component was tared, so Soda Ash hit the 32 kg capacity (read 8.020 kg). In training mode WeighingMS now places the next component's empty container (master tare) on the scale before taring — the physical step the operator performs. Dummy gained `POST /api/control/scales/{id}/load`.
- Write-back lines were ordered by timestamp + random ID; now ordered by recipe sequence.
- A confirm on a completed session reported `NO_ACTIVE_COMPONENT`; now `SESSION_COMPLETED`.
- Deviation from story 004 text: scale unavailable at confirm returns **503** `SCALE_UNAVAILABLE` (dependency failure) rather than 409; the code is the same.

### Recommendations

- Bolt 008 (Screen 2) consumes confirm/override/quit/live incl. `guidance`; regenerate frontend API types first.
- Overrides on a scale with expired calibration are allowed (supervisor authority, Brief FR-35 "calibration bypass"); revisit if FCI wants a separate bypass action.

### Stage checkpoint (delegated, self-validated)

All tests pass; every acceptance criterion verified; evidence for Workbook Steps 24–26 saved. **Approved** — bolt complete.
