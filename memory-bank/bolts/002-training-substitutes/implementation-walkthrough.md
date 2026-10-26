---
stage: implement
bolt: 002-training-substitutes
created: 2026-10-26T06:46:05Z
---

## Implementation Walkthrough: 001-training-substitutes (bolt 2 of 2)

### Summary

The training-substitutes service now simulates both scales (continuous eased readings, tare, calibration, deterministic exact weights), a barcode scanner and a ticket printer, and every external system can be switched unavailable or reset to the seed state through training control endpoints.

### Structure Overview

Each dummy device has its own package with models, state and router. Scale state is held in a thread-safe bank whose readings are computed lazily from elapsed monotonic time by a pure ramp function. Availability is a shared registry turned into per-system FastAPI dependencies, so routers stay unaware of failure injection. One SQLite engine is shared by the OrgaTEX and printer stores; scanner and scale state is in memory. Control endpoints sit outside every availability check.

### Completed Work

- [x] `src/dummy_systems/common/clock.py` - millisecond reading clock and monotonic ticker alongside the second-precision clock
- [x] `src/dummy_systems/common/models.py` - shared `DeviceStatus`
- [x] `src/dummy_systems/control/availability.py` - availability registry for the five systems and 503 dependency
- [x] `src/dummy_systems/control/routes.py` - availability get/set, scale simulate, calibration, reset
- [x] `src/dummy_systems/scale/simulation.py` - pure eased ramp (prototype pour behaviour), both directions
- [x] `src/dummy_systems/scale/bank.py` - scale specs (3 kg precision in g, 32 kg floor in kg), readings rounded to resolution, tare (ramp continues relative to new tare), simulation, calibration, capacity clamp, unit conversion
- [x] `src/dummy_systems/scale/models.py` - scale info, status, reading, simulation and calibration requests
- [x] `src/dummy_systems/scale/routes.py` - list, status, weight, tare
- [x] `src/dummy_systems/scanner/queue.py` - ordered scan queue with cursor
- [x] `src/dummy_systems/scanner/routes.py` - scan, scans after cursor, status
- [x] `src/dummy_systems/printer/store.py` - ticket request/receipt models and SQLite ticket store
- [x] `src/dummy_systems/printer/routes.py` - print, list, get, status
- [x] `src/dummy_systems/app.py` - wires all routers, shared engine, availability on OrgaTEX, reset of all state
- [x] `src/dummy_systems/orgatex/store.py` - now constructed from the shared engine (unused `open` factory removed)

### Key Decisions

- **Lazy, time-based simulation**: no background threads; readings are a pure function of elapsed time, so tests drive a fake ticker and get exact values.
- **WeighingMS computes landing values**: the dummy only knows "ramp to X" or "exact X"; tolerance knowledge stays in WeighingMS (dispense/overshoot/below are labels for the trainer).
- **Status also returns 503 while unavailable**: a disconnected device cannot report its status; the scale list still answers so the station can show which scale is down.
- **Printer prints rendered lines**: WeighingMS composes ticket content (configurable, IR-16); the printer stores what it was sent.

### Deviations from Plan

None.

### Dependencies Added

None.

### Developer Notes

Calibration due defaults to 180 days after start/reset; failure tests set it into the past through `/api/control/scales/{id}/calibration`.

### Stage checkpoint (delegated, self-validated)

All deliverables in place; lint, format and strict typing pass; the existing 18 tests still pass. **Approved** — proceed to Test.
