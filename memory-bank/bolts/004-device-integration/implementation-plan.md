---
stage: plan
bolt: 004-device-integration
created: 2026-10-26T06:55:01Z
---

## Implementation Plan: 004-device-integration

### Objective
Put the station's peripherals behind ports — `ScalePort`, `ScannerPort`, a printer probe and a training-control port — implement them against the dummy service, and give the station a truthful aggregated device status (scales incl. calibration, scanner, printer, OrgaTEX link) with safe failure detection.

### 1. What will change
New port definitions, HTTP adapters for devices and training control, a device-status service, and WeighingMS endpoints for device status, scans and training passthroughs.

### 2. Files to be created / modified
- `src/weighingms/application/ports.py` — add `ScaleReading`, `ScaleState`, `ScalePort`, `ScanEvent`, `ScannerPort`, `PrinterProbe`, `TrainingControlPort`, `ScaleUnavailable`, `ScannerUnavailable` (modified); `OrgatexPort.ping()` (modified)
- `src/weighingms/application/devices.py` — `DeviceStatusService` (aggregation, OrgaTEX probe cached ≤ 2 s, state-transition logging)
- `src/weighingms/infrastructure/devices/scale_adapter.py` — readings (staleness > 2 s → unavailable), tare, status
- `src/weighingms/infrastructure/devices/peripherals_adapter.py` — scanner cursor + availability, printer availability
- `src/weighingms/infrastructure/devices/training_adapter.py` — dummy control passthrough (availability, reset, simulate, calibration)
- `src/weighingms/infrastructure/orgatex/http_adapter.py` — `ping()` (quiet probe) (modified)
- `src/weighingms/api/devices.py` — `GET /api/devices/status`, `GET /api/scanner/scans`
- `src/weighingms/api/training.py` — `/api/training/scan`, `/availability`, `/reset`, `/scales/{id}/simulate`, `/scales/{id}/calibration`
- `src/weighingms/api/container.py`, `api/app.py`, `api/schemas.py` (modified)
- Tests: `tests/integration/weighingms/test_device_adapters.py`, `tests/api/weighingms/test_devices_api.py`, `tests/unit/weighingms/test_device_status.py`

### 3. Requirements and stories implemented
| Story | Requirements |
|-------|--------------|
| 001-live-weight-from-selected-scale | FR-9 |
| 002-tare-and-re-tare | FR-7 |
| 003-scanner-input | FR-2 (scan path), FR-27 (consumer) |
| 004-device-status-and-failure-detection | FR-24, FR-20 |

### 4. APIs involved
Provided by WeighingMS:
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/devices/status` | strip entries: device, label, state (UP/DOWN/DEGRADED), text, OrgaTEX last contact, language |
| GET | `/api/scanner/scans?after=` | new scans in order + `lastSeq` |
| POST | `/api/training/scan` | simulate a scan (training) |
| GET/PUT | `/api/training/availability[/{system}]` | failure injection (training) |
| POST | `/api/training/reset` | reset dummy data (WeighingMS training state joins in bolt 006) |
| POST | `/api/training/scales/{scaleId}/simulate` | explicit simulation (the "landing from the active component" shortcut is added with sessions in bolt 006) |
| PUT | `/api/training/scales/{scaleId}/calibration` | calibration expiry for failure tests |

Used (dummy training contracts): `/api/scales/{id}/weight|status|tare`, `/api/scanner/scans|status`, `/api/printer/status`, `/api/control/*`, OrgaTEX `GET /api/batches` (probe).

### 5. How it will be tested
- Integration (real adapters ↔ real dummy in-process): reading values/units, unavailable via failure injection → `ScaleUnavailable` (never weight 0), stale reading → unavailable (injected clock), tare → net 0, status with calibration, scan cursor ordering, scanner/printer availability, training passthroughs.
- Unit: device-status aggregation rules and transition logging with fake ports; OrgaTEX probe caching.
- API: `/api/devices/status` for all-up, scale down, calibration expired, OrgaTEX down, scanner down; `/api/scanner/scans`; training endpoints.
- Latency: reading path through the adapter < 50 ms locally (smoke measurement).

### Technical Approach
- Adapters take an `httpx.Client` (1 s timeout) and an injectable clock; transport errors/5xx → `*Unavailable`.
- Device-status service never raises: each device is probed independently and reported UP/DOWN/DEGRADED.
- Failure logging: WARNING on state transitions (UP→DOWN etc.) instead of on every poll, so a down device does not flood the log; explicit actions (tare) log failures at WARNING.

### Acceptance Criteria
- [ ] Readings from both scales as exact quantities; unavailable/stale → `ScaleUnavailable`, never 0
- [ ] Tare makes net 0; failure raises and is logged
- [ ] Scans delivered once, in order, via cursor; scanner down → 503 `SCANNER_UNAVAILABLE`
- [ ] Device status: SCALE 3 kg, SCALE 32 kg, SCANNER, PRINTER, ORGATEX with UP/DOWN/DEGRADED ("CAL EXPIRED"), DOWN within 2 s of failure injection
- [ ] Training passthroughs work
- [ ] `npm run check` green

### Checkpoint — plan review (delegated, self-validated)
Covers all four stories; protocols isolated behind ports (A-05 risk); fail-safe semantics (never 0 on failure); testable without hardware. **APPROVE PLAN.**
