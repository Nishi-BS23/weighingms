---
unit: 004-device-integration
intent: 001-assisted-dyestuff-weighing
phase: inception
status: complete
unit_type: backend
default_bolt_type: simple-construction-bolt
created: 2026-10-26T06:40:00.000Z
updated: 2026-10-26T06:40:00.000Z
---

# Unit Brief: Device Integration (scales, scanner, device status)

## Purpose

Isolate the station's peripherals behind ports and give WeighingMS a truthful, safe view of them: live weight from the selected scale, tare commands, scanned codes, and the status of every device and the OrgaTEX link.

## Scope

### In Scope
- `ScalePort` implementation: list scales, read weight, tare, status (incl. calibration), staleness detection (> 2 s → unavailable)
- `ScannerPort` implementation: scan cursor (deliver each scan once, in order), status
- Device status aggregation: scale-3kg, scale-32kg, scanner, printer (status only), OrgaTEX link (from 003's last contact)
- WeighingMS endpoints: `GET /api/devices/status`, `GET /api/scanner/scans?after=`, training passthrough `POST /api/training/...` to dummy control
- Logging of device failures (IR-09)

### Out of Scope
- Tolerance and confirm rules (002) — this unit only reports readings and availability
- Printing (005)

---

## Assigned Requirements

| FR | Requirement | Priority |
|----|-------------|----------|
| FR-7 | Tare | Must |
| FR-9 | Live weight | Must |
| FR-20 | Scale, scanner and printer failure | Must |
| FR-24 | Device and connection status visibility | Must |

---

## Domain Concepts

### Key Entities
| Entity | Description | Attributes |
|--------|-------------|------------|
| ScaleReading | One reading | scaleId, gross, net, unit, stable, readAt |
| ScaleStatus | Availability | scaleId, available, calibrationDue, calibrationValid |
| ScanEvent | Scanned code | seq, code, scannedAt |
| DeviceStatus | Strip entry | device, state (UP/DOWN/DEGRADED), label, since |

### Key Operations
| Operation | Description | Inputs | Outputs |
|-----------|-------------|--------|---------|
| readWeight | Current reading of a scale | scaleId | ScaleReading or Unavailable |
| tare | Zero a scale | scaleId | ScaleReading |
| scansAfter | New scans since cursor | seq | ScanEvent[] |
| deviceStatus | Aggregate status | — | DeviceStatus[] |

---

## Story Summary

| Metric | Count |
|--------|-------|
| Total Stories | 4 |
| Must Have | 4 |
| Should Have | 0 |
| Could Have | 0 |

### Stories

| Story ID | Title | Priority | Status |
|----------|-------|----------|--------|
| 001-live-weight-from-selected-scale | Live weight from the selected scale | Must | Planned |
| 002-tare-and-re-tare | Tare and re-tare | Must | Planned |
| 003-scanner-input | Scanner input | Must | Planned |
| 004-device-status-and-failure-detection | Device status and failure detection | Must | Planned |

---

## Dependencies

### Depends On
| Unit | Reason |
|------|--------|
| 001-training-substitutes | Dummy Scale/Scanner/Printer contracts |

### Depended By
| Unit | Reason |
|------|--------|
| 002-weighing-station | `ScalePort` for evaluation, confirm, tare |
| 006-weighing-station-ui | Device status, scans |

### External Dependencies
| System | Purpose | Risk |
|--------|---------|------|
| Scales, scanner, printer (Dummies in training) | Readings, scans, status | High in reality (A-05); Low in training |

---

## Technical Context

### Suggested Technology
`httpx` clients with 1 s timeout; Pydantic models; FastAPI routers. Base URL from configuration (`DEVICES_BASE_URL`, default `http://127.0.0.1:8100`).

### Integration Points
| Integration | Type | Protocol |
|-------------|------|----------|
| Dummy Scale / Scanner / Printer | API | REST/JSON |
| UI | API | REST/JSON (polling) |

### Data Storage
| Data | Type | Volume | Retention |
|------|------|--------|-----------|
| Scan cursor, last readings | In memory | — | Process |

---

## Constraints

- A failure to read is reported as unavailable, never as weight 0.
- Weight read path must support ≥ 5 Hz polling with < 50 ms added latency.

---

## Success Criteria

### Functional
- [ ] Reading from `scale-3kg` and `scale-32kg` returned as decimal strings with unit
- [ ] Tare makes net ≈ 0
- [ ] Each scan delivered exactly once in order
- [ ] Device down → status DOWN within 2 s

### Non-Functional
- [ ] Added latency < 50 ms per reading on localhost

### Quality
- [ ] Code coverage > 80%
- [ ] All acceptance criteria met
- [ ] Code reviewed and approved

---

## Bolt Suggestions

| Bolt | Type | Stories | Objective |
|------|------|---------|-----------|
| 004-device-integration | Simple | 001, 002, 003, 004 | Scale/scanner adapters, device status |

---

## Notes

Real indicators may push readings over serial at ≥ 10 Hz (IR-10); keep the port shape (latest reading + status) so a streaming implementation can replace polling.
