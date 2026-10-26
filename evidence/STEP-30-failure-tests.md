# STEP 30 — Failure scenario tests

Every scenario below is an automated Playwright test in
[`playwright/tests/failures.spec.ts`](../playwright/tests/failures.spec.ts). Each test runs against the real
stack (Vite UI → WeighingMS API → Dummy APIs), and the training controls make the failures happen. Each scenario
has a recording in [`STEP-30-failure-videos/`](STEP-30-failure-videos/).

- **Run:** `npm run test:e2e`, 2026-10-26, Chromium, 11 / 11 passed. Full output:
  [`STEP-29-30-playwright-run.txt`](STEP-29-30-playwright-run.txt).
- **HTML report:** [`STEP-29-playwright-report/index.html`](STEP-29-playwright-report/index.html).

| Scenario | Expected | Actual | Pass |
|---|---|---|---|
| Scale unavailable | Safe failure | The readout shows `—`, the status line reads **SCALE OFFLINE — CHECK CONNECTION**, **OK · Confirm** is disabled and the status strip shows `SCALE 3 kg · OFFLINE`. Nothing is recorded. When the scale returns, the reading (1242.0 g) and Confirm come back with no operator action. | ✅ |
| OrgaTEX unavailable (batch queue) | Defined behaviour | The queue shows *"OrgaTEX is not reachable. Check the connection and retry."* with a **Retry** button, and the status strip shows `ORGATEX · OFFLINE`. Once OrgaTEX is back, Retry loads the queue. | ✅ |
| OrgaTEX unavailable (during weighing) | Defined behaviour | The recipe snapshot is held locally (ADR-002), so weighing carries on: Blue RSPL is confirmed and the station moves to Red RB while OrgaTEX is down. | ✅ |
| OrgaTEX unavailable (write-back at completion) | Defined behaviour | The batch completes locally and **Written to OrgaTEX** shows `PENDING`. When OrgaTEX is back, **Retry** changes it to `CONFIRMED hh:mm:ss`. OrgaTEX holds **exactly one** consumption posting, because the posting is idempotent and keyed on the session ID. | ✅ |
| Printer unavailable | Defined behaviour | **Print ticket** shows *"Printer not available. Check the printer and try again."* The batch stays completed (`Batch B-24191 weighed`). Once the printer is back, printing works and the screen shows `Ticket printed · TKT-…`. | ✅ |
| Invalid weight | Cannot confirm | 1250.0 g against 1240.0 ± 6.0 g is shown, but Confirm is disabled. A direct `POST /api/sessions/{id}/confirm` that bypasses the UI returns **409 OUT_OF_TOLERANCE**, because the server re-reads the scale. Malformed weights (`-5`, `abc`) are rejected with **422 VALIDATION_ERROR**. No record is written. | ✅ |
| Over tolerance | Cannot confirm | At 1250.0 g the status line reads **OVER TOLERANCE — SURPLUS +10.0 g**, Confirm is disabled and the surplus panel explains how to recover (ADR-004: block and recover, no recalculation). | ✅ |
| Under tolerance | Cannot confirm | At 1200.0 g the status line reads **DISPENSE — 40.0 g REMAINING** and Confirm is disabled. No weighing record exists afterwards. | ✅ |
| Re-tare | Weight reset | With 500.0 g on the scale, **Re-tare (F2)** sets *Weighed now* back to `0.0`. | ✅ |
| Quit | Safe exit | **Quit (F4)** asks for confirmation, then returns to the queue. The unconfirmed 200 g is **not** recorded; only the confirmed Blue RSPL record exists. Reopening B-24187 resumes at Red RB with *1 of 5 components weighed*. | ✅ |
| Incomplete batch | Cannot complete | `POST /api/sessions/{id}/complete` with 0 of 5 weighed returns **409 BATCH_INCOMPLETE**, and the step indicator keeps **3 · Confirm & print** disabled. | ✅ |

## Backend tests behind the same rules

The same failure rules are also checked below the UI by `npm run check`: 214 backend tests at 97.86 %
coverage plus 50 frontend tests. The output is in [`STEP-29-check.txt`](STEP-29-check.txt).

Test files are in `tests/api/weighingms/`.

| Rule | Test |
|---|---|
| Scale offline gives the OFFLINE zone, and confirm is refused | `test_sessions_api.py::test_scale_offline_and_calibration_expired`, `test_completion_api.py::test_confirm_with_the_scale_down_is_refused` |
| A confirm re-reads the scale; out of band gives 409 | `test_completion_api.py::test_confirm_rereads_the_scale_and_rejects_out_of_tolerance` |
| OrgaTEX down: weighing continues; write-back is PENDING, then retried once | `test_sessions_api.py::test_weighing_in_progress_continues_when_orgatex_drops`, `test_completion_api.py::test_orgatex_down_at_completion_leaves_write_back_pending_then_retry` |
| Printer down: the batch stays completed; retry prints the original | `test_tickets_api.py::test_printer_down_keeps_the_batch_completed_and_retry_prints_the_original` |
| Quit records nothing; resume keeps confirmed components | `test_completion_api.py::test_quit_records_nothing_and_resume_keeps_done_components` |
| Incomplete batch gives 409 | `test_completion_api.py::test_incomplete_batch_cannot_be_completed` |
| Malformed simulated weight gives 422 | `test_devices_api.py::test_invalid_simulated_weight_is_rejected` |

## Defects found while writing these tests (fixed)

1. **Spurious 409 after the last confirm.** A live-weight poll could reach the server after the final confirm
   had completed the session, which left a `409 SESSION_COMPLETED` in the browser console. Live polling now
   pauses while an action runs (`frontend/src/features/weighing/WeighScreen.tsx`). The e2e workflow test now
   checks that the console has no errors.
2. **Malformed training weights.** `"abc"` returned 500 and `"-5"` returned 503 TRAINING_CONTROL_UNAVAILABLE.
   `QuantityIn.value` in `src/weighingms/api/training.py` is now checked against a non-negative decimal pattern
   and returns 422, with a regression test.
