---
stage: implement
bolt: 010-weighing-station-ui
created: 2026-10-26T09:12:27Z
---

## Implementation Walkthrough: 006-weighing-station-ui (bolt 3 of 4) — Screen 3, failure messages, function keys

### Summary

Step 3 now reproduces the prototype's Confirm & print view: green completion heading, the six summary rows, per-component results, the consumption note, write-back status with a Retry when OrgaTEX has not received it, Print ticket and Next batch, and a paper-style ticket preview with barcode. All operator-facing errors use plain messages, each screen is wrapped in an error boundary, and the terminal's F-keys work.

### Structure Overview

`DoneScreen` loads the summary and the ticket preview from the API, prints through the ticket endpoint and shows the ticket as last printed. `TicketPreview` renders the ticket data in the prototype's fixed-width layout with bars derived from the barcode value. `useFunctionKeys` maps F1–F4 per screen and is disabled while dialogs are open. `ErrorBoundary` (keyed by step) catches rendering failures and offers a way back to the queue.

### Completed Work

- [x] `frontend/src/api/schema.d.ts`, `api/types.ts`, `api/client.ts` - ticket preview and print
- [x] `frontend/src/features/ticket/DoneScreen.tsx` - Screen 3 (summary, results, write-back + Retry, print, next batch, F1/F3)
- [x] `frontend/src/features/ticket/TicketPreview.tsx`, `barcode.ts` - ticket preview and barcode bars
- [x] `frontend/src/shared/use-function-keys.ts` - F1–F4 handling with browser defaults suppressed
- [x] `frontend/src/shared/ErrorBoundary.tsx` - per-screen fallback with "Back to batch queue"
- [x] `frontend/src/shared/messages.ts` - complete code → plain message table (`KNOWN_CODES`)
- [x] `frontend/src/features/weighing/WeighScreen.tsx` - F1 confirm (only when allowed), F2 re-tare, F4 quit dialog
- [x] `frontend/src/App.tsx` - Screen 3 and error boundaries

### Key Decisions

- **Preview shows the ticket as last printed**: before the first print it shows the ticket that will print; afterwards it shows what was printed (an original stays unmarked, a reprint shows REPRINT).
- **F-keys respect the same rules as the buttons**: F1 confirms only when the API allows it.
- **Results table on Screen 3**: added to the prototype layout because the PDF requires required/actual/status per chemical (inception scope change).

### Deviations from Plan

None.

### Dependencies Added

None.

### Developer Notes

Browser run (no console errors): five components confirmed with **F1**, Screen 3 shows 5 of 5 · YES · 35.322 kg · R. Karim · "CONFIRMED HH:MM:SS"; F1 prints "Ticket printed · TKT-…", second print "Reprint printed" with REPRINT on the ticket; F3 returns to the queue where B-24187 now shows WEIGHED. Evidence: STEP-26-ui.png, STEP-27-ticket.png.

### Stage checkpoint (delegated, self-validated)

Deliverables complete; type check, lint and format clean; verified in a real browser. **Approved** — proceed to Test.
