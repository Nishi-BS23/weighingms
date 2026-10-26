# STEP 33 — Final validation: did we build the product we intended to build?

Prepared by the agent from the artifacts and the running application. **This is a human gate: the participant
confirms it** by running the Step 35 demonstration.

## 1. Product brief: does the product solve the defined problem?
**Yes.** The brief (`docs/brief.md`) describes manual dyestuff weighing with transcription errors, no
enforcement of tolerance, and no traceable consumption. WeighingMS addresses each part:
- It guides one component at a time from the OrgaTEX recipe.
- It selects the right scale automatically.
- It enforces the tolerance (Confirm is impossible outside the band unless a supervisor authorises it with a
  reason).
- It records every weighing durably and immutably: lot, container, tare, scale and operator.
- It posts actual consumption back to OrgaTEX exactly once.
- It prints a ticket to travel with the container.

Out of scope, as agreed in inception: full offline mode, a real OrgaTEX interface and real device protocols
(TA-13, UQ-01 … UQ-14).

## 2. UI/UX: does the application reproduce the intended experience?
**Yes.** All three prototype screens are reproduced with the same data, labels, units and states. Each difference
is either intentional or comes from the prototype's quirks-mode rendering, and each is listed in
`STEP-28-ui-validation/validation.md`. The operator flow (touch or scan, then weigh, then confirm, then print,
then next batch) and the F-keys work as in the prototype.

## 3. Requirements: does every approved requirement have an implementation?
**Yes.**
- All 34 FRs map to stories (41 / 41 complete), and all stories are implemented across 11 completed bolts.
- The NFRs that can be measured are met:
  - Exact `Decimal` arithmetic.
  - Writes committed under WAL and `synchronous=FULL` before the response.
  - Idempotent write-back.
  - Keys 62 px.
  - Configuration file only.
  - `npm run dev` starts everything.
  - Coverage 97.86 %.
- `FINAL-EVIDENCE.md` maps every requirement to its UI, API, code, test and evidence.

## 4. Acceptance criteria: can every important behaviour be demonstrated?
**Yes.** The B-24187 workflow, the scale switch, the tolerance boundaries, overshoot recovery, the supervisor
override, write-back (including PENDING then retry) and ticket print or reprint can all be shown in the running
app with the training controls. The demonstration script is `STEP-35-demo-guide.md`.

## 5. Tests: can the behaviour be proven automatically?
**Yes.**
- `npm run check`: 214 backend and 50 frontend tests.
- `npm run test:e2e`: 11 Playwright tests, covering the full workflow and the 9 failure scenarios.
- Three consecutive green runs; the HTML report and videos are in `STEP-29-*` and `STEP-30-*`.

## Open items that remain the participant's or FCI's
- **Open questions:** answer the 13 pending questions (UQs) with FCI / SETEX before connecting real systems.
- **Override with expired calibration:** decide whether a supervisor may still override when calibration has
  expired (currently allowed; see bolt 007's test report).
- **Stable readings:** decide whether Confirm should also require a stable scale reading (UQ-04).

**Verdict: ready for the final demonstration.**
