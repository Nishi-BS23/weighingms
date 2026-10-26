# Step 6: Intent created + Checkpoint 1 (Intent validation)

Artifact: memory-bank/intents/001-assisted-dyestuff-weighing/ (requirements.md draft + inception-log.md)
Validation: self-validated by the agent on the participant's delegation (2026-10-26)

## Checkpoint 1 checklist
- [x] Business problem is correct — manual, unrecorded weighing; shade failures cannot be attributed (Brief §2)
- [x] Primary user is correct — weighing operator; supervisor secondary (Brief §4)
- [x] Desired outcome is correct — guided end-to-end weighing with tolerance enforcement, traceability, OrgaTEX write-back, ticket
- [x] Scope is reasonable — in/out of scope listed; real integrations and OrgaTEX replacement excluded
- [x] UI/UX is included as a source — docs/customize-weighing-station.html
- [x] Dummy integrations are included — OrgaTEX, scales, scanner, printer (training contracts only)
- [x] Unknowns are identified — 8 topics with Brief assumption/question references
- [x] WeighingMS does not replace OrgaTEX (workbook example correction pre-empted)

Result: APPROVE INTENT

---- Snapshot of requirements.md at intent approval ----
---
intent: 001-assisted-dyestuff-weighing
phase: inception
status: draft
created: 2026-10-26T06:16:00Z
updated: 2026-10-26T06:16:00Z
---

# Requirements: Assisted Dyestuff Weighing Station (WeighingMS)

## Intent Overview

Build **WeighingMS**, an assisted dyestuff weighing station for FCI's dyehouse, as a working training application that reproduces the functional experience of the supplied UI/UX prototype (`docs/customize-weighing-station.html`).

WeighingMS sits between OrgaTEX (FCI's MES, the upstream source of batches and recipes and the downstream recipient of actual consumption) and the weighing operator. It guides the operator through weighing every component of a batch recipe on the automatically selected scale, enforces tolerance at confirmation, records full traceability for each weighing, writes actual consumption back to OrgaTEX, and prints a weighing ticket that travels with the container.

**WeighingMS does not replace OrgaTEX.** OrgaTEX remains the system of record for batches, recipes and dyestuff master data; WeighingMS consumes them read-only and only writes back weighing status and actual consumption (Brief C-01, C-02, BR-04). WeighingMS does not automate dispensing (Brief C-03).

Because the real OrgaTEX, scales, scanner and printer are not available, the product includes **Dummy APIs** (training substitutes) for OrgaTEX, the weighing scales, the barcode scanner and the ticket printer. These are training contracts only — **they are not claims about the real OrgaTEX interface or real device protocols.**

## Business Problem

Today dyestuff weighing is manual and unrecorded (Brief §2, A-13): recipes arrive on paper, operators weigh by eye, and what was actually dispensed is never captured. When a batch fails shade approval, a bad recipe cannot be distinguished from a bad weighing, so failures cannot be attributed and recur.

## Primary Users

- **Weighing operator** (primary): weighs each component at the station; needs a station that is faster and less stressful than paper (Brief §4, BO-06).
- **Dyehouse supervisor** (secondary): authorises tolerance overrides, follows batch progress (Brief §4, BR-13).
- Lab/QA and store (indirect): consume the weighed-vs-recipe record and actual consumption.

## Desired Outcome

An operator can: select a batch from the OrgaTEX queue (by touch or scan) → see its recipe → weigh each component on the automatically selected scale while watching live weight against target and tolerance → confirm only when within tolerance (or with an authorised override) → progress through all components → complete the batch, with consumption written back to OrgaTEX and a ticket printed. The complete workflow must work end to end and be demonstrable and automatically tested (Project Requirement §12; Workbook Rule 6).

## Business Goals

| Goal | Success Metric | Priority |
|------|----------------|----------|
| Prevent out-of-tolerance weighings reaching production (BO-01) | 0 confirmations outside tolerance without a recorded supervisor override, proven by automated tests | Must |
| Component-level traceability for every batch (BO-02) | 100% of confirmed weighings record target, actual, operator, scale, lot, container, tare, timestamp | Must |
| Reconcile actual vs theoretical consumption (BO-04) | Every completed batch posts per-component actual consumption to (Dummy) OrgaTEX | Must |
| Reproduce the supplied UI/UX experience | Screen-by-screen comparison with the prototype shows all screens, states and interactions present | Must |
| Demonstrable, testable product | Playwright end-to-end run of batch B-24187 passes; failure scenarios tested | Must |

## Scope (initial)

### In scope
- Batch queue from OrgaTEX; batch selection by touch or barcode scan
- Recipe retrieval and component list in recipe sequence
- Component identity, dyestuff lot, container and tare for the active component
- Automatic scale selection (precision ≤ 3 kg, floor/heavy-duty > 3 kg), configurable
- Live weight, target, remaining, tolerance band, progress bar, status line
- Tolerance enforcement at confirmation; overshoot detection and a defined training response
- Supervisor override with recorded reason; re-tare; quit/abandon
- Component progression and batch completion
- Weighing records with full traceability; completed-batch summary
- Actual-consumption write-back to OrgaTEX
- Weighing ticket generation and printing (print preview)
- Operator identification and traceability
- Device/system status and safe behaviour on scale, scanner, printer or OrgaTEX failure
- Dummy APIs for OrgaTEX, scales, scanner and printer, with training simulation and failure injection

### Out of scope
- Real OrgaTEX, scale, scanner or printer integration (training substitutes only)
- Inventing or asserting real OrgaTEX API contracts or device protocols
- Dispensing-machine control, automated transport, liquid dosing (Brief §5.2)
- Recipe authoring or modification (recipes stay owned by OrgaTEX)
- Multi-station, multi-site deployment; reporting dashboards; localisation beyond English (deferred)

## Source Artifacts

| Source | Role |
|--------|------|
| `docs/brief.md` | Business requirements (BRD v1.1 draft) — business intent; all of it unconfirmed by FCI |
| `docs/customize-weighing-station.html` | UI/UX prototype — intended visual experience and interaction patterns |
| `docs/project-requirement.pdf` (`.txt`) | Course project requirement — mandatory behaviours for this build |

## Unknowns Identified (to be carried into detailed requirements)

| Topic | Source | Status |
|-------|--------|--------|
| Real OrgaTEX interface and write-back acceptance | Brief A-01, A-02, Q6–Q13 | Unresolved — Dummy API used |
| Continuous weight streaming and scale protocol | Brief A-05, Q15–Q16 | Unresolved — Dummy Scale simulates continuous readings |
| Meaning of "surplus compensation" for over-dose | Brief A-08, Q25–Q26; prototype surplus panel | Unresolved — training rule to be decided (Workbook Step 24) |
| How tolerances are defined, by whom | Brief A-07, Q24; PDF §6/§7 | Partly resolved — per-component, configurable |
| Operator identification method | Brief A-09, Q37 | Unresolved — training assumption needed |
| Container identity, lot capture | Brief A-09, Q28–Q29 | Unresolved — training assumption needed |
| Offline operation expectations | Brief A-03, Q13 | Unresolved — minimal defined behaviour needed |
| Ticket content and printer | Brief A-04, Q18 | Unresolved — prototype content used |
