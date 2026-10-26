---
intent: 001-assisted-dyestuff-weighing
phase: inception
status: units-decomposed
updated: 2026-10-26T06:31:00Z
---

# Assisted Dyestuff Weighing Station - Unit Decomposition

## Project type configuration

`memory-bank/project.yaml` → `full-stack-web` → catalog unit structure: backend units with **domain-driven** decomposition (default `ddd-construction-bolt`) and one **feature-based frontend** unit (default `simple-construction-bolt`). Integration/utility backend units use simple bolts where the work is adapters or contracts rather than domain logic.

## Evaluation of candidate capabilities

| Candidate (workbook) | Verdict | Reasoning |
|----------------------|---------|-----------|
| Batch Management | **Merged** into `orgatex-integration` (queue retrieval) and `weighing-station` (selection rule, session) | Batches are owned by OrgaTEX; WeighingMS has no batch lifecycle of its own beyond the weighing session. A separate unit would be a pass-through with no rules. |
| Recipe & Material Management | **Merged** into `orgatex-integration` (recipe/dyestuff/lot retrieval) and `weighing-station` (scale rule, tolerance policy, containers) | Recipes are read-only OrgaTEX data (BR-04). The only WeighingMS-owned rules on materials — scale selection and tolerance — are part of the weighing domain. |
| Weighing Station | **Kept** as `weighing-station` — the domain core | Holds the business rules and the traceability record: session, progression, tolerance, overshoot, override, completion. More than a screen: it is the aggregate everything else serves. |
| Scale Integration | **Kept and widened** as `device-integration` (scales + scanner + device status) | Same pattern for all station peripherals: protocol adapter, status, failure detection. Scanner alone is too small to be a unit. |
| OrgaTEX Integration | **Kept** as `orgatex-integration` | Brief IR-07 demands one replaceable adapter for all OrgaTEX interaction; it owns idempotent write-back and pending/retry. |
| Ticket & Printing | **Kept** as `ticket-printing` | Distinct capability: ticket composition (configurable content, IR-16) + printer adapter + reprint. |
| *(added)* Training substitutes | **Added** as `training-substitutes` | The Dummy APIs are product artifacts (Workbook Rule 5) with their own contracts, seed data, simulation and failure injection, running as a separate service. |
| *(added)* Operator UI | **Added** as `weighing-station-ui` (catalog frontend unit) | Reproduces the three prototype screens and chrome; consumes only the WeighingMS API. |

The three prototype screens did **not** drive the decomposition: Screen 2 alone spans four units (UI, weighing-station, device-integration, orgatex-integration).

## Units Overview

This intent decomposes into 6 units of work:

### Unit 1: 001-training-substitutes

**Description**: Separate FastAPI service (`:8100`) providing the Dummy OrgaTEX, Dummy Scale (two scales), Dummy Scanner and Dummy Printer with the workbook training contracts, seed data from the prototype, simulation profiles, failure injection and reset.

**Responsibility**: Behave like the external systems at the boundary, deterministically, for training and tests.

**Included capabilities**: batch/recipe/consumption/status contract; scale readings/tare/status/calibration with simulation; scan queue; ticket store; availability toggles; reset.

**Assigned requirements**: FR-25, FR-26, FR-27, FR-28, FR-29

**Stories**: 001-dummy-orgatex-batch-queue, 002-dummy-orgatex-recipe, 003-dummy-orgatex-consumption-and-status, 004-dummy-scale-readings-and-tare, 005-dummy-scanner, 006-dummy-printer, 007-failure-injection-and-reset

**Deliverables**: `src/dummy_systems/` app, `data/seed/orgatex-seed.json`, contract tests

**Dependencies**: Depends on: none · Depended by: orgatex-integration, device-integration, ticket-printing (contracts), weighing-station-ui (training panel, via WeighingMS)

**Why separate**: Must be replaceable by real systems without touching WeighingMS (PDF §9, §11 P3); different lifecycle (training only); own data store.

**Bolt type**: simple-construction-bolt (contracts and utilities, little domain logic)

**Estimated Complexity**: M

### Unit 2: 002-weighing-station

**Description**: The WeighingMS domain core and its application/persistence/API layers: weighing session aggregate, batch selection rule, automatic scale selection, tolerance evaluation, component progression, confirmation, overshoot, supervisor override, quit/abandon, completion, weighing records, audit, operator identity.

**Responsibility**: Enforce the weighing business rules and produce the immutable traceability record.

**Included capabilities**: selection/resume; scale rule; tolerance policy; active-component context (lot, container, tare); confirm with server-side re-read; overshoot rule (Step 24 decision); override; abandon; completion trigger; records and summary; operator session.

