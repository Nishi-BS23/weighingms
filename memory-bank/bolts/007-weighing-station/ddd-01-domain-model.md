---
stage: model
bolt: 007-weighing-station
created: 2026-10-26T08:51:20Z
---

## Static Model: 002-weighing-station (confirmation, exceptions, completion)

Extends the model of bolt 006 (`bolts/006-weighing-station/ddd-01-domain-model.md`). Stories: 004 confirm, 005 overshoot, 006 supervisor override, 008 quit/abandon, 009 batch completion + write-back trigger, 011 summary and records. The overshoot rule is the Step 24 decision (evidence/STEP-24-overshoot-decision.md): **block and recover, no recalculation**.

### Entities

- **WeighingSession** (aggregate root, extended): new behaviour `confirm`, `override`, `abandon`, `complete`, `mark_synced`, `mark_sync_pending` — *Rules*: confirm/override only on the ACTIVE component; COMPLETED only when all components are DONE; after COMPLETED nothing can be activated, confirmed or abandoned.
- **WeighingRecord** (created by the session, persisted insert-only): `recordId`, `sessionId`, `batchId`, `componentId`, `dyestuffCode`, `dyestuffName`, `target`, `actual`, `toleranceMin`, `toleranceMax`, `result` (IN_TOLERANCE | OVERRIDDEN), `surplus` (OVERRIDDEN over-dose only), `operatorId`, `lotId`, `containerId`, `tare`, `scaleId`, `confirmedAt` — *Rules*: immutable; target and band are snapshots (BR-14).
- **Override**: `overrideId`, `recordId`, `supervisorId`, `reason` (non-empty), `authorisedAt` — *Rules*: only a SUPERVISOR with a matching PIN can authorise; only outside tolerance with net > 0.
- **AuditEvent** (extended types): OVERRIDE (actor = supervisor), ABANDON (actor = operator; detail: component, net at quit).

### Value Objects

- **Evaluation** (extended): `guidance` — for OVER: how to recover (remove excess back into the band / empty and re-tare / supervisor override).
- **ConfirmationContext**: net (re-read at confirm), evaluation, operator, now — built by the application layer from a fresh scale reading, never from the UI.
- **Summary**: components weighed, all within tolerance, overridden count, total dispensed (kg), elapsed, operator, write-back status, per-component results.

### Aggregates

- **WeighingSession** — additional invariants:
  8. `confirm` requires an ACTIVE component and an evaluation with `canConfirm` (within tolerance, scale available, calibration valid); otherwise `OUT_OF_TOLERANCE` / `SCALE_UNAVAILABLE` / `SCALE_CALIBRATION_EXPIRED`.
  9. `override` requires an ACTIVE component, an evaluation outside tolerance with net > 0, an authorised supervisor and a reason; result OVERRIDDEN.
  10. A DONE component records its actual and its record ID; DONE never changes (DR-02).
  11. `abandon` returns the ACTIVE component to PENDING and records nothing for it.
  12. `complete` requires all components DONE (`BATCH_INCOMPLETE`); it sets COMPLETED and sync status PENDING.
  13. `mark_synced` only after a successful (or duplicate-acknowledged) OrgaTEX posting; idempotency key = session ID.

### Domain Events

- **ComponentConfirmed**: Trigger: confirm — Payload: componentId, actual, recordId
- **OverrideAuthorised**: Trigger: override — Payload: componentId, actual, supervisorId (reason in the audit event; PIN never)
- **WeighingAbandoned**: Trigger: quit — Payload: componentId, net at quit
- **BatchCompleted**: Trigger: last component DONE → complete — Payload: completedAt
- **ConsumptionPosted** / **WriteBackPending**: Trigger: OrgaTEX posting succeeded / failed — Payload: consumptionId or reason

### Domain Services

- **ToleranceEvaluator** (extended): adds Step 24 guidance for OVER.
- **SupervisorAuthorisation**: Operations: authorise(pin) → supervisor operator (PBKDF2-SHA256, constant-time compare) — Dependencies: operator directory.
- **ConsumptionBuilder**: Operations: payload(session, records) → OrgaTEX consumption lines — Dependencies: none.
- **SummaryBuilder**: Operations: summary(session, records, operators) — Dependencies: none.

### Repository Interfaces

- **WeighingSessionRepository** (extended): `save_with_record(session, record, override?)` — one transaction, so a record and the DONE state are stored together or not at all (NFR-3).
- **WeighingRecordRepository**: Entity: WeighingRecord — Methods: `for_session`, `for_batch`, `clear` (training reset); insert happens only through `save_with_record`.

### Ubiquitous Language (additions)

- **Over-dose / surplus**: net above the band's maximum; surplus = net − target.
- **Recover**: bring an over-dose back inside the band by removing material, or empty and re-tare to weigh again (Step 24).
- **Override**: supervisor authority (PIN + reason) to accept a weighing outside tolerance.
- **Abandon / Quit**: leave the active component without recording it.
- **Completion**: the moment the last component is DONE; triggers the write-back.
- **Write-back pending**: completion stored locally, OrgaTEX posting still to succeed (retry).

### Story coverage

| Story | Model elements |
|-------|----------------|
| 004-confirm-component-weighing | invariant 8, 10; WeighingRecord; ComponentConfirmed; save_with_record |
| 005-overshoot-handling | Evaluation.guidance; Step 24 rule; invariant 8 (blocked) |
| 006-supervisor-override | Override; SupervisorAuthorisation; invariant 9; OVERRIDE audit |
| 008-quit-and-abandon | invariant 11; ABANDON audit |
| 009-batch-completion | invariant 12, 13; ConsumptionBuilder; BatchCompleted / ConsumptionPosted |
| 011-weighing-summary-and-records | SummaryBuilder; record repository queries |

### Stage checkpoint (delegated, self-validated)

All six stories map to model elements; the overshoot rule follows the recorded Step 24 decision. **Approved** — proceed to Technical Design.
