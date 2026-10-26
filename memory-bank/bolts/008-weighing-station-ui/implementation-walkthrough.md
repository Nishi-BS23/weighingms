---
stage: implement
bolt: 008-weighing-station-ui
created: 2026-10-26T09:03:43Z
---

## Implementation Walkthrough: 006-weighing-station-ui (bolt 2 of 4) — Screen 2 · Weigh

### Summary

Selecting a batch now starts or resumes its weighing session and opens Screen 2, which reproduces the prototype's weighing view on live API data: recipe rail, weigh header, scale badge, readout, progress bar with tolerance band and target line, status line, Step 24 surplus panel, and the Confirm / Re-tare / Quit / Supervisor override keys with their dialogs. The operator chip opens a badge sign-in dialog, and the training buttons drive the active component's simulated scale.

### Structure Overview

`WeighScreen` owns the session-facing behaviour (live polling every ~120 ms, actions, dialogs) and passes API data to presentational pieces in `WeighingPanel` and `RecipeRail`; the only arithmetic in the UI is bar geometry. `App` holds the session and step, starts sessions on selection, and wires the operator dialog and simulation controls. A shared `Dialog` renders modals inside the device screen.

### Completed Work

- [x] `frontend/src/api/schema.d.ts`, `api/types.ts`, `api/client.ts` - regenerated types; session, live, actions, operator and training-simulation calls
- [x] `frontend/src/features/weighing/WeighScreen.tsx` - Screen 2 container (live polling, confirm, re-tare, quit, override, activation)
- [x] `frontend/src/features/weighing/RecipeRail.tsx` - rail header, component states, pending-only activation
- [x] `frontend/src/features/weighing/WeighingPanel.tsx` - weigh header, readout, tolerance bar + caption + status line, surplus panel
- [x] `frontend/src/features/weighing/bar-geometry.ts` - display-only bar maths
- [x] `frontend/src/features/weighing/WeighingDialogs.tsx` - quit confirmation and supervisor override (PIN + reason)
- [x] `frontend/src/features/chrome/OperatorDialog.tsx` - badge sign-in
- [x] `frontend/src/shared/Dialog.tsx` - modal with Escape to cancel
- [x] `frontend/src/shared/messages.ts` - plain messages for confirm/override/quit/session errors
- [x] `frontend/src/App.tsx` - session flow, step reachability, operator dialog, simulation wiring
- [x] `frontend/src/features/weighing/RecipePreview.tsx` - removed (replaced by Screen 2)

### Key Decisions

- **Stale readings are ignored**: a live reading is shown only if it belongs to the active component, so switching components never flashes the previous weight.
- **Status line shows "OVERRIDE REQUESTED — AWAITING SUPERVISOR"** while the override dialog is open (prototype behaviour).
- **Surplus panel carries the Step 24 guidance** from the API instead of the prototype's recalculation proposal (ADR-004).
- **Operator chip**: `GET /api/operators/current` now exists, so the chip shows "R. Karim · Shift A" as in the prototype.

### Deviations from Plan

None. Function keys remain in bolt 010 (story 011) as planned.

### Dependencies Added

None.

### Developer Notes

Verified in headless Chromium (no console errors): dispense lands at 1242.4 g "WITHIN TOLERANCE"; Yellow RGB 93.4 → Confirm disabled, 93.5 / 94.0 / 94.5 → enabled, 94.6 → disabled with "OVER TOLERANCE — SURPLUS +0.6 g"; overshoot 96.4 g → surplus panel "+2.4 g (+2.6%)" + guidance; removing excess to 94.2 g → confirm → rail "✓ 94.2"; Sodium Sulphate → "32 kg floor", "CONTAINER D-03 · TARE 1.850 kg", "TOLERANCE ±0.120 kg (23.880 – 24.120)". Evidence: STEP-20, STEP-21 (×2), STEP-22 (×3), STEP-24, STEP-25 screenshots.

### Stage checkpoint (delegated, self-validated)

Deliverables complete; type check, lint and format clean; behaviour verified in a real browser against the prototype. **Approved** — proceed to Test.
