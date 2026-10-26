---
unit: 002-weighing-station
intent: 001-assisted-dyestuff-weighing
phase: inception
status: complete
unit_type: backend
default_bolt_type: ddd-construction-bolt
created: 2026-10-26T06:40:00.000Z
updated: 2026-10-26T06:40:00.000Z
---

# Unit Brief: Weighing Station (domain core)

## Purpose

Own the weighing business rules and the traceability record. Everything the operator does at the station — select a batch, weigh a component, confirm, override, quit, complete — is decided here, so out-of-tolerance weighings cannot reach production unnoticed (BO-01) and every weighing is traceable (BO-02).

## Scope

### In Scope
- Weighing session aggregate (per batch): start, resume, progression, completion, sync status
- Batch selection rule (selectable statuses)
- Automatic scale selection policy (configurable threshold)
- Tolerance policy and evaluation (zones, inclusive bounds, default rule)
- Active-component weighing context: dyestuff, lot, container, tare, scale, target, band
- Confirmation with server-side weight re-read; immutable weighing records
- Overshoot rule (decided at Workbook Step 24)
- Supervisor override (PIN + reason), audit events
- Quit/abandon; operator identity and sign-in by badge
- Completion trigger for write-back (through `OrgatexPort`) and summary/records queries
- Persistence (SQLAlchemy + Alembic, `weighingms.db`) and session API endpoints

### Out of Scope
- HTTP details of OrgaTEX, scales, scanner, printer (adapters in 003/004/005)
- Ticket composition (005)
- Presentation (006)

---

## Assigned Requirements

| FR | Requirement | Priority |
|----|-------------|----------|
| FR-2 | Batch selection | Must |
| FR-5 | Dyestuff lot | Must |
| FR-6 | Container | Must |
| FR-8 | Scale selection | Must |
| FR-10 | Target quantity | Must |
| FR-11 | Remaining quantity | Must |
| FR-12 | Tolerance | Must |
| FR-13 | Confirmation | Must |
| FR-14 | Overshoot | Must |
| FR-15 | Component progression | Must |
| FR-16 | Batch completion | Must |
| FR-19 | Operator traceability | Must |
| FR-21 | Supervisor override | Must |
| FR-22 | Quit (abandon and exit safely) | Must |
| FR-23 | Completed-batch summary and record review | Must |

---

## Domain Concepts

### Key Entities
| Entity | Description | Attributes |
|--------|-------------|------------|
| WeighingSession (aggregate root) | Weighing of one batch at the station | sessionId, batchId, recipe snapshot, operatorId, status (IN_PROGRESS/COMPLETED), activeComponentId, startedAt, completedAt, syncStatus (NOT_REQUIRED/PENDING/SYNCED/FAILED), syncedAt |
| ComponentProgress | State of one recipe component in the session | componentId, sequence, state (PENDING/ACTIVE/DONE), recordId |
| WeighingRecord | Immutable traceability record | recordId, sessionId, batchId, componentId, dyestuffCode/name, targetQty, actualQty, unit, toleranceMin/Max, result (IN_TOLERANCE/OVERRIDDEN), surplusQty, operatorId, lotId, containerId, tareQty, scaleId, confirmedAt |
| Override | Supervisor authorisation | overrideId, recordId, supervisorId, reason, authorisedAt |
| AuditEvent | Privileged/notable action | eventId, sessionId, type (OVERRIDE/ABANDON/OPERATOR_CHANGE/REPRINT), actorId, detail, occurredAt |
| Operator | Person at the station | operatorId, name, shift, badgeId, role (OPERATOR/SUPERVISOR), pinHash |
| Container | WeighingMS master | containerId, type, tareQty, unit |

### Value Objects
Quantity (Decimal value + unit g/kg, conversion, resolution rounding), ToleranceBand (min, max, inclusive), WeighingZone (UNDER/NEAR/WITHIN/OVER), ScaleAssignment (scaleId, class, label).

### Key Operations
| Operation | Description | Inputs | Outputs |
|-----------|-------------|--------|---------|
| startOrResume | Validate status, create or resume session, set first pending active | batchId, operator | session |
| selectScale | Policy: target ≤ threshold → precision, else floor | target quantity | ScaleAssignment |
| evaluate | Zone, remaining, surplus, canConfirm | net weight, band, scale status | Evaluation |
| activateComponent | Make a pending component active; context incl. lot, container, tare | sessionId, componentId | WeighingContext |
| confirm | Re-read weight, require WITHIN, write record, advance | sessionId | record, session |
| override | Verify supervisor PIN + reason, write OVERRIDDEN record + audit | sessionId, pin, reason | record |
| abandon | Discard attempt, audit, keep confirmed work | sessionId | session |
| complete | When all DONE: complete, trigger write-back | sessionId | session (syncStatus) |
| summary / records | Query results | sessionId / batchId | summary, records |

