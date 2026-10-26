---
unit: 001-training-substitutes
intent: 001-assisted-dyestuff-weighing
phase: inception
status: complete
unit_type: backend
default_bolt_type: simple-construction-bolt
created: 2026-10-26T06:40:00.000Z
updated: 2026-10-26T06:40:00.000Z
---

# Unit Brief: Training Substitutes (Dummy APIs)

## Purpose

Provide working stand-ins for OrgaTEX, the two weighing scales, the barcode scanner and the ticket printer, so WeighingMS can be built, demonstrated and tested end to end without real systems. The dummies are product artifacts (Workbook Rule 5) with documented **training** contracts.

## Scope

### In Scope
- Separate FastAPI service (`src/dummy_systems/`, port 8100) with its own data store
- Dummy OrgaTEX: batch queue, batch detail, recipe, consumption (idempotent), status update
- Seed data from the prototype scenario (B-24187 + other queue rows) in `data/seed/orgatex-seed.json`
- Dummy Scale: `scale-3kg`, `scale-32kg`; readings, tare, status, calibration; simulation profiles; exact weight
- Dummy Scanner: simulated scans, ordered delivery, status
- Dummy Printer: accept/store/list tickets, status
- Control endpoints: availability toggles per system, reset to seed

### Out of Scope
- Any WeighingMS business rule (tolerance, scale selection, progression)
- Claims about real OrgaTEX or device protocols
- UI (the training panel lives in `006-weighing-station-ui` and reaches control endpoints through WeighingMS)

---

## Assigned Requirements

| FR | Requirement | Priority |
|----|-------------|----------|
| FR-25 | Dummy OrgaTEX (training substitute) | Must |
| FR-26 | Dummy Scale (training substitute) | Must |
| FR-27 | Dummy Scanner (training substitute) | Must |
| FR-28 | Dummy Printer (training substitute) | Must |
| FR-29 | Training controls (simulation, failure injection, reset) | Must |

---

## Domain Concepts

### Key Entities
| Entity | Description | Attributes |
|--------|-------------|------------|
| Batch (OrgaTEX view) | Dye lot scheduled by OrgaTEX | batchId, orderRef, machineRef, fabricDesc, fabricWeightKg, shadeCode, recipeId, status, releasedAt |
| Recipe / RecipeComponent | Formulation for the batch | recipeId, version, shadeCode; sequence, dyestuffCode, name, colourHex, targetQty, unit, tolerance, lotId |
| ConsumptionPosting | Actual consumption received | idempotencyKey, batchId, sessionId, completedAt, lines[], receivedAt |
| SimulatedScale | Scale state | scaleId, class, label, capacity, resolution, unit, grossWeight, tareWeight, profile, available, calibrationDue |
| Scan | Simulated scan | seq, code, scannedAt |
| PrintedTicket | Ticket received | ticketId, content, reprint, printedAt |

### Key Operations
| Operation | Description | Inputs | Outputs |
|-----------|-------------|--------|---------|
| List / get batches | Training OrgaTEX read | status filter | batches |
| Get recipe | Training OrgaTEX read | batchId | recipe |
| Post consumption | Store once per idempotency key | batchId, payload | 200 + posting |
| Read weight | Current simulated reading | scaleId | gross, net, unit, stable, at |
| Tare | Zero the net reading | scaleId | reading |
| Simulate | Start a profile (dispense/overshoot/below) or set exact weight | scaleId, landing/exact | profile state |
| Scan | Enqueue a code | code | seq |
| Print | Store a ticket | content | ticketId |
| Set availability / reset | Failure injection / restore seed | system, available | state |

---

## Story Summary

| Metric | Count |
|--------|-------|
| Total Stories | 7 |
| Must Have | 7 |
| Should Have | 0 |
| Could Have | 0 |

### Stories

| Story ID | Title | Priority | Status |
|----------|-------|----------|--------|
| 001-dummy-orgatex-batch-queue | Dummy OrgaTEX batch queue and batch detail | Must | Planned |
| 002-dummy-orgatex-recipe | Dummy OrgaTEX recipe | Must | Planned |
| 003-dummy-orgatex-consumption-and-status | Dummy OrgaTEX consumption and status write-back | Must | Planned |
| 004-dummy-scale-readings-and-tare | Dummy scales with simulation and tare | Must | Planned |
| 005-dummy-scanner | Dummy scanner | Must | Planned |
| 006-dummy-printer | Dummy printer | Must | Planned |
| 007-failure-injection-and-reset | Failure injection and reset | Must | Planned |

---

## Dependencies

### Depends On
| Unit | Reason |
|------|--------|
| — | None |

### Depended By
| Unit | Reason |
|------|--------|
| 003-orgatex-integration | Adapter talks to Dummy OrgaTEX |
| 004-device-integration | Adapters talk to Dummy Scale / Scanner / Printer status |
| 005-ticket-printing | Printer adapter talks to Dummy Printer |
| 006-weighing-station-ui | Training panel and E2E rely on control endpoints (through WeighingMS) |

### External Dependencies
| System | Purpose | Risk |
|--------|---------|------|
| — | Self-contained | Low |

---

## Technical Context

### Suggested Technology
Python 3.13, FastAPI, Pydantic (Decimal fields, camelCase aliases), SQLite (consumption + tickets), JSON seed file; Uvicorn on port 8100.

### Integration Points
| Integration | Type | Protocol |
|-------------|------|----------|
| WeighingMS adapters | API | REST/JSON over HTTP |

### Data Storage
| Data | Type | Volume | Retention |
|------|------|--------|-----------|
| Seed batches/recipes | JSON file | 4 batches | Static |
| Consumption postings, tickets, batch status | SQLite (`data/dummy.db`) | Training volume | Until reset |
| Scale/scanner/availability state | In memory | — | Process lifetime / reset |

---

## Constraints

- Contracts are the workbook training contracts; documented as **not** the real OrgaTEX interface.
- Deterministic: exact weights can be set; time-based profiles are computed from elapsed time, not random.
- No import of WeighingMS code; WeighingMS imports nothing from here.

---

## Success Criteria

### Functional
- [ ] `curl :8100/api/batches`, `/api/batches/B-24187`, `/api/batches/B-24187/recipe` return the seed data (Workbook Step 18)
- [ ] Consumption posting stored once per idempotency key and retrievable
- [ ] Both scales simulate dispense/overshoot and exact weights; tare zeros net weight
- [ ] Each system can be made unavailable (503) and restored; reset restores seed

### Non-Functional
- [ ] Weight endpoint responds < 20 ms locally (supports ≥ 10 Hz polling)

### Quality
- [ ] Code coverage > 80%
- [ ] All acceptance criteria met
- [ ] Code reviewed and approved

---

## Bolt Suggestions

| Bolt | Type | Stories | Objective |
|------|------|---------|-----------|
| 001-training-substitutes | Simple | 001, 002, 003 | Project skeleton + Dummy OrgaTEX + seed data |
| 002-training-substitutes | Simple | 004, 005, 006, 007 | Dummy scales, scanner, printer, failure injection, reset |

---

## Notes

Recipes for B-24188, B-24190 and B-24191 are invented training data and must be labelled as such in the seed file (TA-19).
