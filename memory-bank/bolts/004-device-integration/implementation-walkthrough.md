---
stage: implement
bolt: 004-device-integration
created: 2026-10-26T06:58:25Z
---

## Implementation Walkthrough: 004-device-integration

### Summary

The station's peripherals are now behind ports: scales (readings, tare, status), scanner (ordered scans), printer (availability probe) and a training-control port for the training substitutes. A device-status service aggregates scales, scanner, printer and the OrgaTEX link into strip entries (UP/DOWN/DEGRADED), and WeighingMS exposes device status, scanned codes and training passthroughs.

### Structure Overview

Port definitions sit in the application layer; HTTP implementations live in `infrastructure/devices` and share one call helper that turns transport errors and error statuses into the port's *Unavailable error. The device-status service probes each device independently, caches the OrgaTEX probe for 2 seconds, and logs only state transitions. The composition root now builds every adapter from two HTTP clients (OrgaTEX and devices), which tests replace with the in-process dummy app.

### Completed Work

- [x] `src/weighingms/application/ports.py` - `ScalePort`, `ScannerPort`, `PrinterProbe`, `TrainingControlPort`, reading/state/scan DTOs, `ScaleUnavailable`, `ScannerUnavailable`; `OrgatexPort.ping`
- [x] `src/weighingms/application/devices.py` - device-status aggregation, OrgaTEX probe cache, transition logging
- [x] `src/weighingms/clock.py` - injectable wall clock and ticker
- [x] `src/weighingms/infrastructure/devices/contract.py` - dummy device wire models
- [x] `src/weighingms/infrastructure/devices/http.py` - shared call/parse helpers with error translation
- [x] `src/weighingms/infrastructure/devices/scale_adapter.py` - readings (stale > 2 s → unavailable), tare (failure logged), status
- [x] `src/weighingms/infrastructure/devices/peripherals_adapter.py` - scanner cursor (handles scanner restart) and availability; printer probe
- [x] `src/weighingms/infrastructure/devices/training_adapter.py` - availability, reset, simulate, calibration, simulated scan
- [x] `src/weighingms/infrastructure/orgatex/http_adapter.py` - quiet `ping` probe (DEBUG log)
- [x] `src/weighingms/api/devices.py` - `GET /api/devices/status`, `GET /api/scanner/scans`
- [x] `src/weighingms/api/training.py` - `/api/training/scan|availability|reset|scales/{id}/simulate|scales/{id}/calibration`
- [x] `src/weighingms/api/container.py`, `api/app.py` - wiring, reset hooks for later training state

### Key Decisions

- **Never 0 on failure**: any failed or stale read raises `ScaleUnavailable`; the UI will show "—" and block confirmation.
- **Transition logging**: WARNING when a device goes DOWN/DEGRADED, INFO when it recovers — no log flood while polling.
- **OrgaTEX link probe cached 2 s**: the strip is fresh (FR-24 ≤ 2 s) without hammering OrgaTEX.
- **Simulated scan goes through the scanner endpoint**: it fails when the scanner is "down", like a real scanner would.

### Deviations from Plan

None. (As planned, the "simulate from the active component" shortcut arrives with sessions in bolt 006.)

### Dependencies Added

None.

### Developer Notes

Smoke run: all UP; scale-32kg down + scale-3kg calibration expired → "DOWN OFFLINE" / "DEGRADED CAL EXPIRED" with WARNING transition logs; simulated scan visible via `/api/scanner/scans`; training reset → all UP. Dummy weight read median 1.5 ms, p95 1.8 ms.

### Stage checkpoint (delegated, self-validated)

Deliverables complete; lint/types clean; existing tests green. **Approved** — proceed to Test.