**Assigned requirements**: FR-2, FR-5, FR-6, FR-8, FR-10, FR-11, FR-12, FR-13, FR-14, FR-15, FR-16, FR-19, FR-21, FR-22, FR-23

**Stories**: 001-start-or-resume-weighing-session, 002-automatic-scale-selection, 003-tolerance-evaluation, 004-confirm-component-weighing, 005-overshoot-handling, 006-supervisor-override, 007-component-progression, 008-quit-and-abandon, 009-batch-completion, 010-activate-component-weighing-context, 011-weighing-summary-and-records

**Deliverables**: `src/weighingms/domain`, `application`, `infrastructure/persistence`, `api` (session endpoints); Alembic migrations; unit + API tests

**Dependencies**: Depends on: ports implemented by orgatex-integration and device-integration (for application layer); none for the pure domain · Depended by: ticket-printing (records), weighing-station-ui

**Why separate**: Highest rule density and risk (BO-01, BO-02); must be testable without any I/O; changes when FCI answers A-07/A-08 without touching integrations.

**Bolt type**: ddd-construction-bolt

**Estimated Complexity**: L

### Unit 3: 003-orgatex-integration

**Description**: The single OrgaTEX adapter (IR-07) and the WeighingMS batch endpoints the UI uses: batch queue, batch detail, recipe (mapped to the WeighingMS model), batch status write-back, idempotent consumption write-back with PENDING/retry.

**Responsibility**: Isolate everything OrgaTEX-specific behind `OrgatexPort`.

**Included capabilities**: HTTP client to Dummy OrgaTEX; DTO mapping; error translation (`ORGATEX_UNAVAILABLE`); last-sync time; idempotency key; retry.

**Assigned requirements**: FR-1, FR-3, FR-4, FR-17

**Stories**: 001-batch-queue-from-orgatex, 002-batch-detail-and-recipe-from-orgatex, 003-consumption-write-back

**Deliverables**: `src/weighingms/infrastructure/orgatex/`, `src/weighingms/api/batches.py`, adapter tests against the dummy

**Dependencies**: Depends on: training-substitutes (contract, for tests) · Depended by: weighing-station (application layer), weighing-station-ui

**Why separate**: Real interface is the biggest unknown (A-01, A-02, R-01); a change of technology must affect one replaceable part.

**Bolt type**: simple-construction-bolt (integration)

**Estimated Complexity**: M

### Unit 4: 004-device-integration

**Description**: Adapters for the scales and scanner, the live-weight read path, tare/re-tare commands, scan delivery, and aggregated device status (scales incl. calibration, scanner, printer, OrgaTEX link) with failure detection.

**Responsibility**: Isolate device protocols behind `ScalePort` / `ScannerPort` and give the station a truthful device status.

**Included capabilities**: weight polling, staleness detection (> 2 s), tare, scan cursor, status endpoint.

**Assigned requirements**: FR-7, FR-9, FR-20, FR-24

**Stories**: 001-live-weight-from-selected-scale, 002-tare-and-re-tare, 003-scanner-input, 004-device-status-and-failure-detection

**Deliverables**: `src/weighingms/infrastructure/devices/`, `src/weighingms/api/devices.py`, tests against the dummy

**Dependencies**: Depends on: training-substitutes (contracts) · Depended by: weighing-station (application layer), weighing-station-ui

**Why separate**: Device protocol is unknown (A-05, UQ-04); safety-relevant failure detection (IR-13) must be isolated and testable.

**Bolt type**: simple-construction-bolt (integration)

**Estimated Complexity**: M

### Unit 5: 005-ticket-printing

**Description**: Ticket composition from the completed session's records (configurable header/content), printing through the printer adapter, reprint marking.

**Responsibility**: Produce the physical record that travels with the container (BR-15).

**Included capabilities**: ticket model + text layout + barcode value; `PrinterPort` adapter; print/reprint endpoints; printer failure handling.

**Assigned requirements**: FR-18

**Stories**: 001-compose-weighing-ticket, 002-print-ticket, 003-reprint-ticket

**Deliverables**: `src/weighingms/application/tickets.py`, `src/weighingms/infrastructure/printer/`, `src/weighingms/api/tickets.py`, tests

**Dependencies**: Depends on: weighing-station (completed session and records), training-substitutes (printer contract) · Depended by: weighing-station-ui

**Why separate**: Content is undefined by FCI (A-04, Q18) and must change without code changes (IR-16); separate failure boundary (printer).

**Bolt type**: simple-construction-bolt

**Estimated Complexity**: S

### Unit 6: 006-weighing-station-ui

**Description**: React + TypeScript operator terminal reproducing the prototype: device frame and chrome, Screen 1 Select batch, Screen 2 Weigh, Screen 3 Confirm & print, training panel, function keys, operator-facing error states; plus the Playwright end-to-end and failure suites.

