---
stage: design
bolt: 006-weighing-station
created: 2026-10-26T07:13:36Z
---

## Technical Design: 002-weighing-station (core session slice)

### Architecture Pattern

Hexagonal (ports and adapters), as already used by bolts 003–004. The weighing domain is pure Python with `Decimal`; application services orchestrate the aggregate, the repositories and the ports (`OrgatexPort`, `ScalePort`); SQLAlchemy repositories and FastAPI routers are adapters. One station → no event bus; domain events become log lines and audit rows.

### Layer Structure

```text
┌──────────────────────────────────────────────┐
│ Presentation  api/sessions.py, api/operators.py, api/training.py (simulate)
├──────────────────────────────────────────────┤
│ Application   application/sessions.py (SessionService)
│               application/operators.py (OperatorService)
├──────────────────────────────────────────────┤
│ Domain        domain/weighing/session.py (aggregate), evaluation.py,
│               containers.py, display.py, events.py; operator.py
├──────────────────────────────────────────────┤
│ Infrastructure infrastructure/persistence/ (engine, DecimalText type,
│               tables, repositories, Alembic migrations)
└──────────────────────────────────────────────┘
```

Responsibilities: the domain enforces invariants and evaluates weight; the application layer loads/saves the aggregate, talks to ports, records audit events and holds a process-wide lock around mutations (single station, SQLite); presentation maps to camelCase DTOs with decimal-string quantities.

### API Design

- **POST /api/sessions** — Request: `{batchId}` — Response: `SessionOut` (201 started / 200 resumed). Errors: 404 `BATCH_NOT_FOUND`, 409 `BATCH_NOT_SELECTABLE`, 503 `ORGATEX_UNAVAILABLE` (only when no session exists).
- **GET /api/sessions/{sessionId}** — Response: `SessionOut`. 404 `SESSION_NOT_FOUND`.
- **POST /api/sessions/{sessionId}/components/{componentId}/activate** — Response: `SessionOut` (active context filled). 409 `COMPONENT_ALREADY_DONE`, `SESSION_COMPLETED`.
- **GET /api/sessions/{sessionId}/live** — Response: `LiveOut` `{componentId, scaleId, net|null, remaining, surplus|null, surplusPct|null, zone, canConfirm, scaleAvailable, calibrationValid, stable, statusText, allowedActions}`. Never fails because of the scale: an unavailable scale yields zone OFFLINE.
- **POST /api/sessions/{sessionId}/retare** — Response: `LiveOut`. 503 `SCALE_UNAVAILABLE`.
- **GET /api/operators/current** — Response: `OperatorOut {operatorId, name, shift, role}`.
- **POST /api/operators/sign-in** — Request: `{badgeId}` — Response: `OperatorOut`. 404 `OPERATOR_NOT_FOUND`.
- **POST /api/training/simulate** — Request: `{sessionId, kind: dispense|overshoot|below}` — computes the landing net from the active component (dispense = target + 0.4·tol; overshoot = target + 4.8·tol; below = 0.8·target; prototype R15) and drives the training scale. Training mode only.
- **POST /api/training/reset** — additionally clears WeighingMS sessions/records/audit and restores the default operator (reset hook). Training mode only.

`SessionOut`: `sessionId, batchId, orderRef, machineRef, shadeCode, recipeId, status, startedAt, completedAt, syncStatus, progress {done,total}, activeComponentId, active {componentId, containerId, tare, scale, band, displayMax}|null, components [{componentId, sequence, dyestuffCode, name, shortName, colourHex, target, tolerance, scale, lotId, state, actual|null}]`.

### Data Model

SQLite `data/weighingms.db` (WAL, synchronous=FULL), quantities stored as text by a `DecimalText` column type; schema via Alembic (revision 0001 in this bolt; 0002 adds records/overrides in bolt 007).

- **weighing_sessions**: Columns: session_id (PK), batch_id, station_id, status, started_by, started_at, completed_at, sync_status, synced_at, consumption_id, active_component_id, recipe (JSON snapshot) — Relationships: 1..n session_components; partial unique index on batch_id WHERE status = 'IN_PROGRESS' (invariant 1)
- **session_components**: Columns: session_id + component_id (PK), sequence, state, container_id, tare_value, tare_unit, activated_at, record_id — Relationships: n..1 weighing_sessions
- **operators**: Columns: operator_id (PK), name, shift, badge_id (unique), role, pin_hash — seeded from configuration
- **station_state**: Columns: key (PK), value — holds current_operator_id
- **audit_events**: Columns: event_id (PK), session_id, type, actor_id, detail (JSON), occurred_at — insert-only

Containers are master data in `config/station.toml` (`[[containers]]` with dyestuff codes, plus default container per scale class).

### Security Design

- **Training endpoints**: mounted only when `station.training_mode = true` in configuration (see ADR candidate).
- **Operator identity**: badge ID only (training-grade, TA-09); operator change audited.
- **Supervisor PIN** *(used in bolt 007)*: stored as PBKDF2-SHA256 hash with salt in configuration, compared in constant time, never logged.
- **Input validation**: Pydantic models; IDs used only as lookup keys; no SQL built from strings (SQLAlchemy).

### NFR Implementation

- **NFR-1 live weight ≤ 200 ms**: `/live` does one session read (indexed primary key) + one scale read (~2 ms measured); UI polls every ~120 ms; polling logs at DEBUG.
- **NFR-3 durability**: SQLite WAL + synchronous=FULL; each mutation commits before the response.
- **NFR-4 resume**: sessions and component states are persisted; selecting the batch again returns the open session.
- **NFR-11 exact arithmetic**: Decimal only; DecimalText columns; JSON snapshot stores decimals as strings.
- **NFR-13 configurability**: threshold, default tolerance, containers, operators, training mode from `config/station.toml`.
- **Fail safe**: scale unavailable/stale or calibration expired → `canConfirm = false` and zone OFFLINE / status text explains.

### Integration points

- `OrgatexPort.get_batch/get_recipe` at session start (snapshot); `set_batch_status(WEIGHING)` best effort (failure logged, weighing continues).
- `ScalePort.tare` on activation and re-tare; `ScalePort.read_weight/status` for live evaluation.

### Stage checkpoint (delegated, self-validated)

Pattern, layers, API contracts, schema, security and NFR approach are defined and consistent with the standards. **Approved** — proceed to ADR analysis.
