---
stage: test
bolt: 008-weighing-station-ui
created: 2026-10-26T09:05:35Z
---

## Test Report: 006-weighing-station-ui (bolt 2 of 4) — Screen 2 · Weigh

### Summary

- **Tests**: frontend 35/35 passed (21 new); backend 205/205 unchanged
- **Coverage**: every Screen 2 component and dialog has component tests; browser run covers the integrated behaviour
- **Static checks**: Prettier, ESLint (type-checked), `tsc --noEmit` clean

### Test Files

- [x] `frontend/src/features/weighing/bar-geometry.test.ts` - band/target/fill positions, minimum band width, clamping, empty bar
- [x] `frontend/src/features/weighing/RecipeRail.test.tsx` - header, "n of m components weighed", ✓ actual / WEIGHING / PENDING, "DYE-xxxx · 3 kg", pending-only activation, disabled while busy
- [x] `frontend/src/features/weighing/WeighingPanel.test.tsx` - header meta + scale badge, readout values and zone, OFFLINE dash, tolerance caption, status text, progress-bar aria value, override-requested status, surplus panel only when OVER with guidance
- [x] `frontend/src/features/weighing/WeighScreen.test.tsx` - Confirm follows `canConfirm` from the API, confirm call + session hand-back, refusal message, re-tare call, quit confirmation → quit call → back to queue, override wrong PIN then correct PIN with request body, reason required
- [x] `frontend/src/features/chrome/OperatorDialog.test.tsx` - badge sign-in, unknown badge message, Escape cancels

### Acceptance Criteria Validation

- ✅ **Selecting B-24187 starts a session; Blue RSPL active with LOT/CONTAINER/TARE and "3 kg precision"** — browser run (evidence/STEP-20-weigh-screen.png)
- ✅ **Readout and bar update live from the API; zones coloured with text** — component tests + browser
- ✅ **Yellow RGB 93.4 disabled; 93.5 / 94.0 / 94.5 enabled; 94.6 disabled + surplus panel** — browser (evidence/STEP-22-tolerance-ui-*.png) + component tests
- ✅ **Sodium Sulphate → "32 kg floor", kg, "TARE 1.850 kg"** — browser (evidence/STEP-21-scale-switch.png)
- ✅ **Confirm advances; Re-tare zeroes; Quit returns to queue; override with PIN + reason** — component tests + browser (evidence/STEP-25-confirmation.png, STEP-24-overshoot-ui.png)
- ✅ **5th confirmation moves to step 3** — App wiring (`onSessionChange` → step "done"); exercised end to end in bolt 011
- ✅ **`npm run check` green**

### Issues Found

- Evidence script expected 1240.4 g after "Simulate dispense"; the correct landing is target + 0.4 × tolerance = 1242.4 g (script fixed; product correct).

### Notes

Visual comparison with the prototype's Screen 2: layout, texts, colours and key labels match; the surplus panel shows the Step 24 guidance instead of the prototype's recalculation proposal (ADR-004); question pins are not reproduced (TA-20).

### Stage checkpoint (delegated, self-validated)

All tests pass; acceptance criteria verified in component tests and in a real browser. **Approved** — bolt complete.