**Responsibility**: Present the WeighingMS API faithfully to the operator; never re-implement business rules.

**Included capabilities**: API client with generated types; polling for live evaluation, device status and scans; three screens; dialogs (override, quit, operator); training panel; E2E tests.

**Assigned requirements**: FR-30, FR-31, FR-32, FR-33, FR-34

**Stories**: 001-station-shell-and-chrome, 002-batch-queue-screen, 003-select-batch-by-touch-or-scan, 004-recipe-rail, 005-live-weighing-panel, 006-weighing-actions, 007-overshoot-surplus-panel, 008-completion-summary-screen, 009-ticket-preview-and-print, 010-operator-facing-failure-messages, 011-function-keys, 012-end-to-end-workflow-test, 013-failure-scenario-tests

**Deliverables**: `frontend/`, `playwright/`, root `package.json` dev script integration

**Dependencies**: Depends on: all backend units (through the WeighingMS API) · Depended by: none

**Why separate**: Catalog frontend unit; different technology (TypeScript/React) and bolt type; UI fidelity is its own acceptance dimension (Workbook Step 28).

**Bolt type**: simple-construction-bolt

**Estimated Complexity**: L

## Requirement-to-Unit Mapping

Each FR is assigned to exactly one owning unit (stories in other units may also reference it):

- **FR-1** Batch queue → `003-orgatex-integration`
- **FR-2** Batch selection → `002-weighing-station`
- **FR-3** Recipe loading → `003-orgatex-integration`
- **FR-4** Component identification → `003-orgatex-integration`
- **FR-5** Dyestuff lot → `002-weighing-station`
- **FR-6** Container → `002-weighing-station`
- **FR-7** Tare → `004-device-integration`
- **FR-8** Scale selection → `002-weighing-station`
- **FR-9** Live weight → `004-device-integration`
- **FR-10** Target quantity → `002-weighing-station`
- **FR-11** Remaining quantity → `002-weighing-station`
- **FR-12** Tolerance → `002-weighing-station`
- **FR-13** Confirmation → `002-weighing-station`
- **FR-14** Overshoot → `002-weighing-station`
- **FR-15** Component progression → `002-weighing-station`
- **FR-16** Batch completion → `002-weighing-station`
- **FR-17** OrgaTEX write-back → `003-orgatex-integration`
- **FR-18** Ticket generation → `005-ticket-printing`
- **FR-19** Operator traceability → `002-weighing-station`
- **FR-20** Scale/scanner/printer failure → `004-device-integration`
- **FR-21** Supervisor override → `002-weighing-station`
- **FR-22** Quit → `002-weighing-station`
- **FR-23** Summary and record review → `002-weighing-station`
- **FR-24** Device status visibility → `004-device-integration`
- **FR-25** Dummy OrgaTEX → `001-training-substitutes`
- **FR-26** Dummy Scale → `001-training-substitutes`
- **FR-27** Dummy Scanner → `001-training-substitutes`
- **FR-28** Dummy Printer → `001-training-substitutes`
- **FR-29** Training controls → `001-training-substitutes`
- **FR-30** Screen 1 → `006-weighing-station-ui`
- **FR-31** Screen 2 → `006-weighing-station-ui`
- **FR-32** Screen 3 → `006-weighing-station-ui`
- **FR-33** Station chrome → `006-weighing-station-ui`
- **FR-34** Function keys → `006-weighing-station-ui`

Coverage: 34 / 34 FRs assigned; no FR assigned twice.

## Unit Dependency Graph

```text
                    [001-training-substitutes]
                     │          │           │
          (contract) ▼          ▼           ▼ (contract)
 [003-orgatex-integration] [004-device-integration]   │
                     │          │                      │
                     └────┬─────┘                      │
                          ▼                            ▼
                 [002-weighing-station] ──────► [005-ticket-printing]
                          │                            │
                          └─────────────┬──────────────┘
                                        ▼
                             [006-weighing-station-ui]
```

The pure domain of `002-weighing-station` has no dependencies and can be built before the adapters; its application layer needs the ports implemented by 003 and 004. No circular dependencies.

## Execution Order

Following the workbook's construction sequence (Steps 16 → 30):

1. `001-training-substitutes` — dummy layer and seed data (Steps 16–18)
2. `003-orgatex-integration` + `006-weighing-station-ui` (Screen 1) — batch selection end to end (Step 19)
3. `002-weighing-station` domain → `004-device-integration` → `002-weighing-station` application/API (Steps 20–25)
4. `006-weighing-station-ui` Screen 2 (Steps 20–25)
5. `005-ticket-printing` → `006-weighing-station-ui` Screen 3 (Steps 26–27)
6. `006-weighing-station-ui` E2E + failure suites (Steps 28–30)
