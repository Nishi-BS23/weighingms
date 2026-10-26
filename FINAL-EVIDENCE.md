# WeighingMS — Final Evidence Matrix

Workbook Step 34. This matrix links each behaviour the product must show to the screen that presents it, the API
that serves it, the code that implements it, the tests that prove it, and the recorded evidence.

**Paths and test status:**
- **Paths:**
  - **UI** is under `frontend/src/features/`.
  - **Code** is under `src/weighingms/` (`dom/` = `domain/`, `app/` = `application/`, `infra/` = `infrastructure/`).
  - **Tests** are under `tests/` (backend), `frontend/src/**/*.test.tsx` (frontend) and `playwright/tests/` (e2e).
  - **Evidence** is under `evidence/`.
- **Test status** (2026-10-26, details in `evidence/STEP-29-check.txt` and `evidence/STEP-29-30-playwright-run.txt`):
  - `npm run check`: **214** backend tests (97.86 % coverage) and **50** frontend tests passed.
  - `npm run test:e2e`: **11 / 11** Playwright tests passed.

## Required matrix

| Requirement | UI | API | Code | Test | Evidence | Result |
|---|---|---|---|---|---|---|
| **Batch queue** (FR-1) | ✓ `batch-queue/BatchQueueScreen.tsx`, `QueueTable.tsx` | ✓ `GET /api/batches` | ✓ `app/batches.py`, `infra/orgatex/http_adapter.py` | ✓ `test_batches_api.py`, `BatchQueueScreen.test.tsx`, e2e `workflow.spec.ts` | `STEP-19-batch-screen.png`, `STEP-28-ui-validation/screen-1-comparison.png` | ✅ Pass |
| **Batch selection** (FR-2) | ✓ row touch + `ScanPrompt.tsx` (scan/type) | ✓ `GET /api/batches/{id}`, `POST /api/sessions` | ✓ `app/sessions.py` (`start_or_resume`) | ✓ `test_sessions_api.py` (start, resume, WEIGHED refused), `BatchQueueScreen.test.tsx`, e2e network assertion | `STEP-19-after-selection.png`, `STEP-19-network.txt` | ✅ Pass |
| **Recipe** (FR-3) | ✓ `weighing/RecipeRail.tsx` (5 components) | ✓ `GET /api/batches/{id}/recipe` | ✓ `app/batches.py`; recipe snapshot per session `dom/weighing/session.py` (ADR-002) | ✓ `test_batches_api.py`, `RecipeRail.test.tsx`, e2e | `STEP-20-weigh-screen.png`, `STEP-17-dummy-data.json` | ✅ Pass |
| **Scale selection** (FR-8; ≤ 3 kg → precision, > 3 kg → floor) | ✓ "SCALE SELECTED" badge, `WeighingPanel.tsx` | ✓ session `active.scale` via `POST …/activate` | ✓ `dom/scale_selection.py`; threshold in `config/station.toml` | ✓ `test_scale_selection.py` (incl. configurable threshold), `test_sessions_api.py::test_scale_switch_to_the_floor_scale`, e2e boundaries test | `STEP-21-scale-3kg-yellow.png`, `STEP-21-scale-switch.png` | ✅ Pass |
| **Live weight** (FR-9) | ✓ Readout, 120 ms polling `shared/use-polling.ts` | ✓ `GET /api/sessions/{id}/live` | ✓ `app/sessions.py` (`live`), `infra/devices/scale_adapter.py` (stale > 2 s gives OFFLINE) (ADR-001) | ✓ `test_device_adapters.py`, `test_sessions_api.py`, `WeighScreen.test.tsx`, e2e dispense ramp | `STEP-20-weigh-screen.png`, `STEP-29-e2e-video.mp4` | ✅ Pass |
| **Tolerance** (FR-12; under / within / over, configurable) | ✓ tolerance bar, caption, status line, Confirm enabling | — (evaluated inside `/live` and again at `/confirm`) | ✓ `dom/tolerance.py`, `dom/weighing/evaluation.py`; default rule in `config/station.toml` | ✓ `test_tolerance_band.py`, `test_tolerance_evaluation.py`, `WeighingPanel.test.tsx`, e2e 93.4 / 93.5 / 94.0 / 94.5 / 94.6 | `STEP-22-tolerance-tests.txt`, `STEP-22-tolerance-ui-*.png` | ✅ Pass |
| **Lot tracking** (FR-5) | ✓ "LOT 2026-0387" in the weigh header | ✓ `lotId` in recipe, `GET /api/weighing-records`, and the OrgaTEX posting | ✓ `dom/weighing/records.py`, `infra/orgatex/contract.py` | ✓ `test_batches_api.py`, `test_completion_api.py` (record lot / container / scale), `test_session_completion.py`, `WeighingPanel.test.tsx` | `STEP-25-transaction.json`, `STEP-26-writeback.json` | ✅ Pass |
| **Container / tare** (FR-6, FR-7) | ✓ "CONTAINER C-12 · TARE 214.0 g", Re-tare F2 | ✓ `POST …/activate` (tares), `POST …/retare` | ✓ `dom/weighing/containers.py`; containers in `config/station.toml` | ✓ `test_station_master_data.py`, `test_sessions_api.py` (activation tares, re-tare), `test_device_adapters.py`, e2e re-tare | `STEP-21-scale-switch.png` (D-03 · 1.850 kg), `STEP-30-failure-videos/7-re-tare.webm` | ✅ Pass |
| **Component progression** (FR-15) | ✓ rail states done / active / pending, "n of 5 components weighed" | ✓ `POST …/confirm` (activates the next component) | ✓ `dom/weighing/session.py` | ✓ `test_session_aggregate.py`, `test_completion_api.py::test_confirm_records_and_advances_to_the_next_component`, e2e | `STEP-23-five-component-demo.mp4`, `STEP-25-confirmation.png` | ✅ Pass |
| **Overshoot** (FR-14; block and recover, ADR-004) | ✓ `SurplusPanel` (surplus, %, guidance), Supervisor override dialog | ✓ `/live` (`surplus`, `guidance`), `POST …/override` | ✓ `dom/weighing/evaluation.py`, `dom/operators.py` (PIN check) | ✓ `test_completion_api.py` (overshoot blocks then recovers, override, PIN never logged), `test_sessions_api.py::test_overshoot_surplus_in_live_response`, `WeighScreen.test.tsx` | `STEP-24-overshoot-decision.md`, `STEP-24-overshoot-test.txt`, `STEP-24-overshoot-ui.png` | ✅ Pass |
| **OrgaTEX write-back** (FR-17; idempotent, PENDING then retry) | ✓ "Written to OrgaTEX CONFIRMED hh:mm:ss" or PENDING + Retry | ✓ the last `POST …/confirm` completes the batch and posts it; `POST …/complete`, `POST …/sync` (retry) | ✓ `app/sessions.py` (`_write_back`), `infra/orgatex/http_adapter.py` | ✓ `test_completion_api.py` (writes back once, PENDING then retry), `test_orgatex_adapter.py`, `DoneScreen.test.tsx`, e2e (checked on the dummy OrgaTEX) | `STEP-26-writeback.json`, `STEP-26-request-log.txt`, `STEP-26-ui.png` | ✅ Pass |
| **Ticket** (FR-18) | ✓ `ticket/TicketPreview.tsx`, Print ticket F1 | ✓ `GET …/ticket`, `POST …/ticket/print` | ✓ `dom/ticket.py`, `app/tickets.py`, `infra/devices/peripherals_adapter.py` | ✓ `test_ticket.py`, `test_tickets_api.py` (print, reprint, printer down), `TicketPreview.test.tsx`, e2e (checked on the dummy printer) | `STEP-27-ticket.png`, `STEP-27-printer-api.json` | ✅ Pass |