---

## Story Summary

| Metric | Count |
|--------|-------|
| Total Stories | 11 |
| Must Have | 11 |
| Should Have | 0 |
| Could Have | 0 |

### Stories

| Story ID | Title | Priority | Status |
|----------|-------|----------|--------|
| 001-start-or-resume-weighing-session | Start or resume a weighing session as the signed-in operator | Must | Planned |
| 002-automatic-scale-selection | Automatic scale selection | Must | Planned |
| 003-tolerance-evaluation | Tolerance evaluation, target and remaining | Must | Planned |
| 004-confirm-component-weighing | Confirm a component weighing | Must | Planned |
| 005-overshoot-handling | Overshoot detection and defined response | Must | Planned |
| 006-supervisor-override | Supervisor override | Must | Planned |
| 007-component-progression | Component progression | Must | Planned |
| 008-quit-and-abandon | Quit and abandon safely | Must | Planned |
| 009-batch-completion | Batch completion and write-back trigger | Must | Planned |
| 010-activate-component-weighing-context | Activate a component with its weighing context | Must | Planned |
| 011-weighing-summary-and-records | Weighing summary and record review | Must | Planned |

---

## Dependencies

### Depends On
| Unit | Reason |
|------|--------|
| 003-orgatex-integration | `OrgatexPort` implementation (recipe snapshot, status, write-back) for the application layer |
| 004-device-integration | `ScalePort` implementation (readings, tare, status) for the application layer |

### Depended By
| Unit | Reason |
|------|--------|
| 005-ticket-printing | Completed session and records |
| 006-weighing-station-ui | Session API |

### External Dependencies
| System | Purpose | Risk |
|--------|---------|------|
| (via ports) OrgaTEX, scales | Data and readings | Medium — isolated by ports |

---

## Technical Context

### Suggested Technology
Pure-Python domain (dataclasses, `Decimal`), application services, SQLAlchemy 2.0 repositories with Decimal-as-text columns, Alembic, FastAPI routers. Configuration file for scale threshold/definitions and default tolerance rule.

### Integration Points
| Integration | Type | Protocol |
|-------------|------|----------|
| OrgatexPort | Port (implemented in 003) | Python interface |
| ScalePort | Port (implemented in 004) | Python interface |
| UI | API | REST/JSON |

### Data Storage
| Data | Type | Volume | Retention |
|------|------|--------|-----------|
| Sessions, records, overrides, audit, operators, containers | SQLite `weighingms.db` | Training volume | Permanent (records immutable; reset only in training) |

---

## Constraints

- Domain layer has no FastAPI/SQLAlchemy/HTTP imports.
- Quantities are `Decimal`; no floats.
- Confirmed records, overrides and audit events are insert-only.
- The overshoot rule must not be implemented until the Step 24 decision is recorded.

---

## Success Criteria

### Functional
- [ ] Tolerance boundary tests: 93.4 ✗, 93.5 ✓, 94.0 ✓, 94.5 ✓, 94.6 ✗ (Yellow RGB)
- [ ] Scale rule: 3.000 kg → precision, 3.001 kg → floor; prototype components map correctly
- [ ] Progression Blue → Red → Yellow → Sodium Sulphate → Soda Ash; done not re-selectable
- [ ] Completion only at 5/5; write-back triggered; incomplete → `BATCH_INCOMPLETE`
- [ ] Override requires valid PIN + reason; audited

### Non-Functional
- [ ] Confirm durable before response; records immutable
- [ ] Resume after restart with confirmed components intact

### Quality
- [ ] Code coverage > 80% (domain ~100% of rules)
- [ ] All acceptance criteria met
- [ ] Code reviewed and approved

---

## Bolt Suggestions

| Bolt | Type | Stories | Objective |
|------|------|---------|-----------|
| 006-weighing-station | DDD | 001, 002, 003, 007, 010 | Core session slice: domain model, start/resume, scale rule, tolerance, progression, activate/live/re-tare endpoints, persistence |
| 007-weighing-station | DDD | 004, 005, 006, 008, 009, 011 | Confirmation, overshoot (Step 24 decision), override, quit, completion + write-back trigger, summary |

Both bolts are vertical slices (domain → application → persistence → API) so each ends with working, testable endpoints.

---

## Notes

The prototype's surplus recalculation is a business question, not a requirement (ui-analysis R7). Keep tolerance and overshoot policies isolated so FCI's answers to A-07/A-08 change one place.
