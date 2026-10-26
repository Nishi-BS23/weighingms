---
stage: plan
bolt: 010-weighing-station-ui
created: 2026-10-26T09:09:38Z
---

## Implementation Plan: 006-weighing-station-ui (bolt 3 of 4) — Screen 3, failure messages, function keys

### Objective
Reproduce the prototype's "3 · Confirm & print" view on the summary and ticket APIs (Workbook Steps 26–27), make every failure understandable to the operator, and make the F-keys printed on the buttons work.

### 1. What will change
- Step 3 shows the completion screen instead of the interim heading.
- Error codes map to plain messages everywhere; each screen sits in an error boundary.
- F1–F4 work on Screens 2 and 3.

### 2. Files to be created / modified
- `frontend/src/api/schema.d.ts` (regenerated), `api/types.ts`, `api/client.ts` — ticket preview and print
- `frontend/src/features/ticket/DoneScreen.tsx` — summary, results, write-back status + Retry, actions, ticket preview
- `frontend/src/features/ticket/TicketPreview.tsx`, `barcode.ts` — paper-style ticket with barcode bars from the barcode value
- `frontend/src/shared/ErrorBoundary.tsx`, `shared/use-function-keys.ts`
- `frontend/src/shared/messages.ts` — complete code → message table (modified)
- `frontend/src/features/weighing/WeighScreen.tsx` — F1/F2/F4 (modified); `App.tsx` — Screen 3 + boundaries (modified)
- Tests: `DoneScreen.test.tsx`, `TicketPreview.test.tsx`, `barcode.test.ts`, `messages.test.ts`, `use-function-keys.test.tsx`, `ErrorBoundary.test.tsx`

### 3. Requirements and stories implemented
| Story | Requirements |
|-------|--------------|
| 008-completion-summary-screen | FR-32, FR-16, FR-17, FR-23 |
| 009-ticket-preview-and-print | FR-32, FR-18 |
| 010-operator-facing-failure-messages | FR-20, FR-1, NFR-10 |
| 011-function-keys | FR-34 |

### 4. APIs involved
`GET /api/sessions/{id}/summary`, `POST /api/sessions/{id}/sync`, `GET /api/sessions/{id}/ticket`, `POST /api/sessions/{id}/ticket/print`; existing session endpoints for F-keys.

### 5. How it will be tested
- Vitest: summary rows (confirmed vs pending + Retry), results table, print success / printer down / reprint, Next batch; ticket preview fields and barcode; message table complete for all known codes; F-key dispatch and suppression while a dialog is open; error boundary fallback.
- Browser: Workbook evidence STEP-26-ui (written to OrgaTEX confirmed), STEP-27-ticket (preview + printed).

### Acceptance Criteria
- [ ] Screen 3 shows "Batch B-24187 weighed", 5 of 5, YES, 35.322 kg, elapsed, R. Karim, "CONFIRMED HH:MM:SS"
- [ ] Pending write-back shows PENDING + Retry, which turns it CONFIRMED
- [ ] Ticket preview matches the prototype; Print ticket prints, then reprints are marked
- [ ] Printer down → plain message, key stays available
- [ ] Next batch returns to Screen 1
- [ ] F1/F2/F4 on Screen 2 and F1/F3 on Screen 3 work; ignored while a dialog is open
- [ ] No codes/stack traces shown to operators; error boundary per screen
- [ ] `npm run check` green

### Checkpoint — plan review (delegated, self-validated)
Covers stories 008–011; uses only the agreed API; reproduces the prototype's Screen 3. **APPROVE PLAN.**
