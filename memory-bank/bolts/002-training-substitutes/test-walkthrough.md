---
stage: test
bolt: 002-training-substitutes
created: 2026-10-26T06:47:41Z
---

## Test Report: 001-training-substitutes (bolt 2 of 2)

### Summary

- **Tests**: 51/51 passed (33 new in this bolt)
- **Coverage**: 98% (backend total)
- **Static checks**: ruff format/lint and mypy --strict clean (`npm run check`)

### Test Files

- [x] `tests/unit/dummy_systems/test_scale_simulation.py` - ramp start, monotonic eased rise, exact settling, downward ramp, ramp to zero terminates
- [x] `tests/api/dummy_systems/test_scale_api.py` - scale list/specs, initial reading, exact profile, rounding to resolution, g↔kg conversion, dispense ramp (moving then stable), tare, tare during a ramp, capacity clamp, negative weight 422, unknown scale 404, calibration status and expiry
- [x] `tests/api/dummy_systems/test_scanner_printer_api.py` - scan ordering and cursor, empty scan 422, scanner status, ticket print/list/get, empty ticket 422, unknown ticket 404, printer status
- [x] `tests/api/dummy_systems/test_control_api.py` - each of the five systems → 503 only on its own endpoints and recovers (parametrised), availability snapshot + scale list, unknown system 404, control endpoints unaffected, reset restores seed (status, tickets, scans, scales, availability)
- [x] `tests/conftest.py` - `FakeTicker` for deterministic simulation time

### Acceptance Criteria Validation

- ✅ **Two scales listed with class, label, capacity, resolution, availability, calibration**
- ✅ **Readings rounded to resolution; tare zeroes net; ramps settle exactly at landing and report `stable`**
- ✅ **Exact weights deterministic; capacity clamps readings**
- ✅ **Scanner delivers scans in order with a cursor; printer stores and lists tickets**
- ✅ **Each system can be made unavailable (503) and restored; reset restores seed**
- ✅ **`npm run check` green**

### Issues Found

None in this stage. (Tooling: ruff now declares `weighingms`, `dummy_systems`, `tests` as first-party; `.vscode/settings.json` selects the project `.venv` so the editor stops resolving packages from another project's virtualenv.)

### Notes

Uncovered lines are defensive paths (concurrent duplicate insert, real-clock helpers replaced by fakes in tests).

### Stage checkpoint (delegated, self-validated)

All tests pass and every acceptance criterion is verified. **Approved** — bolt complete.
