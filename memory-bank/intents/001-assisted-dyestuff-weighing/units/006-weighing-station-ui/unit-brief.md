---
unit: 006-weighing-station-ui
intent: 001-assisted-dyestuff-weighing
phase: inception
status: complete
unit_type: frontend
default_bolt_type: simple-construction-bolt
created: 2026-10-26T06:40:00.000Z
updated: 2026-10-26T06:40:00.000Z
---

# Unit Brief: Weighing Station UI (operator terminal)

## Purpose

Reproduce the functional experience of the supplied prototype as a React + TypeScript application that consumes only the WeighingMS API, and prove the whole product with Playwright end-to-end and failure suites.

## Scope

### In Scope
- Device frame and chrome: bezel caption, top bar (station, crumb, operator chip), step indicator, status strip (devices, EN, clock)
- Screen 1 Select batch: scan prompt + beam, queue table, touch and scan selection
- Screen 2 Weigh: recipe rail, weigh header + meta, scale badge, readout cells, progress bar with band/target line, tolerance caption, status line, surplus panel, keys (Confirm, Re-tare, Quit, Supervisor override) and dialogs
- Screen 3 Confirm & print: summary, per-component results, write-back status + retry, ticket preview, Print ticket, Next batch
- Training panel outside the device frame (simulate dispense/overshoot, reset weighing, simulate scan, failure toggles, reset training data)
- Function keys F1–F4; operator-facing error messages
- Root `npm run dev` integration; Playwright suites (`playwright/`)

### Out of Scope
- Business rules (rendered from API evaluation only)
- Question pins and meeting notes from the prototype (TA-20)

---

## Assigned Requirements

| FR | Requirement | Priority |
|----|-------------|----------|
| FR-30 | Screen 1 — Select batch | Must |
| FR-31 | Screen 2 — Weigh | Must |
| FR-32 | Screen 3 — Confirm & print | Must |
| FR-33 | Station chrome | Must |
| FR-34 | Function keys | Could |

---

## Domain Concepts

### Key Entities
| Entity | Description | Attributes |
|--------|-------------|------------|
| StationView | Current step | queue / weigh / done |
| LiveEvaluation (from API) | Rendered readout state | net, unit, zone, remaining, surplus, surplusPct, canConfirm, scaleAvailable, statusText |
| DeviceStatus (from API) | Strip entries | device, state, label |

### Key Operations
| Operation | Description | Inputs | Outputs |
|-----------|-------------|--------|---------|
| poll live evaluation | ~8 Hz while weighing | sessionId | LiveEvaluation |
| poll device status | every 1 s | — | DeviceStatus[] |
| poll scans | every 300 ms on Screen 1 | cursor | ScanEvent[] |
| actions | select, activate, confirm, re-tare, quit, override, retry sync, print, next batch | ids, inputs | updated state |

---

## Story Summary

| Metric | Count |
|--------|-------|
| Total Stories | 13 |
| Must Have | 12 |
| Should Have | 0 |
| Could Have | 1 |

### Stories

| Story ID | Title | Priority | Status |
|----------|-------|----------|--------|
| 001-station-shell-and-chrome | Station shell, chrome and training panel | Must | Planned |
| 002-batch-queue-screen | Batch queue screen | Must | Planned |
| 003-select-batch-by-touch-or-scan | Select a batch by touch or scan | Must | Planned |
| 004-recipe-rail | Recipe rail with component states | Must | Planned |
| 005-live-weighing-panel | Live weighing panel | Must | Planned |
| 006-weighing-actions | Weighing actions: confirm, re-tare, quit, override | Must | Planned |
| 007-overshoot-surplus-panel | Overshoot surplus panel | Must | Planned |
| 008-completion-summary-screen | Completion summary and write-back status | Must | Planned |
| 009-ticket-preview-and-print | Ticket preview and print | Must | Planned |
| 010-operator-facing-failure-messages | Operator-facing failure messages | Must | Planned |
| 011-function-keys | Function keys F1–F4 | Could | Planned |
| 012-end-to-end-workflow-test | End-to-end workflow test (B-24187) | Must | Planned |
| 013-failure-scenario-tests | Failure scenario tests | Must | Planned |

---

## Dependencies

### Depends On
| Unit | Reason |
|------|--------|
| 003-orgatex-integration | Batch endpoints |
| 004-device-integration | Device status, scans, training passthrough |
| 002-weighing-station | Session API |
| 005-ticket-printing | Ticket preview/print |

### Depended By
| Unit | Reason |
|------|--------|
| — | — |

### External Dependencies
| System | Purpose | Risk |
|--------|---------|------|
| — | Only the WeighingMS API | Low |

---

## Technical Context

### Suggested Technology
React + TypeScript (strict) + Vite; plain CSS ported from the prototype's design tokens; `openapi-typescript` generated types; Vitest + React Testing Library; Playwright Test (TypeScript) with HTML report and video.

### Integration Points
| Integration | Type | Protocol |
|-------------|------|----------|
| WeighingMS API | API | REST/JSON via Vite proxy `/api` |

### Data Storage
| Data | Type | Volume | Retention |
|------|------|--------|-----------|
| Theme preference | localStorage (guarded) | tiny | Browser |

---

## Constraints

- No hard-coded batch, recipe or weight data in components (Workbook Rule 5).
- Zone, canConfirm, remaining and surplus come from the API; only bar geometry is computed in the UI.
- Do not copy the prototype JavaScript; reuse its visual tokens and layout.

---

## Success Criteria

### Functional
- [ ] All three screens and chrome reproduce the prototype (fidelity checklist in ui-analysis.md)
- [ ] Network shows `GET /api/batches`, `/api/batches/B-24187`, `/api/batches/B-24187/recipe` on selection
- [ ] Playwright E2E for B-24187 passes; failure suite passes

### Non-Functional
- [ ] Live weight visible within 200 ms of change
- [ ] Keys ≥ 62 px high; readout ≥ 52 px

### Quality
- [ ] Code coverage > 80% for logic modules
- [ ] All acceptance criteria met
- [ ] Code reviewed and approved

---

## Bolt Suggestions

| Bolt | Type | Stories | Objective |
|------|------|---------|-----------|
| 005-weighing-station-ui | Simple | 001, 002, 003 | Frontend scaffold, chrome, Screen 1 |
| 008-weighing-station-ui | Simple | 004, 005, 006, 007 | Screen 2 |
| 010-weighing-station-ui | Simple | 008, 009, 010, 011 | Screen 3, failure messages, function keys |
| 011-weighing-station-ui | Simple | 012, 013 | Playwright E2E and failure suites, UI validation |

---

## Notes

The prototype's screen switcher becomes a step indicator (TA-20). The training panel replaces the prototype's "Simulate dispense / overshoot / Reset" buttons and is visibly outside the device frame.
