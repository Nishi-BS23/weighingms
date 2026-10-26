---
stage: model
bolt: 006-weighing-station
created: 2026-10-26T07:12:40Z
---

## Static Model: 002-weighing-station

Scope of this bolt: stories 001 (start/resume session), 002 (scale selection), 003 (tolerance evaluation), 007 (component progression), 010 (activate component with weighing context). The aggregate is modelled completely so bolt 007 (confirmation, overshoot, override, quit, completion) extends it without reshaping; elements marked *(007)* are implemented there.

### Entities

- **WeighingSession** (aggregate root): `sessionId`, `batchId`, `stationId`, `recipe` (RecipeSnapshot), `startedBy` (operatorId), `status` (IN_PROGRESS | COMPLETED), `startedAt`, `completedAt`, `syncStatus` (NOT_SYNCED | PENDING | SYNCED), `syncedAt`, `consumptionId`, `components` (ComponentProgress per recipe component), `activeComponentId` — *Rules*: only a released batch can start a session; at most one ACTIVE component; DONE is terminal; COMPLETED only when every component is DONE *(007)*; the recipe snapshot never changes after start.
- **ComponentProgress** (entity inside the aggregate): `componentId`, `sequence`, `state` (PENDING | ACTIVE | DONE), `activation` (Activation, while ACTIVE), `recordId` *(007)* — *Rules*: PENDING → ACTIVE (activate), ACTIVE → PENDING (another component activated, or quit *(007)*), ACTIVE → DONE (confirm/override *(007)*); DONE never changes.
- **WeighingRecord** *(007)*: immutable traceability record — `recordId`, `sessionId`, `batchId`, `componentId`, dyestuff code/name, target, actual, unit, tolerance min/max, `result` (IN_TOLERANCE | OVERRIDDEN), surplus, operator, lot, container, tare, scale, `confirmedAt` — *Rules*: insert-only (DR-02).
- **Operator**: `operatorId`, `name`, `shift`, `badgeId`, `role` (OPERATOR | SUPERVISOR), `pinHash` (supervisors) — *Rules*: the station always has exactly one current operator (TA-09); changing it is audited.
- **Container** (WeighingMS master data): `containerId`, `type` (BUCKET | DRUM), `tare` (Quantity), `dyestuffCodes` it is assigned to — *Rules*: one container per component (TA-08); a scale class has a default container when no assignment exists.
- **AuditEvent**: `eventId`, `sessionId?`, `type` (OPERATOR_CHANGE; OVERRIDE, ABANDON, REPRINT *(007/009)*), `actorId`, `detail`, `occurredAt` — *Rules*: insert-only.

### Value Objects

- **Quantity**: decimal value + unit (g | kg) — exact; conversion g↔kg; display precision g 1 dp, kg 3 dp; never float.
- **ToleranceBand**: target, ±tolerance, source (RECIPE | DEFAULT) → inclusive min/max.
- **ScaleDefinition**: scaleId, class (PRECISION | FLOOR), label, strip label.
- **ComponentSpec**: componentId, sequence, dyestuffCode, name, shortName, colourHex, target, band, scale, lotId — what the recipe snapshot holds per component (scale and band fixed at session start).
- **RecipeSnapshot**: recipeId, version, shadeCode, orderRef, machineRef, components (ComponentSpec, ordered by sequence).
- **Activation**: containerId, tare (Quantity), activatedAt — the context captured when a component becomes ACTIVE.
- **WeighingZone**: UNDER | NEAR | WITHIN | OVER | OFFLINE — NEAR is a visual cue (net ≥ 90% of target, below the band) (TA-05); OFFLINE when no trustworthy reading exists.
- **Evaluation**: zone, net (or none), remaining, surplus, surplusPct, canConfirm, scaleAvailable, calibrationValid, statusText, allowedActions.
- **DisplayMax**: bar full scale ≈ 4/3 × target rounded up to a tidy value (ui-analysis R12) — display only.

### Aggregates

- **WeighingSession**: Members: ComponentProgress (+ Activation) — Invariants:
  1. Exactly one IN_PROGRESS session per batch.
  2. While IN_PROGRESS, at most one component is ACTIVE; a fresh session activates the lowest-sequence PENDING component.
  3. Activating a PENDING component returns the previously ACTIVE one to PENDING.
  4. A DONE component cannot be activated (`COMPONENT_ALREADY_DONE`).
  5. Progress = DONE count / component count.
  6. The recipe snapshot (targets, bands, scales, lots) is fixed at start; later OrgaTEX changes do not alter it (Brief BR-14).
  7. *(007)* Confirm requires an ACTIVE component and an Evaluation with `canConfirm`; COMPLETED requires all DONE.