## Further behaviours required by the project

| Requirement | UI | API | Code | Test | Evidence | Result |
|---|---|---|---|---|---|---|
| **Confirmation and records** (FR-13; durable, immutable) | ✓ OK · Confirm F1 | ✓ `POST …/confirm` (re-reads the scale) | ✓ `infra/persistence/repositories.py` (`save_with_record`, WAL + `synchronous=FULL`) | ✓ `test_completion_api.py`, `test_persistence.py` | `STEP-25-confirmation.png`, `STEP-25-transaction.json` | ✅ Pass |
| **Batch completion and summary** (FR-16, FR-23) | ✓ `ticket/DoneScreen.tsx` (summary and per-component results) | ✓ `POST …/complete` (409 BATCH_INCOMPLETE), `GET …/summary` | ✓ `app/summary.py`, `dom/weighing/session.py` | ✓ `test_completion_api.py` (incomplete refused, summary matches the prototype), `DoneScreen.test.tsx`, e2e | `STEP-28-ui-validation/screen-3-comparison.png` | ✅ Pass |
| **Quit** (FR-22) | ✓ Quit F4 with confirmation dialog | ✓ `POST …/quit` | ✓ `dom/weighing/session.py` (`abandon`) | ✓ `test_completion_api.py::test_quit_records_nothing_and_resume_keeps_done_components`, e2e | `STEP-30-failure-tests.md`, `STEP-30-failure-videos/8-quit.webm` | ✅ Pass |
| **Device failures** (FR-20; scale, OrgaTEX, printer, scanner) | ✓ plain messages, `chrome/StatusStrip.tsx` | ✓ `GET /api/devices/status`; error codes (503) | ✓ `app/devices.py`, `infra/devices/*` | ✓ `test_device_status.py`, `test_devices_api.py`, `StatusStrip.test.tsx`, `messages.test.ts`, e2e failure suite (9 scenarios) | `STEP-30-failure-tests.md`, `STEP-30-failure-videos/` | ✅ Pass |
| **Operator traceability** (FR-19) | ✓ operator chip + `chrome/OperatorDialog.tsx` | ✓ `GET /api/operators/current`, `POST /api/operators/sign-in` | ✓ `app/operators.py` | ✓ `test_sessions_api.py` (operator identification, operator recorded on the session), `OperatorDialog.test.tsx` | `STEP-27-ticket.png` (OPER. R. Karim) | ✅ Pass |
| **Configurability** (NFR-13) | — | — | ✓ `config/station.toml` (threshold, scales, tolerance rule, ticket header, containers) | ✓ `test_scale_selection.py::test_threshold_is_configurable`, `test_tolerance_band.py` (default rule) | `config/station.toml` | ✅ Pass |
| **Mocks separate from business logic** | — | ✓ separate service on :8100 | ✓ ports in `app/ports.py`, adapters in `infra/`; `src/dummy_systems/` is a separate package | ✓ adapter tests in `tests/integration/` against the dummy app | `STEP-09-system-context.md`, `STEP-18-api-tests.txt` | ✅ Pass |
| **End-to-end workflow** (NFR-17) | ✓ all three screens | ✓ full chain UI → API → Dummy APIs | ✓ whole stack | ✓ `playwright/tests/workflow.spec.ts` | `STEP-29-playwright-report/`, `STEP-29-e2e-video.mp4` | ✅ Pass |
| **UI/UX matches the prototype** | ✓ three screens | — | ✓ `frontend/src/styles/station.css` (ported) | ✓ e2e selectors and texts match the prototype | `STEP-28-ui-validation/` (3 comparisons + `validation.md`) | ✅ Pass (differences documented) |

