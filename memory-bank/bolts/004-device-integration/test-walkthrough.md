---
stage: test
bolt: 004-device-integration
created: 2026-10-26T07:00:00Z
---

## Test Report: 004-device-integration

### Summary

- **Tests**: 112/112 passed (23 new in this bolt)
- **Coverage**: 98% (backend total)
- **Static checks**: ruff format/lint and mypy --strict clean (`npm run check`)

### Test Files

- [x] `tests/integration/weighingms/test_device_adapters.py` - exact readings (g and kg), unavailable scale raises (never 0), stale reading (> 2 s) unavailable, tare → net 0, tare failure, calibration status, scans once/in order, cursor survives scanner restart, scanner unavailable (incl. simulated scan), printer probe, training availability round trip
- [x] `tests/unit/weighingms/test_device_status.py` - all-up strip, down/degraded mapping, OrgaTEX probe cached 2 s, only state transitions logged (WARNING down, INFO recovery)
- [x] `tests/api/weighingms/test_devices_api.py` - status endpoint (labels, station, language, last contact), failed devices, calibration expired → DEGRADED, training scan + scanner endpoint, scanner down 503, training availability/simulate/reset, validation error body
- [x] `tests/conftest.py` - `MutableClock` for staleness; container built from in-process dummy clients

### Acceptance Criteria Validation

- ✅ **Readings from both scales as exact quantities; unavailable/stale → `ScaleUnavailable`, never 0**
- ✅ **Tare makes net 0; failure raises and is logged**
- ✅ **Scans delivered once, in order, via cursor; scanner down → 503 `SCANNER_UNAVAILABLE`**
- ✅ **Device status for SCALE 3 kg, SCALE 32 kg, SCANNER, PRINTER, ORGATEX with UP/DOWN/DEGRADED ("CAL EXPIRED")** — DOWN on the next poll after failure injection (≤ 1 s UI poll, ≤ 2 s OrgaTEX probe)
- ✅ **Training passthroughs work**
- ✅ **`npm run check` green**

### Issues Found

- Test-only: `caplog` could not see records because the app's logging setup disables propagation; the test re-enables propagation for its duration.

### Notes

Latency (smoke): dummy weight read median 1.5 ms, p95 1.8 ms — far inside the 50 ms budget for NFR-1.

### Stage checkpoint (delegated, self-validated)

All tests pass; all acceptance criteria verified. **Approved** — bolt complete.