### Domain Events

- **SessionStarted**: Trigger: new session for a QUEUED batch — Payload: sessionId, batchId, operatorId
- **SessionResumed**: Trigger: selection of a batch with an IN_PROGRESS session — Payload: sessionId, done count
- **ComponentActivated**: Trigger: activate / auto-advance — Payload: sessionId, componentId, scaleId, containerId
- **OperatorChanged**: Trigger: badge sign-in — Payload: from, to (also an AuditEvent)
- *(007)* **ComponentConfirmed**, **OverrideAuthorised**, **WeighingAbandoned**, **BatchCompleted**, **ConsumptionPosted**

Events are recorded on the aggregate and turned into log lines / audit rows by the application layer (no event bus needed for one station).

### Domain Services

- **ScaleSelectionPolicy**: Operations: select(target) → ScaleDefinition (≤ threshold → precision) — Dependencies: configuration
- **ToleranceBandFactory** (`band_for` + DefaultToleranceRule): Operations: band(target, recipe tolerance, scale class) — Dependencies: configuration
- **ToleranceEvaluator**: Operations: evaluate(net or none, band, calibration valid) → Evaluation — Dependencies: none (pure)
- **ContainerAssignmentPolicy**: Operations: container_for(dyestuffCode, scale class) → Container — Dependencies: container master (configuration)
- **DisplayScale**: Operations: display_max(target) → Quantity — Dependencies: none

### Repository Interfaces

- **WeighingSessionRepository**: Entity: WeighingSession — Methods: get(sessionId), find_open(batchId), add(session), save(session), clear() *(training reset)*
- **OperatorRepository**: Entity: Operator — Methods: by_id, by_badge, current(), set_current(operatorId)
- **AuditRepository**: Entity: AuditEvent — Methods: add(event), for_session(sessionId)
- **ContainerMaster**: Entity: Container — Methods: container_for(dyestuffCode, scaleClass) (read-only, from configuration)
- *(007)* **WeighingRecordRepository**: Entity: WeighingRecord — Methods: add, for_session, for_batch (insert-only)

### Ubiquitous Language

- **Batch**: a dye lot scheduled by OrgaTEX, weighed as a unit; identified e.g. B-24187.
- **Recipe**: the versioned formulation for a shade; components with targets and tolerances (read-only, OrgaTEX).
- **Component**: one dyestuff or auxiliary in a recipe, weighed individually.
- **Dyestuff / Lot**: the material (code, name) and the supplier lot being consumed.
- **Container / Tare**: the vessel a component is weighed into, and its empty weight.
- **Precision scale / Floor scale**: the 3 kg and 32 kg scales; chosen automatically from the target.
- **Target / Tolerance band**: required quantity and its inclusive acceptable range.
- **Net weight**: weight on the scale after tare — "Weighed now".
- **Remaining**: target − net, never below zero — "Still to weigh".
- **Zone**: UNDER, NEAR (visual cue), WITHIN, OVER, OFFLINE.
- **Surplus**: net − target when OVER.
- **Weighing session**: the weighing of one batch at the station, from start to completion.
- **Activate**: make a component the one being weighed (scale chosen, tare applied).
- **Confirm / Override / Abandon (Quit)** *(007)*: accept a weighing in tolerance / accept outside tolerance with supervisor authority / leave without recording.
- **Write-back** *(007)*: posting actual consumption to OrgaTEX.

### Story coverage

| Story | Model elements |
|-------|----------------|
| 001-start-or-resume-weighing-session | WeighingSession, invariants 1–2, 6; Operator; SessionStarted/Resumed; OperatorChanged |
| 002-automatic-scale-selection | ScaleSelectionPolicy, ScaleDefinition, ComponentSpec.scale |
| 003-tolerance-evaluation | ToleranceBand, ToleranceEvaluator, Evaluation, WeighingZone |
| 007-component-progression | ComponentProgress states, invariants 2–5 |
| 010-activate-component-weighing-context | Activation, ContainerAssignmentPolicy, DisplayScale, ComponentActivated |

### Stage checkpoint (delegated, self-validated)

Entities, value objects, the aggregate and its invariants, events, services, repositories and the glossary are defined; every story of this bolt maps to model elements. **Approved** — proceed to Technical Design.