## Traceability to the AI-DLC artifacts

| Artifact | Location | Status |
|---|---|---|
| Intent and requirements (34 FR, 18 NFR) | `memory-bank/intents/001-assisted-dyestuff-weighing/requirements.md` | complete |
| Units (6) and stories (41) | `memory-bank/intents/001-assisted-dyestuff-weighing/units/` | 6 / 6 and 41 / 41 complete |
| Bolts (11) with stage artifacts | `memory-bank/bolts/` | 11 / 11 complete |
| Decisions | `memory-bank/standards/decision-index.md` (ADR-001 … ADR-004) | accepted |
| Integrity | `status-integrity.cjs` (0 inconsistencies), `artifact-validator.cjs` (0 issues) | `evidence/STEP-31-project-status.md` |
| Dashboard | specsmd dashboard: 100 %, 41 / 41 stories, 11 / 11 bolts | `evidence/STEP-32-final-dashboard*.png` |

## Known limits (training build)

- **Dummy APIs replace the real systems.** OrgaTEX, the scales, the scanner and the printer are Dummy APIs. The
  real interfaces are open questions for FCI (UQ-01 … UQ-14), and the adapters are the only part to replace.
- **Confirm doesn't wait for a stable reading.** Confirm is gated by tolerance, not by the scale's stability flag
  (UQ-04 is open).
- **Override with expired calibration.** A supervisor override is allowed when calibration has expired. This
  deviation is documented in bolt 007's test report.
- **Scale unavailable at confirm returns 503,** not 409. The UI keeps Confirm disabled either way. This deviation
  is also documented in bolt 007's test report.
