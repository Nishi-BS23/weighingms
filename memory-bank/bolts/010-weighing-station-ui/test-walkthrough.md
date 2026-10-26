---
stage: test
bolt: 010-weighing-station-ui
created: 2026-10-26T09:14:43Z
---

## Test Report: 006-weighing-station-ui (bolt 3 of 4) — Screen 3, failure messages, function keys

### Summary

- **Tests**: frontend 49/49 passed (14 new); backend 213/213 unchanged
- **Static checks**: Prettier, ESLint (type-checked), `tsc --noEmit` clean
- **Message coverage**: every error code declared by the backend has an operator message (cross-checked by grep against `src/weighingms`)

### Test Files

- [x] `frontend/src/features/ticket/DoneScreen.test.tsx` - completion summary rows and CONFIRMED time, results table, consumption note; PENDING → Retry → CONFIRMED; print → "Ticket printed · TKT-…" with the printed (non-reprint) ticket; printer down → plain message, key still enabled; F1 prints, F3 next batch
- [x] `frontend/src/features/ticket/TicketPreview.test.tsx` - prototype ticket fields, barcode bars, REPRINT marker, overridden line "*", result line; deterministic barcode
- [x] `frontend/src/shared/messages.test.ts` - message for every API code; no codes/JSON/stack traces in operator text; specific server wording kept where already plain; generic fallback
- [x] `frontend/src/shared/ErrorBoundary.test.tsx` - broken screen replaced by plain message; "Back to batch queue"
- [x] `frontend/src/features/weighing/WeighScreen.test.tsx` (extended) - F1 blocked while not confirmable, F1 confirms when allowed, F2 re-tares, F4 opens quit dialog, F-keys ignored while a dialog is open

### Acceptance Criteria Validation

- ✅ **008-completion-summary-screen**: heading, 6 summary rows, results, write-back CONFIRMED / PENDING + Retry, consumption note, Next batch → Screen 1 (browser: F3 → queue shows B-24187 WEIGHED)
- ✅ **009-ticket-preview-and-print**: preview with all fields + barcode; print → ticket ID; reprint marked; printer unavailable message (evidence/STEP-27-ticket.png)
- ✅ **010-operator-facing-failure-messages**: complete mapping, no technical text, error boundary per screen
- ✅ **011-function-keys**: F1/F2/F4 on Screen 2, F1/F3 on Screen 3, suppressed in dialogs, browser defaults prevented

### Issues Found

- UX defect fixed during implementation: after the first print the preview showed "*** REPRINT ***" (next-print view); it now shows the ticket as printed.
- Four generic codes (COMPONENT_NOT_FOUND, NOT_FOUND, HTTP_ERROR, DOMAIN_ERROR) lacked operator wording; added.

### Notes

Browser evidence: STEP-26-ui.png (written to OrgaTEX CONFIRMED), STEP-27-ticket.png (printed ticket), whole batch confirmed with F1.

### Stage checkpoint (delegated, self-validated)

All tests pass; acceptance criteria verified. **Approved** — bolt complete.
