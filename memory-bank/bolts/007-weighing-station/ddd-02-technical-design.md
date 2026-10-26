---
stage: design
bolt: 007-weighing-station
created: 2026-10-26T08:51:49Z
---

## Technical Design: 002-weighing-station (confirmation, exceptions, completion)

### Architecture Pattern

Same hexagonal structure as bolt 006. New use cases live in `SessionService`; the write-back goes through `OrgatexPort.post_consumption` (bolt 003 adapter, idempotent). Mutations run under the service lock; a confirm/override writes the record and the session state in **one SQLite transaction**.

### Layer Structure

```text
Presentation   api/sessions.py (+ confirm, override, quit, complete, sync, summary), api/records.py
Application    application/sessions.py (+ use cases), application/summary.py
Domain         domain/weighing/session.py (+ behaviour), records.py, evaluation.py (+ guidance),
               domain/operators.py (+ PIN verification)
Infrastructure persistence: migration 0002 (weighing_records, overrides), repositories (+ records)
```

### API Design

- **POST /api/sessions/{id}/confirm** — Request: none (the backend re-reads the scale) — Response: `SessionOut` (next component active, or session COMPLETED with write-back result). Errors: 409 `OUT_OF_TOLERANCE`, 409 `SCALE_CALIBRATION_EXPIRED`, 503 `SCALE_UNAVAILABLE`, 409 `NO_ACTIVE_COMPONENT`, 409 `SESSION_COMPLETED`.
- **POST /api/sessions/{id}/override** — Request: `{supervisorPin, reason}` — Response: `SessionOut`. Errors: 403 `OVERRIDE_NOT_AUTHORISED`, 422 (empty reason), 409 `OVERRIDE_NOT_NEEDED` (within tolerance or nothing on the scale), 503 `SCALE_UNAVAILABLE`.
- **POST /api/sessions/{id}/quit** — Response: `SessionOut` (no active component). Errors: 409 `SESSION_COMPLETED`.
- **POST /api/sessions/{id}/complete** — Response: `SessionOut`. Errors: 409 `BATCH_INCOMPLETE`. Idempotent for completed sessions.
- **POST /api/sessions/{id}/sync** — retry write-back — Response: `SessionOut` (syncStatus SYNCED or still PENDING).
- **GET /api/sessions/{id}/summary** — Response: `SummaryOut {completed, componentsWeighed {done,total}, allWithinTolerance, overriddenCount, totalDispensed (kg), elapsedSeconds, elapsedText, operatorName, writeBack {status, at, consumptionId}, results[]}`.
- **GET /api/weighing-records?batchId=** — Response: `RecordOut[]` with the full traceability set.
- **LiveOut** gains `guidance` (Step 24 recovery text when OVER).

### Data Model

Alembic revision **0002**:

- **weighing_records**: Columns: record_id (PK), session_id (FK), batch_id (index), component_id, dyestuff_code, dyestuff_name, target_value, unit, actual_value, tolerance_min, tolerance_max, result, surplus_value, operator_id, lot_id, container_id, tare_value, tare_unit, scale_id, confirmed_at — Relationships: n..1 weighing_sessions; unique (session_id, component_id) so a component is recorded once
- **overrides**: Columns: override_id (PK), record_id (FK, unique), supervisor_id, reason, authorised_at

Quantities are DecimalText. No UPDATE/DELETE paths exist for either table except the training reset.

### Security Design

- **Supervisor PIN**: PBKDF2-SHA256 (100 000 iterations, per-user salt) from configuration; `hmac.compare_digest`; the PIN is never logged, echoed or stored; a failed attempt is logged without the PIN.
- **Confirm/override never trust the client**: the backend re-reads the scale and re-evaluates.
- **Audit**: OVERRIDE (supervisor, reason, net, band) and ABANDON events, insert-only.

### NFR Implementation

- **NFR-3 durability**: record + session state committed in one transaction (WAL, synchronous=FULL) before the response.
- **NFR-5 idempotent write-back**: idempotency key = session ID; a duplicate acknowledgement is treated as success.
- **NFR-12 immutability**: unique (session_id, component_id); no update/delete code paths.
- **Continuity (TA-13)**: an OrgaTEX failure at completion leaves the session COMPLETED with sync PENDING; `/sync` retries.
- **NFR-11**: totals computed with Decimal after converting every actual to kg.

### Integration points

- `ScalePort.read_weight/status` (fresh, uncached calibration check) at confirm and override.
- `OrgatexPort.post_consumption` then `set_batch_status(WEIGHED)` at completion and on retry.

### Stage checkpoint (delegated, self-validated)

API, schema, security and NFR handling defined for all six stories. **Approved** — proceed to ADR analysis.
