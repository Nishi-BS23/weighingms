---
stage: plan
bolt: 008-weighing-station-ui
created: 2026-10-26T08:59:40Z
---

## Implementation Plan: 006-weighing-station-ui (bolt 2 of 4) — Screen 2 · Weigh

### Objective
Reproduce the prototype's Weigh screen on top of the session API: recipe rail, weigh header with lot/container/tare and scale badge, live readout, progress bar with tolerance band and target line, status line, surplus panel (Step 24 rule), action keys with quit/override dialogs; wire session start on selection, the operator badge dialog, and the training simulation buttons (Workbook Steps 20–25).

### 1. What will change
- Selecting a batch now starts or resumes a weighing session (`POST /api/sessions`) and opens Screen 2.
- `RecipePreview` is replaced by the full Weigh screen.
- Operator chip opens a badge sign-in dialog.
- "Simulate dispense / overshoot / Reset" drive the active component's training scale.
- Completion moves to step 3 (full Screen 3 in bolt 010).

### 2. Files to be created / modified
- `frontend/src/api/schema.d.ts` (regenerated), `api/types.ts`, `api/client.ts` (session, live, actions, operator, training endpoints)
- `frontend/src/features/weighing/WeighScreen.tsx` — container: session state, live polling (~120 ms), actions, dialogs
- `frontend/src/features/weighing/RecipeRail.tsx`, `WeighHeader.tsx`, `Readout.tsx`, `ProgressBar.tsx` (+ `bar-geometry.ts`), `StatusLine.tsx`, `SurplusPanel.tsx`, `WeighingActions.tsx`
- `frontend/src/shared/Dialog.tsx`; `features/weighing/QuitDialog.tsx`, `OverrideDialog.tsx`; `features/chrome/OperatorDialog.tsx`
- `frontend/src/shared/messages.ts` — codes for confirm/override/quit errors (extended)
- `frontend/src/App.tsx` — session flow, operator dialog, simulation wiring (modified)
- `frontend/src/features/weighing/RecipePreview.tsx` — removed
- Tests: component tests next to each component

### 3. Requirements and stories implemented
| Story | Requirements |
|-------|--------------|
| 004-recipe-rail | FR-31, FR-3, FR-15 |
| 005-live-weighing-panel | FR-31, FR-4 – FR-12 |
| 006-weighing-actions | FR-31, FR-13, FR-7, FR-22, FR-21 |
| 007-overshoot-surplus-panel | FR-31, FR-14 |
| (from bolt 005) operator badge dialog | FR-19 |

### 4. APIs involved
`POST /api/sessions`, `GET /api/sessions/{id}`, `POST /api/sessions/{id}/components/{cid}/activate`, `GET /api/sessions/{id}/live`, `POST /api/sessions/{id}/retare|confirm|override|quit`, `GET /api/operators/current`, `POST /api/operators/sign-in`, `POST /api/training/simulate`, `POST /api/training/reset-weighing`.

### 5. How it will be tested
- Vitest: rail states and activation (pending clickable, done not); bar geometry maths; readout per zone incl. OFFLINE "—"; status line texts; surplus panel only when OVER with guidance; Confirm disabled unless `canConfirm`; quit and override dialogs send the right requests and show errors; operator dialog.
- Real browser (headless Chromium): Workbook evidence screenshots — Step 20 weigh screen, Step 21 scale switch (3 kg precision → 32 kg floor, units kg), Step 22 tolerance UI (93.4 / 93.5 / 94.6), Step 24 overshoot UI, Step 25 confirmation.

### Technical Approach
- UI renders only API values: zone, remaining, surplus, canConfirm, status text, guidance; it computes bar geometry only (coding standards, ADR-001).
- Live polling via `usePolling` (no overlapping requests), paused while a dialog submits and stopped when the session completes.
- Dialog shared component with focus on open and Escape to cancel.

### Acceptance Criteria
- [ ] Selecting B-24187 starts a session and shows Blue RSPL active with "DYE-1180 · LOT 2026-0341 · CONTAINER C-09 · TARE 214.0 g", "3 kg precision"
- [ ] Weighed now / Still to weigh / Target and the bar update live from the API; zones coloured with text
- [ ] Yellow RGB: 93.4 g → Confirm disabled; 93.5 / 94.0 / 94.5 → enabled; 94.6 → disabled + red surplus panel with guidance
- [ ] Sodium Sulphate → "32 kg floor", units kg, "TARE 1.850 kg"
- [ ] Confirm records and advances; Re-tare zeroes; Quit (confirmed) returns to the queue; override dialog works with PIN + reason
- [ ] Completing the 5th component moves to step 3
- [ ] `npm run check` green

### Checkpoint — plan review (delegated, self-validated)
Covers stories 004–007 and the deferred operator dialog; uses only the agreed API; preserves the prototype's layout and texts; testable in components and in a real browser. **APPROVE PLAN.**
