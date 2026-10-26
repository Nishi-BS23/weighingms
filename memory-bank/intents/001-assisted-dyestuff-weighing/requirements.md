---
intent: 001-assisted-dyestuff-weighing
phase: inception
status: complete
created: 2026-10-26T06:16:00.000Z
updated: 2026-10-26T06:24:00.000Z
---

# Requirements: Assisted Dyestuff Weighing Station (WeighingMS)

## Intent Overview

Build **WeighingMS**, an assisted dyestuff weighing station, as a working training application that reproduces the functional experience of the supplied UI/UX prototype (`docs/customize-weighing-station.html`). WeighingMS sits between **OrgaTEX** (FCI's MES — upstream source of batches and recipes, downstream recipient of actual consumption) and the **weighing operator**. It guides the operator through weighing every recipe component on the automatically selected scale, enforces tolerance at confirmation, records full traceability, writes actual consumption back to OrgaTEX, and prints a weighing ticket.

WeighingMS **does not replace OrgaTEX** and does not automate dispensing. The real OrgaTEX, scales, scanner and printer are unavailable, so the product includes **Dummy APIs** (training substitutes). Their contracts are training contracts only and make **no claim about the real OrgaTEX interface or device protocols**.

## Clarifying Questions (Checkpoint 1) — answered from the source artifacts

Answered by the agent on the participant's delegation; every answer cites its source.

| # | Question | Answer |
|---|----------|--------|
| 1 | Who are the primary users? | Weighing operator (primary); dyehouse supervisor (override authority). Lab/QA and store consume records indirectly. (Brief §4) |
| 2 | What key outcomes matter? | A complete end-to-end guided weighing workflow: tolerance enforced, every weighing traceable, consumption written back, ticket printed. (Brief §3; PDF §12) |
| 3 | Constraints? | Training build: Dummy APIs only, no real OrgaTEX contracts; reproduce the prototype's experience; start with `npm run dev`; approved standards (Python/FastAPI, React, SQLite). (Workbook; course instructions; standards) |
| 4 | How will success be measured? | The workbook demonstration (Step 35) runs end to end; Playwright E2E for batch B-24187 passes; tolerance boundary tests pass; failure scenarios behave as defined. |
| 5 | Biggest concerns? | Over-dose ("surplus compensation") meaning (A-08); tolerance definition (A-07); behaviour when OrgaTEX or a device is unavailable (A-03). |

## Classification Legend

Every requirement and acceptance criterion carries a basis tag:

| Tag | Meaning |
|-----|---------|
| **[C] Confirmed** | Required for this training build: stated explicitly by the course Project Requirement (PDF) and/or the workbook, and consistent with the Brief and prototype. *Note: nothing in the Brief is confirmed by FCI; "confirmed" here means confirmed for this build.* |
| **[A] Assumption** | A position we take where sources are silent, ambiguous or conflicting. Listed in the Assumptions register (TA-xx) with risk and mitigation. |
| **[Q] Unresolved** | An open question that remains open. Listed in Unresolved Questions (UQ-xx). The build must not pretend it is answered. |
| **[T] Training-only** | Dummy behaviour that exists only because real systems are unavailable. Listed in Training-only Dummy Behaviour (TD-xx). |

## Business Goals

| Goal | Success Metric | Priority |
|------|----------------|----------|
| Prevent out-of-tolerance weighings reaching production (BO-01) | 0 confirmations outside tolerance without a recorded supervisor override (automated tests) | Must |
| Component-level traceability (BO-02) | 100% of confirmed weighings store target, actual, unit, tolerance band, operator, scale, lot, container, tare, timestamp | Must |
| Reconcile actual vs theoretical consumption (BO-04) | Every completed batch posts per-component actual consumption to (Dummy) OrgaTEX exactly once | Must |
| Reproduce the supplied UI/UX | Screen comparison (Workbook Step 28) shows all three screens, their states and interactions | Must |
| Demonstrable, testable product | Playwright E2E for B-24187 passes; failure scenarios tested | Must |

## Training Scenario (from the prototype)

Batch **B-24187** · Order **SO-9931** · Machine **JET-04** · Fabric **100% CTN knit · 480 kg** · Shade **Teal 4C** · Station **STATION 01** · Operator **R. Karim · Shift A**

| Seq | Component | Code | Target | Tolerance | Accept range | Scale | Lot | Container | Tare |
|-----|-----------|------|--------|-----------|--------------|-------|-----|-----------|------|
| 1 | Remazol Brill. Blue RSPL | DYE-1180 | 1240.0 g | ±6.0 g | 1234.0 – 1246.0 g | 3 kg precision | 2026-0341 | C-09 | 214 g |
| 2 | Remazol Red RB | DYE-2204 | 386.0 g | ±2.0 g | 384.0 – 388.0 g | 3 kg precision | 2026-0298 | C-11 | 214 g |
| 3 | Remazol Yellow RGB | DYE-4471 | 94.0 g | ±0.5 g | 93.5 – 94.5 g | 3 kg precision | 2026-0387 | C-12 | 214 g |
| 4 | Sodium Sulphate | AUX-0101 | 24.000 kg | ±0.120 kg | 23.880 – 24.120 kg | 32 kg floor | 2026-0112 | D-03 | 1.850 kg |
| 5 | Soda Ash | AUX-0107 | 9.600 kg | ±0.048 kg | 9.552 – 9.648 kg | 32 kg floor | 2026-0155 | D-05 | 1.850 kg |

Other queue rows (prototype): B-24188 (SO-9931, JET-07, 100% CTN knit · 520 kg, Teal 4C, 5 comp.), B-24190 (SO-9944, JET-02, CVC fleece · 310 kg, Navy 12, 7 comp.), B-24191 (SO-9947, WINCH-01, Viscose jersey · 190 kg, Rose 08, 4 comp.). Their recipes are not in the prototype — see TA-19.

---

## Functional Requirements

### FR-1: Batch queue
- **Description**: WeighingMS retrieves the batches released to this station from OrgaTEX (Dummy OrgaTEX in training) and presents them as a queue. Batches are never hard-coded in the UI. [C] (PDF §4.1, §6 Step 1; Brief FR-01, FR-04; Workbook Step 19)
- **Acceptance Criteria**:
  - Given the Dummy OrgaTEX holds the seed batches, When the operator opens the batch screen, Then the queue lists B-24187, B-24188, B-24190 and B-24191 obtained via `GET /api/batches`. [C]
  - Each row shows Batch, Order, Machine, Fabric / lot, Shade, Comp. (component count) and Status, matching the prototype columns. [C]
  - The screen shows when the queue was received from OrgaTEX ("Queue received from OrgaTEX at HH:MM"). [C]
  - Given OrgaTEX is unavailable, When the queue is requested, Then the operator sees a plain-language "OrgaTEX unavailable" message with a Retry action, and no stale data is presented as current. [A] TA-13
- **Priority**: Must
- **Related Stories**: orgatex-integration/001, weighing-station-ui/002, training-substitutes/001

### FR-2: Batch selection
- **Description**: The operator starts or resumes weighing a batch by touching its row or scanning its batch barcode. Only batches in a selectable status may be weighed. [C] (PDF §6 Step 2; Brief FR-02, FR-03, BR-03)
- **Acceptance Criteria**:
  - Given the queue is displayed, When the operator touches the B-24187 row, Then WeighingMS requests `GET /api/batches/B-24187` and `GET /api/batches/B-24187/recipe` and opens the Weigh screen for that batch. [C]
  - Given the batch screen is displayed, When the barcode "B-24187" is scanned (scanner or keyboard-wedge entry), Then the same selection happens. [C]
  - Given a batch has status QUEUED or WEIGHING, When selected, Then weighing starts (QUEUED) or resumes with confirmed components preserved (WEIGHING). [A] TA-02
  - Given a batch has status WEIGHED or CANCELLED, or an unknown batch ID is scanned, When selected, Then selection is refused and the reason is shown. [C] (Brief FR-03)
  - Starting weighing sets the batch status in OrgaTEX to WEIGHING. [A] TA-12 (Brief IR-06)
- **Priority**: Must
- **Related Stories**: weighing-station/001, device-integration/003, weighing-station-ui/003

### FR-3: Recipe loading
- **Description**: On selection, WeighingMS retrieves the batch's recipe and presents all components in recipe sequence, keeping the batch and recipe associated throughout weighing. [C] (PDF §6 Steps 2–3; Brief FR-05, FR-06)
- **Acceptance Criteria**:
  - Given B-24187 is selected, Then the recipe rail shows "Recipe · Teal 4C", "B-24187" and the five components in sequence 1–5 as in the training scenario. [C]
  - Each component shows name, code, scale class, target quantity with unit, and weighing state (✓ actual / WEIGHING / PENDING). [C]
  - The rail header shows "{n} of {total} components weighed". [C]
  - The recipe snapshot used for weighing is stored when the session starts, so a later OrgaTEX outage does not stop weighing in progress. [A] TA-13 (Brief BR-16)
  - Recipe is displayed within 3 s of selection (NFR-2). [C]
- **Priority**: Must
- **Related Stories**: orgatex-integration/002, weighing-station-ui/004, training-substitutes/002

### FR-4: Component identification
- **Description**: The operator can identify the component being weighed by name, dyestuff code and colour swatch, sourced from the recipe and dyestuff master data. [C] (PDF §6 Step 3; prototype rail and weigh header)
- **Acceptance Criteria**:
  - The active component's name (e.g. "Remazol Yellow RGB") and code (e.g. "DYE-4471") are shown in the weigh header. [C]
  - Each rail item shows a colour swatch from dyestuff master data. [C]
  - Identity verification by scanning a dyestuff barcode is **not** implemented in this build. [Q] UQ-13
- **Priority**: Must
- **Related Stories**: orgatex-integration/002, weighing-station-ui/005

### FR-5: Dyestuff lot
- **Description**: The dyestuff lot being consumed is shown for the active component and recorded on its weighing record. [C] (Brief BR-11, FR-10; prototype "LOT 2026-0387")
- **Acceptance Criteria**:
  - Given Yellow RGB is active, Then the header shows "LOT 2026-0387". [C]
  - The confirmed weighing record stores the lot ID. [C]
  - The lot is the one assigned to the component by OrgaTEX lot data; manual lot capture by scan is not implemented. [A] TA-07, [Q] UQ-09
- **Priority**: Must
- **Related Stories**: weighing-station/010, weighing-station/004

### FR-6: Container
- **Description**: The container used for the active component is shown and recorded. Containers come from a WeighingMS-owned container master. [A] TA-08 (Brief §9.3; prototype "CONTAINER C-12")
- **Acceptance Criteria**:
  - Given Yellow RGB is active, Then the header shows "CONTAINER C-12". [A]
  - Given Sodium Sulphate is active, Then the header shows "CONTAINER D-03". [A]
  - The confirmed weighing record stores the container ID. [C] (Workbook Step 25)
- **Priority**: Must
- **Related Stories**: weighing-station/010, weighing-station/004

### FR-7: Tare
- **Description**: The container tare is known from the container master, shown in the header, and applied so that "Weighed now" shows the net dispensed quantity. The operator can re-tare. [C] (Brief FR-11, IR-12; prototype "TARE 214 g", Re-tare key)
- **Acceptance Criteria**:
  - Given Yellow RGB is active, Then the header shows "TARE 214 g"; for Sodium Sulphate "TARE 1.850 kg". [C]
  - When a component is activated, WeighingMS issues a tare to the selected scale (`POST /api/scales/{scaleId}/tare`) and "Weighed now" starts at 0. [A] TA-06
  - Given weight is on the scale, When the operator presses Re-tare (F2), Then the scale is tared again and "Weighed now" returns to 0.0 (g) / 0.000 (kg). [C] (Workbook Step 30 "Re-tare → weight reset")
  - The confirmed weighing record stores the tare value and unit. [C]
- **Priority**: Must
- **Related Stories**: device-integration/002, weighing-station/010, weighing-station-ui/006

### FR-8: Scale selection
- **Description**: WeighingMS selects the scale for each component automatically from its target quantity: ≤ 3 kg → 3 kg precision scale; > 3 kg → 32 kg floor (heavy-duty) scale. The threshold and scale definitions are configurable. [C] (PDF §5.1–§5.3; Brief BR-05, FR-07; prototype)
- **Acceptance Criteria**:
  - Target 1240.0 g, 386.0 g, 94.0 g → "3 kg precision". [C]
  - Target 24.000 kg, 9.600 kg → "32 kg floor". [C]
  - Target exactly 3.000 kg → precision; 3.001 kg → floor. [C] (PDF §5.3)
  - The weigh header shows "Scale selected / {scale} / automatic". [C]
  - Changing the configured threshold changes the selection without code changes. [C] (PDF §5.3)
  - Selecting Sodium Sulphate after Yellow RGB switches the scale badge to "32 kg floor" and the units to kg. [C] (Workbook Step 21)
  - Manual scale reselection (supervisor) is not implemented in this build. [A] TA-04
- **Priority**: Must
- **Related Stories**: weighing-station/002, weighing-station-ui/005

### FR-9: Live weight
- **Description**: The weigh screen shows the current net weight from the selected scale, updating continuously. [C] (PDF §6 Step 5; Brief FR-13; prototype "Weighed now")
- **Acceptance Criteria**:
  - The weight comes from the Dummy Scale API for the selected scale (via WeighingMS), not from UI-side simulation. [C] (Workbook Steps 16, 21)
  - The display refreshes at least 5 times per second while a component is active; displayed weight lags the scale by ≤ 200 ms (NFR-1). [C]
  - Grams display 1 decimal place (e.g. "93.5 g"); kilograms display 3 decimal places (e.g. "23.880 kg"). [C] (prototype `dp()`)
  - The readout colour reflects the zone: under = neutral, near = amber, ok = green, over = red, and the zone is also given in text (status line). [C]
  - Given the selected scale is unavailable, Then the readout shows "—" and "SCALE OFFLINE"; see FR-20. [C]
- **Priority**: Must
- **Related Stories**: device-integration/001, weighing-station-ui/005, training-substitutes/004

### FR-10: Target quantity
- **Description**: The target quantity of the active component is shown with its unit, as supplied by the recipe. [C] (PDF §6 Step 3; prototype "Target")
- **Acceptance Criteria**:
  - Given Yellow RGB is active, Then Target shows "94.0 g"; for Sodium Sulphate "24.000 kg". [C]
  - The target (snapshot) is stored on the weighing record. [C]
- **Priority**: Must
- **Related Stories**: weighing-station/003, weighing-station-ui/005

### FR-11: Remaining quantity
- **Description**: "Still to weigh" shows target minus net weight, never below zero. [C] (Brief FR-14; prototype)
- **Acceptance Criteria**:
  - Given target 94.0 g and net 60.0 g, Then Still to weigh shows "34.0 g". [C]
  - Given net weight ≥ target, Then Still to weigh shows "0.0 g". [C]
  - The status line reads "DISPENSE — {remaining} {unit} REMAINING" while under tolerance. [C]
- **Priority**: Must
- **Related Stories**: weighing-station/003, weighing-station-ui/005

### FR-12: Tolerance
- **Description**: Each component has an explicit acceptable range around its target. WeighingMS classifies the net weight as **underweight**, **within tolerance** or **overweight**, with an additional visual "near" cue when underweight but ≥ 90% of target. Tolerances are per component and configurable — no universal tolerance. [C] (PDF §6 Step 6, §7; Brief BR-07, BR-09, FR-15–17; prototype `zone()`)
- **Acceptance Criteria**:
  - The tolerance comes from the recipe component (e.g. Yellow RGB ±0.5 g). If a recipe component carries no tolerance, the configured default rule for its scale class applies. [A] TA-03
  - Bounds are inclusive. For Yellow RGB (94.0 g ±0.5 g): 93.4 g → underweight, cannot confirm; 93.5 g → within, can confirm; 94.0 g → within (target), can confirm; 94.5 g → within, can confirm; 94.6 g → overweight, cannot confirm. [C] (Workbook Step 22)
  - The caption shows "TOLERANCE ±0.5 g (93.5 – 94.5)". [C]
  - The progress bar shows the fill, the tolerance band and the target line; its fill colour follows the zone. [C]
  - Status line texts: under → "DISPENSE — {x} {u} REMAINING"; within → "WITHIN TOLERANCE — PRESS OK TO CONFIRM"; over → "OVER TOLERANCE — SURPLUS +{x} {u}". [C] (prototype)
  - Tolerance evaluation happens in the backend; the UI displays the result (coding standards). [C]
  - The tolerance band (min/max) is snapshotted onto the weighing record. [C] (Brief §9.2)
- **Priority**: Must
- **Related Stories**: weighing-station/003, weighing-station-ui/005

### FR-13: Confirmation
- **Description**: The operator confirms the weighing of the active component with OK · Confirm (F1). Confirmation is possible only while the weight is within tolerance and the scale is available, or via an authorised supervisor override (FR-21). [C] (PDF §6 Step 7; Brief FR-18, FR-25; Workbook Step 25)
- **Acceptance Criteria**:
  - Given the zone is under or over, Then OK · Confirm is disabled. Given the zone is within tolerance, Then it is enabled. [C]
  - When confirmed, the backend re-reads the current weight from the scale and re-evaluates tolerance; it never trusts a weight sent by the UI. A confirmation that is no longer within tolerance is rejected with `OUT_OF_TOLERANCE`. [A] TA-16
  - A weighing record is stored with: batch, component, dyestuff code/name, target, actual weight, unit, tolerance min/max, result (IN_TOLERANCE), operator, lot, container, tare, scale, timestamp. [C] (Workbook Step 25; PDF §10)
  - The record is durable before the confirmation is acknowledged (NFR-3) and is immutable afterwards. [C]
  - The component is then shown as done with "✓ {actual}". [C]
- **Priority**: Must
- **Related Stories**: weighing-station/004, weighing-station-ui/006

### FR-14: Overshoot
- **Description**: When the net weight exceeds the upper tolerance bound, WeighingMS detects the over-dose, shows the surplus, blocks normal confirmation and applies a **defined** response. The exact training response is decided at Workbook Step 24 and recorded in `STEP-24-overshoot-decision.md`. [C] detection (Brief BR-08, FR-20; PDF §6 Step 6), [Q] response UQ-07
- **Acceptance Criteria**:
  - Given Yellow RGB at 96.4 g, Then the zone is over, the status line reads "OVER TOLERANCE — SURPLUS +2.4 g", and a surplus panel shows "Surplus +2.4 g (+2.6%) — over tolerance". [C]
  - Surplus = net weight − target; surplus % = surplus / target × 100, 1 decimal. [C] (prototype)
  - OK · Confirm stays disabled while overweight. [C]
  - Until the Step 24 decision, the provisional rule is: no automatic recalculation of remaining components; the operator recovers by removing excess (weight returns into the band), re-taring and re-weighing, or requesting a supervisor override. [A] TA-11
- **Priority**: Must
- **Related Stories**: weighing-station/005, weighing-station-ui/007

### FR-15: Component progression
- **Description**: Components are weighed one at a time in recipe sequence. After a confirmation the next pending component becomes active automatically; the operator may also pick any pending component. [C] (PDF §6 Step 8; Brief FR-06; prototype `select()` / confirm handler)
- **Acceptance Criteria**:
  - Given B-24187 starts fresh, Then Blue RSPL (seq 1) is active and the others pending. [C]
  - When the active component is confirmed, Then it becomes done and the next pending component in sequence becomes active (Blue RSPL → Red RB → Yellow RGB → Sodium Sulphate → Soda Ash). [C] (Workbook Step 23)
  - When the operator touches a pending component, Then it becomes active, the previously active (unconfirmed) component returns to pending, and the scale is re-selected and tared. [C]
  - A done component cannot be re-selected or re-weighed. [C] (prototype; Brief DR-02)
  - A component cannot become done unless its weight was valid (within tolerance) or overridden. [C]
- **Priority**: Must
- **Related Stories**: weighing-station/007, weighing-station-ui/004

### FR-16: Batch completion
- **Description**: The batch is complete only when every component is confirmed. On completion WeighingMS moves to the Confirm & print screen. [C] (PDF §6 Step 9; Workbook Step 23)
- **Acceptance Criteria**:
  - Given 4 of 5 components are done, Then the batch cannot be completed and the API rejects completion with `BATCH_INCOMPLETE`. [C] (Workbook Step 30)
  - When the 5th component is confirmed, Then the session is completed, write-back starts (FR-17) and the Confirm & print screen shows "Batch B-24187 weighed". [C]
  - The summary shows: Components weighed "5 of 5"; All within tolerance "YES" (or "NO — {n} overridden"); Total dispensed in kg (3 decimals, e.g. "35.322 kg" for the prototype actuals); Elapsed time ("6 min 41 s" format); Operator; Written to OrgaTEX status. [C]
- **Priority**: Must
- **Related Stories**: weighing-station/009, weighing-station-ui/008

### FR-17: OrgaTEX write-back
- **Description**: On batch completion WeighingMS posts actual consumption per component to OrgaTEX and sets the batch status to WEIGHED. Posting is idempotent and failures are surfaced, not hidden. [C] (Brief BR-12, FR-26, IR-05, IR-08; Workbook Step 26)
- **Acceptance Criteria**:
  - When B-24187 completes, WeighingMS sends `POST /api/batches/B-24187/consumption` to the Dummy OrgaTEX with, per component: component/dyestuff code, lot, target, actual, unit, scale, operator, confirmed-at; plus batch, session ID and completion time. [C]
  - The Dummy OrgaTEX responds 200 OK and stores the consumption record, which can be retrieved for evidence. [C] [T] TD-01
  - The summary then shows "Written to OrgaTEX · CONFIRMED HH:MM:SS". [C]
  - Re-sending the same completion (same session ID / idempotency key) does not create a second consumption record. [C] (Brief IR-08)
  - Given OrgaTEX is unavailable at completion, Then the batch is still completed locally, the summary shows "Written to OrgaTEX · PENDING" with a Retry action, and retrying after OrgaTEX returns posts exactly once. [A] TA-13
- **Priority**: Must
- **Related Stories**: orgatex-integration/003, training-substitutes/003, weighing-station-ui/008

### FR-18: Ticket generation
- **Description**: On the Confirm & print screen the operator prints a weighing ticket to the (dummy) printer; a print preview of the same ticket is always shown. [C] (Brief BR-15, FR-27, FR-28; Workbook Step 27; prototype ticket)
- **Acceptance Criteria**:
  - The ticket shows: "FCI DYEING — WEIGHING TICKET"; Batch; Order; Machine; Shade; Date (YYYY-MM-DD HH:MM); Operator; per component short name, target, actual and unit; an overall result line ("ALL WITHIN TOLERANCE" or "{n} OVERRIDDEN"); a barcode encoding the batch ID; the batch ID under the barcode. [A] TA-15
  - When the operator presses Print ticket (F1), WeighingMS sends `POST /api/tickets` to the Dummy Printer and shows "Ticket printed" with the printer's ticket ID. [C]
  - Printing again marks the ticket "REPRINT". [C] (Brief FR-28) — Could
  - Given the printer is unavailable, Then a clear message is shown, the ticket can be printed later, and batch completion is unaffected. [C] (Workbook Step 30)
- **Priority**: Must
- **Related Stories**: ticket-printing/001, ticket-printing/002, ticket-printing/003, weighing-station-ui/009, training-substitutes/006

### FR-19: Operator traceability
- **Description**: Every weighing session and record is attributable to an identified operator, shown on screen. [C] (Brief BR-19, FR-34; PDF §10)
- **Acceptance Criteria**:
  - The top bar shows "Operator {name} · {shift}" (e.g. "R. Karim · Shift A"). [C]
  - The station has a signed-in operator; in training, R. Karim is signed in by default. The operator can be changed by entering a badge ID. [A] TA-09, [T] TD-08
  - Every weighing record, override and audit event stores the operator ID. [C]
  - Changing operator is recorded as an audit event. [A]
- **Priority**: Must
- **Related Stories**: weighing-station/001, weighing-station/004, weighing-station-ui/001

### FR-20: Scale, scanner and printer failure
- **Description**: Device failures are detected, shown to the operator and handled safely: never a wrong confirmation, never a silent loss. [C] (Brief IR-13, IR-18; Workbook Step 30)
- **Acceptance Criteria**:
  - Given the selected scale becomes unavailable, Then within 2 s the readout shows "—", the status line shows "SCALE OFFLINE — CHECK CONNECTION", OK · Confirm is disabled, and the status strip shows the scale as down. [C] (Brief IR-13)
  - Given the scanner is unavailable, Then the scan prompt says the scanner is unavailable and touch selection still works. [A]
  - Given the printer is unavailable, Then printing fails with a clear message and can be retried; completion is unaffected (FR-18). [C]
  - Given a scale's calibration is expired, Then the strip shows "CAL EXPIRED" for that scale and confirmation on it is blocked. [A] TA-18 (Brief BR-24, FR-12) — Should
  - Every device failure is logged with diagnostic detail (Brief IR-09). [C]
- **Priority**: Must
- **Related Stories**: device-integration/004, weighing-station-ui/010, weighing-station-ui/013, training-substitutes/007

### FR-21: Supervisor override
- **Description**: A supervisor can authorise confirmation of an out-of-tolerance weighing with their PIN and a mandatory reason; the record is marked OVERRIDDEN and audited. [C] (Brief BR-07, BR-13, FR-23, FR-24, FR-35; PDF §6 Step 7 "explicit, authorized exception"; prototype "Supervisor override")
- **Acceptance Criteria**:
  - Given the weight is outside tolerance and > 0, When "Supervisor override" is pressed, Then a dialog asks for supervisor PIN and reason. [A] TA-10
  - Given a wrong PIN or empty reason, Then the override is refused and nothing is recorded. [C]
  - Given a valid PIN and reason, Then the weighing is recorded with result OVERRIDDEN, an override record (supervisor, reason, time) and an audit event, and the component becomes done. [C]
  - While waiting, the status line shows "OVERRIDE REQUESTED — AWAITING SUPERVISOR". [C] (prototype)
  - The PIN is never logged or stored in plain text (NFR-6). [C]
- **Priority**: Must
- **Related Stories**: weighing-station/006, weighing-station-ui/006

### FR-22: Quit (abandon and exit safely)
- **Description**: Quit (F4) abandons the current component attempt and returns to the batch queue without recording anything for that component; confirmed components are kept and the batch can be resumed. [C] (Brief FR-19; Workbook Step 30 "Quit → safe exit")
- **Acceptance Criteria**:
  - When Quit is pressed and confirmed, Then no weighing record is created for the active component, an ABANDON audit event is stored, and the batch queue is shown. [C]
  - Given B-24187 had 2 confirmed components, When it is selected again, Then the session resumes with those 2 done and the next pending component active (NFR-4). [C]
- **Priority**: Must
- **Related Stories**: weighing-station/008, weighing-station-ui/006

### FR-23: Completed-batch summary and record review
- **Description**: After completion, the summary of the batch's weighing results — required vs actual quantity and final status per component — is shown and remains retrievable. [C] (PDF §6 Step 9, §10; Brief BR-14, FR-29)
- **Acceptance Criteria**:
  - The Confirm & print screen lists each component with target, actual, unit and result (IN TOLERANCE / OVERRIDDEN). [C]
  - `GET /api/weighing-records?batchId=B-24187` returns all confirmed records for the batch with the full traceability set. [C]
- **Priority**: Must
- **Related Stories**: weighing-station/011, weighing-station-ui/008

### FR-24: Device and connection status visibility
- **Description**: The status strip continuously shows the state of both scales, scanner, printer and the OrgaTEX link. [C] (Brief IR-18, FR-32; prototype status strip)
- **Acceptance Criteria**:
  - The strip shows "SCALE 3 kg · READY", "SCALE 32 kg · READY", "SCANNER", "PRINTER", "ORGATEX · LINKED HH:MM", the language "EN" and a running clock. [C]
  - Each item has a green dot when up and a red/amber dot with a text state when down or degraded, refreshed at least every 2 s. [C]
- **Priority**: Must
- **Related Stories**: device-integration/004, weighing-station-ui/001

### FR-25: Dummy OrgaTEX (training substitute)
- **Description**: A separate dummy service plays OrgaTEX with the workbook's training contract. [T] TD-01 (Workbook Step 16; PDF §4, §9)
- **Acceptance Criteria**:
  - Provides `GET /api/batches`, `GET /api/batches/{batchId}`, `GET /api/batches/{batchId}/recipe`, `POST /api/batches/{batchId}/consumption`, plus `GET /api/batches/{batchId}/consumption` and `PATCH /api/batches/{batchId}/status` for evidence and status write-back. [T]
  - Data is seeded from a JSON file containing the training scenario (B-24187 and the other queue rows). [T]
  - Unknown batch → 404 with the standard error body. [T]
  - Its contract is documented as a training contract, not the real OrgaTEX interface. [C]
- **Priority**: Must
- **Related Stories**: training-substitutes/001, training-substitutes/002, training-substitutes/003

### FR-26: Dummy Scale (training substitute)
- **Description**: A dummy service simulates the two scales with continuous readings. [T] TD-02 (Workbook Step 16; PDF §9)
- **Acceptance Criteria**:
  - Provides `GET /api/scales`, `GET /api/scales/{scaleId}/status`, `GET /api/scales/{scaleId}/weight`, `POST /api/scales/{scaleId}/tare`. [T]
  - Two scales: `scale-3kg` (precision, capacity 3 kg, 0.1 g resolution) and `scale-32kg` (floor, capacity 32 kg, 0.001 kg resolution). [A] TA-04
  - Simulation scenarios: weight gradually increasing toward a landing value (easing as it approaches), staying below range, entering range, exceeding range, and setting an exact weight instantly (deterministic, for tests). [T] (PDF §9)
  - Readings are rounded to the scale's resolution and never exceed capacity. [T]
- **Priority**: Must
- **Related Stories**: training-substitutes/004

### FR-27: Dummy Scanner (training substitute)
- **Description**: A dummy service stands in for the barcode scanner. [T] TD-03
- **Acceptance Criteria**:
  - A scan can be simulated (`POST /api/scanner/scans` with a code) and the station receives it in order exactly once. [T]
  - Scanner status is available for the status strip. [T]
- **Priority**: Must
- **Related Stories**: training-substitutes/005

### FR-28: Dummy Printer (training substitute)
- **Description**: A dummy service stands in for the ticket printer. [T] TD-04
- **Acceptance Criteria**:
  - `POST /api/tickets` accepts a ticket, stores it and returns a ticket ID and status PRINTED. [T]
  - Printed tickets can be listed and retrieved for evidence. [T]
- **Priority**: Must
- **Related Stories**: training-substitutes/006

### FR-29: Training controls (simulation, failure injection, reset)
- **Description**: Trainers and tests can drive the dummy systems: simulate dispensing, make any external system unavailable, and reset to seed data. [T] TD-05, TD-06, TD-07
- **Acceptance Criteria**:
  - Each of OrgaTEX, scale-3kg, scale-32kg, scanner and printer can be switched unavailable and back. [T]
  - A reset restores all dummy data and WeighingMS training state to the seed scenario. [T]
  - The UI offers these controls in a training panel outside the device frame (like the prototype's control bar): Simulate dispense, Simulate overshoot, Reset weighing, Simulate scan, failure toggles, Reset training data. [T]
- **Priority**: Must
- **Related Stories**: training-substitutes/007, weighing-station-ui/001

### FR-30: Screen 1 — Select batch
- **Description**: Reproduce the prototype's "1 · Select batch" view functionally. [C] (PDF §8; prototype View 1)
- **Acceptance Criteria**:
  - Scan prompt with animated scan beam: "Scan a batch card to begin" / "Or touch a row below. Queue received from OrgaTEX at HH:MM." [C]
  - Queue table per FR-1 with status tags (WEIGHING highlighted amber). [C]
  - Touch or scan selection per FR-2. [C]
- **Priority**: Must
- **Related Stories**: weighing-station-ui/002, weighing-station-ui/003

### FR-31: Screen 2 — Weigh
- **Description**: Reproduce the prototype's "2 · Weigh" view functionally. [C] (PDF §8; prototype View 2; Workbook Step 20)
- **Acceptance Criteria**:
  - Left recipe rail (FR-3, FR-15) and right weighing stage with: component name; meta line "{code} · LOT {lot} · CONTAINER {container} · TARE {tare}"; scale badge (FR-8); readout cells Weighed now / Still to weigh / Target; progress bar with band and target line; tolerance caption; status line; surplus panel (FR-14); keys OK · Confirm (F1), Re-tare (F2), Quit (F4), Supervisor override. [C]
- **Priority**: Must
- **Related Stories**: weighing-station-ui/004, weighing-station-ui/005, weighing-station-ui/006, weighing-station-ui/007

### FR-32: Screen 3 — Confirm & print
- **Description**: Reproduce the prototype's "3 · Confirm & print" view functionally. [C] (PDF §8; prototype View 3; Workbook Step 27)
- **Acceptance Criteria**:
  - Heading "Batch {id} weighed", summary (FR-16), per-component results (FR-23), consumption note, keys Print ticket (F1) and Next batch (F3), ticket preview (FR-18). [C]
  - Next batch returns to Screen 1 with a refreshed queue. [C]
- **Priority**: Must
- **Related Stories**: weighing-station-ui/008, weighing-station-ui/009

### FR-33: Station chrome
- **Description**: Reproduce the prototype's device frame: dark HMI panel in a bezel labelled '15" INDUSTRIAL TOUCH TERMINAL', top bar, step indicator and status strip. [C] (prototype)
- **Acceptance Criteria**:
  - Top bar: "WeighingMS" + "STATION 01"; crumb "BATCH {id} · ORDER {order} · MACHINE {machine}" when a batch is active; operator chip (FR-19). [C]
  - Step indicator "1 · Select batch / 2 · Weigh / 3 · Confirm & print" reflects the current step; navigation follows the workflow (a step is reachable only when its data exists). [A] TA-20
  - Status strip per FR-24. The device screen stays dark in both light and dark page themes. [C]
  - The prototype's "question pins" are a discussion aid and are not reproduced. [A] TA-20
- **Priority**: Must
- **Related Stories**: weighing-station-ui/001

### FR-34: Function keys
- **Description**: The physical-terminal function keys shown on the prototype keys work from a keyboard. [C] (Brief IR-17; prototype F1/F2/F3/F4 labels)
- **Acceptance Criteria**:
  - Weigh screen: F1 = OK · Confirm (only when enabled), F2 = Re-tare, F4 = Quit. Confirm & print screen: F1 = Print ticket, F3 = Next batch. [C]
- **Priority**: Could
- **Related Stories**: weighing-station-ui/011

---

## Non-Functional Requirements

### Performance
| Requirement | Metric | Target |
|-------------|--------|--------|
| NFR-1 Live weight responsiveness | Lag between dummy scale value change and display | ≤ 200 ms (poll interval ≤ 150 ms; backend round trip < 50 ms on localhost) (Brief NFR-01) |
| NFR-2 Recipe display | Batch selection → recipe rail rendered | ≤ 3 s (Brief NFR-02) |

### Scalability
| Requirement | Metric | Target |
|-------------|--------|--------|
| Stations | Concurrent stations | 1 (single station, single site — Brief A-11) |
| Data volume | Records | Training volumes only; no special scaling |

### Security
| Requirement | Standard | Notes |
|-------------|----------|-------|
| NFR-6 Privileged actions | Supervisor PIN | Required for override; PIN stored hashed, never logged; training-grade only (tech-stack) |
| Authentication | Badge ID | Operator identification only; no passwords (TA-09) |

### Reliability
| Requirement | Metric | Target |
|-------------|--------|--------|
| NFR-3 Durability | Confirmed weighing survives restart / power loss | Record committed (SQLite WAL, `synchronous=FULL`) before the confirm response (Brief NFR-05) |
| NFR-4 Resume | Interrupted session | Resumable at the next pending component with confirmed components intact (Brief NFR-06) |
| NFR-5 Idempotent write-back | Duplicate consumption postings | 0 duplicates under retry (Brief IR-08) |
| NFR-7 Fail safe | Confirmation while scale unavailable or out of tolerance | Never possible without override (Brief IR-13) |

### Usability
| Requirement | Metric | Target |
|-------------|--------|--------|
| NFR-8 Touch targets | Primary action key height | ≥ 62 px (≈ 15 mm at the 15" terminal; Brief NFR-07; prototype `.key`) |
| NFR-9 Readout legibility | Live weight font size | ≥ 52 px (prototype; Brief NFR-08) |
| NFR-10 Plain language | Operator messages | No codes or stack traces shown; colour never the only signal (Brief C-05) |
| Language | Interface | English only (TA-17) |

### Data integrity and maintainability
| Requirement | Metric | Target |
|-------------|--------|--------|
| NFR-11 Exact arithmetic | Floating point in quantity arithmetic | None — `Decimal` in backend, decimal strings over the API (Brief NFR-16; standards) |
| NFR-12 Immutability | Updates/deletes of confirmed records | None (Brief DR-02) |
| NFR-13 Configurability | Code changes needed to change scale threshold, scale definitions, default tolerance rule, ticket header | None — configuration file (PDF §5.3, §6; Brief NFR-14) |
| NFR-14 Startup | `npm run dev` at repo root | Starts dummy systems, WeighingMS API and UI; UI reachable at the printed URL within 30 s (course instruction) |

### Testability
| Requirement | Metric | Target |
|-------------|--------|--------|
| NFR-15 Deterministic dummies | Tests depending on timing/randomness | 0 — exact weights can be set (standards) |
| NFR-16 Coverage | Backend line coverage; business rules with explicit tests | ≥ 80%; 100% of rules (standards) |
| NFR-17 E2E | Playwright suite for B-24187 and failure scenarios | Passes, HTML report + video (Workbook Steps 29–30) |

### Compliance
| Requirement | Standard | Notes |
|-------------|----------|-------|
| NFR-18 Audit trail | AUDIT_EVENT records | Overrides, abandons, reprints and operator changes are audited and immutable (Brief NFR-13, FR-36) |

---

## Constraints

### Technical Constraints

**Project-wide standards**: Required standards will be loaded from memory-bank standards folder by Construction Agent

**Intent-specific constraints**:
- Dummy APIs are training contracts; they must not be described as, or shaped to claim to be, the real OrgaTEX interface or device protocols (Workbook; Brief §10.1 "illustrative").
- The Dummy systems run as a separate service from WeighingMS; WeighingMS reaches them only over HTTP through adapters, so they can be replaced by real integrations (PDF §9, §11 Priority 3; Brief IR-07).
- No scenario data is hard-coded in UI components; all batch, recipe, weight and device data comes through APIs (Workbook Rule 5, Step 19).
- `npm run dev` at the repository root must start the complete application (course instruction).
- The prototype's JavaScript is not copied; behaviour is rebuilt from these requirements (Workbook Step 20).

### Business Constraints
- OrgaTEX stays the system of record; WeighingMS never edits recipes or batch data other than weighing status and consumption (Brief C-01, C-02).
- No control of dispensing machinery (Brief C-03).
- Operators may have limited computer literacy (Brief C-05).

---

## Assumptions (Training-build register)

| ID | Assumption | Basis | Risk if Invalid | Mitigation |
|----|------------|-------|-----------------|------------|
| TA-01 | The Dummy OrgaTEX contract is the workbook's training contract (`/api/batches…`), not the Brief's illustrative `/api/v1/…` shape and not the real interface | Workbook Step 16; Brief A-01 | Real interface differs | All OrgaTEX access isolated in one adapter (IR-07) |
| TA-02 | The prototype's QUEUED status means "released to this station and awaiting weighing" (Brief's RELEASED); QUEUED and WEIGHING are selectable; WEIGHED and CANCELLED are not | Prototype queue tags vs Brief BATCH.status | Status semantics differ in OrgaTEX | Selectable statuses are configurable |
| TA-03 | Tolerance is a per-component absolute ± value delivered with the recipe (prototype values ≈ 0.5% of target). If absent, a configured default per scale class applies: 0.5% of target, minimum 0.2 g (precision) / 0.010 kg (floor). Bounds inclusive | Prototype data; PDF §6–§7; Brief A-07 | FCI uses banded or per-dyestuff rules | Tolerance rule isolated in domain policy; default configurable |
| TA-04 | Two scales: 3 kg precision (0.1 g resolution) and 32 kg floor (0.001 kg resolution); threshold 3 kg on target quantity; no manual reselection in this build | PDF §5; prototype; Brief glossary | Container + material may exceed precision capacity near 3 kg (UQ-05) | Threshold/capacities configurable |
| TA-05 | The amber "near" zone (≥ 90% of target, below range) is a visual cue only; business classes are underweight / within / overweight | Prototype `zone()`; PDF §6 Step 6 | — | — |
| TA-06 | "Weighed now" is net weight: the scale is tared with the empty container at component activation; the container master tare is shown and recorded for traceability | Prototype (starts at 0.0, shows TARE); Brief FR-11 | FCI weighs gross and subtracts master tare | Tare source recorded (`MASTER` / `WEIGHED`) |
| TA-07 | The dyestuff lot is pre-assigned per component by OrgaTEX lot data; no manual lot scan | Prototype lots; Brief A-09, IR-04 | Lots captured at the station | Lot capture can be added as a story later |
| TA-08 | One container per component from a WeighingMS container master (C-09, C-11, C-12 buckets 214 g; D-03, D-05 drums 1.850 kg) | Prototype; Brief §9.3 | One container holds a whole recipe (Q29) | Container assignment isolated |
| TA-09 | The station always has a signed-in operator; in training R. Karim (Shift A) is signed in by default; change by badge ID; no password | Prototype top bar; Brief A-09 | Individual login required | Operator session API supports explicit sign-in |
| TA-10 | Supervisor override is available whenever the weight is outside tolerance and > 0; requires a seeded supervisor's PIN and a reason | Brief FR-23, FR-35; prototype key | Override not allowed for overweight, or needs remote approval (Q33) | Override policy in domain; revisited at Step 24 |
| TA-11 | Provisional overshoot response (until Step 24): no automatic recalculation; recover by removing excess, re-tare/re-weigh, or supervisor override | Workbook Step 24; Brief A-08 risk | FCI expects compensation | Step 24 decision record; compensation as a separate story if chosen |
| TA-12 | Completion and write-back start automatically when the last component is confirmed; batch status is set to WEIGHING at session start and WEIGHED after successful write-back | Prototype flow; Brief IR-05, IR-06 | OrgaTEX status model differs | Status mapping in adapter |
| TA-13 | Minimal continuity: a recipe snapshot is stored at session start so weighing continues if OrgaTEX drops; write-back failures become PENDING with retry; full offline mode (start new batches offline) is out of scope | Brief A-03, BR-16–18 | FCI requires full offline | Sync queue design allows extension |
| TA-14 | Tickets print on operator command on the Confirm & print screen, not automatically | Prototype "Print ticket" key | Auto-print expected | Trivial to switch |
| TA-15 | Ticket content follows the prototype; barcode encodes the batch ID (Code 128 rendered as bars) | Prototype ticket ("Label content is invented") | FCI defines different content (Q18) | Ticket template configurable |
| TA-16 | Live weight is polled through WeighingMS from the Dummy Scale (≥ 5 Hz); the backend re-reads weight at confirmation | Workbook Step 21; Brief A-05 | Real scales push or only send stable values | Scale adapter isolates protocol |
| TA-17 | Interface language is English | Prototype "EN"; Brief A-10 | Other language needed (Q35) | Strings centralised |
| TA-18 | Dummy scales expose a calibration due date; expired calibration blocks confirmation on that scale | Brief BR-24, FR-12 | — | Should priority |
| TA-19 | Recipes for B-24188, B-24190, B-24191 are invented training data (B-24188 = B-24187 recipe scaled by fabric weight 520/480; Navy 12 with 7 components; Rose 08 with 4 components), clearly labelled as such in the seed file | Prototype shows only B-24187's recipe | — | Labelled in seed data |
| TA-20 | The prototype's screen switcher becomes a workflow step indicator; question pins and meeting notes are not product features | Prototype notes ("Not a specification") | — | — |

## Open Questions (Unresolved)

| ID | Question | Brief ref | Owner | Resolution |
|----|----------|-----------|-------|------------|
| UQ-01 | What is the real OrgaTEX interface (technology, endpoints, auth, licence)? | A-01, Q6–Q10 | FCI / SETEX | Pending — Dummy API used |
| UQ-02 | Does OrgaTEX accept actual-consumption and status write-back from an external system? With what payload? | A-02, Q11–Q12 | FCI / SETEX | Pending |
| UQ-03 | During an OrgaTEX outage, should the station continue and sync later, or stop? | A-03, Q13 | FCI | Pending — minimal continuity (TA-13) |
| UQ-04 | Scale make, model, protocol; is weight streamed continuously with a stability flag? | A-05, Q15–Q16 | FCI | Pending — Dummy Scale simulates continuous readings |
| UQ-05 | Scale-selection boundary behaviour near 3 kg, including container weight on the precision scale | A-06, Q15 | FCI production | Pending |
| UQ-06 | How are tolerances defined (percentage, per dyestuff, banded) and by whom; do they come from OrgaTEX? | A-07, Q24 | FCI production | Pending — TA-03 |
| UQ-07 | What does "surplus compensation" mean, and what happens when an over-dose cannot be compensated? | A-08, Q25–Q26 | FCI production | Training decision at Workbook Step 24 |
| UQ-08 | Who may override a tolerance failure; must it be approved remotely? | Q33 | FCI | Pending — TA-10 |
| UQ-09 | How are dyestuff lots captured; how are containers identified? | A-09, Q28–Q29 | FCI | Pending — TA-07, TA-08 |
| UQ-10 | Do operators log in individually; how (badge, PIN)? | A-09, Q37 | FCI | Pending — TA-09 |
| UQ-11 | Which ticket printer, what label content, which barcode symbology? | A-04, Q18 | FCI | Pending — TA-15 |
| UQ-12 | Which interface language? | A-10, Q35 | FCI | Pending — TA-17 |
| UQ-13 | Do dyestuff containers carry scannable barcodes for identity verification? | A-10, Q19 | FCI | Pending — identity scan not built |
| UQ-14 | Daily batch volume; is one station enough? | A-15, Q21 | FCI | Pending |

## Training-only Dummy Behaviour

| ID | Behaviour | Why it exists |
|----|-----------|---------------|
| TD-01 | Dummy OrgaTEX serves seed batches, recipes, dyestuffs and lots from JSON; accepts status updates; stores consumption postings (idempotent by key) and exposes them for evidence | Real OrgaTEX unavailable |
| TD-02 | Dummy Scale simulates `scale-3kg` and `scale-32kg`: gross/net weight, tare, status, calibration date; time-based simulation profiles (dispense with easing, overshoot, stay below) and instant exact weight | Real scales unavailable; PDF §9 scenarios |
| TD-03 | Dummy Scanner accepts simulated scans and delivers them to the station in order; keyboard-wedge entry also accepted in the UI | Real scanner unavailable |
| TD-04 | Dummy Printer accepts tickets, stores them, returns ticket ID / PRINTED, lists them for evidence | Real printer unavailable |
| TD-05 | Failure injection per system (OrgaTEX, each scale, scanner, printer): unavailable → HTTP 503 | Workbook Step 30 failure tests |
| TD-06 | Reset to seed state (dummy data and WeighingMS training data) | Repeatable demos and tests |
| TD-07 | Training panel in the UI outside the device frame: Simulate dispense / overshoot, Reset weighing, Simulate scan, failure toggles, Reset training data | Mirrors the prototype's control bar |
| TD-08 | Default operator R. Karim signed in; seeded supervisor with training PIN | No real identity system |

## Traceability: Workbook requirement areas → FRs

| # | Workbook area | FR |
|---|---------------|----|
| 1 | Batch queue | FR-1 |
| 2 | Batch selection | FR-2 |
| 3 | Recipe loading | FR-3 |
| 4 | Component identification | FR-4 |
| 5 | Dyestuff lot | FR-5 |
| 6 | Container | FR-6 |
| 7 | Tare | FR-7 |
| 8 | Scale selection | FR-8 |
| 9 | Live weight | FR-9 |
| 10 | Target quantity | FR-10 |
| 11 | Remaining quantity | FR-11 |
| 12 | Tolerance | FR-12 |
| 13 | Confirmation | FR-13 |
| 14 | Overshoot | FR-14 |
| 15 | Component progression | FR-15 |
| 16 | Batch completion | FR-16 |
| 17 | OrgaTEX write-back | FR-17 |
| 18 | Ticket generation | FR-18 |
| 19 | Operator traceability | FR-19 |
| 20 | Scale/scanner/printer failure | FR-20 |
| — | Supporting | FR-21 – FR-34 |
