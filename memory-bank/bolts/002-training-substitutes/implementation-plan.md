---
stage: plan
bolt: 002-training-substitutes
created: 2026-10-26T06:43:00Z
---

## Implementation Plan: 001-training-substitutes (bolt 2 of 2)

### Objective
Complete the training-substitutes service: two simulated scales with continuous readings, tare, calibration and deterministic simulation profiles; a dummy scanner; a dummy printer; failure injection for every external system; and a reset to the seed state.

### 1. What will change
New `scale`, `scanner`, `printer` and `control` packages in `src/dummy_systems`; the OrgaTEX router gains the availability dependency; the app factory wires everything with injectable clocks.

### 2. Files to be created / modified
- `src/dummy_systems/control/availability.py` — availability registry for `orgatex`, `scale-3kg`, `scale-32kg`, `scanner`, `printer` + FastAPI dependency raising 503 `SYSTEM_UNAVAILABLE`
- `src/dummy_systems/control/routes.py` — `GET /api/control/availability`, `PUT /api/control/availability/{system}`, `POST /api/control/reset`, `POST /api/control/scales/{scaleId}/simulate`, `PUT /api/control/scales/{scaleId}/calibration`
- `src/dummy_systems/scale/models.py`, `simulation.py` (pure ramp maths), `bank.py` (scale state, thread-safe), `routes.py`
- `src/dummy_systems/scanner/models.py`, `queue.py`, `routes.py`
- `src/dummy_systems/printer/models.py`, `store.py` (SQLite), `routes.py`
- `src/dummy_systems/common/clock.py` — add millisecond UTC clock and monotonic ticker type
- `src/dummy_systems/app.py` — wire the new routers and the availability dependency (modified)
- Tests: `tests/unit/dummy_systems/test_scale_simulation.py`, `tests/api/dummy_systems/test_scale_api.py`, `test_scanner_printer_api.py`, `test_control_api.py`; `tests/conftest.py` gains a controllable ticker (modified)

### 3. Requirements and stories implemented
| Story | Requirements |
|-------|--------------|
| 004-dummy-scale-readings-and-tare | FR-26, FR-9 (source), FR-7 (receiver) |
| 005-dummy-scanner | FR-27, FR-2 (scan source) |
| 006-dummy-printer | FR-28, FR-18 (receiver) |
| 007-failure-injection-and-reset | FR-29, FR-20 (simulation) |

### 4. APIs involved (training contracts)
| Method | Path |
|--------|------|
| GET | `/api/scales` |
| GET | `/api/scales/{scaleId}/status` |
| GET | `/api/scales/{scaleId}/weight` → `{scaleId, gross, tare, net, stable, readAt}` |
| POST | `/api/scales/{scaleId}/tare` |
| POST | `/api/scanner/scans`, GET `/api/scanner/scans?after=`, GET `/api/scanner/status` |
| POST | `/api/tickets`, GET `/api/tickets`, GET `/api/tickets/{ticketId}`, GET `/api/printer/status` |
| GET/PUT/POST | `/api/control/...` (availability, reset, simulate, calibration) — never affected by availability |

### 5. How it will be tested
- Pure unit tests of the ramp with a fake ticker: monotonic rise, easing, exact landing, downward ramp (removing excess), settles → stable.
- API tests: scale list/specs, reading rounding to resolution (0.1 g / 0.001 kg), tare → net 0, tare during a ramp continues relative to the new tare, exact profile, capacity clamp, unit conversion (g ↔ kg), unknown scale 404, calibration expiry visible in status.
- Scanner ordering and cursor; printer store/list/get; 422s.
- Availability: each toggle → 503 on exactly that system's endpoints; control endpoints unaffected; reset restores seed (status, consumption, tickets, scans, scales, availability).

### Technical Approach
- Simulation reproduces the prototype's pour (ui-analysis R14): every 34 ms, step = max(0.4% of landing, 5.5% of remaining), computed lazily on read from elapsed time — no background threads. Arithmetic in `Decimal`; time from an injectable monotonic ticker.
- Native units: `scale-3kg` grams (resolution 0.1 g, capacity 3 kg), `scale-32kg` kilograms (resolution 0.001 kg, capacity 32 kg). Requests in either unit are converted exactly.
- Calibration due date defaults to 180 days after startup/reset; a control endpoint can set it into the past for failure tests.
- Thread safety: scale bank and scanner queue guarded by locks (sync endpoints run in a thread pool).

### Acceptance Criteria
- [ ] Two scales listed with class, label, capacity, resolution, availability, calibration
- [ ] Readings rounded to resolution; tare zeroes net; ramps settle exactly at landing and report `stable`
- [ ] Exact weights are deterministic; capacity clamps readings
- [ ] Scanner delivers scans in order with a cursor; printer stores and lists tickets
- [ ] Each system can be made unavailable (503) and restored; reset restores seed
- [ ] `npm run check` green

### Checkpoint — plan review (delegated, self-validated)
Plan covers every acceptance criterion of stories 004–007, keeps the dummies free of WeighingMS rules (WeighingMS computes landing values), uses the agreed contracts, and is fully testable without hardware. **APPROVE PLAN.**
